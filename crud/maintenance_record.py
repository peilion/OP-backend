from databases import Database
from sqlalchemy.orm import Session

from crud.decorator import con_warpper, query2sql
from db import meta_engine
from db.db_config import session_make
from db_model import MaintenanceRecord, Asset


@con_warpper
async def get_multi(conn: Database,
                    skip: int,
                    limit: int,
                    asset_id: int,
                    session: Session = session_make(engine=None)):
    query = session. \
        query(MaintenanceRecord, Asset.name.label('asset_name')). \
        join(Asset, Asset.id == MaintenanceRecord.asset_id). \
        order_by(MaintenanceRecord.statu.desc()). \
        offset(skip). \
        limit(limit)
    if asset_id:
        query = query.filter(Asset.id == asset_id)
    return await conn.fetch_all(query2sql(query))


@con_warpper
async def get(conn: Database, id: int, session: Session = session_make(engine=meta_engine)):
    query = session. \
        query(MaintenanceRecord, Asset.name.label('asset_name')). \
        join(Asset, Asset.id == MaintenanceRecord.asset_id). \
        filter(MaintenanceRecord.id == id)
    res = await conn.fetch_one(query2sql(query))

    return res