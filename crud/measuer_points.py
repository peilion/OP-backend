from databases import Database
from sqlalchemy import func
from sqlalchemy.orm import Session

from crud.decorator import con_warpper, query2sql
from db.db_config import session_make
from db_model import MeasurePoint, Station, Asset


@con_warpper
async def get_multi(conn: Database, skip: int, limit: int, brief: bool,
                    session: Session = session_make(engine=None), **kwargs):
    if brief:
        query = session.query(
            MeasurePoint.id,
            MeasurePoint.name,
            MeasurePoint.type)
    else:
        query = session.query(
            MeasurePoint.id,
            MeasurePoint.name,
            MeasurePoint.type,
            MeasurePoint.md_time,
            MeasurePoint.statu,
            MeasurePoint.health_indicator,
            MeasurePoint.sample_freq,
            MeasurePoint.sample_interval,
            Station.id.label('staion_id'),
            Station.name.label('station_name'),
            Asset.id.label('asset_id'),
            Asset.name.label('asset_name'))
    query = query.order_by(MeasurePoint.type). \
        offset(skip). \
        limit(limit). \
        join(Station, MeasurePoint.station_id == Station.id). \
        join(Asset, MeasurePoint.asset_id == Asset.id)
    if kwargs['station_id']:
        query = query.filter(MeasurePoint.station_id == kwargs['station_id'])
    if kwargs['asset_id']:
        query = query.filter(MeasurePoint.asset_id == kwargs['asset_id'])
    query = query.order_by(MeasurePoint.id)
    return await conn.fetch_all(query2sql(query))


@con_warpper
async def get(conn: Database, id: int, session: Session = session_make(engine=None)):
    query = session.query(
        MeasurePoint.id,
        MeasurePoint.name,
        MeasurePoint.type,
        MeasurePoint.md_time,
        MeasurePoint.statu,
        MeasurePoint.sample_freq,
        MeasurePoint.sample_interval).order_by(
        MeasurePoint.id).filter(
        MeasurePoint.id == id)
    return await conn.fetch_one(query2sql(query))


@con_warpper
async def get_stat(conn: Database, rule: str, session: Session = session_make(engine=None)):
    if rule == 'station':
        query = session.query(MeasurePoint.station_id, func.count(
            '*').label('cnt')).group_by(MeasurePoint.station_id)
    elif rule == 'asset':
        query = session.query(MeasurePoint.asset_id, func.count(
            '*').label('cnt')).group_by(MeasurePoint.asset_id)
    elif rule == 'statu':
        query = session.query(MeasurePoint.statu, func.count(
            '*').label('cnt')).group_by(MeasurePoint.statu)
    else:
        return None

    return await conn.fetch_all(query2sql(query))
