import random

from db import meta_engine
from db.db_config import session_make
from db_model import Asset, Manufacturer
import datetime

session = session_make(meta_engine)
assets = session.query(Asset).all()
manufactures = session.query(Manufacturer).all()

for asset in assets:
    Motor = Asset(
        name="驱动电机#{0}".format(random.randint(100, 999)),
        sn="".join(random.sample("zyxwvutsrqponmlkjihgfedcba", 8)),
        asset_level=1,
        asset_type=2,
        st_time=datetime.datetime.fromisoformat("2014-09-09 10:24:25"),
        memo="N/A",
        station=asset.station,
        admin=asset.admin,
        repairs=random.randint(0, 5),
        health_indicator=85,
        parent_id=asset.id,
        manufacturer=random.choice(manufactures),
    )

    Bearing1 = Asset(
        name="驱动端轴承#{0}".format(random.randint(100, 999)),
        sn="".join(random.sample("zyxwvutsrqponmlkjihgfedcba", 8)),
        asset_level=2,
        asset_type=5,
        st_time=datetime.datetime.fromisoformat("2014-09-09 10:24:25"),
        memo="N/A",
        station=asset.station,
        admin=asset.admin,
        repairs=random.randint(0, 5),
        health_indicator=85,
        manufacturer=random.choice(manufactures),
    )

    Bearing2 = Asset(
        name="非驱动端轴承#{0}".format(random.randint(100, 999)),
        sn="".join(random.sample("zyxwvutsrqponmlkjihgfedcba", 8)),
        asset_level=2,
        asset_type=5,
        st_time=datetime.datetime.fromisoformat("2014-09-09 10:24:25"),
        memo="N/A",
        station=asset.station,
        admin=asset.admin,
        repairs=random.randint(0, 5),
        health_indicator=85,
        manufacturer=random.choice(manufactures),
    )

    Pump = Asset(
        name="泵体#{0}".format(random.randint(100, 999)),
        sn="".join(random.sample("zyxwvutsrqponmlkjihgfedcba", 8)),
        asset_level=1,
        asset_type=1,
        st_time=datetime.datetime.fromisoformat("2014-09-09 10:24:25"),
        memo="N/A",
        station=asset.station,
        admin=asset.admin,
        repairs=random.randint(0, 5),
        health_indicator=85,
        parent_id=asset.id,
        manufacturer=random.choice(manufactures),
    )

    Bearing3 = Asset(
        name="驱动端轴承#{0}".format(random.randint(100, 999)),
        sn="".join(random.sample("zyxwvutsrqponmlkjihgfedcba", 8)),
        asset_level=2,
        asset_type=5,
        st_time=datetime.datetime.fromisoformat("2014-09-09 10:24:25"),
        memo="N/A",
        station=asset.station,
        admin=asset.admin,
        repairs=random.randint(0, 5),
        health_indicator=85,
        manufacturer=random.choice(manufactures),
    )

    Bearing4 = Asset(
        name="非驱动端轴承#{0}".format(random.randint(100, 999)),
        sn="".join(random.sample("zyxwvutsrqponmlkjihgfedcba", 8)),
        asset_level=2,
        asset_type=5,
        st_time=datetime.datetime.fromisoformat("2014-09-09 10:24:25"),
        memo="N/A",
        station=asset.station,
        admin=asset.admin,
        repairs=random.randint(0, 5),
        health_indicator=85,
        manufacturer=random.choice(manufactures),
    )

    Motor.children = [Bearing1, Bearing2]
    Pump.children = [Bearing3, Bearing4]
    session.add(Motor)
    session.add(Pump)

session.commit()
