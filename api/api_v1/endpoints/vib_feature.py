from datetime import datetime
from typing import List

from databases import Database
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import ORJSONResponse

from core.dependencies import get_db
from crud.feature import get_latest, get_multi, get
from db_model import VibFeature

router = APIRouter()


@router.get("/mp/{mp_id}/vib_feature/latest/", response_class=ORJSONResponse)
async def read_the_latest_vibration_feature(
    mp_id: int,
    features: List[str] = Query(
        ["rms", "max", "p2p", "avg", "var", "kurtosis"],
        description="Only these fileds can be returned now.",
    ),
    conn: Database = Depends(get_db),
):

    res = await get_latest(
        conn=conn,
        mp_id=mp_id,
        require_mp_type=0,
        fileds=features,
        orm_model=VibFeature,
    )
    return dict(res)


@router.get("/mp/{mp_id}/vib_feature/list/", response_class=ORJSONResponse)
async def read_vibration_features(
    mp_id: int,
    time_before: datetime = Query(None, description="e.x. 2016-07-01 00:00:00"),
    time_after: datetime = Query(None, description="e.x. 2016-01-01 00:00:00"),
    features: List[str] = Query(
        ["rms", "max", "p2p", "avg", "var", "kurtosis", "similarity"],
        description="Only these fileds can be returned now.",
    ),
    limit: int = None,
    with_estimated: bool = False,
    conn: Database = Depends(get_db),
):
    res = await get_multi(
        conn=conn,
        mp_id=mp_id,
        require_mp_type=0,
        fileds=features,
        time_before=str(time_before),
        time_after=str(time_after),
        limit=limit,
        with_estimated=with_estimated,
        orm_model=VibFeature,
    )
    if not res:
        raise HTTPException(
            status_code=400, detail="No signal collected between the time range"
        )
    return res


@router.get("/mp/{mp_id}/vib_feature/{data_id}/", response_class=ORJSONResponse)
async def read_vibration_feature_by_id(
    mp_id: int,
    data_id: int,
    features: List[str] = Query(
        ["rms", "max", "p2p", "avg", "var", "kurtosis"],
        description="Only these fileds can be returned now.",
    ),
    conn: Database = Depends(get_db),
):
    res = await get(
        conn=conn,
        mp_id=mp_id,
        require_mp_type=0,
        data_id=data_id,
        fileds=features,
        orm_model=VibFeature,
    )
    return dict(res)
