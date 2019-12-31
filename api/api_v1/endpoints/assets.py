from enum import Enum
from typing import List, Optional

from databases import Database
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from starlette.responses import UJSONResponse

from crud.assets import get_multi, get, get_info, create, get_cards
from crud.assets_hi import (
    get_avg_hi_during_time,
    get_avg_hi_pre,
    get_avg_hi_before_limit,
    get_avg_hi_multi,
    get_avg_hi_limit_latest,
)

from db import session_make
from db.conn_engine import meta_engine, META_URL
from model.assets import (
    FlattenAssetSchema,
    FlattenAssetListSchema,
    AssetPostSchema,
    AssetCardSchema,
)
from services.query_processors.asset import tree_list_format

router = APIRouter()


@router.get("/", response_class=UJSONResponse)
async def read_assets(
    skip: int = None,
    limit: int = None,
    iftree: bool = False,
    type: int = None,
    level: int = None,
    station_name: str = None,
    station_id: int = None,
):
    """
    Get Asset List.
    """
    conn = Database(META_URL)
    items = await get_multi(
        conn=conn,
        skip=skip,
        limit=limit,
        type=type,
        level=level,
        station_name=station_name,
        station_id=station_id,
    )
    if not iftree:
        return FlattenAssetListSchema(asset=items)
    elif iftree:
        return tree_list_format(items)
    # return NestAssetListSchema(asset=res)


@router.get(
    "/cards/",
    response_class=UJSONResponse,
    response_model=Optional[List[Optional[AssetCardSchema]]],
)
async def read_assets_card(skip: int = None, limit: int = None):
    """
    Get Asset List.
    """
    conn = Database(META_URL)
    items = await get_cards(conn=conn, skip=skip, limit=limit)
    items = await get_avg_hi_limit_latest(
        conn=conn, assets=[dict(item) for item in items], limit=20
    )
    return items
    # return NestAssetListSchema(asset=res)


@router.get("/{id}/", response_class=UJSONResponse, response_model=FlattenAssetSchema)
async def read_by_id(id: int):
    """
    Get Asset by ID.
    """
    conn = Database(META_URL)
    res = await get(conn=conn, id=id)
    if not res:
        raise HTTPException(status_code=400, detail="Item not found")
    return res


@router.get("/{id}/info/", response_class=UJSONResponse)
async def read_asset_info(id: int,):
    """
    Get Asset Info by ID.
    """
    conn = Database(META_URL)
    session = session_make(meta_engine)
    info = await get_info(session=session, conn=conn, id=id)
    if not info:
        raise HTTPException(
            status_code=400,
            detail="Item not found. / Asset Information have not been record.",
        )
    return dict(info)


@router.get("/{id}/avghi/", response_class=UJSONResponse)
async def read_asset_avghi(
    id: int,
    time_before: str = Query(None, description="e.x. 2016-07-01 00:00:00"),
    time_after: str = Query(None, description="e.x. 2016-01-10 00:00:00"),
    interval: int = None,
    limit: int = None,
    pre_query: bool = True,
):
    """
    Get avg Asset HI by time range and interval.
    """
    conn = Database(META_URL)
    if pre_query:
        res = await get_avg_hi_pre(conn=conn)
        return res
    if not pre_query:
        if (limit is not None) & (interval is not None):
            res = await get_avg_hi_before_limit(
                conn=conn, asset_id=id, interval=interval, limit=limit
            )

        elif (limit is None) & (interval is not None):
            res = await get_avg_hi_during_time(
                conn=conn,
                asset_id=id,
                time_before=time_before,
                time_after=time_after,
                interval=interval,
            )
        elif (limit is not None) & (interval is None):
            res = await get_avg_hi_multi(
                conn=conn, asset_id=id, time_before=time_before, limit=limit
            )

        if not res["time_list"]:
            raise HTTPException(
                status_code=200,
                detail="No health indicator calculated in the time range",
            )
        return res


@router.post("/", response_class=UJSONResponse)
async def create_asset(asset: AssetPostSchema):
    try:
        conn = Database(META_URL)
        res = await create(conn=conn, data=asset)
        if res == True:
            return {"msg": "Asset successfully added."}
        else:
            raise HTTPException(
                status_code=409, detail="Error happened when creating table."
            )
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Conflict asset already exsit in the database."
        )
    # finally:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Unexpected error.")
