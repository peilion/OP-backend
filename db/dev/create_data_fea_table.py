import datetime
import random

import MySQLdb
import numpy as np
from sqlalchemy.ext.declarative import declarative_base

from db import session_make, meta_engine
from db_model import VibData, VibFeature, MeasurePoint
from utils.simulators import unbalance, misalignment, a_loose, b_loose, rubbing

session = session_make(meta_engine)
x = session.query(MeasurePoint).all()

base = declarative_base()
for row in x:
    model = VibData.model(
        point_id=row.id, base=base
    )  # registe to metadata for all pump_unit
    fea_model = VibFeature.model(point_id=row.id, base=base)

from sqlalchemy import create_engine

META_URL = "mysql://root:8315814@127.0.0.1/op_meta?charset=utf8"
engine = create_engine(META_URL, encoding="utf-8", pool_pre_ping=True)
base.metadata.create_all(engine)

for row in x:
    initial_datetime = datetime.datetime(2016, 1, 1, 0, 0, 0, 0)
    tmp = []
    model = VibData.model(point_id=row.id)  # registe to metadata for all pump_unit
    for i in range(1, 10):
        simu_meth = random.choice([unbalance, misalignment, a_loose, b_loose, rubbing])
        data, _ = simu_meth(3, 50, FS=10000, T=0.5)
        r = model(
            id=i,
            time=str(initial_datetime),
            rms=np.sqrt(np.mean(np.square(data))),
            ima=MySQLdb.Binary(data.astype(np.float32)),
        )
        initial_datetime += datetime.timedelta(days=1)
        tmp.append(r)
    session.add_all(tmp)
    session.commit()
