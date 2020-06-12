from databases import Database
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import ORJSONResponse

from core.dependencies import get_db
from crud.threshold import get_multi, update
from model.threshold import ThresholdSchema, MotorDrivenEndPostSchema
from typing import List

router = APIRouter()


@router.get("/", response_class=ORJSONResponse, response_model=List[ThresholdSchema])
async def read_thresholds(conn: Database = Depends(get_db),):
    """
    Get Warning List.
    """
    items = await get_multi(conn=conn)
    return items


@router.post("/motor_driven/", response_class=ORJSONResponse)
async def update_motor_driven_threshold(
    diag_threshold: MotorDrivenEndPostSchema, conn: Database = Depends(get_db)
):
    res = await update(
        conn=conn, mp_pattern="motor_driven", diag_threshold=diag_threshold.dict()
    )
    if res == True:
        return {"msg": "Threshold was updated successfully."}
