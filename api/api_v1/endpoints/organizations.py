from typing import List, Optional

from databases import Database
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from core.dependencies import get_db
from crud.stations import get_bc, get_rc
from model.organizations import BranchSchema, RegionSchema

router = APIRouter()


@router.get(
    "/branch_companies",
    response_model=List[Optional[BranchSchema]],
    response_class=ORJSONResponse,
)
async def read_branch_companies(
    skip: int = 0, limit: int = None, conn: Database = Depends(get_db)
):
    """
    Get Asset List.
    """

    items = await get_bc(conn=conn, skip=skip, limit=limit)
    return items


@router.get(
    "/region_companies",
    response_model=List[Optional[RegionSchema]],
    response_class=ORJSONResponse,
)
async def read_region_companies(
    skip: int = 0, limit: int = None, conn: Database = Depends(get_db)
):
    """
    Get Asset List.
    """

    items = await get_rc(conn=conn, skip=skip, limit=limit)
    return items
