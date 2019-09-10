from sqlalchemy import Column, Integer, SmallInteger, \
    ForeignKey, Float, DateTime, func
from sqlalchemy import String, Text
from sqlalchemy.orm import relationship

from db import Base, table_args


class Asset(Base):
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
