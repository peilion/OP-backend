from __future__ import absolute_import, unicode_literals

from typing import List

import numpy as np
from db.conn_engine import meta_engine
from db.db_config import session_make
from db_model import MeasurePoint, ElecFeature, ElecData, Motor
from utils.elec_feature_tool import feature_calculator


def fetch_mps(session):
    mps = (
        session.query(MeasurePoint.station_id, MeasurePoint.inner_station_id, MeasurePoint.asset_id)
            .filter(MeasurePoint.type == 1)
            .all()
    )
    return mps


def fetch_data(session, station_id, inner_station_id):
    data_model = ElecData.model(station_id=station_id, inner_id=inner_station_id)
    feature_model = ElecFeature.model(station_id=station_id, inner_id=inner_station_id)
    data = (
        session.query(data_model.id, data_model.ucur, data_model.vcur, data_model.wcur, data_model.time)
            .join(feature_model, feature_model.data_id == data_model.id, isouter=True)
            .filter(feature_model.data_id == None)
            .limit(10)
            .all()
    )
    # ("SELECT d.id,d.time as time, d.ima as vib "
    #  "from vib_data_{0}_{1} as d "
    #  "LEFT JOIN vib_feature_{0}_{1} as f on d.id = f.data_id "
    #  "where f.data_id is null "
    #  "limit 10;".format(station_id, inner_station_id))
    return data


def calculate_feature_row(row, station_id, inner_station_id):
    feature_model = ElecFeature.model(station_id=station_id, inner_id=inner_station_id)
    u = np.fromstring(row.ucur, dtype=np.float32)
    v = np.fromstring(row.vcur, dtype=np.float32)
    w = np.fromstring(row.wcur, dtype=np.float32)
    (
        rms_list,
        THD_list,
        harmonics_list,
        max_list,
        min_list,
        brb_list,
        params,
        n_rms,
        p_rms,
        z_rms,
        fundamental
    ) = feature_calculator(u, v, w)

    return fundamental, feature_model(
        data_id=row.id,
        time=row.time,
        urms=rms_list[0],
        uthd=THD_list[0],
        uharmonics=harmonics_list[0].astype(np.float32).tostring(),
        umax_current=max_list[0],
        umin_current=min_list[0],
        ufbrb=brb_list[0].astype(np.float32).tostring(),
        vrms=rms_list[1],
        vthd=THD_list[1],
        vharmonics=harmonics_list[1].astype(np.float32).tostring(),
        vmax_current=max_list[1],
        vmin_current=min_list[1],
        vfbrb=brb_list[1].astype(np.float32).tostring(),
        wrms=rms_list[2],
        wthd=THD_list[2],
        wharmonics=harmonics_list[2].astype(np.float32).tostring(),
        wmax_current=max_list[2],
        wmin_current=min_list[2],
        wfbrb=brb_list[2].astype(np.float32).tostring(),
        n_rms=n_rms,
        p_rms=p_rms,
        z_rms=z_rms,
        imbalance=(n_rms / p_rms * 100) if p_rms > 0.1 else 0,
        uamplitude=params[0][0],
        ufrequency=params[0][1],
        uinitial_phase=params[0][2],
        vamplitude=params[1][0],
        vfrequency=params[1][1],
        vinitial_phase=params[1][2],
        wamplitude=params[2][0],
        wfrequency=params[2][1],
        winitial_phase=params[2][2],
    )


def insert_feature(session, to_save):
    try:
        session.add_all(to_save)
        session.commit()
        # session.close()
    except Exception as e:
        session.rollback()
        print(e)
    return len(to_save)


def hi_convert(feature, levels):
    statu = np.searchsorted(levels, feature)
    if statu == 0:
        return 100 - 10 * (feature - 0) / levels[0]
    elif statu == 1:
        return 90 - 10 * (feature - levels[0]) / (levels[1] - levels[0])
    elif statu == 2:
        return 80 - 20 * (feature - levels[1]) / (levels[2] - levels[1])
    elif statu == 3:
        return 60 - 60 * (feature - levels[2]) / (levels[2])


def health_evaluate(feature, fundamental):
    if feature.urms < 0.1:
        return 4, 0
    else:
        har = np.fromstring(feature.uharmonics, dtype=np.float32)
        hi_stator = 0.8 * hi_convert(feature.imbalance, [2, 4, 10]) + \
                    0.2 * hi_convert(har[1], [0.001, 0.0126, 0.0468])
        brb = np.sum(np.fromstring(feature.uharmonics, dtype=np.float32))
        hi_rotor = hi_convert(brb / fundamental, [0.002, 0.0079, 0.0158])

        hi_power = hi_convert(feature.uthd, [0.05, 0.10, 0.15])

        hi = max(0, 0.5 * hi_stator + 0.25 * hi_rotor + 0.25 * hi_power)
        statu = 3 - np.searchsorted([90, 80, 60], hi)
        return statu, hi


def cal_elec_feature():
    processed_rows = 0
    session = session_make(engine=meta_engine)
    mps: List[MeasurePoint] = fetch_mps(session=session)
    for mp in mps:  # Each measure points
        data = fetch_data(
            session=session,
            station_id=mp.station_id,
            inner_station_id=mp.inner_station_id,
        )
        if len(data) > 0:
            feature_insert_value = []
            for index, row in enumerate(data):  # each row
                fundamental, feature = calculate_feature_row(
                    row=row,
                    station_id=mp.station_id,
                    inner_station_id=mp.inner_station_id,
                )
                feature_insert_value.append(feature)
                if index == len(data) - 1:
                    statu, hi = health_evaluate(feature, fundamental)
                    session.query(Motor).filter(Motor.asset_id == mp.asset_id).update(
                        {
                            "statu": statu,
                            "health_indicator": hi,
                        }
                    )
                    session.commit()

            processed_rows += insert_feature(
                session=session, to_save=feature_insert_value
            )
    session.close()
    return processed_rows
