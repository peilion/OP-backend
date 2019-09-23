from databases import Database
from sqlalchemy.orm import Session

from crud.decorator import con_warpper, query2sql
from db.db_config import session_make
from db_model.station import Station


@con_warpper
async def get_multi(conn: Database, skip: int, limit: int, session: Session = session_make(engine=None)):
    query = session. \
        query(Station). \
        order_by(Station.id).\
        offset(skip). \
        limit(limit)
    return await conn.fetch_all(query2sql(query))


@con_warpper
async def get(conn: Database, id: int, session: Session = session_make(engine=None)):
    query = session. \
        query(Station). \
        filter(Station.id == id)

    return await conn.fetch_one(query2sql(query))
