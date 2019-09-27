from fastapi import APIRouter
from starlette.responses import UJSONResponse

router = APIRouter()


@router.get("/statu_mapper/", response_class=UJSONResponse)
async def read_statu_mapper(
):
    return {0: 'Excellent', 1: 'Good', 2: 'Moderate', 3: 'Poor', 4: 'Offline'}


@router.get("/level_mapper/", response_class=UJSONResponse)
async def read_equip_level_mapper(
):
    return {0: 'Unit', 1: 'Equip', 2: 'Component'}


@router.get("/station_mapper/", response_class=UJSONResponse)
async def read_equip_level_mapper(
):
    return {1: '呼和浩特', 2: '鄂托克旗', 3: '包头'}


@router.get("/warning_servity_mapper/", response_class=UJSONResponse)
async def read_warning_servity_mapper(
):
    return {0: 'Slight', 1: 'Attention', 2: 'Serious'}
