from databases import Database
from sqlalchemy.orm import Session, joinedload

from crud.decorator import con_warpper, query2sql
from db.db_config import session_make
from db_model import Asset, Station, Bearing, PumpUnit, Motor, Pump, Stator, Rotor

info_model_mapper = {
    0: PumpUnit,
    1: Pump,
    2: Motor,
    3: Rotor,
    4: Stator,
    5: Bearing}


@con_warpper
async def get_multi(conn: Database, skip: int, limit: int, type: int, session: Session = session_make(engine=None)):
    query = session. query(
        Asset.id,
        Asset.name,
        Asset.sn,
        Asset.lr_time,
        Asset.cr_time,
        Asset.md_time,
        Asset.st_time,
        Asset.asset_level,
        Asset.memo,
        Asset.health_indicator,
        Asset.statu,
        Asset.parent_id,
        Asset.station_id,
        Asset.repairs,
        Station.name.label('station_name')). join(
        Station,
        Station.id == Asset.station_id). order_by(
            Asset.id). offset(skip). limit(limit)
    if type is not None:
        query = query.filter(Asset.asset_type == type)
    return await conn.fetch_all(query2sql(query))


@con_warpper
async def get(conn: Database, id: int, session: Session = session_make(engine=None)):
    query = session. query(
        Asset.id,
        Asset.name,
        Asset.sn,
        Asset.lr_time,
        Asset.cr_time,
        Asset.md_time,
        Asset.asset_level,
        Asset.memo,
        Asset.health_indicator,
        Asset.statu,
        Station.name.label('station_name')). join(
        Station,
        Station.id == Asset.station_id). filter(
            Asset.id == id)

    return await conn.fetch_one(query2sql(query))


@con_warpper
async def get_info(session: Session, conn: Database, id: int):
    asset_type = session.query(
        Asset.asset_type).filter(
        Asset.id == id).one().asset_type
    model = info_model_mapper[asset_type]
    query = session. \
        query(model). \
        filter(model.asset_id == id)
    # Sqlalchemy query do not support async/await
    return await conn.fetch_one(query2sql(query))


def get_multi_tree(session: Session, skip: int, limit: int, ):
    query = session. \
        query(Asset). \
        filter(Asset.asset_level == 0). \
        options(joinedload(Asset.children)). \
        order_by(Asset.id). \
        offset(skip). \
        limit(limit)

    return query.all()  # Sqlalchemy query do not support async/await


def get_tree(session: Session, id: int):
    query = session. \
        query(Asset). \
        filter(Asset.id == id)

    return query.one()
