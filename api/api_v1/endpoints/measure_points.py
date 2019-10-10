from enum import Enum
from typing import List, Optional

from databases import Database
from fastapi import APIRouter, HTTPException, Query
from starlette.responses import UJSONResponse

from crud.measuer_points import get_multi, get, get_stat
from db.conn_engine import META_URL
from model.measure_points import MeasurePointSchema

router = APIRouter()


class GroupRule(str, Enum):
    statu = "statu"
    station = "station"
    asset = "asset"


@router.get("/", response_class=UJSONResponse,
            response_model=List[Optional[MeasurePointSchema]])
async def read_measure_points(
        skip: int = None,
        limit: int = None,
        brief: bool = False,
        station_id: int = Query(default=None, description='Filtering measure points with station\'s id'),
        asset_id: int = Query(default=None,
                              description='Filtering measure points with asset\'s id , **only one of the two filtering conditions shuold be given**'),
):
    if station_id and asset_id:
        raise HTTPException(
            status_code=400,
            detail="Only one of station_id and asset_id should be given.")
    conn = Database(META_URL)
    item = await get_multi(conn=conn, skip=skip, limit=limit, brief=brief, station_id=station_id, asset_id=asset_id)
    return item


@router.get("/stat/", response_class=UJSONResponse)
async def read_measure_point_statistic_report(
        rule: GroupRule = Query(default=None, description='Rule to generate statistic report.')
):
    conn = Database(META_URL)
    res = await get_stat(conn=conn, rule=rule.value)
    return [dict(row) for row in res]


@router.get("/{id}/", response_class=UJSONResponse,
            response_model=Optional[MeasurePointSchema])
async def read_measure_point_by_id(
        id: int
):
    conn = Database(META_URL)
    item = await get(conn=conn, id=id)
    if not item:
        raise HTTPException(status_code=400, detail="Measure point not found")
    return item
