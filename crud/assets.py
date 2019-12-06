from databases import Database
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable

from crud.base import con_warpper, query2sql
from db import meta_engine
from db.db_config import session_make
from db_model import Asset, Station, AssetHI
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
    pre_query_res = await conn.fetch_one(
        query2sql(session.query(Asset.asset_type).filter(Asset.id == id))
    )
    model = info_models_mapper[
        enum_mapper[pre_query_res["asset_type"]]
    ]  # int -> asset_type -> model class

    query = session.query(model).filter(model.asset_id == id)
    return await conn.fetch_one(query2sql(query))


@con_warpper
async def create(conn: Database, data):
    data = jsonable_encoder(data)
    transaction = await conn.transaction()
    id = False
    try:
        id = await conn.execute(query=Asset.__table__.insert(), values=data["base"])
        model = AssetHI.model(point_id=id)  # register to metadata for all pump_unit
        if data["base"]["asset_type"] == 0:
            await conn.execute(str(CreateTable(model.__table__).compile(meta_engine)))
        await transaction.commit()
        return True
    except Exception as e:
        # print(e)
        if id:
            query = Asset.__table__.delete().where(Asset.__table__.c.id == id)
            await conn.execute(
                query=str(query.compile(compile_kwargs={"literal_binds": True}))
            )
            await transaction.commit()
        return False
