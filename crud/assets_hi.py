from databases import Database
from sqlalchemy import text
from sqlalchemy.orm import Session

from crud.decorator import con_warpper, query2sql
from db import session_make
from db_model import Asset
from utils.query_result_reformat import format_timediff_result


@con_warpper
async def get_avg_hi_pre(conn: Database, session: Session = session_make(engine=None)):
    query = session.query(Asset.id, Asset.name).filter(Asset.asset_type == 0)
    res = await conn.fetch_all(query2sql(query))
    return res


@con_warpper
async def get_avg_hi_during_time(
    conn: Database, asset_id: int, time_before: str, time_after: str, interval: int
):
    query = text(
        "SELECT datediff( time, '{0}' ) DIV {3} AS diff, AVG( health_indicator ) as avg FROM asset_hi_{2} "
        "WHERE time BETWEEN '{0}' and '{1}' "
        "GROUP BY( datediff( time, '{0}' ) DIV {3} )".format(
            time_after, time_before, asset_id, interval
        )
    )

    res = await conn.fetch_all(query)
    res = format_timediff_result(res, time_after=time_after, interval=interval)
    return res


@con_warpper
async def get_avg_hi_before_limit(
    conn: Database, asset_id: int, interval: int, limit: int
):
    import datetime

    time_before = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    query = text(
        "SELECT datediff( time, '{0}' ) DIV {2} AS diff, AVG( health_indicator ) as avg "
        "FROM asset_hi_{1} "
        "WHERE time <= '{0}' "
        "GROUP BY diff "
        "limit {3}".format(time_before, asset_id, interval, limit)
    )

    res = await conn.fetch_all(query)

    res = format_timediff_result(res, time_after=time_before, interval=interval)
    return res


@con_warpper
async def get_avg_hi_multi(conn: Database, asset_id: int, time_before: str, limit: int):
    query = text(
        "SELECT time, health_indicator FROM asset_hi_{0} "
        "WHERE time <= '{1}' "
        "order by time desc "
        "limit {2}".format(asset_id, time_before, limit)
    )
    res = await conn.fetch_all(query)

    dic = {"time_list": [], "health_indicator": []}
    for row in reversed(res):  # Ordered results are required in Chartist.js.
        dic["time_list"].append(str(row["time"]))
        dic["health_indicator"].append(row["health_indicator"])
    return dic
