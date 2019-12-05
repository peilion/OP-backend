import datetime

import MySQLdb
from sqlalchemy.sql import text

from db import meta_engine
from utils.simulators import *


def insert_vib_2_one_table(simu_meth, table_id, station_id):
    engine = meta_engine
    initial_datetime = datetime.datetime(2016, 1, 1, 0, 0, 0, 0)

    for i in range(11):
        with engine.begin() as connection:
            s = text(
                "INSERT INTO b_vib_{0} (time,ima) "
                "values ('{1}',:data);".format(table_id, str(initial_datetime))
            )
            data, _ = simu_meth(3, 50, FS=10000, T=0.5)
            result = connection.execute(s, data=MySQLdb.Binary(data.astype(np.float32)))
        print(str(i) + " processed!")
        initial_datetime += datetime.timedelta(days=1)


insert_vib_2_one_table(unbalance, table_id=0, station_id=1)
insert_vib_2_one_table(a_loose, table_id=1, station_id=1)
insert_vib_2_one_table(rubbing, table_id=2, station_id=1)
insert_vib_2_one_table(misalignment, table_id=3, station_id=1)
