from databases import Database

from crud.base import query2sql
from db import session_make
from db.conn_engine import META_URL
from db_model import MeasurePoint

measure_point_regsiter = {}


async def get_mp_mapper():
    if len(measure_point_regsiter) == 0:
        async with Database(META_URL) as conn:
            session = session_make(engine=None)
            query = session.query(MeasurePoint)
            res = await conn.fetch_all(query2sql(query))
            for row in res:
                measure_point_regsiter[row["id"]] = {
                    "shard_id": row["id"],
                    "type": row["type"],
                }
    return measure_point_regsiter


def mp_change_commit():
    measure_point_regsiter = {}
