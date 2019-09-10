from sqlalchemy import Column, Integer, SmallInteger, \
    ForeignKey, DateTime, func
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from db import Base, table_args


class MeasurePoint(Base):
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
