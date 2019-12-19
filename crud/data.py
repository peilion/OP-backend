from datetime import datetime

from databases import Database
from sqlalchemy.orm import Session, joinedload

from crud.base import con_warpper, query2sql
from db.db_config import session_make


@con_warpper
async def get_latest(
    conn: Database,
    orm_model,
    shard_id: int,
    session: Session = session_make(engine=None),
):
    model = orm_model.model(point_id=shard_id)
    query = (
        session.query(model).order_by(model.id.desc()).limit(1)
    )  # query all the defined fields
    return await conn.fetch_one(query2sql(query))


@con_warpper
async def get_by_id(
    conn: Database,
    orm_model,
    shard_id: int,
    data_id: int,
    session: Session = session_make(engine=None),
):
    model = orm_model.model(point_id=shard_id)
    query = session.query(model).filter(model.id == data_id)
    return await conn.fetch_one(query2sql(query))


@con_warpper
async def get_data_join_feature_by_id(
    conn: Database,
    data_model,
    feature_model,
    shard_id: int,
    data_id: int,
    data_fileds: tuple,
    feature_fileds: tuple,
    session: Session = session_make(engine=None),
):
    data_model = data_model.model(point_id=shard_id)
    feature_model = feature_model.model(point_id=shard_id)
    feature_attr = []
    for feature in feature_fileds:
        feature_attr.append(getattr(feature_model, feature))
    data_attr = []
    for data in data_fileds:
        data_attr.append(getattr(data_model, data))
    query = (
        session.query(*tuple(data_attr), *tuple(feature_attr))
        .select_from(data_model)
        .join(feature_model, feature_model.data_id == data_model.id)
        .filter(data_model.id == data_id)
    )
    return await conn.fetch_one(query2sql(query))


@con_warpper
async def get_multi(
    conn: Database,
    orm_model,
    shard_id: int,
    time_before: datetime,
    time_after: datetime,
    session: Session = session_make(engine=None),
):
    model = orm_model.model(point_id=shard_id)
    query = (
        session.query(model.id, model.time)
        .filter(model.time.between(str(time_before), str(time_after)))
        .order_by(model.id)
    )
    return await conn.fetch_all(query2sql(query))
