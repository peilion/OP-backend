from typing import List, Optional

from databases import Database
from fastapi import APIRouter

from crud.stations import get_bc, get_rc
from db.conn_engine import META_URL
from model.organizations import BranchSchema, RegionSchema

router = APIRouter()

@router.get("/branch_companies", response_model=List[Optional[BranchSchema]])
async def read_branch_companies(
        skip: int = 0,
        limit: int = None,
):
    """
    Get Asset List.
    """
    conn = Database(META_URL)
    items = await get_bc(conn=conn, skip=skip, limit=limit)
    return items

@router.get("/region_companies", response_model=List[Optional[RegionSchema]])
async def read_region_companies(
        skip: int = 0,
        limit: int = None,
):
    """
    Get Asset List.
    """
    conn = Database(META_URL)
    items = await get_rc(conn=conn, skip=skip, limit=limit)
    return items