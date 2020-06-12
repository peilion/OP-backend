import datetime
import json
from typing import Dict

import ujson
from fastapi import HTTPException
import orjson
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


async def update(conn: Database, mp_pattern: str, diag_threshold: Dict):
    threshold_update_query = "UPDATE threshold_copy1 SET md_time=:md_time,  diag_threshold=:diag_threshold where mp_pattern = :mp_pattern"
    transaction = await conn.transaction(force_rollback=True)
    try:
        await conn.execute(
            query=threshold_update_query,
            values={
                "md_time": datetime.datetime.now(),
                "diag_threshold": ujson.dumps(diag_threshold),
                "mp_pattern": mp_pattern,
            },
        )
    except Exception as e:
        await transaction.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    else:
        await transaction.commit()
        return True
