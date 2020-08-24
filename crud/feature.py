from typing import List

from databases import Database
from fastapi import HTTPException
from sqlalchemy.orm import Session, load_only

from core.dependencies import get_shard_model
from crud.base import query2sql
from db.db_config import session_make


async def get(
    conn: Database,
    mp_id: int,
    require_mp_type: int,
    orm_model,
    fileds: List[str],
    data_id: int,
    session: Session = session_make(engine=None),
):
    model = get_shard_model(orm_model, mp_id=mp_id, require_mp_type=require_mp_type)

    query = session.query(model)
    for filed in fileds + ["id", "time"]:
        query = query.options(load_only(filed))
    query = query.filter(model.data_id == data_id)

    res = await conn.fetch_one(query2sql(query))
    return res


async def get_latest(
    conn: Database,
    mp_id: int,
    require_mp_type: int,
    orm_model,
    fileds: List[str],
    session: Session = session_make(engine=None),
):
    model = get_shard_model(orm_model, mp_id=mp_id, require_mp_type=require_mp_type)

    query = session.query(model)
    for filed in fileds:
        query = query.options(load_only(filed))
    query = query.order_by(model.id.desc()).limit(1)

    res = await conn.fetch_one(query2sql(query))
    return res


async def get_multi(
    conn: Database,
    mp_id: int,
    require_mp_type: int,
    orm_model,
    fileds: List[str],
    time_before: str,
    time_after: str,
    limit: int,
    with_estimated: bool = False,
    session: Session = session_make(engine=None),
):
    model = get_shard_model(orm_model, mp_id=mp_id, require_mp_type=require_mp_type)

    query = session.query(model)
    for filed in fileds + ["id", "time", "data_id"]:
        query = query.options(load_only(filed))

    if with_estimated:
        for filed in fileds:
            query = (
                query.options(load_only("est_" + filed))
                if filed != "similarity"
                else query
            )

    if time_before != "None":
        query = query.filter(model.time.between(str(time_after), str(time_before)))
        query = query.order_by(model.time.desc())

    if limit:
        query = query.order_by(model.time.desc()).limit(limit)
    res = await conn.fetch_all(query2sql(query))
    res.reverse()
    if len(res) == 0:
        raise HTTPException(
            status_code=400, detail="No signal collected between the time range"
        )

    dic = {}
    keys = res[0].keys()
    for row in res:
        for key in keys:
            if key == "time":
                dic.setdefault(key, []).append(str(row[key]))
            else:
                dic.setdefault(key, []).append(row[key])
    return dic
