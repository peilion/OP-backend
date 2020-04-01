from datetime import datetime
from typing import List

from databases import Database
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import ORJSONResponse

from core.dependencies import get_db
from crud.feature import get_latest, get_multi, get
from db_model import ElecFeature

router = APIRouter()
FEATURE_FIELDS = [
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
]


@router.get("/mp/{mp_id}/elec_feature/latest/", response_class=ORJSONResponse)
async def read_the_latest_elec_feature(
    mp_id: int,
    features: List[str] = Query(
        FEATURE_FIELDS, description="Only these fileds can be returned now."
    ),
    conn: Database = Depends(get_db),
):

    res = await get_latest(
        conn=conn,
        mp_id=mp_id,
        require_mp_type=1,
        fileds=features,
        orm_model=ElecFeature,
    )
    return dict(res)


@router.get("/mp/{mp_id}/elec_feature/list/", response_class=ORJSONResponse)
async def read_elec_features(
    mp_id: int,
    features: List[str] = Query(
        FEATURE_FIELDS, description="Only these fileds can be returned now."
    ),
    time_before: datetime = Query(None, description="e.x. 2016-01-05 00:00:00"),
    time_after: datetime = Query(None, description="e.x. 2016-01-01 00:00:00"),
    limit: int = None,
    conn: Database = Depends(get_db),
):
    res = await get_multi(
        conn=conn,
        mp_id=mp_id,
        require_mp_type=1,
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


@router.get("/mp/{mp_id}/elec_feature/{data_id}/", response_class=ORJSONResponse)
async def read_elec_feature_by_id(
    mp_id: int,
    data_id: int,
    features: List[str] = Query(
        FEATURE_FIELDS, description="Only these fileds can be returned now."
    ),
    conn: Database = Depends(get_db),
):
    res = await get(
        conn=conn,
        mp_id=mp_id,
        require_mp_type=1,
        data_id=data_id,
        fileds=features,
        orm_model=ElecFeature,
    )
    return dict(res)
