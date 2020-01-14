from typing import List, Optional

from databases import Database
from fastapi import APIRouter, HTTPException, Depends

from core.dependencies import get_db
from crud.stations import get_multi, get, get_tree
from model.organizations import StationSchema

router = APIRouter()


@router.get("/", response_model=List[Optional[StationSchema]])
async def read_stations(
    skip: int = 0, limit: int = None, conn: Database = Depends(get_db)
):
    """
    Get Asset List.
    """

    items = await get_multi(conn=conn, skip=skip, limit=limit)
    return items


@router.get("/tree/")
async def read_station_tree(conn: Database = Depends(get_db)):
    """
    Get Asset by ID.
    """
    item = await get_tree(conn=conn)
    if not item:
        raise HTTPException(status_code=400, detail="Item not found")
    return item


@router.get("/{id}/", response_model=Optional[StationSchema])
async def read_station_by_id(id: int, conn: Database = Depends(get_db)):
    """
    Get Station by ID.
    """
    item = await get(conn=conn, id=id)
    if not item:
        raise HTTPException(status_code=400, detail="Item not found")
    return item
