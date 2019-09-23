from typing import List

from databases import Database
from fastapi import APIRouter, HTTPException
from starlette.responses import UJSONResponse
from crud.warning import get_multi, get, get_warning_calendar, get_warning_stat_by_station,get_warning_stat_by_asset
from db.conn_engine import  META_URL
from model.warning import WarningLogSchema
from typing import Optional
from enum import Enum

router = APIRouter()


class GroupRule(str, Enum):
    date = "date"
    station = "station"
    asset = "asset"


@router.get("/", response_class=UJSONResponse, response_model=List[Optional[WarningLogSchema]])
async def read_warning_logs(
        skip: int = None,
        limit: int = None,
        asset_id: int = None
):
    """
    Get Warning List.
    """
    conn = Database(META_URL)
    items = await get_multi(conn=conn, skip=skip, limit=limit, asset_id=asset_id)
    return items


@router.get("/stat", response_class=UJSONResponse)
async def read_warning_logs_statistic(
        group_by: GroupRule,
):
    """
    Response Schema:

    - if **group_by = date**: [[date,warning number in this date],...]
    - if **group_by = station**: [[station_id,warning number in this station],...]
    - if **group_by = asset**: [[asset_id,warning number of this asset],...]
    """
    conn = Database(META_URL)

    if group_by == GroupRule.date:
        item = await get_warning_calendar(conn=conn)
        return item

    if group_by == GroupRule.station:
        item = await get_warning_stat_by_station(conn=conn)
        return item

    if group_by == GroupRule.asset:
        item = await get_warning_stat_by_asset(conn=conn)
        return item
    else:
        raise HTTPException(status_code=400, detail="Bad query parameters")

@router.get("/{id}", response_class=UJSONResponse, response_model=WarningLogSchema)
async def read_warning_logs_by_id(
        id: int,
):
    """
    Get warning log by ID.
    """
    conn = Database(META_URL)
    item = await get(conn=conn, id=id)
    if not item:
        raise HTTPException(status_code=400, detail="Item not found")
    return item
