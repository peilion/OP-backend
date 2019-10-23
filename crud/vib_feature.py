from typing import List

from databases import Database
from fastapi import HTTPException
from sqlalchemy.orm import Session, load_only

from crud.decorator import con_warpper, query2sql
from db.db_config import session_make
from db_model import VibFeature


@con_warpper
async def get(conn: Database, shard_id: int, fileds: List[str], data_id: int,
              session: Session = session_make(engine=None)):
    model = VibFeature.model(point_id=shard_id)

    query = session.query(model)
    for filed in fileds + ['id', 'time']:
        query = query.options(load_only(filed))
    query = query.filter(model.id == data_id)

    res = await conn.fetch_one(query2sql(query))
    return res


@con_warpper
async def get_latest(conn: Database, shard_id: int, fileds: List[str], session: Session = session_make(engine=None)):
    model = VibFeature.model(point_id=shard_id)

    query = session.query(model)
    # for filed in fileds + ['id', 'time']:
    for filed in fileds:
        query = query.options(load_only(filed))
    query = query.order_by(model.id.desc()).limit(1)

    res = await conn.fetch_one(query2sql(query))
    return res


@con_warpper
async def get_multi(conn: Database, shard_id: int, fileds: List[str], time_before: str, time_after: str, limit: int,
                    session: Session = session_make(engine=None)):
    model = VibFeature.model(point_id=shard_id)

    query = session.query(model)
    for filed in fileds + ['id', 'time']:
        query = query.options(load_only(filed))

    if time_before != 'None':
        query = query. \
            filter(model.time.between(str(time_after), str(time_before)))
    query = query.order_by(model.time)

    if limit:
        query = query.limit(limit)
    res = await conn.fetch_all(query2sql(query))

    if len(res) == 0 :
        raise HTTPException(status_code=400,
                            detail="No signal collected between the time range")

    dic = {}
    keys = res[0].keys()
    for row in res:
        for key in keys:
            if key == 'time':
                dic.setdefault(key, []).append(str(row[key]))
            else:
                dic.setdefault(key, []).append(row[key])
    return dic
