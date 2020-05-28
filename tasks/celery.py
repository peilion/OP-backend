from __future__ import absolute_import, unicode_literals

import asyncio
import json
import os

import numpy as np
import random
from celery import Celery
from databases import Database
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base

from db.conn_engine import meta_engine, META_URL
from db.db_config import session_make
from db_model import MeasurePoint, VibFeature, VibData, PumpUnit, AssetHI
from services.signal.vibration.vibration_class import VibrationSignal
from services.MSET.core import Temp_MemMat, mset_estimate, threshold_caculate, calculate_similarity
from crud.base import query2sql
from tasks.test import expert_system_diagnosis

Base = declarative_base()

app = Celery(
    "tasks",
    broker=os.getenv("RABBITMQ_URL"),
    # broker='pyamqp://guest@localhost//',
    # backend='redis://@localhost'
)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=10, timezone="Asia/Shanghai", worker_max_tasks_per_child=100
)

app.conf.beat_schedule = {
    "cal-vib-feature-in-60-seconds-task": {
        "task": "tasks.celery.cal_vib_feature",
        "schedule": 60.0,
    }
}


@app.task(ignore_result=True)
def cal_vib_feature():
    detected_rows = 0
    processed_rows = 0
    session = session_make(engine=meta_engine)
    mps = (
        session.query(MeasurePoint.station_id, MeasurePoint.inner_station_id, MeasurePoint)
            .filter(MeasurePoint.type == 0)
            .all()
    )
    session.close()

    for mp in mps:  # Each measure points
        engine = meta_engine
        s = text(
            "SELECT d.id,d.time as time, d.ima as vib "
            "from vib_data_{0}_{1} as d "
            "LEFT JOIN vib_feature_{0}_{1} as f on d.id = f.data_id "
            "where f.data_id is null "
            "limit 10;".format(mp.station_id, mp.inner_station_id)
        )
        conn = engine.connect()
        result = conn.execute(s)
        data = result.fetchall()
        result.close()
        conn.close()

        # memory_mat = np.load(mp.model_name)
        # feature_matrix_max = memory_mat[-2, :]
        # feature_matrix_min = memory_mat[-1, :]
        # memory_mat = memory_mat[:-2, :]
        # temp_memory_mat = Temp_MemMat(memory_mat)

        detected_rows += len(data)

        if len(data) > 0:

            feature = VibFeature.model(station_id=mp.station_id, inner_id=mp.inner_station_id)
            # important! do not comment next line
            data_model = VibData.model(station_id=mp.station_id, inner_id=mp.inner_station_id)

            to_save = []
            for row in data:  # each row
                signal = np.fromstring(row.vib, dtype=np.float32)
                signal = VibrationSignal(data=signal, fs=10000)
                feature_row = np.array(
                    [signal.rms_fea, signal.max_fea, signal.pp_fea, np.mean(signal.data), signal.var_fea,
                     signal.kurtosis])
                # feature_matrix = (feature_row - feature_matrix_min) / (feature_matrix_max - feature_matrix_min)
                # feature_matrix = np.expand_dims(feature_matrix, axis=0)
                # Kest = mset_estimate(memorymat=memory_mat, Kobs=feature_matrix,
                #                      Temp=temp_memory_mat)
                # sim = calculate_similarity(feature_matrix, Kest)
                # thres, warning_index = threshold_caculate(sim)
                #
                # Kest = Kest * (feature_matrix_max - feature_matrix_min) + feature_matrix_min

                to_save.append(
                    feature(
                        rms=feature_row[0],
                        max=feature_row[1],
                        p2p=feature_row[2],
                        avg=feature_row[3],
                        var=feature_row[4],
                        kurtosis=feature_row[5],
                        # est_rms=Kest[0, 0],
                        # est_max=Kest[0, 1],
                        # est_p2p=Kest[0, 2],
                        # est_avg=Kest[0, 3],
                        # est_var=Kest[0, 4],
                        # est_kurtosis=Kest[0, 5],
                        # similarity=sim[0, 0],
                        # threshold=thres[0, 0],
                        data_id=row.id,
                        time=row.time,
                    )
                )
            session = session_make(engine=engine)
            try:
                session.add_all(to_save)
                session.commit()
                session.close()
                processed_rows += len(to_save)
            except Exception as e:
                session.rollback()
                print(e)

    print('Detected Rows: {0}, Processed Rows: {1}'.format(detected_rows, processed_rows))


