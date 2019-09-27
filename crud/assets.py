from databases import Database
from sqlalchemy.orm import Session, joinedload

from crud.decorator import con_warpper, query2sql
from db.db_config import session_make
from db_model import Asset, Station, Bearing, PumpUnit, Motor, Pump, Stator, Rotor


info_model_mapper = {
    'Bearing': Bearing, 'PumpUnit': PumpUnit, 'Motor': Motor, 'Pump': Pump, 'Stator': Stator, 'Rotor': Rotor
}


@con_warpper
async def get_multi(conn: Database, skip: int, limit: int, session: Session = session_make(engine=None)):
    query = session. \
        query(Asset.id, Asset.name, Asset.sn, Asset.lr_time, Asset.cr_time, Asset.md_time, Asset.asset_level,
              Asset.memo, Asset.health_indicator, Asset.statu, Asset.parent_id, Asset.station_id,
              Station.name.label('station_name')). \
        join(Station, Station.id == Asset.station_id). \
        order_by(Asset.id). \
        offset(skip). \
        limit(limit)
    return await conn.fetch_all(query2sql(query))


@con_warpper
async def get(conn: Database, id: int, session: Session = session_make(engine=None)):
    query = session. \
        query(Asset.id, Asset.name, Asset.sn, Asset.lr_time, Asset.cr_time, Asset.md_time, Asset.asset_level,
              Asset.memo, Asset.health_indicator, Asset.statu, Station.name.label('station_name')). \
        join(Station, Station.id == Asset.station_id). \
        filter(Asset.id == id)

    return await conn.fetch_one(query2sql(query))

@con_warpper
async def get_info(session: Session,conn: Database, id: int):
    name = session.query(Asset.name).filter(Asset.id == id).one().name.split('#')[0]
    model = info_model_mapper[name]
    query = session. \
        query(model). \
        filter(model.asset_id == id)
    return await conn.fetch_one(query2sql(query))  # Sqlalchemy query do not support async/await


def get_multi_tree(session: Session, skip: int, limit: int, ):
    query = session. \
        query(Asset). \
        filter(Asset.asset_level == 0). \
        options(joinedload(Asset.children)). \
        order_by(Asset.id). \
        offset(skip). \
        limit(limit)

    return query.all()  # Sqlalchemy query do not support async/await


def get_tree(session: Session, id: int):
    query = session. \
        query(Asset). \
        filter(Asset.id == id)

    return query.one()


@con_warpper
async def get_count_by_statu(conn: Database):
    query = 'SELECT statu, COUNT(*) as cnt FROM `asset` GROUP BY statu'
    res = await conn.fetch_all(query)
    dic = {}
    for row in res:
        dic[Asset.STATUS[row.statu]] = row.cnt
    return dic


@con_warpper
async def get_count_by_station(conn: Database):
    query = 'SELECT station_id, COUNT(*) as cnt FROM `asset` GROUP BY station_id'
    return await conn.fetch_all(query)


@con_warpper
async def get_count_by_both(conn: Database):
    query = 'SELECT station_id,statu, COUNT(*) as cnt FROM `asset` GROUP BY statu,station_id ORDER BY statu'
    res = await conn.fetch_all(query)
    res_dict = {}
    for item in res:
        station_name = Station.STATIONS[item[0]]
        statu_name = Asset.STATUS[item[1]]
        if res_dict.get(station_name) is None:
            res_dict.setdefault(station_name, {})
            res_dict[station_name][statu_name] = item[2]
        else:
            res_dict[station_name][statu_name] = item[2]
    return res_dict
