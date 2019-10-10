from sqlalchemy import Column, Integer, SmallInteger, \
    ForeignKey, DateTime, func, Boolean, String
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from db import Base, table_args


class MaintenanceRecord(Base):
    __tablename__ = 'maintenance_record'
    __table_args__ = table_args

    STATUS = {0: 'awaiting', 1: 'working', 2: 'finished'}

    id = Column(Integer, primary_key=True)
    cr_time = Column(DateTime, nullable=True, default=func.now(), index=True)
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())

    description = Column(Text, nullable=False)
    asset_id = Column(Integer, ForeignKey('asset.id'))
    statu = Column(SmallInteger)

    asset = relationship("Asset", back_populates="maintlogs")
