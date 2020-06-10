import random

from db import meta_engine
from db.db_config import session_make
from db_model import Asset, Manufacturer, Bearing, Threshold
import datetime
import re

session = session_make(meta_engine)
bearings = session.query(Asset).filter(Asset.asset_type == 5)

for bearing in bearings:
    bearing_info = Bearing(
        is_driven_end=0 if re.search("非驱动端", bearing.name) else 1,
        bpfi=random.choice([4.19, 3.71]),
        bpfo=random.choice([5.81, 5.29]),
        bsf=random.choice([2.99, 2.75]),
        ftf=random.choice([0.42, 0.29]),
        asset=bearing,
    )
    session.add(bearing_info)
session.commit()

th1 = Threshold(
    mp_pattern="motor_driven",
    diag_threshold={
        "Unbalance": [1, 2, 3],
        "Misalignment": [1, 2, 3],
        "RollBearing": [1, 2, 3],
        "ALoose": [1, 2, 3],
        "BLoose": [1, 2, 3],
        "Rubbing": [1, 2, 3],
        "thd": 0.2,
        "kurtosis": 6,
        "harmonic_threshold": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "subharmonic_threshold": [1, 1, 1, 1, 1],
    },
)

th2 = Threshold(
    mp_pattern="motor_non_driven",
    diag_threshold={
        "Unbalance": [1, 2, 3],
        "RollBearing": [1, 2, 3],
        "ALoose": [1, 2, 3],
        "BLoose": [1, 2, 3],
        "thd": 0.2,
        "kurtosis": 6,
        "harmonic_threshold": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    },
)

th3 = Threshold(
    mp_pattern="pump_driven",
    diag_threshold={
        "Unbalance": [1, 2, 3],
        "Misalignment": [1, 2, 3],
        "RollBearing": [1, 2, 3],
        "ALoose": [1, 2, 3],
        "BLoose": [1, 2, 3],
        "Surge": [1, 2, 3],
        "Rubbing": [1, 2, 3],
        "thd": 0.2,
        "kurtosis": 6,
        "harmonic_threshold": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "subharmonic_threshold": [1, 1, 1, 1, 1],
    },
)

th4 = Threshold(
    mp_pattern="pump_non_driven",
    diag_threshold={
        "Unbalance": [1, 2, 3],
        "RollBearing": [1, 2, 3],
        "Surge": [1, 2, 3],
        "ALoose": [1, 2, 3],
        "BLoose": [1, 2, 3],
        "thd": 0.2,
        "kurtosis": 6,
        "harmonic_threshold": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    },
)

session.add_all([th1, th2, th3, th4])
