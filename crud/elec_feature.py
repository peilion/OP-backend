"""
This file is really similar to ./vib_feature, except the imported sharding model. It's a good idea to integrate them in the future.
"""

from databases import Database
from sqlalchemy.orm import Session, load_only
from crud.decorator import con_warpper, query2sql
from db.db_config import session_make
from db_model import ElecFeature
from typing import List


@con_warpper
async def get(conn: Database, shard_id: int, fileds: List[str], data_id: int,
              session: Session = session_make(engine=None)):
    model = ElecFeature.model(point_id=shard_id)

    query = session.query(model)
    for filed in fileds + ['id', 'time']:
        query = query.options(load_only(filed))
    query = query.filter(model.id == data_id)

    res = await conn.fetch_one(query2sql(query))
    return res


@con_warpper
async def get_latest(conn: Database, shard_id: int, fileds: List[str], session: Session = session_make(engine=None)):
    model = ElecFeature.model(point_id=shard_id)

    query = session.query(model)
    for filed in fileds + ['id', 'time']:
        query = query.options(load_only(filed))
    query = query.order_by(model.id.desc())

    res = await conn.fetch_one(query2sql(query))
    return res


@con_warpper
async def get_multi(conn: Database, shard_id: int, fileds: List[str], time_before: str, time_after: str, limit: 50,
                    session: Session = session_make(engine=None)):
    model = ElecFeature.model(point_id=shard_id)

    query = session.query(model)
    for filed in fileds + ['id', 'time']:
        query = query.options(load_only(filed))
    if limit is None:
        query = query. \
            order_by(model.id). \
            filter(model.time.between(str(time_after), str(time_before)))
    if limit:
        query = query.order_by(model.id.desc()).limit(limit)
    res = await conn.fetch_all(query2sql(query))


    dic = {}
    keys = res[0].keys()
    for row in reversed(res): # Ordered results are required in Chartist.js.
        for key in keys:
            if key == 'time':
                dic.setdefault(key, []).append(str(row[key]))
            else:
                dic.setdefault(key, []).append(row[key])
    return dic
