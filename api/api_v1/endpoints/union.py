from typing import List, Optional

from databases import Database
from fastapi import APIRouter
from starlette.responses import UJSONResponse

from crud.union import get_warning_and_maintenace
from db.conn_engine import META_URL
from model.log import WarningAndMainteSchema

router = APIRouter()


@router.get(
    "/warnandmaint/{id}/",
    response_class=UJSONResponse,
    response_model=List[Optional[WarningAndMainteSchema]],
)
async def read_by_id(id: int,):
    conn = Database(META_URL)
    res = await get_warning_and_maintenace(conn=conn, asset_id=id)
    return res
