from databases import Database
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.ddl import CreateTable

from core.dependencies import mp_change_commit
from crud.base import con_warpper, query2sql
from db.conn_engine import META_URL, STATION_URLS, meta_engine
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


async def create(data: MeasurePointInputSchema,
                 session: Session = session_make(engine=None)):
    data = jsonable_encoder(data)
    data_model = VibData if (data['type'] == 0) else ElecData
    feature_model = VibFeature if (data['type'] == 0) else ElecFeature
    id = 0
    async with Database(META_URL) as conn:
        query = session.query(MeasurePoint.id_inner_station) \
            .filter(MeasurePoint.station_id == data["station_id"]) \
            .order_by(MeasurePoint.id_inner_station.desc()) \
            .limit(1)
        res = await conn.fetch_one(query2sql(query))
        table_id = res['id_inner_station'] + 1
        mp_data = {**data, 'id_inner_station': table_id}
        id = await conn.execute(query=MeasurePoint.__table__.insert(), values=mp_data)
        if id:
            async with Database(STATION_URLS[data["station_id"] - 1]) as conn:
                data_table = data_model.model(point_id=table_id)
                feature_table = feature_model.model(point_id=table_id)
                await conn.execute(str(CreateTable(data_table.__table__).compile(meta_engine)))
                await conn.execute(str(CreateTable(feature_table.__table__).compile(meta_engine)))
    mp_change_commit()
