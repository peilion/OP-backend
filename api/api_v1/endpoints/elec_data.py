from datetime import datetime
from typing import List

from databases import Database
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.responses import UJSONResponse

from core.dependencies import get_mp_mapper
from crud.data import get_latest, get_by_id, get_multi
from db.conn_engine import STATION_URLS
from db_model import ElecData
from model.elec_data import ElecSignalListSchema, ElecSignalSchema
from utils.vib_feature_tools import fftransform

router = APIRouter()


@router.get(
    "/mp/{mp_id}/elec/latest/",
    response_class=UJSONResponse,
    response_model=ElecSignalSchema,
)
async def read_the_latest_electric_signal(
    mp_id: int, mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info["type"] == 0:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect vibration data, try to use the approaprite endpoint.",
        )

    conn = Database(STATION_URLS[mp_shard_info["station_id"] - 1])
    res = await get_latest(
        conn=conn, shard_id=mp_shard_info["inner_id"], orm_model=ElecData
    )
    final = {}
    for phase in ["u", "v", "w"]:
        processed_res = fftransform(res[phase + "cur"])
        final[phase + "cur"] = processed_res["vib"]
        final[phase + "fft"] = processed_res["spec"][:300]
    return {**final, **{"id": res["id"], "time": res["time"]}}


@router.get(
    "/mp/{mp_id}/elec/all/",
    response_class=UJSONResponse,
    response_model=List[ElecSignalListSchema],
)
async def read_all_electric_signal_info(
    mp_id: int,
    time_before: datetime = Query(default="2016-01-01 00:00:00"),
    time_after: datetime = Query(default="2016-07-10 00:00:00"),
    mp_mapper: dict = Depends(get_mp_mapper),
):
    """
    Diagnosis info will be joined to the response in the future.
    """
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info["type"] == 0:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect vibration data, try to use the approaprite endpoint.",
        )

    conn = Database(STATION_URLS[mp_shard_info["station_id"] - 1])
    res = await get_multi(
        conn=conn,
        shard_id=mp_shard_info["inner_id"],
        time_before=time_before,
        time_after=time_after,
        orm_model=ElecData,
    )
    if not res:
        raise HTTPException(
            status_code=400, detail="No signal collected between the time range"
        )
    return [dict(row) for row in res]


@router.get(
    "/mp/{mp_id}/elec/{data_id}/",
    response_class=UJSONResponse,
    response_model=ElecSignalSchema,
)
async def read_electric_signal_by_id(
    mp_id: int, data_id: int, mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info["type"] == 0:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect vibration data, try to use the approaprite endpoint.",
        )

    conn = Database(STATION_URLS[mp_shard_info["station_id"] - 1])
    res = await get_by_id(
        conn=conn,
        shard_id=mp_shard_info["inner_id"],
        data_id=data_id,
        orm_model=ElecData,
    )

    final = {}
    for phase in ["u", "v", "w"]:
        processed_res = fftransform(res[phase + "cur"])
        final[phase + "cur"] = processed_res["vib"]
        final[phase + "fft"] = processed_res["spec"][:300]
    return {**final, **{"id": res["id"], "time": res["time"]}}
