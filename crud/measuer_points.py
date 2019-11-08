from databases import Database
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from core.dependencies import mp_change_commit
from crud.base import con_warpper, query2sql
from db import station_engines
from db.db_config import session_make
from db_model import (
    MeasurePoint,
    Station,
    Asset,
    VibFeature,
    VibData,
    ElecFeature,
    ElecData,
)
from model.measure_points import MeasurePointInputSchema


@con_warpper
async def get_multi(
    conn: Database,
    skip: int,
    limit: int,
    brief: bool,
    session: Session = session_make(engine=None),
    **kwargs
):
    if brief:
        query = session.query(
            MeasurePoint.id,
            MeasurePoint.name,
            MeasurePoint.type,
            MeasurePoint.health_indicator,
        )
    else:
        query = session.query(
            MeasurePoint.id,
            MeasurePoint.name,
            MeasurePoint.type,
            MeasurePoint.md_time,
            MeasurePoint.statu,
            MeasurePoint.health_indicator,
            MeasurePoint.sample_freq,
            MeasurePoint.sample_interval,
            Station.id.label("staion_id"),
            Station.name.label("station_name"),
            Asset.id.label("asset_id"),
            Asset.name.label("asset_name"),
        )
    query = (
        query.order_by(MeasurePoint.type)
        .offset(skip)
        .limit(limit)
        .join(Station, MeasurePoint.station_id == Station.id)
        .join(Asset, MeasurePoint.asset_id == Asset.id)
    )
    if kwargs["station_id"]:
        query = query.filter(MeasurePoint.station_id == kwargs["station_id"])
    if kwargs["asset_id"]:
        query = query.filter(MeasurePoint.asset_id == kwargs["asset_id"])
    query = query.order_by(MeasurePoint.id)
    return await conn.fetch_all(query2sql(query))


@con_warpper
async def get(conn: Database, id: int, session: Session = session_make(engine=None)):
    query = (
        session.query(
            MeasurePoint.id,
            MeasurePoint.name,
            MeasurePoint.type,
            MeasurePoint.md_time,
            MeasurePoint.statu,
            MeasurePoint.sample_freq,
            MeasurePoint.asset_id,
            Station.id.label("staion_id"),
            Station.name.label("station_name"),
            MeasurePoint.sample_interval,
        )
        .join(Station, MeasurePoint.station_id == Station.id)
        .order_by(MeasurePoint.id)
        .filter(MeasurePoint.id == id)
    )
    return await conn.fetch_one(query2sql(query))


@con_warpper
async def get_stat(
    conn: Database, rule: str, session: Session = session_make(engine=None)
):
    if rule == "station":
        query = session.query(
            MeasurePoint.station_id, func.count("*").label("cnt")
        ).group_by(MeasurePoint.station_id)
    elif rule == "asset":
        query = session.query(
            MeasurePoint.asset_id, func.count("*").label("cnt")
        ).group_by(MeasurePoint.asset_id)
    elif rule == "statu":
        query = session.query(
            MeasurePoint.statu, func.count("*").label("cnt")
        ).group_by(MeasurePoint.statu)
    else:
        return None

    return await conn.fetch_all(query2sql(query))


def create(session: Session, data: MeasurePointInputSchema):  # TODO: rewrite to async func
    data = jsonable_encoder(data)

    latest_id = (
        session.query(MeasurePoint.id_inner_station)
        .filter(MeasurePoint.station_id == data["station_id"])
        .order_by(MeasurePoint.id_inner_station.desc())
        .limit(1)
        .one()
        .id_inner_station
    )

    mp = MeasurePoint(id_inner_station=latest_id + 1, **data)
    session.add(mp)
    session.commit()
    session.refresh(mp)
    add_mp_data_and_feature_table(mp)
    session.close()
    mp_change_commit()


def add_mp_data_and_feature_table(mp):
    data_model = VibData if (mp.type == 0) else ElecData
    feature_model = VibFeature if (mp.type == 0) else ElecFeature
    base = declarative_base()
    data_table = data_model.model(point_id=mp.id_inner_station, base=base)
    feature_table = feature_model.model(point_id=mp.id_inner_station, base=base)
    base.metadata.create_all(station_engines[mp.station_id - 1])
