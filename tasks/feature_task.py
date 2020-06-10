from __future__ import absolute_import, unicode_literals

from typing import List

import numpy as np
from sqlalchemy import text
from databases import Database

from crud.base import query2sql
from db.conn_engine import META_URL, meta_engine
from db.db_config import session_make
from db_model import MeasurePoint, VibFeature, VibData
from services.signal.vibration.vibration_class import VibrationSignal


def fetch_mps(session):
    mps = (
        session.query(MeasurePoint.station_id, MeasurePoint.inner_station_id)
        .filter(MeasurePoint.type == 0)
        .all()
    )
    return mps


def fetch_data(session, station_id, inner_station_id):
    data_model = VibData.model(station_id=station_id, inner_id=inner_station_id)
    feature_model = VibFeature.model(station_id=station_id, inner_id=inner_station_id)
    data = (
        session.query(data_model.id, data_model.time, data_model.ima)
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
    feature_model = VibFeature.model(station_id=station_id, inner_id=inner_station_id)
    signal = np.fromstring(row.ima, dtype=np.float32)
    signal = VibrationSignal(data=signal, fs=10000)
    return feature_model(
        rms=float(signal.rms_fea),
        max=float(signal.max_fea),
        p2p=float(signal.pp_fea),
        avg=float(np.mean(signal.data)),
        var=float(signal.var_fea),
        kurtosis=float(signal.kurtosis),
        data_id=row.id,
        time=row.time,
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


def cal_vib_feature():
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
