from db import session_make, meta_engine
from db.conn_engine import META_URL
from db_model import MeasurePoint
from crud.base import query2sql
from databases import Database

measure_point_regsiter = {}


async def get_mp_mapper():
    if len(measure_point_regsiter) == 0:
        async with Database(META_URL) as conn:
            session = session_make(engine=None)
            query = session.query(
                MeasurePoint.id,
                MeasurePoint.station_id,
                MeasurePoint.id_inner_station,
                MeasurePoint.type,
            )
            res = await conn.fetch_all(query2sql(query))
            for row in res:
                measure_point_regsiter[row['id']] = {
                    "station_id": row['station_id'],
                    "inner_id": row['id_inner_station'],
                    "type": row['type'],
                }
    return measure_point_regsiter


def mp_change_commit():
    measure_point_regsiter = {}
