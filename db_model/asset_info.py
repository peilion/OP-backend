from sqlalchemy import Column, Integer, Float, SmallInteger, ForeignKey, Boolean, String
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import relationship

from db import Base, table_args


class Bearing(Base):
    __tablename__ = "bearing"
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    is_driven_end = Column(SmallInteger, nullable=False)
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
    health_indicator = Column(Float, default=0)
    statu = Column(SmallInteger, default=0)
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
    mset_model_path = Column(String(255))


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
