from databases import Database
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from core.dependencies import get_db
from crud.threshold import get_multi
from model.threshold import ThresholdSchema
from typing import List

router = APIRouter()


@router.get("/", response_class=ORJSONResponse, response_model=List[ThresholdSchema])
async def read_thresholds(conn: Database = Depends(get_db),):
    """
    Get Warning List.
    """
    items = await get_multi(conn=conn)
    return items
