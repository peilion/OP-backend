from typing import List, Optional

from databases import Database
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import ORJSONResponse

from core.dependencies import get_db
from crud.stations import get_multi, get, get_tree, get_weathers
from model.organizations import StationSchema, StationWeatherSchema

router = APIRouter()


@router.get(
    "/", response_model=List[Optional[StationSchema]], response_class=ORJSONResponse
)
async def read_stations(
    skip: int = 0, limit: int = None, conn: Database = Depends(get_db)
):
    """
    Get Asset List.
    """

    items = await get_multi(conn=conn, skip=skip, limit=limit)
    return items


@router.get("/tree/", response_class=ORJSONResponse)
async def read_station_tree(conn: Database = Depends(get_db)):
    """
    Get Asset by ID.
    """
    item = await get_tree(conn=conn)
    if not item:
        raise HTTPException(status_code=400, detail="Item not found")
    return item


@router.get(
    "/weather/",
    response_class=ORJSONResponse,
    response_model=List[Optional[StationWeatherSchema]],
)
async def read_stations_weather(conn: Database = Depends(get_db)):
    """
    Get Asset List.
    """

    items = await get_weathers(conn=conn)
    return items


@router.get(
    "/{id}/", response_class=ORJSONResponse, response_model=Optional[StationSchema]
)
async def read_station_by_id(id: int, conn: Database = Depends(get_db)):
    """
    Get Station by ID.
    """
    item = await get(conn=conn, id=id)
    if not item:
        raise HTTPException(status_code=400, detail="Item not found")
    return item
