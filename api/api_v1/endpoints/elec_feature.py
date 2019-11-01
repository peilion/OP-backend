from datetime import datetime
from typing import List

from databases import Database
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.responses import UJSONResponse

from core.dependencies import get_mp_mapper
from crud.feature import get_latest, get_multi, get
from db.conn_engine import STATION_URLS
from db_model import ElecFeature

router = APIRouter()


@router.get("/mp/{mp_id}/elec_feature/latest/", response_class=UJSONResponse)
async def read_the_latest_vibration_feature(
    mp_id: int,
    features: List[str] = Query(
        [
            "urms",
            "uthd",
            "umax_current",
            "umin_current",
            "ufrequency",
            "uamplitude",
            "uinitial_phase",
            "vrms",
            "vthd",
            "vmax_current",
            "vmin_current",
            "vfrequency",
            "vamplitude",
            "vinitial_phase",
            "wrms",
            "wthd",
            "wmax_current",
            "wmin_current",
            "wfrequency",
            "wamplitude",
            "winitial_phase",
            "n_rms",
            "p_rms",
            "z_rms",
            "imbalance",
            "health_indicator",
        ],
        description="Only these fileds can be returned now.",
    ),
    mp_mapper: dict = Depends(get_mp_mapper),
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info["type"] == 0:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect vibration data, try to use the approaprite endpoint.",
        )

    conn = Database(STATION_URLS[mp_shard_info["station_id"] - 1])

    res = await get_latest(
        conn=conn,
        shard_id=mp_shard_info["inner_id"],
        fileds=features,
        orm_model=ElecFeature,
    )
    return dict(res)


@router.get("/mp/{mp_id}/elec_feature/list/", response_class=UJSONResponse)
async def read_vibration_features(
    mp_id: int,
    time_before: datetime = Query(default="2016-07-01 00:00:00"),
    time_after: datetime = Query(default="2016-01-10 00:00:00"),
    features: List[str] = Query(
        [
            "urms",
            "uthd",
            "umax_current",
            "umin_current",
            "ufrequency",
            "uamplitude",
            "uinitial_phase",
            "vrms",
            "vthd",
            "vmax_current",
            "vmin_current",
            "vfrequency",
            "vamplitude",
            "vinitial_phase",
            "wrms",
            "wthd",
            "wmax_current",
            "wmin_current",
            "wfrequency",
            "wamplitude",
            "winitial_phase",
            "n_rms",
            "p_rms",
            "z_rms",
            "imbalance",
            "health_indicator",
        ],
        description="Only these fileds can be returned now.",
    ),
    limit: int = None,
    mp_mapper: dict = Depends(get_mp_mapper),
):
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
        fileds=features,
        time_before=str(time_before),
        time_after=str(time_after),
        limit=limit,
        orm_model=ElecFeature,
    )
    if not res:
        raise HTTPException(
            status_code=400, detail="No signal collected between the time range"
        )
    return res


@router.get("/mp/{mp_id}/elec_feature/{data_id}/", response_class=UJSONResponse)
async def read_vibration_feature_by_id(
    mp_id: int,
    data_id: int,
    features: List[str] = Query(
        [
            "urms",
            "uthd",
            "umax_current",
            "umin_current",
            "ufrequency",
            "uamplitude",
            "uinitial_phase",
            "vrms",
            "vthd",
            "vmax_current",
            "vmin_current",
            "vfrequency",
            "vamplitude",
            "vinitial_phase",
            "wrms",
            "wthd",
            "wmax_current",
            "wmin_current",
            "wfrequency",
            "wamplitude",
            "winitial_phase",
            "n_rms",
            "p_rms",
            "z_rms",
            "imbalance",
            "health_indicator",
        ],
        description="Only these fileds can be returned now.",
    ),
    mp_mapper: dict = Depends(get_mp_mapper),
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info["type"] == 0:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect vibration data, try to use the approaprite endpoint.",
        )

    conn = Database(STATION_URLS[mp_shard_info["station_id"] - 1])
    res = await get(
        conn=conn,
        shard_id=mp_shard_info["inner_id"],
        data_id=data_id,
        fileds=features,
        orm_model=ElecFeature,
    )
    return dict(res)
