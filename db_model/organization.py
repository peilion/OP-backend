from sqlalchemy import Column, Integer,ForeignKey
from sqlalchemy import String, Text
from sqlalchemy.orm import relationship

from db import Base, table_args


class Station(Base):
    __tablename__ = 'station'
    __table_args__ = table_args

    STATIONS =  {1: 'HuHeHaoTe', 2: 'ErTuoKeQi', 3: 'BaoTou'}

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    location = Column(String(32), nullable=True)
    memo = Column(Text, nullable=True)
    telephone = Column(String(30), nullable=True)

    bc_id = Column(Integer, ForeignKey('branch_company.id'))
    rc_id = Column(Integer, ForeignKey('region_company.id'))
    sharding_db_id = Column(Integer, nullable=False)  # 指向该站数据库id

    assets = relationship('Asset', back_populates='station')
    measure_points = relationship('MeasurePoint', back_populates="station")


class BranchCompany(Base):
    __tablename__ = 'branch_company'
    __table_args__ = table_args
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    memo = Column(Text, nullable=True)
    telephone = Column(String(30), nullable=True)

class RegionCompany(Base):
    __tablename__ = 'region_company'
    __table_args__ = table_args
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    memo = Column(Text, nullable=True)
    telephone = Column(String(30), nullable=True)

class Pipeline(Base):
    __tablename__ = 'pipeline'
    __table_args__ = table_args
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)