from __future__ import absolute_import, unicode_literals
from celery import Celery
from sqlalchemy import text
from db.db_config import session_make
from db.conn_engine import meta_engine, station_engines
import numpy as np
from db_model.meta_models import MeasurePoint
from db_model.sharding_models import ElecFeature, ElecData, VibFeature, VibData
from utils.elec_feature_tools import threephase_deserialize, feature_calculator
from sqlalchemy.ext.declarative import declarative_base
from utils import vib_feature_tools

Base = declarative_base()

app = Celery('tasks',
             broker='pyamqp://guest@localhost//',
             # backend='redis://@localhost'
             )

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=10,
    timezone='Asia/Shanghai',
    worker_max_tasks_per_child=100
)

app.conf.beat_schedule = {
    "cal-elec-feature-in-60-seconds-task": {
        "task": "core.celery.cal_elec_feature",
        "schedule": 60.0,
    },
    "cal-vib-feature-in-60-seconds-task": {
        "task": "core.celery.cal_vib_feature",
        "schedule": 60.0,
    },
}


@app.task(ignore_result=True)
def cal_elec_feature():
    session = session_make(engine=meta_engine)
    mps = session \
        .query(MeasurePoint.station_id, MeasurePoint.id_inner_station) \
        .filter(MeasurePoint.type == 1) \
        .all()
    session.close()

    group_dict = {}
    for mp in mps:
        if mp.station_id not in group_dict.keys():
            group_dict[mp.station_id] = []
        group_dict[mp.station_id].append(mp.id_inner_station)

    for station_id in group_dict.keys():
        mp_ids = group_dict[station_id]
        for mp_id in mp_ids:
            engine = station_engines[station_id - 1]
            s = text(
                'SELECT d.id,d.time as time, d.ucur as u , d.vcur as v,d.wcur as w from elec_data_{} as d LEFT JOIN elec_feature_{} as f on d.id = f.data_id where f.data_id is null limit 10;'.format(
                    mp_id, mp_id))
            conn = engine.connect()
            result = conn.execute(s)
            data = result.fetchall()
            result.close()

            data_model = ElecData.model(point_id=mp_id, base=Base)
            feature = ElecFeature.model(point_id=mp_id, base=Base)

            to_save = []
            for row in data:
                u, v, w = threephase_deserialize(row.u, row.v, row.w)
                rms_list, THD_list, harmonics_list, max_list, min_list, brb_list, params, n_rms, p_rms, z_rms = feature_calculator(
                    u,
                    v,
                    w)
                to_save.append(feature(data_id=row.id, time=row.time,
                                       urms=rms_list[0], uthd=THD_list[0],
                                       uharmonics=harmonics_list[0].astype(np.float32).tostring(),
                                       umax_current=max_list[0], umin_current=min_list[0],
                                       ufbrb=brb_list[0].astype(np.float32).tostring(),
                                       vrms=rms_list[1], vthd=THD_list[1],
                                       vharmonics=harmonics_list[1].astype(np.float32).tostring(),
                                       vmax_current=max_list[1], vmin_current=min_list[1],
                                       vfbrb=brb_list[1].astype(np.float32).tostring(),
                                       wrms=rms_list[2], wthd=THD_list[2],
                                       wharmonics=harmonics_list[2].astype(np.float32).tostring(),
                                       wmax_current=max_list[2], wmin_current=min_list[2],
                                       wfbrb=brb_list[2].astype(np.float32).tostring(),
                                       n_rms=n_rms, p_rms=p_rms, z_rms=z_rms, imbalance=n_rms / p_rms,
                                       health_indicator=85,
                                       uamplitude=params[0][0], ufrequency=params[0][1], uinitial_phase=params[0][2],
                                       vamplitude=params[1][0], vfrequency=params[1][1], vinitial_phase=params[1][2],
                                       wamplitude=params[2][0], wfrequency=params[2][1], winitial_phase=params[2][2], ))
            session = session_make(engine=engine)
            try:
                session.add_all(to_save)
                session.commit()
                session.close()
                print('inserted rows/uncalculated rows: {}/{}'.format(len(to_save), len(data)))
            except Exception as e:
                session.rollback()
                print(e)


@app.task(ignore_result=True)
def cal_vib_feature():
    session = session_make(engine=meta_engine)
    mps = session \
        .query(MeasurePoint.station_id, MeasurePoint.id_inner_station) \
        .filter(MeasurePoint.type == 0) \
        .all()
    session.close()

    group_dict = {}
    for mp in mps:
        if mp.station_id not in group_dict.keys():
            group_dict[mp.station_id] = []
        group_dict[mp.station_id].append(mp.id_inner_station)

    for station_id in group_dict.keys():
        mp_ids = group_dict[station_id]
        for mp_id in mp_ids:
            engine = station_engines[station_id - 1]
            s = text(
                'SELECT d.id,d.time as time, d.vib as vib from vib_data_{} as d LEFT JOIN vib_feature_{} as f on d.id = f.data_id where f.data_id is null limit 10;'.format(
                    mp_id, mp_id))
            conn = engine.connect()
            result = conn.execute(s)
            data = result.fetchall()
            result.close()

            if len(data) > 0 :

                data_model = VibData.model(point_id=mp_id, base=Base)
                feature = VibFeature.model(point_id=mp_id, base=Base)

                to_save = []
                for row in data:
                    signal = np.fromstring(row.vib, dtype=np.float32)
                    to_save.append(feature(rms=vib_feature_tools.rms_fea(signal),
                                           max=vib_feature_tools.max_fea(signal),
                                           p2p=vib_feature_tools.pp_fea(signal),
                                           avg=np.mean(signal),
                                           var=vib_feature_tools.var_fea(signal),
                                           kurtosis=vib_feature_tools.kurt_fea(signal),
                                           data_id=row.id, time=row.time))
                session = session_make(engine=engine)
                try:
                    session.add_all(to_save)
                    session.commit()
                    session.close()
                    print('inserted rows: {}'.format(len(to_save)))
                except Exception as e:
                    session.rollback()
                    print(e)

            else:
                print('No new row detected')