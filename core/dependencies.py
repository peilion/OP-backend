from databases import Database
from fastapi import HTTPException

from crud.base import query2sql
from db import session_make
from db.conn_engine import META_URL
from db_model import MeasurePoint

measure_point_router = {}


async def get_mp_mapper():
    if len(measure_point_router) == 0:
        async with Database(META_URL) as conn:
            session = session_make(engine=None)
            query = session.query(MeasurePoint)
            res = await conn.fetch_all(query2sql(query))
            for row in res:
                measure_point_router[row["id"]] = {
                    "sid": row["station_id"],
                    "iid": row["inner_station_id"],
                    "type": row["type"],
                }
    return measure_point_router


def mp_change_commit():
    measure_point_router = {}


def get_shard_model(model, mp_id: int, require_mp_type: int):
    mp_shard_info = measure_point_router[mp_id]
    if mp_shard_info["type"] != require_mp_type:
        raise HTTPException(
            status_code=400,
            detail="The given measure point collect different type, try to use the appropriate endpoint.",
        )
    return model.model(station_id=mp_shard_info["sid"], inner_id=mp_shard_info["iid"])


async def get_db():
    try:
        db = Database(META_URL)
        await db.connect()
        yield db
    finally:
        await db.disconnect()
