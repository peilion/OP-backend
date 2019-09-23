from fastapi import APIRouter
from starlette.responses import UJSONResponse
from sqlalchemy import text
from databases import Database
from db.conn_engine import INFO_URL
import psutil
from model.server import ServerInfoSchema
router = APIRouter()


@router.get("/", response_class=UJSONResponse,response_model=ServerInfoSchema)
async def read_equip_level_mapper(
):
    conn = Database(INFO_URL)
    s = text(
        "select concat(round(data_length/1024/1024,2),'MB') as table_volume, table_rows "
        "from tables "
        "where table_schema='op_1' and table_name='vib_data_1'")
    await conn.connect()
    res = await conn.fetch_one(s)
    await conn.disconnect()

    return {'table_volume': res.table_volume,
            'table_count': res.table_rows,
            'cpu_statu': psutil.cpu_percent(None),
            'memory_statu': psutil.virtual_memory().percent}
