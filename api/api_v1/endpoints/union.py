from typing import List, Optional

from databases import Database
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from core.dependencies import get_db
from crud.union import get_warning_and_maintenace
from model.log import WarningAndMainteSchema

router = APIRouter()


@router.get(
    "/warnandmaint/{id}/",
    response_class=ORJSONResponse,
    response_model=List[Optional[WarningAndMainteSchema]],
)
async def read_by_id(id: int, conn: Database = Depends(get_db)):
    res = await get_warning_and_maintenace(conn=conn, asset_id=id)
    return res
