from fastapi import APIRouter, Depends
from starlette.responses import UJSONResponse
from dependencies import get_mp_mapper
from databases import Database
from db.conn_engine import STATION_URLS
from crud.vib_signal import get

router = APIRouter()


@router.get("/measure_point/{measure_point}", response_class=UJSONResponse)
async def demo(
        measure_point: int,
        mp_mapper: dict = Depends(get_mp_mapper)
):
    mp_shard_info = mp_mapper[measure_point]
    conn = Database(STATION_URLS[mp_shard_info['station_id']])
    res = await get(conn=conn, id=mp_shard_info['inner_id'])
    return {'msg': res['id']}
