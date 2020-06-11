from sqlalchemy import (
    Column,
    Integer,
    SmallInteger,
    ForeignKey,
    DateTime,
    func,
    Float,
    Enum,
)
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import relationship
import enum
from db import Base, table_args


class DirectionEnum(enum.Enum):
    horizontal = 1
    vertical = 2
    axial = 3


class PositionEnum(enum.Enum):
    motor_driven = 1
    motor_non_driven = 2
    pump_driven = 3
    pump_non_driven = 4
    pipeline = 5


class MeasurePoint(Base):
    __tablename__ = "measure_point"
    __table_args__ = (
        UniqueConstraint(
            "station_id", "inner_station_id", name="uix_stationid_innerstationid"
        ),
        table_args,
    )

    TYPES = {0: "Vibration", 1: "Current", 2: "Third party Integration"}

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    cr_time = Column(DateTime, nullable=True, default=func.now())
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())
    health_indicator = Column(Float, default=85, nullable=True)
    type = Column(SmallInteger, nullable=False)  # 键含义参照 TYPES
    sample_interval = Column(Integer)  # 单位为 s
    sample_sensitive = Column(Float)  # 单位为 mv/g
    sample_freq = Column(Integer)  # 单位为 Hz
    statu = Column(SmallInteger, default=0)  # 值含义见 STATUS
    asset_id = Column(Integer, ForeignKey("asset.id"))
    station_id = Column(Integer, ForeignKey("station.id"))
    inner_station_id = Column(Integer)
    last_diag_id = Column(Integer)
    direction = Column(Enum(DirectionEnum), nullable=True)
    position = Column(Enum(PositionEnum), nullable=True)
    asset = relationship("Asset", back_populates="measure_points")
    station = relationship("Station", back_populates="measure_points")
