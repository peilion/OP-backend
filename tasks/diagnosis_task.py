import datetime
from typing import Dict

import numpy as np

from custom_lib.treelib import Tree
from db import session_make
from db.conn_engine import meta_engine
from db_model import Asset, MeasurePoint, Bearing, Threshold, WarningLog, VibData
from services.diagnosis.processors import (
    motor_non_driven_end_diagnosis,
    motor_driven_end_diagnosis,
    pump_non_driven_end_diagnosis,
    pump_driven_end_diagnosis,
)

position_type_mapper = {
    "motor_non_driven": (
        2,
        "非",
        motor_non_driven_end_diagnosis,
    ),  # asset_type, bearing position , and diagnosis method
    "motor_driven": (2, "驱", motor_driven_end_diagnosis),
    "pump_non_driven": (1, "非", pump_non_driven_end_diagnosis),
    "pump_driven": (1, "驱", pump_driven_end_diagnosis),
}


def fetch_assets(session):
    assets = session.query(
        Asset.id, Asset.name, Asset.parent_id, Asset.asset_type
    ).all()
    tree = Tree()
    tree.create_node(tag="root", identifier="root")
    for item in assets:
        tree.create_node(data=item._asdict(), identifier=item.id, parent="root")

    for node in tree.expand_tree(mode=Tree.WIDTH):
        if node != "root":
            if tree[node].data["parent_id"]:
                tree.move_node(node, tree[node].data["parent_id"])
    assets = tree.to_dict(with_data=True)["children"]

    return {asset["id"]: asset for asset in assets}


def fetch_mps(session):
    mps = (
        session.query(
            MeasurePoint.id,
            MeasurePoint.name,
            MeasurePoint.station_id,
            MeasurePoint.inner_station_id,
            MeasurePoint.asset_id,
            MeasurePoint.last_diag_id,
            MeasurePoint.position,
            MeasurePoint.direction,
        )
        .filter(MeasurePoint.type == 0, MeasurePoint.position != "pipeline")
        .all()
    )
    return mps


def fetch_data(session, mp: Dict):
    data_model = VibData.model(
        station_id=mp["station_id"], inner_id=mp["inner_station_id"]
    )
    last_diag_id = mp["last_diag_id"] if mp["last_diag_id"] is not None else 0
    signals = (
        session.query(data_model.id, data_model.time, data_model.ima.label("vib"))
        .filter(data_model.id > last_diag_id)
        .limit(10)
        .all()
    )
    return signals


def fetch_bearing_info(session, asset: Dict, mp: Dict):
    bearing_id = None
    for equip in asset["children"]:
        if equip["asset_type"] == position_type_mapper[mp["position"].name][0]:
            for bearing in equip["children"]:
                if bearing["name"].startswith(
                    position_type_mapper[mp["position"].name][1]
                ):
                    bearing_id = bearing["id"]

    bearing_info = (
        session.query(Bearing.bpfi, Bearing.bpfo, Bearing.bsf, Bearing.ftf)
        .filter(Bearing.asset_id == bearing_id)
        .limit(1)
        .one()
    )
    return bearing_id, bearing_info


def expert_system_diagnosis():
    session = session_make(engine=meta_engine)
    assets = fetch_assets(session)
    mps = fetch_mps(session)
    processed_row = 0
    # 获取设备-测点树
    for mp in mps:
        assets[mp.asset_id].setdefault("mps", {})
        assets[mp.asset_id]["mps"][mp.name] = mp._asdict()

    for (asset_id, asset) in assets.items():  # 遍历所有设备
        if "mps" in asset:  # 跳过未添加测点的设备
            for (mp_name, mp) in asset["mps"].items():  # 遍历某设备的所有测点

                signal_list = fetch_data(session, mp)
                # 获取轴承信息
                bearing_id, bearing_info = fetch_bearing_info(
                    session, asset=asset, mp=mp
                )

                if (bearing_id is not None) & (len(bearing_info) != 0):
                    th = (
                        session.query(Threshold.id, Threshold.diag_threshold)
                        .filter(Threshold.mp_pattern == mp["position"].name)
                        .order_by(Threshold.id.desc())
                        .one()
                    )

                    diag_res_insert_value = []
                    for index, signal in enumerate(signal_list):
                        diag_method = position_type_mapper[mp["position"].name][2]
                        diag_res, marks, indicators = diag_method(
                            data=signal.vib,
                            fs=10000,
                            R=2800,
                            bearing_ratio=bearing_info._asdict(),
                            th=th.diag_threshold,
                        )
                        diag_res_sum = np.array(list(diag_res.values())).sum()
                        try:
                            if diag_res_sum != 0:
                                diag_res_insert_value.append(
                                    WarningLog(
                                        description=diag_res,
                                        marks=marks,
                                        threshold_id=th.id,
                                        severity=int(diag_res_sum - 1)
                                        if diag_res_sum < 3
                                        else 2,
                                        asset_id=asset_id,
                                        mp_id=mp["id"],
                                        cr_time=signal.time,
                                        is_read=False,
                                        data_id=signal.id,
                                        **indicators
                                    )
                                )
                            if index == len(signal_list) - 1:
                                session.query(MeasurePoint).filter(
                                    MeasurePoint.id == mp["id"]
                                ).update(
                                    {
                                        "id": mp["id"],
                                        "statu": int(diag_res_sum)
                                        if diag_res_sum < 4
                                        else 3,
                                        "md_time": datetime.datetime.now(),
                                        "last_diag_id": signal.id,
                                    }
                                )
                                session.add_all(diag_res_insert_value)
                            session.commit()
                            processed_row += 1
                        except Exception as e:
                            session.rollback()
                            print(e)
    session.close()
    return processed_row


if __name__ == "__main__":
    expert_system_diagnosis()
