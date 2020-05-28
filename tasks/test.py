from databases import Database
import asyncio
from crud.base import query2sql
from custom_lib.treelib import Tree
from db import session_make
from db.conn_engine import META_URL
from db_model import Asset, MeasurePoint, Bearing, Threshold
from services.diagnosis.processors import motor_non_driven_end_diagnosis, motor_driven_end_diagnosis, \
    pump_non_driven_end_diagnosis, pump_driven_end_diagnosis
import orjson

position_type_mapper = {
    'motor_non_driven': (2, 'N', motor_non_driven_end_diagnosis),
    'motor_driven': (2, 'D', motor_driven_end_diagnosis),
    'pump_non_driven': (1, 'N', pump_non_driven_end_diagnosis),
    'pump_driven': (1, 'D', pump_driven_end_diagnosis),
}


def tree_list_format(items: list):
    tree = Tree()
    tree.create_node(tag="root", identifier="root")
    items = [dict(row) for row in items]
    for item in items:
        tree.create_node(data=item, identifier=item["id"], parent="root")

    for node in tree.expand_tree(mode=Tree.WIDTH):
        if node != "root":
            if tree[node].data["parent_id"]:
                tree.move_node(node, tree[node].data["parent_id"])
    return tree.to_dict(with_data=True)["children"]


async def expert_system_diagnosis():
    db = Database(META_URL)
    await db.connect()
    session = session_make(engine=None)
    assets = await db.fetch_all(
        query2sql(
            session.query(Asset.id, Asset.name, Asset.parent_id, Asset.asset_type)
        ))
    assets = tree_list_format(assets)
    assets = {asset['id']: asset for asset in assets}

    mps = await db.fetch_all(
        query2sql(
            session.query(MeasurePoint.id, MeasurePoint.name, MeasurePoint.station_id, MeasurePoint.inner_station_id,
                          MeasurePoint.asset_id, MeasurePoint.last_diag_id, MeasurePoint.position,
                          MeasurePoint.direction).filter(MeasurePoint.type == 0)
        ))
    for mp in mps:
        assets[mp.asset_id].setdefault('mps', {})
        assets[mp.asset_id]['mps'][mp.name] = {**dict(mp)}

    for (asset_id, asset) in assets.items():
        if 'mps' in asset:  # 跳过未添加测点的设备
            for (mp_name, mp) in asset['mps'].items():
                query = "SELECT id, ima as vib " \
                        "from vib_data_{0}_{1} as d " \
                        "where id > {2} " \
                        "limit 10;".format(mp['station_id'], mp['inner_station_id'],
                                           mp['last_diag_id'] if mp['last_diag_id'] is not None else 0)
                signals = await db.fetch_all(query)

                bearing_id = None
                for equip in asset['children']:
                    if equip['asset_type'] == position_type_mapper[mp['position']][0]:
                        for bearing in equip['children']:
                            if bearing['name'].startswith(position_type_mapper[mp['position']][1]):
                                bearing_id = bearing['id']

                bearing_info = await db.fetch_one(
                    query2sql(
                        session.query(Bearing.bpfi, Bearing.bpfo, Bearing.bsf, Bearing.ftf).
                            filter(Bearing.asset_id == bearing_id).
                            limit(1)
                    ))
                if bearing_id & bearing_info:
                    th = await db.fetch_one(
                        query2sql(
                            session.query(Threshold.diag_threshold).filter(Threshold.mp_pattern == mp['position'])
                        )
                    )
                    diag_res = None
                    for signal in signals:
                        diag_method = position_type_mapper[mp['position']][2]
                        diag_res = diag_method(data=signal['vib'], fs=10000, R=2800, bearing_ratio=dict(bearing_info),
                                               th=orjson.loads(th['diag_threshold']))

    await db.disconnect()
    return diag_res


if __name__ == '__main__':
    x = asyncio.run(expert_system_diagnosis())
