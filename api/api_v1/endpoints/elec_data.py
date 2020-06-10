from datetime import datetime
from enum import Enum
from typing import List

from databases import Database
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import ORJSONResponse

from core.dependencies import get_db
from crud.data import get_latest, get_by_id, get_multi, get_data_join_feature_by_id
from crud.feature import get
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


class AnalyzeRule(str, Enum):
    hilbert = "hilbert"
    dq = "dq"
    symetry = "symetry"
    harmonic = "harmonic"


@router.get(
    "/mp/{mp_id}/elec/latest/",
    response_class=ORJSONResponse,
    response_model=ElecSignalSchema,
)
async def read_the_latest_electric_signal(mp_id: int, conn: Database = Depends(get_db)):
    res = await get_latest(
        conn=conn, mp_id=mp_id, require_mp_type=1, orm_model=ElecData,
    )
    processed = three_phase_fast_fournier_transform(
        u=res["ucur"], v=res["vcur"], w=res["wcur"]
    )
    return {**processed, **{"id": res["id"], "time": res["time"]}}


@router.get(
    "/mp/{mp_id}/elec/all/",
    response_class=ORJSONResponse,
    response_model=List[ElecSignalListSchema],
)
async def read_all_electric_signal_info(
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
        require_mp_type=1,
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
    response_class=ORJSONResponse,
    response_model=ElecSignalSchema,
)
async def read_electric_signal_by_id(
    mp_id: int, data_id: int, conn: Database = Depends(get_db)
):
    res = await get_by_id(
        conn=conn, mp_id=mp_id, require_mp_type=1, data_id=data_id, orm_model=ElecData,
    )
    processed = three_phase_fast_fournier_transform(
        u=res["ucur"], v=res["vcur"], w=res["wcur"]
    )
    return {**processed, **{"id": res["id"], "time": res["time"]}}


@router.get("/mp/{mp_id}/elec/{data_id}/analysis/", response_class=ORJSONResponse)
async def analyze_electric_signal(
    mp_id: int,
    data_id: int,
    method: AnalyzeRule = Query(None),
    conn: Database = Depends(get_db),
):
    if method == AnalyzeRule.harmonic:
        res = await get(
            conn=conn,
            mp_id=mp_id,
            require_mp_type=1,
            data_id=data_id,
            orm_model=ElecFeature,
            fileds=["uharmonics", "vharmonics", "wharmonics"],
        )

        return ElecHarmonicSchema(
            **{
                "id": res["id"],
                "time": res["time"],
                "uharmonics": res["uharmonics"],
                "vharmonics": res["vharmonics"],
                "wharmonics": res["wharmonics"],
            }
        )

    elif method == AnalyzeRule.hilbert:
        res = await get_by_id(
            conn=conn,
            mp_id=mp_id,
            require_mp_type=1,
            data_id=data_id,
            orm_model=ElecData,
        )
        processed_res = three_phase_hilbert_transform(
            u=res["ucur"], v=res["vcur"], w=res["wcur"]
        )
        return ElecEnvelopeSchema(
            **processed_res, **{"id": res["id"], "time": res["time"]}
        )

    elif method == AnalyzeRule.dq:
        res = await get_by_id(
            conn=conn,
            mp_id=mp_id,
            require_mp_type=1,
            data_id=data_id,
            orm_model=ElecData,
        )
        processed_res = dq_transform(u=res["ucur"], v=res["vcur"], w=res["wcur"])
        return ElecDQSchema(**processed_res, **{"id": res["id"], "time": res["time"]})

    elif method == AnalyzeRule.symetry:
        res = await get(
            conn=conn,
            mp_id=mp_id,
            require_mp_type=1,
            data_id=data_id,
            orm_model=ElecFeature,
            fileds=[
                "uamplitude",
                "vamplitude",
                "wamplitude",
                "ufrequency",
                "wfrequency",
                "vfrequency",
                "uinitial_phase",
                "vinitial_phase",
                "winitial_phase",
            ],
        )
        processed_res = sym_analyze(res=res)
        return ElecSymSchema(**processed_res, **{"id": res["id"], "time": res["time"]})
