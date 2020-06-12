import datetime

import orjson
from databases import Database
from sqlalchemy import text, func
from sqlalchemy.orm import Session

from crud.base import query2sql
from db import meta_engine
from db.db_config import session_make
from db_model import WarningLog, Asset, Station, MeasurePoint, MsetWarningLog, Threshold
from db_model.log import MaintenanceSuggestion
from db_model.organization import BranchCompany, RegionCompany
from services.query_processors.warning import warning_description_formatter


async def get_multi(
    conn: Database,
    skip: int,
    limit: int,
    asset_id: int,
    isread: bool,
    session: Session = session_make(engine=None),
):
    query = (
        session.query(
            WarningLog.id,
            WarningLog.severity,
            WarningLog.description,
            WarningLog.cr_time,
            WarningLog.is_read,
            MeasurePoint.name.label("measure_point_name"),
            WarningLog.data_id,
            WarningLog.mp_id,
            Asset.name.label("asset_name"),
            WarningLog.asset_id,
        )
        .join(Asset, Asset.id == WarningLog.asset_id)
        .join(MeasurePoint, MeasurePoint.id == WarningLog.mp_id)
        .order_by(WarningLog.cr_time.desc())
    )
    if asset_id:
        query = query.filter(Asset.id == asset_id)
    if isread is not None:
        query = query.filter(WarningLog.is_read == int(isread))
    query = query.offset(skip).limit(limit)
    res = await conn.fetch_all(query2sql(query))
    return res


async def get(
    conn: Database, id: int, session: Session = session_make(engine=meta_engine)
):
    query = (
        session.query(WarningLog, Threshold.diag_threshold.label("thres"))
        .filter(WarningLog.id == id)
        .join(Threshold, Threshold.id == WarningLog.threshold_id)
    )
    res = await conn.fetch_one(query2sql(query))
    diag_res = orjson.loads(res["description"])
    suggestions = []
    for fault_pattern, severity in diag_res.items():
        if severity != 0:
            query = session.query(MaintenanceSuggestion.suggestion).filter(
                MaintenanceSuggestion.fault_pattern == fault_pattern,
                MaintenanceSuggestion.severity == severity,
            )
            suggestion = await conn.fetch_one(query2sql(query))
            suggestions.append(suggestion["suggestion"])
    if not res.is_read:
        update_query = "Update warning_log set is_read=:isread where id = :id"
        await conn.execute(update_query, {"isread": True, "id": id})
    return {"suggestions": suggestions, **dict(res)}


async def get_warning_calendar(conn: Database):
    query = text(
        "SELECT date(warning_log.cr_time) as date ,count(*) as num "
        "from warning_log "
        "GROUP BY date(warning_log.cr_time) "
        "order by num desc"
    )

    res = await conn.fetch_all(query)
    return [{"date": row["date"], "count": row["num"]} for row in res]


async def get_warning_stat_by_station(
    conn: Database, session: Session = session_make(engine=None)
):
    query = (
        session.query(
            Asset.station_id, Station.name, func.count(WarningLog.asset_id).label("cnt")
        )
        .select_from(WarningLog)
        .join(Asset)
        .join(Station, Asset.station_id == Station.id)
        .group_by(Asset.station_id)
    )

    res = await conn.fetch_all(query2sql(query))
    labels = []
    series = []
    for row in res:
        labels.append(row["name"])
        series.append(row["cnt"])
    return {"series": series, "labels": labels}


async def get_warning_stat_by_branch_company(
    conn: Database, session: Session = session_make(engine=None)
):
    query = (
        session.query(BranchCompany.name, func.count(WarningLog.asset_id).label("cnt"))
        .select_from(WarningLog)
        .join(Asset)
        .join(Station, Asset.station_id == Station.id)
        .join(BranchCompany, Station.bc_id == BranchCompany.id)
        .group_by(Asset.station_id)
    )

    res = await conn.fetch_all(query2sql(query))
    labels = []
    series = []
    for row in res:
        labels.append(row["name"])
        series.append(row["cnt"])
    return {"series": series, "labels": labels}


async def get_warning_stat_by_region_company(
    conn: Database, session: Session = session_make(engine=None)
):
    query = (
        session.query(RegionCompany.name, func.count(WarningLog.asset_id).label("cnt"))
        .select_from(WarningLog)
        .join(Asset)
        .join(Station, Asset.station_id == Station.id)
        .join(RegionCompany, Station.rc_id == RegionCompany.id)
        .group_by(Asset.station_id)
    )

    res = await conn.fetch_all(query2sql(query))
    labels = []
    series = []
    for row in res:
        labels.append(row["name"])
        series.append(row["cnt"])
    return {"series": series, "labels": labels}


async def get_warning_stat_by_asset(
    conn: Database, session: Session = session_make(engine=None)
):
    query = session.query(WarningLog.asset_id, func.count("*").label("cnt")).group_by(
        WarningLog.asset_id
    )
    res = await conn.fetch_all(query2sql(query))
    return [[row["asset_id"], row["cnt"]] for row in res]


async def get_warning_stat_by_isreadable(
    conn: Database, session: Session = session_make(engine=None)
):
    query = session.query(WarningLog.is_read, func.count("*").label("cnt")).group_by(
        WarningLog.is_read
    )
    res = await conn.fetch_all(query2sql(query))
    if len(res) != 0:
        return {"unread": res[0][0], "read": res[0][1]}
    else:
        return {"unread": 0, "read": 0}


async def get_warning_stat_by_period(
    conn: Database, session: Session = session_make(engine=None)
):
    now = datetime.datetime.now()
    last_day = now - datetime.timedelta(days=1)
    last_week = now - datetime.timedelta(days=7)
    last_month = now - datetime.timedelta(weeks=4)
    last_year = now - datetime.timedelta(weeks=48)
    final = []
    for start_date in [last_day, last_week, last_month, last_year]:
        query1 = (
            session.query(func.count("*").label("cnt"))
            .select_from(WarningLog)
            .filter(WarningLog.cr_time.between(str(start_date), str(now)))
        )
        query2 = (
            session.query(func.count("*").label("cnt"))
            .select_from(MsetWarningLog)
            .filter(MsetWarningLog.cr_time.between(str(start_date), str(now)))
        )
        res1 = await conn.fetch_one(query2sql(query1))
        res2 = await conn.fetch_one(query2sql(query2))

        final.append([res1["cnt"], res2["cnt"]])
    return {
        "last_day": final[0][0] + final[0][1],
        "last_week": final[1][0] + final[1][1],
        "last_month": final[2][0] + final[2][1],
        "last_year": final[3][0] + final[3][1],
    }
