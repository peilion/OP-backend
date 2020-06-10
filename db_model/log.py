from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    func,
    Text, Binary,
    ForeignKey,
    SmallInteger, Float,
    Boolean, JSON, UniqueConstraint)
from sqlalchemy.orm import relationship

from db import Base, table_args


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_record"
    __table_args__ = table_args

    STATUS = {0: "awaiting", 1: "working", 2: "finished"}

    id = Column(Integer, primary_key=True)
    cr_time = Column(DateTime, nullable=True, default=func.now(), index=True)
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())

    description = Column(Text, nullable=False)
    asset_id = Column(Integer, ForeignKey("asset.id"))
    statu = Column(SmallInteger)

    asset = relationship("Asset", back_populates="maintlogs")


class WarningLog(Base):
    __tablename__ = "warning_log"
    __table_args__ = (
        UniqueConstraint(
            "mp_id", "data_id", name="uix_mpid_dataid"
        ),
        table_args,
    )
    SEVERITIES = {0: "轻微", 1: "较严重", 2: "严重"}

    id = Column(Integer, primary_key=True)
    cr_time = Column(DateTime, nullable=True, default=func.now(), index=True)
    description = Column(JSON, nullable=False)
    severity = Column(SmallInteger, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    asset_id = Column(Integer, ForeignKey("asset.id"))
    mp_id = Column(Integer, ForeignKey("measure_point.id"))
    data_id = Column(Integer, index=True)
    ib_indicator = Column(Float, server_default='0')
    ma_indicator = Column(Float, server_default='0')
    bw_indicator = Column(Binary, server_default='')
    al_indicator = Column(Float, server_default='0')
    bl_indicator = Column(Float, server_default='0')
    rb_indicator = Column(Float, server_default='0')
    sg_indicator = Column(Float, server_default='0')
    env_kurtosis = Column(Float, server_default='0')
    vel_thd = Column(Float)

    asset = relationship("Asset", back_populates="warninglogs")


class MsetWarningLog(Base):
    __tablename__ = "mset_warning_log"
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    cr_time = Column(DateTime, nullable=True, default=func.now(), index=True)
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())

    description = Column(Text, nullable=False)
    asset_id = Column(Integer, ForeignKey("asset.id"))
    reporter_id = Column(Integer, index=True)

    # asset = relationship("Asset", back_populates="MsetWarningLogs")
