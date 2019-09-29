from sqlalchemy import Column, Integer, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship

from db import Base, table_args


class PumpUnit(Base):
    __tablename__ = 'pump_unit'
    __table_args__ = table_args

    OIL_TYPES = {0: 'Crude', 1: 'Refined'}

    id = Column(Integer, primary_key=True)
    oil_type = Column(Integer)
    is_domestic = Column(Boolean, nullable=False)
    design_output = Column(Float)
    asset_id = Column(Integer, ForeignKey('asset.id'))
    pipeline_id = Column(Integer, ForeignKey('pipeline.id'))

    asset = relationship("Asset", uselist=False)
