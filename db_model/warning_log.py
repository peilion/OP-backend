from sqlalchemy import Column, Integer, SmallInteger, \
    ForeignKey, DateTime, func
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from db import Base, table_args


class WarningLog(Base):
    __tablename__ = 'warning_log'
    __table_args__ = table_args

    SEVERITIES = {0: 'Slight', 1: 'Attention', 2: 'Serious'}

    id = Column(Integer, primary_key=True)
    cr_time = Column(DateTime, nullable=True, default=func.now())
    description = Column(Text, nullable=False)
    severity = Column(SmallInteger, nullable=False)

    asset_id = Column(Integer, ForeignKey('asset.id'))
    asset = relationship("Asset", back_populates="warninglogs")
