from databases import Database
from sqlalchemy import text
from sqlalchemy.orm import Session

from crud.base import query2sql
from db import session_make
from db_model import Asset, AssetHI
from services.query_processors.asset import format_timediff_result
from crud.base import multi_result_to_array
import json


async def get_avg_hi_pre(conn: Database, session: Session = session_make(engine=None)):
    query = session.query(Asset.id, Asset.name).filter(Asset.asset_type == 0)
    res = await conn.fetch_all(query2sql(query))
    return res


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


async def get_avg_hi_limit_latest(conn: Database, assets: list, limit: int) -> list:
    for index, asset in enumerate(assets):
        query = text(
            "SELECT time, health_indicator FROM asset_hi_{0} "
            "order by id desc "
            "limit {1}".format(asset["id"], limit)
        )
        res = await conn.fetch_all(query)
        res.reverse()
        assets[index]["health_indicator_history"] = [
            row["health_indicator"] for row in res
        ]

    return assets


async def get_similarity_threshold_during_time(
    conn: Database,
    asset_id: int,
    time_before: str,
    time_after: str,
    session: Session = session_make(engine=None),
):
    hi_model = AssetHI.model(point_id=asset_id)
    query = session.query(
        hi_model.id, hi_model.time, hi_model.similarity, hi_model.threshold
    ).filter(hi_model.time.between(str(time_after), str(time_before)))

    res = await conn.fetch_all(query2sql(query))
    dic = multi_result_to_array(res)
    return dic

async def get_similarity_threshold_near_by(
    conn: Database,
    asset_id: int,
    data_id: int,
    session: Session = session_make(engine=None),
):
    hi_model = AssetHI.model(point_id=asset_id)
    query = session.query(
        hi_model.id, hi_model.time, hi_model.similarity, hi_model.threshold
    ).filter(hi_model.id<=data_id).order_by(hi_model.id.desc()).limit(10)

    res = await conn.fetch_all(query2sql(query))
    res.reverse()
    dic = multi_result_to_array(res)
    return dic


async def get_similarity_threshold_recently(
    conn: Database,
    asset_id: int,
    limit: int,
    session: Session = session_make(engine=None),
):
    hi_model = AssetHI.model(point_id=asset_id)
    query = (
        session.query(
            hi_model.id, hi_model.time, hi_model.similarity, hi_model.threshold
        )
        .order_by(hi_model.time.desc())
        .limit(limit)
    )
    res = await conn.fetch_all(query2sql(query))
    res.reverse()
    dic = multi_result_to_array(res)
    return dic


async def get_estimated_value_by_id(
    conn: Database,
    asset_id: int,
    data_id: int,
    session: Session = session_make(engine=None),
):
    hi_model = AssetHI.model(point_id=asset_id)
    query = session.query(hi_model.id, hi_model.est).filter(hi_model.id == data_id)
    res = await conn.fetch_one(query2sql(query))
    dic = {"id": res["id"], "est": json.loads(res["est"])}
    return dic


async def get_estimated_value_multi(
    conn: Database,
    asset_id: int,
    time_before: str,
    time_after: str,
    session: Session = session_make(engine=None),
):
    hi_model = AssetHI.model(point_id=asset_id)
    query = session.query(hi_model.id, hi_model.time, hi_model.est).filter(
        hi_model.time.between(str(time_after), str(time_before))
    )
    res = await conn.fetch_all(query2sql(query))

    dic = {}
    for row in res:
        dic.setdefault("id", []).append(row["id"])
        dic.setdefault("time", []).append(str(row["time"]))

        serialized = json.loads(row["est"])
        for index, fileds in enumerate(serialized["label"]):
            dic.setdefault(fileds + "—原始值", []).append(serialized["raw"][index])
            dic.setdefault(fileds + "-估计值", []).append(serialized["est"][index])
    return dic
