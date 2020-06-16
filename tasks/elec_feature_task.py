from __future__ import absolute_import, unicode_literals

from typing import List

import numpy as np
from db.conn_engine import meta_engine
from db.db_config import session_make
from db_model import MeasurePoint, ElecFeature, ElecData
from utils.elec_feature_tool import feature_calculator


def fetch_mps(session):
    mps = (
        session.query(MeasurePoint.station_id, MeasurePoint.inner_station_id)
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
    ) = feature_calculator(u, v, w)

    return feature_model(
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
        session.close()
    except Exception as e:
        session.rollback()
        print(e)
    return len(to_save)


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
            for row in data:  # each row
                feature_insert_value.append(
                    calculate_feature_row(
                        row=row,
                        station_id=mp.station_id,
                        inner_station_id=mp.inner_station_id,
                    )
                )
            processed_rows += insert_feature(
                session=session, to_save=feature_insert_value
            )
    session.close()
    return processed_rows
