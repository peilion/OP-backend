import random

import numpy as np
from databases import Database
from crud.base import query2sql
from db.conn_engine import META_URL
from db_model import VibFeature, PumpUnit, MeasurePoint, VibData
from db.db_config import session_make
from sqlalchemy.orm import load_only
import asyncio
import time
from services.MSET.core import memory_mat_train, Temp_MemMat

asset_id = 7


async def get_data(query):
    db = Database(META_URL)
    await db.connect()
    res = await db.fetch_all(query2sql(query))
    await db.disconnect()
    return res


async def get_time_relate_data(mps_info, base_data_list):
    db = Database(META_URL)
    feature_matrix = []
    await db.connect()
    for base_data in base_data_list:
        feature_row = [base_data["rms"]]
        for mp in mps_info[1:]:  # 某设备所拥有的测点inner_station_id的排序必须一致
            query = "select rms from vib_data_{0}_{1} order by abs(datediff(time,'{2}')) limit 1".format(
                mp["station_id"], mp["inner_station_id"], str(base_data["time"])
            )
            res = await db.fetch_all(query)
            # feature_row.append(res[0]['rms'])
            feature_row.append(res[0]["rms"] + random.random())

        feature_matrix.append(feature_row)
    await db.disconnect()
    return feature_matrix


session = session_make(None)
query = (
    session.query(MeasurePoint.station_id, MeasurePoint.inner_station_id)
    .filter(MeasurePoint.asset_id == asset_id, MeasurePoint.type == 0)
    .order_by(MeasurePoint.inner_station_id)
)

mps_info = asyncio.run(get_data(query))

base_data_model = VibData.model(
    station_id=mps_info[0]["station_id"], inner_id=mps_info[0]["inner_station_id"]
)
base_data_query = session.query(base_data_model.time, base_data_model.rms).order_by(
    base_data_model.time.desc()
)
base_data_list = asyncio.run(get_data(base_data_query))

feature_matrix = asyncio.run(get_time_relate_data(mps_info, base_data_list))

feature_matrix = np.array(feature_matrix)

feature_matrix_max = np.max(feature_matrix, axis=0)
feature_matrix_min = np.min(feature_matrix, axis=0)

feature_matrix = (feature_matrix - (feature_matrix_min)) / (
    feature_matrix_max - feature_matrix_min
)

memory_mat = memory_mat_train(feature_matrix)  # 训练得到记忆矩阵
np.save(
    "./services/MSET/models/asset{0}_{1}.npy".format(
        asset_id, time.strftime("%Y%m%d%H%M%S", time.localtime()),
    ),
    np.vstack((memory_mat, feature_matrix_max, feature_matrix_min)),
)
# 倒数第二行为最大值行，最后一行为最小值行
