from databases import Database
from sqlalchemy import func
from sqlalchemy.orm import Session

from crud.base import query2sql
from db.db_config import session_make
from db_model.organization import Pipeline


async def get_multi(
    conn: Database, skip: int, limit: int, session: Session = session_make(engine=None)
):
    query = session.query(Pipeline).order_by(Pipeline.id).offset(skip).limit(limit)
    return await conn.fetch_all(query2sql(query))


async def get_total_length(
    conn: Database, session: Session = session_make(engine=None)
):
    query = session.query(func.sum(Pipeline.length).label("value")).select_from(
        Pipeline
    )
    return await conn.fetch_one(query2sql(query))