async def mset_evaluate(cycle_number):
    estimate_count = 0

    db = Database(META_URL)
    await db.connect()
    session = session_make(engine=None)
    pumps = await db.fetch_all(
        query2sql(
            session.query(PumpUnit.asset_id, PumpUnit.mset_model_path).filter(PumpUnit.mset_model_path != None)
        ))

    for pump in pumps:

        asset_hi_model = AssetHI.model(point_id=pump['asset_id'])

        mps = await db.fetch_all(query2sql(
            session.query(MeasurePoint.name, MeasurePoint.station_id, MeasurePoint.inner_station_id).
                filter(MeasurePoint.asset_id == pump['asset_id'], MeasurePoint.type == 0).
                order_by(MeasurePoint.inner_station_id)
        ))
        if len(mps) > 0:
            base_data_query = ("SELECT d.id as id, d.time as time, d.rms as rms "
                               "from vib_data_{0}_{1} as d "
                               "LEFT JOIN asset_hi_{2} as h on d.id = h.data_id "
                               "where h.data_id is null "
                               "limit {3};".format(mps[0]['station_id'], mps[0]['inner_station_id'], pump['asset_id'],
                                                   cycle_number))
            base_data_list = await db.fetch_all(base_data_query)
            if base_data_list == 3:
                feature_matrix = []
                for base_data in base_data_list:
                    feature_row = [base_data['rms']]
                    for mp in mps[1:]:
                        query = "select rms from vib_data_{0}_{1} order by abs(datediff(time,'{2}')) limit 1".format(
                            mp['station_id'], mp['inner_station_id'], base_data['time'])
                        res = await db.fetch_all(query)
                        feature_row.append(res[0]['rms'])
                    feature_matrix.append(feature_row)
                feature_matrix = np.array(feature_matrix)

                memory_mat = np.load(pump['mset_model_path'])
                feature_matrix_max = memory_mat[-2, :]
                feature_matrix_min = memory_mat[-1, :]
                memory_mat = memory_mat[:-2, :]
                temp_memory_mat = Temp_MemMat(memory_mat)

                feature_matrix = (feature_matrix - feature_matrix_min) / (feature_matrix_max - feature_matrix_min)
                Kest = mset_estimate(memorymat=memory_mat, Kobs=feature_matrix,
                                     Temp=temp_memory_mat)

                sim = calculate_similarity(feature_matrix, Kest)
                thres, warning_index = threshold_caculate(sim)
                Kest = Kest * (feature_matrix_max - feature_matrix_min) + feature_matrix_min

                to_save = []

                for i in range(len(base_data_list)):
                    to_save.append(
                        asset_hi_model(
                            health_indicator=80 + random.random() * 10,
                            similarity=sim[i][0],
                            threshold=thres[i][0],
                            time=base_data_list[i]['time'],
                            data_id=base_data_list[i]['id'],
                            est=json.dumps({'label': [mp['name'] for mp in mps],
                                            'raw': feature_matrix[i].tolist(),
                                            'est': Kest[i].tolist()})
                        ))
                session = session_make(engine=meta_engine)
                try:
                    session.add_all(to_save)
                    session.commit()
                    session.close()
                    estimate_count += len(to_save)
                except Exception as e:
                    session.rollback()
                    print(e)
    await db.disconnect()

    return estimate_count


@app.task(ignore_result=True)
def make_estimate():
    estimate_count = asyncio.run(mset_evaluate(3))
    print('{0} estimate finished.'.format(estimate_count))


if __name__=='__main__':
    x = asyncio.run(expert_system_diagnosis())
