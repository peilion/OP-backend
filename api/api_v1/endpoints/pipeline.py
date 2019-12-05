from typing import List, Optional

from databases import Database
from fastapi import APIRouter

from crud.pipeline import get_multi, get_total_length
from db.conn_engine import META_URL
from model.organizations import PipelineSchema

router = APIRouter()


@router.get("/", response_model=List[Optional[PipelineSchema]])
async def read_pipelines(skip: int = 0, limit: int = None):
    """
    Get Pipeline List.
    """
    conn = Database(META_URL)
    items = await get_multi(conn=conn, skip=skip, limit=limit)
    return items


@router.get("/total", response_model=float)
async def read_pipeline_length(skip: int = 0, limit: int = None):
    """
    Get Pipeline List.
    """
    conn = Database(META_URL)
    res = await get_total_length(conn=conn)
    return res.value
