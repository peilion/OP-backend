#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, SmallInteger, \
    ForeignKey, Float, DateTime, func
from sqlalchemy import String, Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from db.conn import meta_engine
from db_config import table_args

meta_base = declarative_base(meta_engine)


class User(meta_base):
    __tablename__ = 'user'
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    cr_time = Column(DateTime, nullable=True, default=func.now())
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())

    assets = relationship('Asset', back_populates='admin')


class Manufacturer(meta_base):
    __tablename__ = 'manufacturer'
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    telephone = Column(String(30), nullable=True)
    cr_time = Column(DateTime, nullable=True, default=func.now())
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())

    assets = relationship('Asset', back_populates='manufacturer')


class Station(meta_base):
    __tablename__ = 'station'
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    location = Column(String(32), nullable=True)
    memo = Column(Text, nullable=True)
    telephone = Column(String(30), nullable=True)
    cr_time = Column(DateTime, nullable=True, default=func.now())
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())

    sharding_db_id = Column(Integer, nullable=False)  # 指向该站数据库id

    assets = relationship('Asset', back_populates='station')
    measure_points = relationship('MeasurePoint', back_populates="station")


class Asset(meta_base):
    LEVELS = {0: 'Unit', 1: 'Equip', 2: 'Component'}
    STATUS = {0: 'Excellent', 1: 'Good', 2: 'Moderate', 3: 'Poor', 4: 'Offline'}

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    sn = Column(String(128), unique=True)
    lr_time = Column(DateTime, nullable=True)
    cr_time = Column(DateTime, nullable=True, default=func.now())
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())
    asset_level = Column(SmallInteger, nullable=False)  # 值含义见 LEVELS
    memo = Column(Text, nullable=True)

    health_indicator = Column(Float, default=85, nullable=True)
    statu = Column(SmallInteger, default=4)  # 值含义见 STATUS

    parent_id = Column(Integer, ForeignKey('asset.id'), nullable=True)
    manufacturer_id = Column(Integer, ForeignKey('manufacturer.id'))
    station_id = Column(Integer, ForeignKey('station.id'))
    admin_id = Column(Integer, ForeignKey('user.id'), nullable=True)

    children = relationship("Asset")
    manufacturer = relationship("Manufacturer", back_populates="assets")
    station = relationship('Station', back_populates='assets')
    admin = relationship('User', back_populates='assets')
    warninglogs = relationship('WarningLog', back_populates='asset')
    measure_points = relationship('MeasurePoint', back_populates='asset')

    __tablename__ = 'asset'
    __table_args__ = table_args


class PumpUnit(meta_base):
    __tablename__ = 'pump_unit'
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)

    asset_id = Column(Integer, ForeignKey('asset.id'))
    asset = relationship("Asset", uselist=False)


class Motor(meta_base):
    __tablename__ = 'motor'
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    phase_number = Column(SmallInteger, nullable=True, default=3)
    pole_pairs_number = Column(SmallInteger, nullable=True, default=2)
    turn_number = Column(SmallInteger, nullable=True, default=50)
    rated_voltage = Column(Float, nullable=True, default=220)
    rated_speed = Column(Float, nullable=True, default=5000)

    asset_id = Column(Integer, ForeignKey('asset.id'))
    asset = relationship("Asset", uselist=False)


class Pump(meta_base):
    __tablename__ = 'pump'
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    flow = Column(Float, nullable=True)
    work_pressure = Column(Float, nullable=True)
    blade_number = Column(SmallInteger, nullable=True)
    stage_number = Column(SmallInteger, nullable=True)

    asset_id = Column(Integer, ForeignKey('asset.id'))
    asset = relationship("Asset", uselist=False)


