import psutil
from databases import Database
from fastapi import APIRouter
from sqlalchemy import text
from fastapi.responses import ORJSONResponse

from db.conn_engine import INFO_URL
from model.others import ServerInfoSchema

router = APIRouter()


@router.get("/", response_class=ORJSONResponse, response_model=ServerInfoSchema)
async def read_equip_level_mapper():
    conn = Database(INFO_URL)
    s = text("select sum(data_length) as volume " "from tables")
    await conn.connect()
    res = await conn.fetch_one(s)
    await conn.disconnect()

    return {
        "table_volume": str(res.volume) + " Bytes",
        "disk_usage": round(res.volume / 1024 / 1024 / 1024 / 3072 * 100, 2),
        "cpu_statu": psutil.cpu_percent(None),
        "memory_statu": psutil.virtual_memory().percent,
    }


psutil.net_io_counters()
