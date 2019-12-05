from sqlalchemy import Column, Integer, Float, SmallInteger, ForeignKey, Boolean
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import relationship

from db import Base, table_args


class Bearing(Base):
    __tablename__ = "bearing"
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

    asset_id = Column(Integer, ForeignKey("asset.id"))
    asset = relationship("Asset", uselist=False)


class Motor(Base):
    __tablename__ = "motor"
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    phase_number = Column(SmallInteger, nullable=True, default=3)
    pole_pairs_number = Column(SmallInteger, nullable=True, default=2)
    turn_number = Column(SmallInteger, nullable=True, default=50)
    rated_voltage = Column(Float, nullable=True, default=220)
    rated_speed = Column(Float, nullable=True, default=5000)

    asset_id = Column(Integer, ForeignKey("asset.id"))
    asset = relationship("Asset", uselist=False)


class Pump(Base):
    __tablename__ = "pump"
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    flow = Column(Float, nullable=True)
    work_pressure = Column(Float, nullable=True)
    blade_number = Column(SmallInteger, nullable=True)
    stage_number = Column(SmallInteger, nullable=True)

    asset_id = Column(Integer, ForeignKey("asset.id"))
    asset = relationship("Asset", uselist=False)


class PumpUnit(Base):
    __tablename__ = "pump_unit"
    __table_args__ = table_args

    OIL_TYPES = {0: "Crude", 1: "Refined"}

    id = Column(Integer, primary_key=True)
    oil_type = Column(Integer)
    is_domestic = Column(Boolean, nullable=False)
    design_output = Column(Float)
    asset_id = Column(Integer, ForeignKey("asset.id"))
    pipeline_id = Column(Integer, ForeignKey("pipeline.id"))

    asset = relationship("Asset", uselist=False)


class Rotor(Base):
    __tablename__ = "rotor"
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)

    length = Column(Float, nullable=True)
    outer_diameter = Column(Float, nullable=True)
    inner_diameter = Column(Float, nullable=True)
    slot_number = Column(Integer, nullable=True)

    asset_id = Column(Integer, ForeignKey("asset.id"))
    asset = relationship("Asset", uselist=False)


class Stator(Base):
    __tablename__ = "stator"
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)

    length = Column(Float, nullable=True)
    outer_diameter = Column(Float, nullable=True)
    inner_diameter = Column(Float, nullable=True)
    slot_number = Column(Integer, nullable=True)

    asset_id = Column(Integer, ForeignKey("asset.id"))
    asset = relationship("Asset", uselist=False)


info_models_mapper = {
    key: value
    for key, value in locals().items()
    if (value.__class__ == DeclarativeMeta) & (key != "Base")
}
