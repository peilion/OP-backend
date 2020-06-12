from enum import Enum
from typing import List, Any
from typing import Optional

import numpy as np
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import ORJSONResponse
from starlette.responses import JSONResponse

from core.dependencies import get_db
from crud.warning import *
from db_model import VibData
from model.log import WarningLogSchema, WarningDetailSchema, WarningData
from crud.data import get_by_id as get_data_by_id
from services.signal.vibration.vibration_class import VibrationSignal

router = APIRouter()


class GroupRule(str, Enum):
    date = "date"
    station = "station"
    asset = "asset"
    isread = "isread"
    branch = "branch"
    region = "region"
    period = "period"


class FaultRule(str, Enum):
    ub = "不平衡故障"
    ma = "不对中故障"
    bw = "滚动轴承故障"
    al = "A类松动"
    bl = "B类松动"
    sg = "喘振故障"
    rb = "碰磨故障"


@router.get(
    "/", response_class=ORJSONResponse, response_model=List[Optional[WarningLogSchema]]
)
async def read_warning_logs(
    skip: int = None,
    limit: int = None,
    asset_id: int = None,
    isread: bool = None,
    conn: Database = Depends(get_db),
):
    """
    Get Warning List.
    """
    items = await get_multi(
        conn=conn, skip=skip, limit=limit, asset_id=asset_id, isread=isread
    )
    return items


@router.get("/stat/", response_class=ORJSONResponse)
async def read_warning_logs_statistic(
    group_by: GroupRule, conn: Database = Depends(get_db)
):
    """
    Response Schema:

    - if **group_by = date**: [[date,warning number in this date],...]
    - if **group_by = station/region/company**: return two fields 'labels' and 'series' for pie chart drawing.
    - if **group_by = asset**: [[asset_id,warning number of this asset],...]
    - if **group_by = isread**: [[ 0,unread warninglog],[1,read warninglog]]

    """

    if group_by == GroupRule.date:
        res = await get_warning_calendar(conn=conn)
        return res
    elif group_by == GroupRule.station:
        res = await get_warning_stat_by_station(conn=conn)
        return res
    elif group_by == GroupRule.asset:
        res = await get_warning_stat_by_asset(conn=conn)
        return res
    elif group_by == GroupRule.isread:
        res = await get_warning_stat_by_isreadable(conn=conn)
        return res
    elif group_by == GroupRule.branch:
        res = await get_warning_stat_by_branch_company(conn=conn)
        return res
    elif group_by == GroupRule.region:
        res = await get_warning_stat_by_region_company(conn=conn)
        return res
    elif group_by == GroupRule.period:
        res = await get_warning_stat_by_period(conn=conn)
        return res
    else:
        raise HTTPException(status_code=400, detail="Bad query parameters")


@router.get("/data/", response_class=ORJSONResponse, response_model=WarningData)
async def read_warning_log_data_by_id(
    data_id: int, mp_id: int, fault_mode: FaultRule, conn: Database = Depends(get_db)
):
    """
    Get warning log data by ID and fault pattern.
    """
    data = await get_data_by_id(
        conn=conn, mp_id=mp_id, orm_model=VibData, require_mp_type=0, data_id=data_id,
    )
    if not data:
        raise HTTPException(status_code=400, detail="Item not found")
    signal = VibrationSignal(
        data=np.fromstring(data["ima"], dtype=np.float32), fs=10000, type=2
    )

    if (
        fault_mode == FaultRule.ub
        or fault_mode == FaultRule.ma
        or fault_mode == FaultRule.al
        or fault_mode == FaultRule.bl
        or fault_mode == FaultRule.rb
    ):
        signal = signal.to_velocity(detrend_type="poly")
        signal.compute_spectrum()
        return {"spec": signal.spec, "freq": signal.freq}
    if fault_mode == FaultRule.bw:
        signal = signal.to_filted_signal(
            filter_type="highpass", co_frequency=2 * 1000 / 10000
        ).to_envelope()
        signal.compute_spectrum()
        return {"spec": signal.spec, "freq": signal.freq}
    if fault_mode == FaultRule.sg:
        signal.compute_spectrum()
        return {"spec": signal.spec, "freq": signal.freq}


@router.get("/{id}/", response_class=ORJSONResponse, response_model=WarningDetailSchema)
async def read_warning_logs_by_id(id: int, conn: Database = Depends(get_db)):
    """
    Get warning log by ID.
    """
    item = await get(conn=conn, id=id)
    if not item:
        raise HTTPException(status_code=400, detail="Item not found")
    return item
