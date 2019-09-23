from databases import Database
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from crud.decorator import con_warpper, query2sql
from db.db_config import session_make
from db_model import WarningLog, Asset


@con_warpper
async def get_multi(conn: Database,
                    skip: int,
                    limit: int,
                    asset_id: int,
                    session: Session = session_make(engine=None)):
    query = session. \
        query(WarningLog, Asset.name.label('asset_name')). \
        join(Asset, Asset.id == WarningLog.asset_id). \
        order_by(WarningLog.id). \
        offset(skip). \
        limit(limit)
    if asset_id:
        query = query.filter(Asset.id == asset_id)
    return await conn.fetch_all(query2sql(query))


@con_warpper
async def get(conn: Database, id: int, session: Session = session_make(engine=None)):
    query = session. \
        query(WarningLog, Asset.name.label('asset_name')). \
        join(Asset, Asset.id == WarningLog.asset_id). \
        filter(WarningLog.id == id)
    return await conn.fetch_one(query2sql(query))


@con_warpper
async def get_warning_calendar(conn: Database):
    query = text('SELECT date(warning_log.cr_time) as date ,count(*) as num '
                 'from warning_log '
                 'GROUP BY date(warning_log.cr_time)')

    res = await conn.fetch_all(query)
    return [[row.date, row.num] for row in res]


@con_warpper
async def get_warning_stat_by_station(conn: Database, session: Session = session_make(engine=None)):
    query = session. \
        query(Asset.station_id, func.count(WarningLog.asset_id).label('cnt')). \
        join(Asset). \
        group_by(Asset.station_id)

    res = await conn.fetch_all(query2sql(query))
    return [[row.station_id, row.cnt] for row in res]


@con_warpper
async def get_warning_stat_by_asset(conn: Database, session: Session = session_make(engine=None)):
    query = session.query(WarningLog.asset_id, func.count('*').label('cnt')). \
        group_by(WarningLog.asset_id)
    res = await conn.fetch_all(query2sql(query))
    return [ [row.asset_id,row.cnt] for row in res]
