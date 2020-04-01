from typing import List
from typing import Optional

from databases import Database
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import ORJSONResponse

from core.dependencies import get_db
from crud.maintenance_record import get_multi, get, get_statu_stat
from model.log import MaintenanceRecordSchema

router = APIRouter()


@router.get(
    "/",
    response_class=ORJSONResponse,
    response_model=List[Optional[MaintenanceRecordSchema]],
)
async def read_maintenance_record(
    skip: int = None,
    limit: int = None,
    asset_id: int = None,
    conn: Database = Depends(get_db),
):
    """
    Get Warning List.
    """
    items = await get_multi(conn=conn, skip=skip, limit=limit, asset_id=asset_id)
    return items


@router.get("/stat/", response_class=ORJSONResponse)
async def read_maintenance_record_count_by_statu(conn: Database = Depends(get_db)):
    """
    Get warning stats by ID.
    """
    res = await get_statu_stat(conn=conn)
    if not res:
        raise HTTPException(status_code=400, detail="Item not found")
    return res


@router.get(
    "/{id}/", response_class=ORJSONResponse, response_model=MaintenanceRecordSchema
)
async def read_maintenance_record_by_id(id: int, conn: Database = Depends(get_db)):
    """
    Get warning log by ID.
    """

    item = await get(conn=conn, id=id)
    if not item:
        raise HTTPException(status_code=400, detail="Item not found")
    return item
