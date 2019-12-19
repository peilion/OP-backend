from datetime import datetime
from typing import List

from databases import Database
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.responses import UJSONResponse

from core.dependencies import get_mp_mapper
from crud.data import get_latest, get_by_id, get_multi, get_data_join_feature_by_id
from crud.feature import get as get_feature
from db.conn_engine import META_URL
from db_model import ElecData, ElecFeature
from model.elec_data import (
    ElecSignalListSchema,
    ElecSignalSchema,
    ElecEnvelopeSchema,
    ElecDQSchema,
    ElecSymSchema,
    ElecHarmonicSchema,
)
from services.signal.electric.processors import (
    three_phase_fast_fournier_transform,
    three_phase_hilbert_transform,
    dq_transform,
    sym_analyze,
)

router = APIRouter()


@router.get(
    "/mp/{mp_id}/elec/latest/",
    response_class=UJSONResponse,
    response_model=ElecSignalSchema,
)
async def read_the_latest_electric_signal(
    mp_id: int, mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info["type"] == 0:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect vibration data, try to use the approaprite endpoint.",
        )

    conn = Database(META_URL)
    res = await get_latest(
        conn=conn, shard_id=mp_shard_info["shard_id"], orm_model=ElecData
    )
    processed = three_phase_fast_fournier_transform(
        u=res["ucur"], v=res["vcur"], w=res["wcur"]
    )
    return {**processed, **{"id": res["id"], "time": res["time"]}}


@router.get(
    "/mp/{mp_id}/elec/all/",
    response_class=UJSONResponse,
    response_model=List[ElecSignalListSchema],
)
async def read_all_electric_signal_info(
    mp_id: int,
    time_before: datetime = Query(default="2016-01-01 00:00:00"),
    time_after: datetime = Query(default="2016-07-10 00:00:00"),
    mp_mapper: dict = Depends(get_mp_mapper),
):
    """
    Diagnosis info will be joined to the response in the future.
    """
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info["type"] == 0:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect vibration data, try to use the approaprite endpoint.",
        )

    conn = Database(META_URL)
    res = await get_multi(
        conn=conn,
        shard_id=mp_shard_info["shard_id"],
        time_before=time_before,
        time_after=time_after,
        orm_model=ElecData,
    )
    if not res:
        raise HTTPException(
            status_code=400, detail="No signal collected between the time range"
        )
    return [dict(row) for row in res]


@router.get(
    "/mp/{mp_id}/elec/{data_id}/",
    response_class=UJSONResponse,
    response_model=ElecSignalSchema,
)
async def read_electric_signal_by_id(
    mp_id: int, data_id: int, mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info["type"] == 0:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect vibration data, try to use the approaprite endpoint.",
        )

    conn = Database(META_URL)
    res = await get_by_id(
        conn=conn,
        shard_id=mp_shard_info["shard_id"],
        data_id=data_id,
        orm_model=ElecData,
    )

    processed = three_phase_fast_fournier_transform(
        u=res["ucur"], v=res["vcur"], w=res["wcur"]
    )
    return {**processed, **{"id": res["id"], "time": res["time"]}}


@router.get(
    "/mp/{mp_id}/elec/{data_id}/hilbert",
    response_class=UJSONResponse,
    response_model=ElecEnvelopeSchema,
)
async def analyze_electric_signal_with_hilbert(
    mp_id: int, data_id: int, mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info["type"] == 0:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect vibration data, try to use the approaprite endpoint.",
        )

    conn = Database(META_URL)
    res = await get_by_id(
        conn=conn,
        shard_id=mp_shard_info["shard_id"],
        data_id=data_id,
        orm_model=ElecData,
    )

    processed_res = three_phase_hilbert_transform(
        u=res["ucur"], v=res["vcur"], w=res["wcur"]
    )
    return {**processed_res, **{"id": res["id"], "time": res["time"]}}


@router.get(
    "/mp/{mp_id}/elec/{data_id}/dq",
    response_class=UJSONResponse,
    response_model=ElecDQSchema,
)
async def analyze_electric_signal_with_dq(
    mp_id: int, data_id: int, mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info["type"] == 0:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect vibration data, try to use the approaprite endpoint.",
        )

    conn = Database(META_URL)
    res = await get_by_id(
        conn=conn,
        shard_id=mp_shard_info["shard_id"],
        data_id=data_id,
        orm_model=ElecData,
    )

    processed_res = dq_transform(u=res["ucur"], v=res["vcur"], w=res["wcur"])
    return {**processed_res, **{"id": res["id"], "time": res["time"]}}


@router.get(
    "/mp/{mp_id}/elec/{data_id}/sym",
    response_class=UJSONResponse,
    response_model=ElecSymSchema,
)
async def analyze_electric_signal_with_sym(
    mp_id: int, data_id: int, mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info["type"] == 0:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect vibration data, try to use the approaprite endpoint.",
        )

    conn = Database(META_URL)
    res = await get_feature(
        conn=conn,
        shard_id=mp_shard_info["shard_id"],
        data_id=data_id,
        fileds=[
            "ufrequency",
            "uamplitude",
            "uinitial_phase",
            "vfrequency",
            "vamplitude",
            "vinitial_phase",
            "wfrequency",
            "wamplitude",
            "winitial_phase",
        ],
        orm_model=ElecFeature,
    )

    processed_res = sym_analyze(res=res)
    return {**processed_res, **{"id": res["id"], "time": res["time"]}}


@router.get(
    "/mp/{mp_id}/elec/{data_id}/har",
    response_class=UJSONResponse,
    response_model=ElecHarmonicSchema,
)
async def analyze_electric_signal_harmonic(
    mp_id: int, data_id: int, mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[mp_id]
    if mp_shard_info["type"] == 0:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect vibration data, try to use the approaprite endpoint.",
        )

    conn = Database(META_URL)
    res = await get_data_join_feature_by_id(
        conn=conn,
        shard_id=mp_shard_info["shard_id"],
        data_id=data_id,
        data_model=ElecData,
        feature_model=ElecFeature,
        feature_fileds=("uharmonics", "vharmonics", "wharmonics"),
        data_fileds=("ucur", "vcur", "wcur", "time", "id"),
    )

    processed_res = three_phase_fast_fournier_transform(
        u=res["ucur"], v=res["vcur"], w=res["wcur"], if_return_raw=False
    )
    return {
        **processed_res,
        "id": res["id"],
        "time": res["time"],
        "uharmonics": res["uharmonics"],
        "vharmonics": res["vharmonics"],
        "wharmonics": res["wharmonics"],
    }
