from databases import Database
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from crud.decorator import con_warpper, query2sql
from db.db_config import session_make
from db_model import VibData


@con_warpper
async def get(conn: Database, id: int, session: Session = session_make(engine=None)):
    model = VibData.model(point_id=id)
    query = session. \
        query(model). \
        order_by(model.id.desc())
    return await conn.fetch_one(query2sql(query))
