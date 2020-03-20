import numpy as np
from databases import Database
from crud.base import query2sql
from db.conn_engine import META_URL
from db_model import VibFeature
from db.db_config import session_make
from sqlalchemy.orm import load_only
import asyncio
import time
from services.MSET.core import memory_mat_train, Temp_MemMat

station_id = 1
inner_id = 1
model = VibFeature.model(station_id, inner_id)
session = session_make(None)
query = session.query(model)
fileds = ["rms", "max", "p2p", "avg", "var", "kurtosis"]
for filed in fileds + ["id", "time", "data_id"]:
    query = query.options(load_only(filed))

query = query.order_by(model.time).limit(5)


async def get_data():
    db = Database(META_URL)
    await db.connect()
    res = await db.fetch_all(query2sql(query))
    await db.disconnect()
    return res


res = asyncio.run(get_data())
dic = {}
keys = res[0].keys()
for row in res:
    for key in keys:
        if key == "time":
            dic.setdefault(key, []).append(str(row[key]))
        else:
            dic.setdefault(key, []).append(row[key])

feature_matrix = np.array([dic['rms'], dic['max'], dic['p2p'], dic['avg'], dic['var'], dic['kurtosis']]).T

feature_matrix_max = np.max(feature_matrix, axis=0)
feature_matrix_min = np.min(feature_matrix, axis=0)

feature_matrix = (feature_matrix - feature_matrix_min) / (feature_matrix_max - feature_matrix_min)

memory_mat = memory_mat_train(feature_matrix)  # 训练得到记忆矩阵
np.save('./services/MSET/models/{0}_station{1}_mp{2}.npy'.format(time.strftime("%Y%m%d%H%M%S", time.localtime()),
                                                                 station_id, inner_id),
        np.vstack((memory_mat, feature_matrix_max, feature_matrix_min)))
# 倒数第二行为最大值行，最后一行为最小值行
