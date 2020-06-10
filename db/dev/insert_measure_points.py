import random

from db import meta_engine
from db.db_config import session_make
from db_model import Asset, Manufacturer, Bearing, Threshold, Station, MeasurePoint
import datetime
import re

session = session_make(meta_engine)
stations = session.query(Station).all()
for station in stations:
    assets = (
        session.query(Asset)
        .filter(Asset.asset_type == 0, Asset.station_id == station.id)
        .all()
    )
    inner_id = -1
    for asset in assets:
        if asset.mp_configuration == 1:
            for name in [
                ["电机非驱动端Y向", "vertical", "motor_non_driven"],
                ["电机驱动端Y向", "vertical", "motor_driven"],
                ["泵非驱动端Y向", "vertical", "pump_non_driven"],
                ["泵驱动端Y向", "vertical", "pump_driven"],
            ]:
                inner_id = inner_id + 1
                session.add(
                    MeasurePoint(
                        type=0,
                        name=name[0],
                        sample_interval=300,
                        sample_freq=10000,
                        station_id=station.sharding_db_id,
                        asset=asset,
                        inner_station_id=inner_id,
                        direction=name[1],
                        position=name[2],
                    )
                )
            session.commit()
        if asset.mp_configuration == 2:
            for name in [
                ["电机非驱动端Y向", "vertical", "motor_non_driven"],
                ["电机非驱动端X向", "horizontal", "motor_non_driven"],
                ["电机驱动端Y向", "vertical", "motor_driven"],
                ["电机驱动端X向", "horizontal", "motor_driven"],
                ["泵非驱动端Y向", "vertical", "pump_non_driven"],
                ["泵非驱动端X向", "horizontal", "pump_non_driven"],
                ["泵驱动端Y向", "vertical", "pump_driven"],
                ["泵驱动端X向", "horizontal", "pump_driven"],
                ["进口管线", None, None],
                ["出口管线", None, None],
            ]:
                inner_id = inner_id + 1
                session.add(
                    MeasurePoint(
                        type=0,
                        name=name[0],
                        sample_interval=300,
                        sample_freq=10000,
                        station_id=station.sharding_db_id,
                        asset=asset,
                        inner_station_id=inner_id,
                        direction=name[1],
                        position=name[2],
                    )
                )
            session.commit()
        if asset.mp_configuration == 3:
            for name in [
                ["电机非驱动端Y向", "vertical", "motor_non_driven"],
                ["电机非驱动端X向", "horizontal", "motor_non_driven"],
                ["电机驱动端Y向", "vertical", "motor_driven"],
                ["电机驱动端X向", "horizontal", "motor_driven"],
                ["泵非驱动端Y向", "vertical", "pump_non_driven"],
                ["泵非驱动端X向", "horizontal", "pump_non_driven"],
                ["泵驱动端Y向", "vertical", "pump_driven"],
                ["泵驱动端X向", "horizontal", "pump_driven"],
            ]:
                inner_id = inner_id + 1

                session.add(
                    MeasurePoint(
                        type=0,
                        name=name[0],
                        sample_interval=300,
                        sample_freq=10000,
                        station_id=station.sharding_db_id,
                        asset=asset,
                        inner_station_id=inner_id,
                        direction=name[1],
                        position=name[2],
                    )
                )
            session.commit()
    for asset in assets:
        if (asset.mp_configuration == 2) | (asset.mp_configuration == 3):
            inner_id = inner_id + 1
            session.add(
                MeasurePoint(
                    type=1,
                    name="电机电流电压",
                    sample_interval=300,
                    sample_freq=10000,
                    station_id=station.sharding_db_id,
                    asset=asset,
                    inner_station_id=inner_id,
                )
            )
            session.commit()
