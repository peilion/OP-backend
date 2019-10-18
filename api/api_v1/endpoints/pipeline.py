from typing import List, Optional

from databases import Database
from fastapi import APIRouter, HTTPException

from crud.pipeline import get_multi
from db.conn_engine import META_URL
from model.pipeline import PipelineSchema

router = APIRouter()

@router.get("/", response_model=List[Optional[PipelineSchema]])
async def read_pipelines(
        skip: int = 0,
        limit: int = None,
):
    """
    Get Pipeline List.
    """
    conn = Database(META_URL)
    items = await get_multi(conn=conn, skip=skip, limit=limit)
    return items