class Bearing(meta_base):
    __tablename__ = 'bearing'
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    inner_race_diameter = Column(Float, nullable=True)
    inner_race_width = Column(Float, nullable=True)
    outter_race_diameter = Column(Float, nullable=True)
    outter_race_width = Column(Float, nullable=True)
    roller_diameter = Column(Float, nullable=True)
    roller_number = Column(SmallInteger, nullable=True)
    contact_angle = Column(Float, nullable=True)
    model = Column(Float, nullable=True)

    bpfi = Column(Float, nullable=True)
    bpfo = Column(Float, nullable=True)
    bsf = Column(Float, nullable=True)
    ftf = Column(Float, nullable=True)

    asset_id = Column(Integer, ForeignKey('asset.id'))
    asset = relationship("Asset", uselist=False)


class Rotor(meta_base):
    __tablename__ = 'rotor'
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)

    length = Column(Float, nullable=True)
    outer_diameter = Column(Float, nullable=True)
    inner_diameter = Column(Float, nullable=True)
    slot_number = Column(Integer, nullable=True)

    asset_id = Column(Integer, ForeignKey('asset.id'))
    asset = relationship("Asset", uselist=False)


class Stator(meta_base):
    __tablename__ = 'stator'
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)

    length = Column(Float, nullable=True)
    outer_diameter = Column(Float, nullable=True)
    inner_diameter = Column(Float, nullable=True)
    slot_number = Column(Integer, nullable=True)

    asset_id = Column(Integer, ForeignKey('asset.id'))
    asset = relationship("Asset", uselist=False)


class WarningLog(meta_base):
    __tablename__ = 'warning_log'
    __table_args__ = table_args

    SEVERITIES = {0: 'Slight', 1: 'Attention', 2: 'Serious'}

    id = Column(Integer, primary_key=True)
    cr_time = Column(DateTime, nullable=True, default=func.now())
    description = Column(Text, nullable=False)
    severity = Column(SmallInteger, nullable=False)

    asset_id = Column(Integer, ForeignKey('asset.id'))
    asset = relationship("Asset", back_populates="warninglogs")


class MeasurePoint(meta_base):
    __tablename__ = 'measure_point'
    __table_args__ = (
        UniqueConstraint("station_id", "id_inner_station", name='uix_stationid_innerstationid'),
        table_args
    )

    TYPES = {0: 'Vibration', 1: 'Current', 2: 'Third party Integration'}

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    cr_time = Column(DateTime, nullable=True, default=func.now())
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())

    type = Column(SmallInteger, nullable=False)  # 键含义参照 TYPES

    sample_interval = Column(Integer)  # 单位为 s
    sample_freq = Column(Integer)  # 单位为 Hz

    asset_id = Column(Integer, ForeignKey('asset.id'))

    station_id = Column(Integer, ForeignKey('station.id'))
    id_inner_station = Column(Integer)

    asset = relationship("Asset", back_populates="measure_points")
    station = relationship('Station', back_populates="measure_points")

# meta_base.metadata.drop_all()
# meta_base.metadata.create_all()

