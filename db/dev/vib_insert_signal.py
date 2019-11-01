import datetime

import MySQLdb
from sqlalchemy.sql import text

from db import station_engines
from utils.simulators import *


def insert_vib_2_one_table(simu_meth, table_id, station_id):
    engine = station_engines[station_id - 1]
    initial_datetime = datetime.datetime(2016, 1, 1, 0, 0, 0, 0)

    for i in range(900):
        with engine.begin() as connection:
            s = text(
                "INSERT INTO vib_data_{0} (time,vib) "
                "values ({1},:data);".format(table_id, str(initial_datetime))
            )
            data, _ = simu_meth(3, 50, FS=10000, T=1)
            result = connection.execute(s, data=MySQLdb.Binary(data.astype(np.float32)))
        print(str(i) + " processed!")
        initial_datetime += datetime.timedelta(days=1)
