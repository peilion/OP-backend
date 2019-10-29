from typing import List
from typing import Optional

from databases import Database
from fastapi import APIRouter, HTTPException
from starlette.responses import UJSONResponse

from crud.maintenance_record import get_multi, get
from db.conn_engine import META_URL
from model.maintenace_record import MaintenanceRecord

router = APIRouter()


@router.get("/", response_class=UJSONResponse, response_model=List[Optional[MaintenanceRecord]])
async def read_maintenance_record(
        skip: int = None,
        limit: int = None,
        asset_id: int = None
):
    """
    Get Warning List.
    """
    conn = Database(META_URL)
    items = await get_multi(conn=conn, skip=skip, limit=limit, asset_id=asset_id)
    return items


@router.get("/{id}/", response_class=UJSONResponse, response_model=MaintenanceRecord)
async def read_maintenance_record_by_id(
        id: int,
):
    """
    Get warning log by ID.
    """
    conn = Database(META_URL)
    item = await get(conn=conn, id=id)
    if not item:
        raise HTTPException(status_code=400, detail="Item not found")
    return item
