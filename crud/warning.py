from databases import Database
from sqlalchemy import text, func
from sqlalchemy.orm import Session

from crud.base import con_warpper, query2sql
from db import meta_engine
from db.db_config import session_make
from db_model import WarningLog, Asset, Station
from db_model.organization import BranchCompany, RegionCompany


@con_warpper
async def get_multi(
    conn: Database,
    skip: int,
    limit: int,
    asset_id: int,
    session: Session = session_make(engine=None),
):
    query = (
        session.query(WarningLog, Asset.name.label("asset_name"))
        .join(Asset, Asset.id == WarningLog.asset_id)
        .order_by(WarningLog.cr_time.desc())
        .offset(skip)
        .limit(limit)
    )
    if asset_id:
        query = query.filter(Asset.id == asset_id)
    return await conn.fetch_all(query2sql(query))


@con_warpper
async def get(
    conn: Database, id: int, session: Session = session_make(engine=meta_engine)
):
    query = (
        session.query(WarningLog, Asset.name.label("asset_name"))
        .join(Asset, Asset.id == WarningLog.asset_id)
        .filter(WarningLog.id == id)
    )
    res = await conn.fetch_one(query2sql(query))
    if not res.is_read:
        session.query(WarningLog).filter(WarningLog.id == id).update(
            {WarningLog.is_read: True}
        )
        session.commit()
        session.close()
    return res


@con_warpper
async def get_warning_calendar(conn: Database):
    query = text(
        "SELECT date(warning_log.cr_time) as date ,count(*) as num "
        "from warning_log "
        "GROUP BY date(warning_log.cr_time) "
        "order by num desc"
    )

    res = await conn.fetch_all(query)
    return [{"date": row.date, "count": row.num} for row in res]


@con_warpper
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
        labels.append(row.name)
        series.append(row.cnt)
    return {"series": series, "labels": labels}


@con_warpper
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
        labels.append(row.name)
        series.append(row.cnt)
    return {"series": series, "labels": labels}


@con_warpper
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
        labels.append(row.name)
        series.append(row.cnt)
    return {"series": series, "labels": labels}


@con_warpper
async def get_warning_stat_by_asset(
    conn: Database, session: Session = session_make(engine=None)
):
    query = (
        session.query(WarningLog.asset_id, func.count("*").label("cnt"))
        .group_by(WarningLog.asset_id)
    )
    res = await conn.fetch_all(query2sql(query))
    return [[row.asset_id, row.cnt] for row in res]


@con_warpper
async def get_warning_stat_by_isreadable(
    conn: Database, session: Session = session_make(engine=None)
):
    query = (
        session.query(WarningLog.is_read, func.count("*").label("cnt"))
        .group_by(WarningLog.is_read)
    )
    res = await conn.fetch_all(query2sql(query))
    return [[row.is_read, row.cnt] for row in res]
