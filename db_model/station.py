from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy import String, Text
from sqlalchemy.orm import relationship

from db import Base, table_args


class Station(Base):
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
