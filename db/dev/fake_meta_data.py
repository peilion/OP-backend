import random

from db import meta_engine
from db.db_config import session_make
from db_model import User, Manufacturer, Station, Asset, MeasurePoint

session = session_make(meta_engine)

admin = User(name="admin")
simens = Manufacturer(name="Simens", telephone="88835569")
hhht = Station(
    name="呼和浩特站", location="内蒙古", sharding_db_id=1, memo="N/A", telephone="89656985"
)
et = Station(
    name="鄂托克旗站", location="内蒙古", sharding_db_id=2, memo="N/A", telephone="89656985"
)
bt = Station(
    name="包头站", location="内蒙古", sharding_db_id=3, memo="N/A", telephone="89656985"
)

session.add_all([admin, simens, hhht, et, bt])
session.commit()

asset_list = []
stations = session.query(Station).all()
admin = session.query(User).one()

for station_id, units in enumerate([[1, 1], [2, 2], [3, 3]]):
    mp_id = 0
    for i in units:
        unit_name = "PumpUnit#" + str(random.randint(100, 999))
        PumpUnit = Asset(
            name=unit_name,
            sn="".join(random.sample("zyxwvutsrqponmlkjihgfedcba", 8)),
            asset_level=0,
            memo="N/A",
            station=stations[station_id],
            admin=admin,
        )

        Rotor = Asset(
            name="Rotor#{0}".format(random.randint(100, 999)),
            sn="".join(random.sample("zyxwvutsrqponmlkjihgfedcba", 8)),
            asset_level=2,
            memo="N/A",
            station=stations[station_id],
            admin=admin,
        )

        Stator = Asset(
            name="Stator#{0}".format(random.randint(100, 999)),
            sn="".join(random.sample("zyxwvutsrqponmlkjihgfedcba", 8)),
            asset_level=2,
            memo="N/A",
            station=stations[station_id],
            admin=admin,
        )

        Bearing1 = Asset(
            name="Bearing#{0}".format(random.randint(100, 999)),
            sn="".join(random.sample("zyxwvutsrqponmlkjihgfedcba", 8)),
            asset_level=2,
            memo="N/A",
            station=stations[station_id],
            admin=admin,
        )

        Bearing2 = Asset(
            name="Bearing#{0}".format(random.randint(100, 999)),
            sn="".join(random.sample("zyxwvutsrqponmlkjihgfedcba", 8)),
            asset_level=2,
            memo="N/A",
            station=stations[station_id],
            admin=admin,
        )

        motor = Asset(
            name="Motor#{0}".format(random.randint(100, 999)),
            sn="".join(random.sample("zyxwvutsrqponmlkjihgfedcba", 8)),
            asset_level=1,
            memo="N/A",
            station=stations[station_id],
            admin=admin,
        )

        pump = Asset(
            name="Pump#{0}".format(random.randint(100, 999)),
            sn="".join(random.sample("zyxwvutsrqponmlkjihgfedcba", 8)),
            asset_level=1,
            memo="N/A",
            station=stations[station_id],
            admin=admin,
        )

        mp1 = MeasurePoint(
            type=0,
            name=unit_name + "电机非驱动端X向",
            sample_interval=300,
            sample_freq=10000,
            station=stations[station_id],
            id_inner_station=mp_id + 1,
        )
        mp_id = mp_id + 1
        mp2 = MeasurePoint(
            type=0,
            name=unit_name + "电机非驱动端Y向",
            sample_interval=300,
            sample_freq=10000,
            station=stations[station_id],
            id_inner_station=mp_id + 1,
        )
        mp_id = mp_id + 1
        mp3 = MeasurePoint(
            type=0,
            name=unit_name + "电机驱动端X向",
            sample_interval=300,
            sample_freq=10000,
            station=stations[station_id],
            id_inner_station=mp_id + 1,
        )
        mp_id = mp_id + 1
        mp4 = MeasurePoint(
            type=0,
            name=unit_name + "电机驱动端Y向",
            sample_interval=300,
            sample_freq=10000,
            station=stations[station_id],
            id_inner_station=mp_id + 1,
        )
        mp_id = mp_id + 1
        mp5 = MeasurePoint(
            type=0,
            name=unit_name + "泵非驱动端X向",
            sample_interval=300,
            sample_freq=10000,
            station=stations[station_id],
            id_inner_station=mp_id + 1,
        )
        mp_id = mp_id + 1
        mp6 = MeasurePoint(
            type=0,
            name=unit_name + "泵非驱动端Y向",
            sample_interval=300,
            sample_freq=10000,
            station=stations[station_id],
            id_inner_station=mp_id + 1,
        )
        mp_id = mp_id + 1
        mp7 = MeasurePoint(
            type=0,
            name=unit_name + "泵驱动端X向",
            sample_interval=300,
            sample_freq=10000,
            station=stations[station_id],
            id_inner_station=mp_id + 1,
        )
        mp_id = mp_id + 1
        mp8 = MeasurePoint(
            type=0,
            name=unit_name + "泵驱动端Y向",
            sample_interval=300,
            sample_freq=10000,
            station=stations[station_id],
            id_inner_station=mp_id + 1,
        )
        mp_id = mp_id + 1
        cur = MeasurePoint(
            type=1,
            name=unit_name + "电机电流电压",
            sample_interval=300,
            sample_freq=20480,
            station=stations[station_id],
            id_inner_station=mp_id + 1,
        )
        mp_id = mp_id + 1

        motor.children = [Rotor, Stator, Bearing1, Bearing2]

        PumpUnit.children = [motor, pump]

        PumpUnit.measure_points = [mp1, mp2, mp3, mp4, mp5, mp6, mp7, mp8, cur]
        session.add(PumpUnit)
        session.commit()
