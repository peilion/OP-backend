from databases import Database
from sqlalchemy import text
from utils.query_result_reformat import format_timediff_result
from crud.decorator import con_warpper, query2sql
from db_model import Asset
from sqlalchemy.orm import Session
from db import session_make


@con_warpper
async def get_avg_hi_pre(conn: Database, session: Session = session_make(engine=None)):
    query = session.query(Asset.id, Asset.name).filter(Asset.asset_type == 0)
    res = await conn.fetch_all(query2sql(query))
    return res


@con_warpper
async def get_avg_hi_during_time(conn: Database, asset_id: int, time_before: str, time_after: str, interval: int):
    query = text('SELECT datediff( time, \'{0}\' ) DIV {3} AS diff, AVG( health_indicator ) as avg FROM asset_hi_{2} ' \
                 'WHERE time BETWEEN \'{0}\' and \'{1}\' ' \
                 'GROUP BY( datediff( time, \'{0}\' ) DIV {3} )'.format(time_after, time_before, asset_id, interval))

    res = await conn.fetch_all(query)
    res = format_timediff_result(res, time_after=time_after, interval=interval)
    return res


@con_warpper
async def get_avg_hi_before_limit(conn: Database, asset_id: int, time_before: str, interval: int, limit: int):
    query = text('SELECT datediff( time, \'{0}\' ) DIV {2} AS diff, AVG( health_indicator ) as avg '
                 'FROM asset_hi_{1} ' \
                 'WHERE time <= \'{0}\' ' \
                 'GROUP BY diff desc '
                 'limit {3}'.format(time_before, asset_id, interval, limit))

    res = await conn.fetch_all(query)

    res = format_timediff_result(res, time_after=time_before, interval=interval)
    return res
