import json
from datetime import datetime
from typing import List

from databases import Database
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.responses import UJSONResponse, JSONResponse

from core.dependencies import get_mp_mapper
from crud.data import get_latest, get_by_id, get_multi
from db.conn_engine import STATION_URLS
from db_model import VibData
from model.vib_data import VibrationSignalSchema, VibrationSignalListSchema, VibrationEnvelopeSchema, \
    VibrationSTFTSchema, VibrationWelchSchema, VibrationCumtrapzSchema
from utils.vib_feature_tools import fftransform, hilbert, stft, musens, welch, toVelocity

router = APIRouter()


@router.get(
    "/mp/{mp_id}/vib_data/latest/",
    response_class=UJSONResponse,
    response_model=VibrationSignalSchema)
async def read_the_latest_vibration_signal(
        mp_id: int,
        mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info['type'] == 1:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect elecdata, try to use the approaprite endpoint.")

    conn = Database(STATION_URLS[mp_shard_info['station_id'] - 1])
    res = await get_latest(conn=conn, shard_id=mp_shard_info['inner_id'], orm_model=VibData)
    processed_res = fftransform(res['vib'])
    return {**processed_res, **{'id': res['id'],
                                'time': res['time']}}


@router.get(
    "/mp/{mp_id}/vib_data/list/",
    response_class=UJSONResponse,
    response_model=List[VibrationSignalListSchema])
async def read_all_vibration_signal_info(
        mp_id: int,
        time_before: datetime = Query(default='2016-01-01 00:00:00'),
        time_after: datetime = Query(default='2016-07-10 00:00:00'),
        mp_mapper: dict = Depends(get_mp_mapper)
):
    """
    Diagnosis info will be joined to the response in the future.
    """
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info['type'] == 1:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect elecdata, try to use the approaprite endpoint.")

    conn = Database(STATION_URLS[mp_shard_info['station_id'] - 1])
    res = await get_multi(conn=conn, shard_id=mp_shard_info['inner_id'], time_before=time_before, time_after=time_after,
                          orm_model=VibData)
    if not res:
        raise HTTPException(
            status_code=400,
            detail="No signal collected between the time range")
    return [dict(row) for row in res]


@router.get(
    "/mp/{mp_id}/vib_data/{data_id}/",
    response_class=UJSONResponse,
    response_model=VibrationSignalSchema)
async def read_vibration_signal_by_id(
        mp_id: int,
        data_id: int,
        mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info['type'] == 1:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect elecdata, try to use the approaprite endpoint.")

    conn = Database(STATION_URLS[mp_shard_info['station_id'] - 1])
    res = await get_by_id(conn=conn, shard_id=mp_shard_info['inner_id'], data_id=data_id, orm_model=VibData)
    processed_res = fftransform(res['vib'])
    return {**processed_res, **{'id': res['id'],
                                'time': res['time']}}


@router.get(
    "/mp/{mp_id}/vib_data/{data_id}/hilbert",
    response_class=UJSONResponse,
    response_model=VibrationEnvelopeSchema)
async def analyze_vibration_signal_with_hilbert(
        mp_id: int,
        data_id: int,
        mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info['type'] == 1:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect elecdata, try to use the approaprite endpoint.")

    conn = Database(STATION_URLS[mp_shard_info['station_id'] - 1])
    res = await get_by_id(conn=conn, shard_id=mp_shard_info['inner_id'], data_id=data_id, orm_model=VibData)

    processed_res = hilbert(res['vib'])
    return {**processed_res, **{'id': res['id'],
                                'time': res['time']}}


@router.get(
    "/mp/{mp_id}/vib_data/{data_id}/stft",
    response_class=UJSONResponse,
    response_model=VibrationSTFTSchema)
async def analyze_vibration_signal_with_stft(
        mp_id: int,
        data_id: int,
        mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info['type'] == 1:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect elecdata, try to use the approaprite endpoint.")

    conn = Database(STATION_URLS[mp_shard_info['station_id'] - 1])
    res = await get_by_id(conn=conn, shard_id=mp_shard_info['inner_id'], data_id=data_id, orm_model=VibData)

    processed_res = stft(res['vib'])
    return {**processed_res, **{'id': res['id'],
                                'time': res['time']}}


@router.get(
    "/mp/{mp_id}/vib_data/{data_id}/musens",
    # response_class=JSONResponse,
)
async def analyze_vibration_signal_with_musens(
        mp_id: int,
        data_id: int,
        mp_mapper: dict = Depends(get_mp_mapper)
):
    """
    Use 'Json.parse(response.data)' rather than 'response.data'
    """
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info['type'] == 1:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect elecdata, try to use the approaprite endpoint.")

    conn = Database(STATION_URLS[mp_shard_info['station_id'] - 1])
    res = await get_by_id(conn=conn, shard_id=mp_shard_info['inner_id'], data_id=data_id, orm_model=VibData)

    processed_res = musens(
        res['vib'],
        n_Fs=10000,
        n_Ssta=1.0,
        n_Send=8.0,
        n_Sint=0.2)
    x = json.dumps({**processed_res, **{'id': res['id'],
                                        'time': str(res['time'])}})
    # using json response directly to skip data validation, for extreme large
    # array.
    return JSONResponse(content=x)


@router.get(
    "/mp/{mp_id}/vib_data/{data_id}/welch",
    response_class=UJSONResponse,
    response_model=VibrationWelchSchema
)
async def analyze_vibration_signal_with_welch(
        mp_id: int,
        data_id: int,
        mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info['type'] == 1:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect elecdata, try to use the approaprite endpoint.")

    conn = Database(STATION_URLS[mp_shard_info['station_id'] - 1])
    res = await get_by_id(conn=conn, shard_id=mp_shard_info['inner_id'], data_id=data_id, orm_model=VibData)

    processed_res = welch(res['vib'])
    return {**processed_res, **{'id': res['id'],
                                'time': res['time']}}


@router.get(
    "/mp/{mp_id}/vib_data/{data_id}/cumtrapz",
    response_class=UJSONResponse,
    response_model=VibrationCumtrapzSchema
)
async def analyze_vibration_signal_with_cumtrapz(
        mp_id: int,
        data_id: int,
        mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info['type'] == 1:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect elecdata, try to use the approaprite endpoint.")

    conn = Database(STATION_URLS[mp_shard_info['station_id'] - 1])
    res = await get_by_id(conn=conn, shard_id=mp_shard_info['inner_id'], data_id=data_id, orm_model=VibData)

    processed_res = toVelocity(res['vib'])
    return {**processed_res, **{'id': res['id'],
                                'time': res['time']}}
