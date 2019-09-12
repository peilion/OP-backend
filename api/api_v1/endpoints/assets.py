from typing import List, Optional

from databases import Database
from fastapi import APIRouter, HTTPException

from crud.assets import get_multi, get
from db.conn_engine import META_URL
from model.assets import Asset

router = APIRouter()


@router.get("/", response_model=List[Optional[Asset]])
async def read_assets(
        skip: int = 0,
        limit: int = None,
):
    """
    Get Assets.
    """
    conn = Database(META_URL)
    items = await get_multi(conn=conn, skip=skip, limit=limit)
    return items


@router.get("/{id}", response_model=Optional[Asset])
async def read_asset_by_id(
        id: int,
):
    """
    Get Asset by ID.
    """
    conn = Database(META_URL)
    item = await get(conn=conn, id=id)
    if not item:
        raise HTTPException(status_code=400, detail="Item not found")
    return item
