import enum

from sqlalchemy import Column, Integer, Enum, JSON, func, DateTime

from db import Base, table_args


class MPPatternEnum(enum.Enum):
    motor_driven = 1
    motor_non_driven = 2
    pump_driven = 3
    pump_non_driven = 4


class Threshold(Base):
    __tablename__ = "threshold"
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    mp_pattern = Column(Enum(MPPatternEnum), nullable=True)
    diag_threshold = Column(JSON, nullable=True)
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())
    # diag_threshold字段内部形如：
    # { '不平衡': [0,1,2], '不对中': [0,1,2] ... }
    # { 故障名: [轻度故障阈值,中度故障阈值,严重故障阈值]}
