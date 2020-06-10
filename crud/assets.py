from databases import Database
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable

from crud.base import query2sql
from db import meta_engine
from db.db_config import session_make
from db_model import (
    Asset,
    Station,
    AssetHI,
    PumpUnit,
    Pipeline,
    BranchCompany,
    RegionCompany,
)
from db_model.asset_info import info_models_mapper

enum_mapper = Asset.TYPES


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
        )  # short query when the level filed is given, for relate asset dropdown
    if station_id is not None:
        query = query.filter(Asset.station_id == station_id)
    if type is not None:
        query = query.filter(Asset.asset_type == type)
    if station_name is not None:
        query = query.filter(Station.name == station_name)

    return await conn.fetch_all(query2sql(query))


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


async def get_info(session: Session, conn: Database, id: int):
    pre_query_res = await conn.fetch_one(
        query2sql(session.query(Asset.asset_type).filter(Asset.id == id))
    )
    model = info_models_mapper[
        enum_mapper[pre_query_res["asset_type"]]
    ]  # int -> asset_type -> model class

    query = session.query(model).filter(model.asset_id == id)
    return await conn.fetch_one(query2sql(query))


async def get_cards(
    conn: Database, skip: int, limit: int, session: Session = session_make(engine=None),
):
    query = (
        session.query(
            Asset.id,
            Asset.name,
            Asset.sn,
            Asset.st_time,
            Asset.health_indicator,
            Asset.statu,
            Asset.repairs,
            Asset.mp_configuration,
            Station.name.label("station_name"),
            PumpUnit.is_domestic,
            PumpUnit.oil_type,
            PumpUnit.design_output,
        )
        .join(Station, Station.id == Asset.station_id)
        .join(PumpUnit, PumpUnit.asset_id == Asset.id)
        .order_by(Asset.id)
        .filter(Asset.asset_type == 0)
        .offset(skip)
        .limit(limit)
    )
    return await conn.fetch_all(query2sql(query))


async def get_card_by_id(
    conn: Database, id: int, session: Session = session_make(engine=None),
):
    query = (
        session.query(
            Asset.id,
            Asset.name,
            Asset.sn,
            Asset.st_time,
            Asset.health_indicator,
            Asset.mp_configuration,
            Asset.statu,
            Asset.repairs,
            Station.name.label("station_name"),
            PumpUnit.is_domestic,
            PumpUnit.oil_type,
            PumpUnit.design_output,
        )
        .join(Station, Station.id == Asset.station_id)
        .join(PumpUnit, PumpUnit.asset_id == Asset.id)
        .filter(Asset.id == id)
    )
    return await conn.fetch_one(query2sql(query))


async def get_detail_by_id(
    conn: Database, id: int, session: Session = session_make(engine=None),
):
    query = (
        session.query(
            Asset.id,
            Asset.name,
            Asset.sn,
            Asset.lr_time,
            Asset.cr_time,
            Asset.md_time,
            Asset.st_time,
            Asset.memo,
            Asset.health_indicator,
            Asset.statu,
            Asset.asset_type,
            Asset.repairs,
            Station.name.label("station_name"),
            Pipeline.name.label("pipeline_name"),
            BranchCompany.name.label("branch_name"),
            RegionCompany.name.label("region_name"),
            PumpUnit.is_domestic,
            PumpUnit.oil_type,
            PumpUnit.design_output,
        )
        .join(Station, Station.id == Asset.station_id)
        .join(PumpUnit, PumpUnit.asset_id == Asset.id)
        .join(Pipeline, Pipeline.id == PumpUnit.pipeline_id)
        .join(BranchCompany, BranchCompany.id == Station.bc_id)
        .join(RegionCompany, RegionCompany.id == Station.rc_id)
        .filter(Asset.id == id)
    )
    return await conn.fetch_one(query2sql(query))


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
