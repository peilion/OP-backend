from sqlalchemy import Column, Integer, SmallInteger, \
    ForeignKey, DateTime, func, Boolean, String
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from db import Base, table_args


class WarningLog(Base):
    __tablename__ = 'warning_log'
    __table_args__ = table_args

    SEVERITIES = {0: 'Slight', 1: 'Attention', 2: 'Serious'}

    id = Column(Integer, primary_key=True)
    cr_time = Column(DateTime, nullable=True, default=func.now(), index=True)
    description = Column(Text, nullable=False)
    severity = Column(SmallInteger, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    fp_hash = Column(String(21), nullable=False)  # generate by: hash(falut_pattern_array[set])
    asset_id = Column(Integer, ForeignKey('asset.id'))

    asset = relationship("Asset", back_populates="warninglogs")
