from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from db import Base, table_args


class PumpUnit(Base):
    __tablename__ = 'pump_unit'
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)

    asset_id = Column(Integer, ForeignKey('asset.id'))
    asset = relationship("Asset", uselist=False)
