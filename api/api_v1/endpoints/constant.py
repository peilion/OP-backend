from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

router = APIRouter()


@router.get("/statu_mapper/", response_class=ORJSONResponse)
async def read_statu_mapper():
    return {0: "Excellent", 1: "Good", 2: "Moderate", 3: "Poor", 4: "Offline"}


@router.get("/level_mapper/", response_class=ORJSONResponse)
async def read_equip_level_mapper():
    return {0: "Unit", 1: "Equip", 2: "Component"}


@router.get("/warning_servity_mapper/", response_class=ORJSONResponse)
async def read_warning_servity_mapper():
    return {0: "Slight", 1: "Attention", 2: "Serious"}
