from typing import List
from typing import Optional

from databases import Database
from fastapi import APIRouter, HTTPException
from starlette.responses import UJSONResponse

from crud.maintenance_record import get_multi, get, get_statu_stat
from db.conn_engine import META_URL
from model.log import MaintenanceRecordSchema

router = APIRouter()


@router.get(
    "/",
    response_class=UJSONResponse,
    response_model=List[Optional[MaintenanceRecordSchema]],
)
async def read_maintenance_record(
    skip: int = None, limit: int = None, asset_id: int = None
):
    """
    Get Warning List.
    """
    conn = Database(META_URL)
    items = await get_multi(conn=conn, skip=skip, limit=limit, asset_id=asset_id)
    return items


@router.get("/stat/", response_class=UJSONResponse)
async def read_maintenance_record_count_by_statu():
    """
    Get warning stats by ID.
    """
    conn = Database(META_URL)
    res = await get_statu_stat(conn=conn)
    if not res:
        raise HTTPException(status_code=400, detail="Item not found")
    return res


@router.get(
    "/{id}/", response_class=UJSONResponse, response_model=MaintenanceRecordSchema
)
async def read_maintenance_record_by_id(id: int):
    """
    Get warning log by ID.
    """
    conn = Database(META_URL)
    item = await get(conn=conn, id=id)
    if not item:
        raise HTTPException(status_code=400, detail="Item not found")
    return item
