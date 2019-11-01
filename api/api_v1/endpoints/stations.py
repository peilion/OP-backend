from typing import List, Optional

from databases import Database
from fastapi import APIRouter, HTTPException

from crud.stations import get_multi, get, get_tree
from db.conn_engine import META_URL
from model.organizations import StationSchema

router = APIRouter()


@router.get("/", response_model=List[Optional[StationSchema]])
async def read_stations(skip: int = 0, limit: int = None):
    """
    Get Asset List.
    """
    conn = Database(META_URL)
    items = await get_multi(conn=conn, skip=skip, limit=limit)
    return items


@router.get("/tree/")
async def read_station_tree():
    """
    Get Asset by ID.
    """
    conn = Database(META_URL)
    item = await get_tree(conn=conn)
    if not item:
        raise HTTPException(status_code=400, detail="Item not found")
    return item


@router.get("/{id}/", response_model=Optional[StationSchema])
async def read_station_by_id(id: int,):
    """
    Get Asset by ID.
    """
    conn = Database(META_URL)
    item = await get(conn=conn, id=id)
    if not item:
        raise HTTPException(status_code=400, detail="Item not found")
    return item
