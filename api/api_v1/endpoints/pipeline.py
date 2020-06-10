from typing import List, Optional

from databases import Database
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from core.dependencies import get_db
from crud.pipeline import get_multi, get_total_length
from model.organizations import PipelineSchema

router = APIRouter()


@router.get(
    "/", response_model=List[Optional[PipelineSchema]], response_class=ORJSONResponse
)
async def read_pipelines(
    skip: int = 0, limit: int = None, conn: Database = Depends(get_db)
):
    """
    Get Pipeline List.
    """
    items = await get_multi(conn=conn, skip=skip, limit=limit)
    return items


@router.get("/total", response_model=float, response_class=ORJSONResponse)
async def read_pipeline_length(conn: Database = Depends(get_db)):
    """
    Get Pipeline List.
    """
    res = await get_total_length(conn=conn)
    return res.value
