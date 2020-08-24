from typing import List, Optional

from databases import Database
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from core.dependencies import get_db
from crud.union import get_recent_asset_event, get_recent_warning, get_warning_table
from model.log import WarningAndMainteSchema, WarningTableSchema

router = APIRouter()


@router.get(
    "/warning/",
    response_class=ORJSONResponse,
    response_model=List[Optional[WarningAndMainteSchema]],
)
async def read_warning_and_mset_warning(conn: Database = Depends(get_db)):
    res = await get_recent_warning(conn=conn)
    return res

@router.get(
    "/warning/table/",
    response_class=ORJSONResponse,
    response_model=List[Optional[WarningTableSchema]],
)
async def read_warning_table(conn: Database = Depends(get_db)):
    res = await get_warning_table(conn=conn)
    return res

@router.get(
    "/event/{id}/",
    response_class=ORJSONResponse,
    response_model=List[Optional[WarningAndMainteSchema]],
)
async def read_recent_asset_event(id: int, conn: Database = Depends(get_db)):
    res = await get_recent_asset_event(conn=conn, asset_id=id)
    return res
