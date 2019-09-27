from databases import Database
from sqlalchemy import func
from sqlalchemy.orm import Session

from crud.decorator import con_warpper, query2sql
from db.db_config import session_make
from db_model import MeasurePoint, Station, Asset


@con_warpper
async def get_multi(conn: Database, skip: int, limit: int,
                    session: Session = session_make(engine=None), **kwargs):
    query = session. \
        query(MeasurePoint.id, MeasurePoint.name, MeasurePoint.type, MeasurePoint.md_time, MeasurePoint.cr_time,MeasurePoint.statu,
              Station.id.label('staion_id'), Station.name.label('station_name'),
              Asset.id.label('asset_id'), Asset.name.label('asset_name')). \
        order_by(MeasurePoint.id). \
        offset(skip). \
        limit(limit). \
        join(Station, MeasurePoint.station_id == Station.id). \
        join(Asset, MeasurePoint.asset_id == Asset.id)
    if kwargs['station_id']:
        query = query.filter(MeasurePoint.station_id == kwargs['station_id'])
    if kwargs['asset_id']:
        query = query.filter(MeasurePoint.asset_id == kwargs['asset_id'])
    return await conn.fetch_all(query2sql(query))


@con_warpper
async def get(conn: Database, id: int, session: Session = session_make(engine=None)):
    query = session. \
        query(MeasurePoint.id, MeasurePoint.name, MeasurePoint.type, MeasurePoint.md_time, MeasurePoint.cr_time,MeasurePoint.statu,
              Station.id.label('staion_id'), Station.name.label('station_name'),
              Asset.id.label('asset_id'), Asset.name.label('asset_name')). \
        order_by(MeasurePoint.id). \
        join(Station, MeasurePoint.station_id == Station.id). \
        join(Asset, MeasurePoint.asset_id == Asset.id). \
        filter(MeasurePoint.asset_id == id)
    return await conn.fetch_one(query2sql(query))


@con_warpper
async def get_stat(conn: Database, rule: str, session: Session = session_make(engine=None)):
    query = None
    if rule == 'station':
        query = session.query(MeasurePoint.station_id, func.count('*').label('cnt')). \
            group_by(MeasurePoint.station_id)
    elif rule == 'asset':
        query = session.query(MeasurePoint.asset_id, func.count('*').label('cnt')). \
            group_by(MeasurePoint.asset_id)
    elif rule == 'statu':
        query = session.query(MeasurePoint.statu, func.count('*').label('cnt')). \
            group_by(MeasurePoint.statu)
    else:
        return None

    return await conn.fetch_all(query2sql(query))
