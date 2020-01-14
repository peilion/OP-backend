from databases import Database
from sqlalchemy import func
from sqlalchemy.orm import Session

from crud.base import query2sql
from db import meta_engine
from db.db_config import session_make
from db_model import MaintenanceRecord, Asset
from services.query_processors.general import format_single_grouped_result


async def get_multi(
    conn: Database,
    skip: int,
    limit: int,
    asset_id: int,
    session: Session = session_make(engine=None),
):
    query = (
        session.query(MaintenanceRecord, Asset.name.label("asset_name"))
        .join(Asset, Asset.id == MaintenanceRecord.asset_id)
        .order_by(MaintenanceRecord.statu.desc())
        .offset(skip)
        .limit(limit)
    )
    if asset_id:
        query = query.filter(Asset.id == asset_id)
    return await conn.fetch_all(query2sql(query))


async def get(
    conn: Database, id: int, session: Session = session_make(engine=meta_engine)
):
    query = (
        session.query(MaintenanceRecord, Asset.name.label("asset_name"))
        .join(Asset, Asset.id == MaintenanceRecord.asset_id)
        .filter(MaintenanceRecord.id == id)
    )
    res = await conn.fetch_one(query2sql(query))

    return res


async def get_statu_stat(
    conn: Database, session: Session = session_make(engine=meta_engine)
):
    query = (
        session.query(MaintenanceRecord.statu, func.count("*"))
        .select_from(MaintenanceRecord)
        .group_by(MaintenanceRecord.statu)
    )
    res = await conn.fetch_all(query2sql(query))

    return format_single_grouped_result(res=res, group_names=MaintenanceRecord.STATUS)
