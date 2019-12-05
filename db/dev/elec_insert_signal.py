import datetime
import os

import MySQLdb
import numpy as np
import scipy.io as sio
from numpy import ndarray
from services.signal.electric.elec_feature_tools import feature_calculator
from sqlalchemy.sql import text

from db import station_engines

SAMPLING_RATE = 20480
# ROOT_PATHS = [r"G:\Researchs\Motor fusion\30HzData", r"G:\Researchs\Motor fusion\40HzData", r"G:\Researchs\Motor fusion\50HzData"]
ROOT_PATHS = [
    r"G:\Researchs\Motor fusion\nEW\40HzData",
    r"G:\Researchs\Motor fusion\nEW\50HzData",
]
PHASE_SHIFT = [171, 137]
SUFFIX = [9, 18]
j = 1
motor_id = 1

engine = station_engines[0]
# INSERT signal

for root_path, shift, suffix in zip(ROOT_PATHS, PHASE_SHIFT, SUFFIX):
    files = os.listdir(root_path)

    for file in files:

        loadtext = root_path + "/" + file
        data = sio.loadmat(loadtext)
        for key in data.keys():
            if isinstance(data[key], ndarray):
                data = data[key][500000:1000000, 0]
        for i in range(10):
            # Starting a transaction.
            with engine.begin() as connection:
                s = text(
                    "INSERT INTO elec_data_{0} (time,motor_id,rpm,ucur,vcur,wcur) "
                    "values (NOW(),:motor_id,3000,:u,:v,:w);".format(suffix)
                )

                result = connection.execute(
                    s,
                    motor_id=motor_id,
                    u=MySQLdb.Binary(
                        data[
                            1000 + i * 10000 - shift : 1000 + i * 10000 + 8192 - shift
                        ].astype(np.float32)
                    ),
                    v=MySQLdb.Binary(
                        data[1000 + i * 10000 : 1000 + i * 10000 + 8192].astype(
                            np.float32
                        )
                    ),
                    w=MySQLdb.Binary(
                        data[
                            1000 + i * 10000 + shift : 1000 + i * 10000 + 8192 + shift
                        ].astype(np.float32)
                    ),
                )
        print(file + " processed!")
    motor_id = motor_id + 1

# UPDATE datetime field
for item in [0, 1, 2]:
    s = text("SELECT id FROM elecdata_%s order by id" % item)
    conn = engine.connect()
    id = conn.execute(s).fetchall()

    initial_datetime = datetime.datetime(2016, 1, 1, 0, 0, 0, 0)
    for i in id:
        s = text(
            "UPDATE elecdata_%s SET time = '%s'  WHERE id =%s"
            % (item, str(initial_datetime), i[0])
        )
        conn = engine.connect()
        conn.execute(s)
        initial_datetime += datetime.timedelta(days=1)

# Calculate Features
for item in [0, 1, 2]:
    s = text("SELECT id FROM elecdata_%s order by id" % item)
    conn = engine.connect()
    id = conn.execute(s).fetchall()

    for i in id:
        s = text(
            "select ucur,vcur,wcur " "from elecdata_%s " "where (id = :id)" % (item)
        )

        conn = engine.connect()
        result = conn.execute(s, id=i[0]).fetchone()
        u = np.fromstring(result[0], dtype=np.float32)
        v = np.fromstring(result[1], dtype=np.float32)
        w = np.fromstring(result[2], dtype=np.float32)

        rms_list, THD_list, harmonics_list, max_list, min_list, brb_list, params, n_rms, p_rms, z_rms = feature_calculator(
            u, v, w
        )

        s = text(
            "INSERT INTO feature_{} ("
            "urms,uthd,uharmonics,umax_current,umin_current,ufbrb,uamplitude,ufrequency,uinitial_phase,"
            "vrms,vthd,vharmonics,vmax_current,vmin_current,vfbrb,vamplitude,vfrequency,vinitial_phase,"
            "wrms,wthd,wharmonics,wmax_current,wmin_current,wfbrb,wamplitude,wfrequency,winitial_phase,"
            "n_rms,p_rms,z_rms,imbalance,data_id) "
            "values ("
            ":urms,:uthd,:uharmonics,:umax_current,:umin_current,:ufbrb,:uamp,:ufreq,:uip,"
            ":vrms,:vthd,:vharmonics,:vmax_current,:vmin_current,:vfbrb,:vamp,:vfreq,:vip,"
            ":wrms,:wthd,:wharmonics,:wmax_current,:wmin_current,:wfbrb,:wamp,:wfreq,:wip,"
            ":nrms,:prms,:zrms,:imbalance,:data_id)".format(item)
        )

        conn.execute(
            s,
            data_id=i[0],
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
            nrms=n_rms,
            prms=p_rms,
            zrms=z_rms,
            imbalance=n_rms / p_rms,
            uamp=params[0][0],
            ufreq=params[0][1],
            uip=params[0][2],
            vamp=params[1][0],
            vfreq=params[1][1],
            vip=params[1][2],
            wamp=params[2][0],
            wfreq=params[2][1],
            wip=params[2][2],
        )
        print(i + " processed")