# class StatorEvalStd(Base):
#     __tablename__ = 'stator_evaluate_standard'
#     __table_args__ = table_args
#
#     id = Column(Integer, primary_key=True)
#     i_imbalance_lv1 = Column(Float, default=2)
#     i_imbalance_lv2 = Column(Float, default=4)
#     i_imbalance_lv3 = Column(Float, default=10)
#
#     u_imbalance_lv1 = Column(Float, default=2)
#     u_imbalance_lv2 = Column(Float, default=4)
#     u_imbalance_lv3 = Column(Float, default=10)
#
#     irms_imbalance_lv1 = Column(Float, default=2)
#     irms_imbalance_lv2 = Column(Float, default=4)
#     irms_imbalance_lv3 = Column(Float, default=10)
#
#     har3_lv1 = Column(Float, default=0.5)
#     har3_lv2 = Column(Float, default=1)
#     har3_lv3 = Column(Float, default=2)
#
#     uz_type = Column(SmallInteger, default=1)  # 0:额定报警 1:零序/正序报警, 针对绝缘故障
#     uz_imbalance_lv1 = Column(Float, default=2)
#     uz_imbalance_lv2 = Column(Float, default=4)
#     uz_imbalance_lv3 = Column(Float, default=10)
#
#     iz_type = Column(SmallInteger, default=1)  # 0:额定报警 1:零序/正序报警，针对单相接地
#     iz_imbalance_lv1 = Column(Float, default=2)
#     iz_imbalance_lv2 = Column(Float, default=4)
#     iz_imbalance_lv3 = Column(Float, default=10)
#
#     md_time = Column(DateTime, default=func.now(), onupdate=func.now())
#
#
# class RotorEvalStd(Base):
#     __tablename__ = 'rotor_evaluate_standard'
#     __table_args__ = table_args
#
#     id = Column(Integer, primary_key=True)
#     slip = Column(Float, default=0.006)
#     sideband_lv1 = Column(Float, default=0.2)
#     sideband_lv2 = Column(Float, default=1.58)
#     sideband_lv3 = Column(Float, default=3.16)
#
#     md_time = Column(DateTime, default=func.now(), onupdate=func.now())
#
#
# class BearingEvalStd(Base):
#     __tablename__ = 'bearing_evaluate_standard'
#     __table_args__ = table_args
#
#     id = Column(Integer, primary_key=True)
#
#     bpfi_lv1 = Column(Float, default=0.5)
#     bpfi_lv2 = Column(Float, default=1.0)
#     bpfi_lv3 = Column(Float, default=2.0)
#
#     bsf_lv1 = Column(Float, default=0.5)
#     bsf_lv2 = Column(Float, default=1.0)
#     bsf_lv3 = Column(Float, default=2.0)
#
#     bpfo_lv1 = Column(Float, default=0.5)
#     bpfo_lv2 = Column(Float, default=1.0)
#     bpfo_lv3 = Column(Float, default=2.0)
#
#     ftf_lv1 = Column(Float, default=0.5)
#     ftf_lv2 = Column(Float, default=1.0)
#     ftf_lv3 = Column(Float, default=2.0)
#
#     har5_lv1 = Column(Float, default=0.5)
#     har5_lv2 = Column(Float, default=1.0)
#     har5_lv3 = Column(Float, default=2.0)
#
#     md_time = Column(DateTime, default=func.now(), onupdate=func.now())
#
#
# class PowerEvalStd(Base):
#     __tablename__ = 'power_evaluate_standard'
#     __table_args__ = table_args
#
#     id = Column(Integer, primary_key=True)
#
#     i_imbalance_lv1 = Column(Float, default=2)
#     i_imbalance_lv2 = Column(Float, default=4)
#     i_imbalance_lv3 = Column(Float, default=10)
#
#     u_imbalance_lv1 = Column(Float, default=2)
#     u_imbalance_lv2 = Column(Float, default=4)
#     u_imbalance_lv3 = Column(Float, default=10)
#
#     uthd_lv1 = Column(Float, default=4 / 3)
#     uthd_lv2 = Column(Float, default=8 / 3)
#     uthd_lv3 = Column(Float, default=4)
#
#     ithd_lv1 = Column(Float, default=4 / 3)
#     ithd_lv2 = Column(Float, default=8 / 3)
#     ithd_lv3 = Column(Float, default=4)
#
#     uhar_odd_lv1 = Column(Float, default=3.2 / 3)
#     uhar_odd_lv2 = Column(Float, default=3.2 * 2 / 3)
#     uhar_odd_lv3 = Column(Float, default=3.2)
#
#     uhar_even_lv1 = Column(Float, default=0.5)
#     uhar_even_lv2 = Column(Float, default=1.0)
#     uhar_even_lv3 = Column(Float, default=1.5)
#
#     power_factor_lv1 = Column(Float, default=0.8)
#     power_factor_lv2 = Column(Float, default=0.6)
#     power_factor_lv3 = Column(Float, default=0.4)
#
#     md_time = Column(DateTime, default=func.now(), onupdate=func.now())
