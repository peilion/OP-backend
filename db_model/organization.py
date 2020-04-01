from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy import String, Text
from sqlalchemy.orm import relationship

from db import Base, table_args


class Station(Base):
    __tablename__ = "station"
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    location = Column(String(32), nullable=True)
    memo = Column(Text, nullable=True)
    telephone = Column(String(30), nullable=True)

    bc_id = Column(Integer, ForeignKey("branch_company.id"))
    rc_id = Column(Integer, ForeignKey("region_company.id"))

    sharding_db_id = Column(Integer, nullable=False)  # 指向该站数据库id
    latitude = Column(Float)
    longitude = Column(Float)
    weather = Column(Text, nullable=True)

    assets = relationship("Asset", back_populates="station")
    measure_points = relationship("MeasurePoint", back_populates="station")

    branch_company = relationship("BranchCompany", back_populates="stations")


class BranchCompany(Base):
    __tablename__ = "branch_company"
    __table_args__ = table_args
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    memo = Column(Text, nullable=True)
    telephone = Column(String(30), nullable=True)
    rc_id = Column(Integer, ForeignKey("region_company.id"))

    region_company = relationship("RegionCompany", back_populates="branch_companies")
    stations = relationship("Station", back_populates="branch_company")


class RegionCompany(Base):
    __tablename__ = "region_company"
    __table_args__ = table_args
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    memo = Column(Text, nullable=True)
    telephone = Column(String(30), nullable=True)

    branch_companies = relationship("BranchCompany", back_populates="region_company")


class Pipeline(Base):
    __tablename__ = "pipeline"
    __table_args__ = table_args
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    length = Column(Float)
