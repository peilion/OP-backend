from sqlalchemy import Column, Integer, DateTime, func, Text, ForeignKey, SmallInteger, Boolean, String
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
    __table_args__ = table_args

    SEVERITIES = {0: "Slight", 1: "Attention", 2: "Serious"}

    id = Column(Integer, primary_key=True)
    cr_time = Column(DateTime, nullable=True, default=func.now(), index=True)
    description = Column(Text, nullable=False)
    severity = Column(SmallInteger, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    fp_hash = Column(
        String(21), nullable=False
    )  # generate by: hash(falut_pattern_array[set])

    asset_id = Column(Integer, ForeignKey("asset.id"))
    mp_id = Column(Integer, ForeignKey("measure_point.id"))
    data_id = Column(Integer)

    asset = relationship("Asset", back_populates="warninglogs")