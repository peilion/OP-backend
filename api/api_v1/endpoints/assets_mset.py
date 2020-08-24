from typing import List, Optional

from databases import Database
from fastapi import APIRouter, Query, Depends
from fastapi.responses import ORJSONResponse

from core.dependencies import get_db
from crud.assets_hi import (
    get_similarity_threshold_during_time,
    get_estimated_value_multi,
    get_estimated_value_by_id,
    get_similarity_threshold_recently,
    get_similarity_threshold_near_by)
from db import session_make
from db.conn_engine import meta_engine
from model.assets import MSETSimilaritySchema

router = APIRouter()


@router.get(
    "/{asset_id}/mset/",
    response_class=ORJSONResponse,
    response_model=MSETSimilaritySchema,
)
async def read_asset_similarities_and_threshold(
    asset_id: int = None,
    time_before: str = Query(None, description="e.x. 2016-07-01 00:00:00"),
    time_after: str = Query(None, description="e.x. 2016-01-10 00:00:00"),
    limit: int = Query(None),
    near_by: int = Query(None),
    conn: Database = Depends(get_db),
):
    """
    Get feature similarities and dynamic thresholds.
    """
    if limit:
        items = await get_similarity_threshold_recently(
            conn=conn, asset_id=asset_id, limit=limit
        )
    elif near_by:
        items = await get_similarity_threshold_near_by(
            conn=conn, asset_id=asset_id, data_id=near_by
        )
    else:
        items = await get_similarity_threshold_during_time(
            conn=conn,
            asset_id=asset_id,
            time_before=time_before,
            time_after=time_after,
        )

    return items


@router.get("/{asset_id}/est/", response_class=ORJSONResponse)
async def read_asset_similarities_and_threshold(
    asset_id: int = None,
    time_before: str = Query(None, description="e.x. 2016-07-01 00:00:00"),
    time_after: str = Query(None, description="e.x. 2016-01-10 00:00:00"),
    conn: Database = Depends(get_db),
):
    """
    Get feature similarities and dynamic thresholds.
    """
    items = await get_estimated_value_multi(
        conn=conn, asset_id=asset_id, time_before=time_before, time_after=time_after,
    )

    return items


@router.get("/{asset_id}/est/{id}/", response_class=ORJSONResponse)
async def read_asset_similarities_and_threshold(
    id: int, asset_id: int = None, conn: Database = Depends(get_db),
):
    """
    Get feature similarities and dynamic thresholds.
    """
    items = await get_estimated_value_by_id(conn=conn, asset_id=asset_id, data_id=id)

    return items
