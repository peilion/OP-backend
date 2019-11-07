from databases import Database
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.schema import CreateTable

from crud.base import con_warpper, query2sql
from db import meta_engine
from db.db_config import session_make
from db_model import (
    Asset,
    Station,
    AssetHI,
)
from db_model.asset_info import info_models_mapper
enum_mapper = Asset.TYPES


@con_warpper
async def get_multi(
    conn: Database,
    skip: int,
    limit: int,
    type: int,
    station_name: str,
    level: int,
    station_id: int,
    session: Session = session_make(engine=None),
):
    if level is None:
        query = (
            session.query(
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
                Station.name.label("station_name"),
            )
            .join(Station, Station.id == Asset.station_id)
            .order_by(Asset.id)
            .offset(skip)
            .limit(limit)
        )
    else:
        query = session.query(Asset.id, Asset.name).filter(
            Asset.asset_level == level
        )  # short query when the level filed is given.
    if station_id is not None:
        query = query.filter(Asset.station_id == station_id)
    if type is not None:
        query = query.filter(Asset.asset_type == type)
    if station_name is not None:
        query = query.filter(Station.name == station_name)

    return await conn.fetch_all(query2sql(query))


@con_warpper
async def get(conn: Database, id: int, session: Session = session_make(engine=None)):
    query = (
        session.query(
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
            Station.name.label("station_name"),
        )
        .join(Station, Station.id == Asset.station_id)
        .filter(Asset.id == id)
    )

    return await conn.fetch_one(query2sql(query))


@con_warpper
async def get_info(session: Session, conn: Database, id: int):
    asset_type = session.query(Asset.asset_type).filter(Asset.id == id).one().asset_type
    model = info_models_mapper[enum_mapper[asset_type]] # int -> asset_type -> model class
    query = session.query(model).filter(model.asset_id == id)
    return await conn.fetch_one(query2sql(query))


def get_multi_tree(session: Session, skip: int, limit: int):
    query = (
        session.query(Asset)
        .filter(Asset.asset_level == 0)
        .options(joinedload(Asset.children))
        .order_by(Asset.id)
        .offset(skip)
        .limit(limit)
    )

    return query.all()  # sqlalchemy query do not support async/await


def get_tree(session: Session, id: int):
    query = session.query(Asset).filter(Asset.id == id)

    return query.one()

@con_warpper
async def create(session: Session, conn: Database, data):
    data = jsonable_encoder(data)
    query = Asset.__table__.insert()

    transaction = await conn.transaction()
    try:
        id = await conn.execute(query=query, values=data['base'])
        model = AssetHI.model(point_id=id)  # register to metadata for all pump_unit
        table_sql = CreateTable(model.__table__).compile(meta_engine)
        if data["base"]["asset_type"] == 0:
            await conn.execute(str(table_sql))
    except Exception as e:
        print(e)
        await transaction.rollback()
        return False
    else:
        await transaction.commit()
        return True
    # asset = Asset(**data["base"])
    # session.add(asset)
    # if data["base"]["asset_type"] == 0:
    #     session.flush()
    #     model = AssetHI.model(point_id=36)  # register to metadata for all pump_unit
    #     table_sql = CreateTable(model.__table__).compile(meta_engine)
    #     try:
    #         session.execute(table_sql.statement)
    #         session.commit()
    #         session.close()
    #         return True
    #     except Exception as e:
    #         session.delete(asset)
    #         session.commit()
    #         session.close()
    #         return False
    # else:
    #     session.commit()
    #     session.close()
    #     return True
