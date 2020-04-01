import json
from datetime import datetime
from enum import Enum
from typing import List

from databases import Database
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import ORJSONResponse, JSONResponse

from core.dependencies import get_db
from crud.data import get_latest, get_by_id, get_multi
from db_model import VibData
from model.vib_data import (
    VibrationSignalSchema,
    VibrationSignalListSchema,
    VibrationEnvelopeSchema,
    VibrationSTFTSchema,
    VibrationWelchSchema,
    VibrationCumtrapzSchema,
    VibrationEMDSchema,
)
from services.signal.vibration.processors import (
    fast_fournier_transform,
    hilbert,
    short_time_fournier_transform,
    multi_scale_envelope_spectrum,
    welch_spectrum_estimation,
    acceleration_to_velocity,
    empirical_mode_decomposition,
)

router = APIRouter()


class AnalyzeRule(str, Enum):
    hilbert = "hilbert"
    stft = "stft"
    musens = "musens"
    welch = "welch"
    cumtrapz = "cumtrapz"
    emd = "emd"


@router.get(
    "/mp/{mp_id}/vib_data/latest/",
    response_class=ORJSONResponse,
    response_model=VibrationSignalSchema,
)
async def read_the_latest_vibration_signal(
    mp_id: int, conn: Database = Depends(get_db)
):
    res = await get_latest(conn=conn, mp_id=mp_id, orm_model=VibData, require_mp_type=0)
    processed_res = fast_fournier_transform(res["ima"])
    return {**processed_res, **{"id": res["id"], "time": res["time"]}}


@router.get(
    "/mp/{mp_id}/vib_data/list/",
    response_class=ORJSONResponse,
    response_model=List[VibrationSignalListSchema],
)
async def read_all_vibration_signal_info(
    mp_id: int,
    time_before: datetime = Query(default="2016-01-01 00:00:00"),
    time_after: datetime = Query(default="2016-07-10 00:00:00"),
    conn: Database = Depends(get_db),
):
    """
    Diagnosis info will be joined to the response in the future.
    """

    res = await get_multi(
        conn=conn,
        mp_id=mp_id,
        orm_model=VibData,
        require_mp_type=0,
        time_before=time_before,
        time_after=time_after,
    )
    if not res:
        raise HTTPException(
            status_code=400, detail="No signal collected between the time range"
        )
    return [dict(row) for row in res]


@router.get(
    "/mp/{mp_id}/vib_data/{data_id}/",
    response_class=ORJSONResponse,
    response_model=VibrationSignalSchema,
)
async def read_vibration_signal_by_id(
    mp_id: int, data_id: int, conn: Database = Depends(get_db)
):
    res = await get_by_id(
        conn=conn, mp_id=mp_id, orm_model=VibData, require_mp_type=0, data_id=data_id,
    )
    processed_res = fast_fournier_transform(res["ima"])
    return {**processed_res, **{"id": res["id"], "time": res["time"]}}


@router.get("/mp/{mp_id}/vib_data/{data_id}/analysis/", response_class=ORJSONResponse)
async def analyze_vibration_signal(
    mp_id: int,
    data_id: int,
    method: AnalyzeRule = Query(None),
    conn: Database = Depends(get_db),
):
    res = await get_by_id(
        conn=conn, mp_id=mp_id, orm_model=VibData, require_mp_type=0, data_id=data_id,
    )
    # analysis method dispatch
    if method == AnalyzeRule.hilbert:
        processed_res = hilbert(res["ima"])
        return VibrationEnvelopeSchema(
            **{**processed_res, **{"id": res["id"], "time": res["time"]}}
        )

    if method == AnalyzeRule.stft:
        processed_res = short_time_fournier_transform(res["ima"])
        return VibrationSTFTSchema(
            **{**processed_res, **{"id": res["id"], "time": res["time"]}}
        )

    if method == AnalyzeRule.musens:
        processed_res = multi_scale_envelope_spectrum(res["ima"])
        x = json.dumps({**processed_res, **{"id": res["id"], "time": str(res["time"])}})
        return JSONResponse(content=x)

    if method == AnalyzeRule.welch:
        processed_res = welch_spectrum_estimation(res["ima"])
        return VibrationWelchSchema(
            **{**processed_res, **{"id": res["id"], "time": res["time"]}}
        )

    if method == AnalyzeRule.cumtrapz:
        processed_res = acceleration_to_velocity(res["ima"])
        return VibrationCumtrapzSchema(
            **{**processed_res, **{"id": res["id"], "time": res["time"]}}
        )

    if method == AnalyzeRule.emd:
        processed_res = empirical_mode_decomposition(res["ima"])
        return VibrationEMDSchema(
            **{**processed_res, **{"id": res["id"], "time": res["time"]}}
        )
