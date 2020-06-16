import datetime
import random

import MySQLdb
import numpy as np
from sqlalchemy.ext.declarative import declarative_base
from db.conn_engine import META_URL
from db import session_make, meta_engine
from db_model import VibData, VibFeature, MeasurePoint, ElecFeature, ElecData
from utils.elec_feature_tool import feature_calculator
from utils.simulators import unbalance, misalignment, a_loose, b_loose, rubbing
from sqlalchemy import create_engine

session = session_make(meta_engine)

base = declarative_base()
engine = create_engine(META_URL, encoding="utf-8", pool_pre_ping=True)
x = session.query(MeasurePoint).filter(
    MeasurePoint.station_id == 7, MeasurePoint.type == 0
)

for row in x:
    model = VibData.model(
        station_id=row.station_id, inner_id=row.inner_station_id, base=base
    )  # registe to metadata for all pump_unit
    fea_model = VibFeature.model(
        station_id=row.station_id, inner_id=row.inner_station_id, base=base
    )

base.metadata.create_all(engine)

x = session.query(MeasurePoint).filter(
    MeasurePoint.station_id == 7, MeasurePoint.type == 1
)
base = declarative_base()
for row in x:
    model = ElecData.model(
        station_id=row.station_id, inner_id=row.inner_station_id, base=base
    )  # registe to metadata for all pump_unit
    fea_model = ElecFeature.model(
        station_id=row.station_id, inner_id=row.inner_station_id, base=base
    )
base.metadata.create_all(engine)

x = (
    session.query(MeasurePoint)
        .filter(MeasurePoint.station_id != 7, MeasurePoint.type == 1)
        .all()
)
model = VibData.model(
    station_id=7, inner_id=0, base=base
)  # registe to metadata for all pump_unit
data = session.query(model).all()
for row in x:
    model = ElecData.model(
        station_id=row.station_id, inner_id=row.inner_station_id, base=base
    )  # registe to metadata for all pump_unit
    tmp = []
    for item in data:
        r = model(
            time=item.time,
            ucur=item.ucur,
            vcur=item.vcur,
            wcur=item.wcur,
            uvolt=item.uvolt,
            vvolt=item.vvolt,
            wvolt=item.wvolt,
        )
        tmp.append(r)
    session.add_all(tmp)
    session.commit()

x = session.query(MeasurePoint).filter(MeasurePoint.type == 1).all()
for mp in x:
    fea_model = ElecFeature.model(
        station_id=mp.station_id, inner_id=mp.inner_station_id
    )  # registe to metadata for all pump_unit
    data_model = ElecData.model(
        station_id=mp.station_id, inner_id=mp.inner_station_id
    )
    data = (
        session.query(data_model.id, data_model.ucur, data_model.vcur, data_model.wcur, data_model.time)
            .join(fea_model, fea_model.data_id == data_model.id, isouter=True)
            .filter(fea_model.data_id == None)
            .limit(10)
            .all()
    )
    tmp = []
    for item in data:
        u = np.fromstring(item.ucur, dtype=np.float32)
        v = np.fromstring(item.vcur, dtype=np.float32)
        w = np.fromstring(item.wcur, dtype=np.float32)
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
        r = fea_model(
            data_id=item.id,
            time=item.time,
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
        tmp.append(r)
    session.add_all(tmp)
    session.commit()
