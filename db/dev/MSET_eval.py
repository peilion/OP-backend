import numpy as np
from databases import Database
from crud.base import query2sql
from db.conn_engine import META_URL
from db_model import VibFeature, MeasurePoint
from db.db_config import session_make
from sqlalchemy.orm import load_only
import asyncio
from services.MSET.Model import (
    pic_vars,
    Temp_MemMat,
    MSET,
    Cal_sim,
    Cal_thres,
    error_contribution,
    Accumu_errorContirbution,
)
import matplotlib.pyplot as plt

station_id = 1
inner_id = 1
model = VibFeature.model(station_id, inner_id)
session = session_make(None)
query = session.query(model)
model_name_query = (
    session.query(MeasurePoint.model_name)
    .filter(
        MeasurePoint.station_id == station_id, MeasurePoint.inner_station_id == inner_id
    )
    .limit(1)
)

fileds = ["rms", "max", "p2p", "avg", "var", "kurtosis"]
for filed in fileds + ["id", "time", "data_id"]:
    query = query.options(load_only(filed))

query = query.order_by(model.time).offset(5).limit(4)


async def get_data():
    db = Database(META_URL)
    await db.connect()
    res = await db.fetch_all(query2sql(query))
    modelName = await db.fetch_one(query2sql(model_name_query))
    await db.disconnect()
    return res, modelName


res, modelName = asyncio.run(get_data())
dic = {}
keys = res[0].keys()
for row in res:
    for key in keys:
        if key == "time":
            dic.setdefault(key, []).append(str(row[key]))
        else:
            dic.setdefault(key, []).append(row[key])

feature_matrix = np.array(
    [dic["rms"], dic["max"], dic["p2p"], dic["avg"], dic["var"], dic["kurtosis"]]
).T

memory_mat = np.load(modelName["model_name"])
feature_matrix_max = memory_mat[-2, :]
feature_matrix_min = memory_mat[-1, :]
feature_matrix = (feature_matrix - feature_matrix_min) / (
    feature_matrix_max - feature_matrix_min
)
memory_mat = memory_mat[:-2, :]
temp_memory_mat = Temp_MemMat(memory_mat)

sim = np.zeros((feature_matrix.shape[0], 1))
thres = np.zeros((feature_matrix.shape[0], 1))
Kest = np.zeros((feature_matrix.shape[0], feature_matrix.shape[1]))

N = 2  # cycle number

for i in range(int(feature_matrix.shape[0] / N)):
    Kest[i * N : (i + 1) * N] = MSET(
        memorymat=memory_mat,
        Kobs=feature_matrix[i * N : (i + 1) * N],
        Temp=temp_memory_mat,
    )
    sim[i * N : (i + 1) * N] = Cal_sim(
        feature_matrix[i * N : (i + 1) * N], Kest[i * N : (i + 1) * N]
    )
    thres[i * N : (i + 1) * N], warning_index = Cal_thres(sim[i * N : (i + 1) * N])
    if any(warning_index):
        # 如果故障索引存在值，打印该点编号并显示误差贡献率
        print("第%d次循环中的故障点：" % (i + 1), warning_index)
        error_contribution(
            feature_matrix[i * N : (i + 1) * N],
            Kest[i * N : (i + 1) * N],
            warning_index[0],
            fileds,
        )
        Accumu_errorContirbution(
            feature_matrix[i * N : (i + 1) * N],
            Kest[i * N : (i + 1) * N],
            warning_index[0],
            N - warning_index[0],
            fileds,
        )

pic_vars(
    fileds, feature_matrix, Kest, feature_matrix_max, feature_matrix_min
)  # 各变量的估计结果及误差
plt.ion()
plt.plot(sim, label="相似度曲线")
plt.plot(thres, label="动态阈值")
plt.ylim((0, 1))
plt.legend()
plt.show()
