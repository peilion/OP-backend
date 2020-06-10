from databases import Database
from sqlalchemy.orm import Session

from crud.base import query2sql
from db.db_config import session_make
from db_model import Threshold


async def get_multi(
    conn: Database, session: Session = session_make(engine=None),
):
    query = session.query(Threshold)

    return await conn.fetch_all(query2sql(query))
