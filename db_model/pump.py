from sqlalchemy import Column, Integer, SmallInteger, ForeignKey, Float
from sqlalchemy.orm import relationship

from db import Base, table_args


class Pump(Base):
    __tablename__ = "pump"
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    flow = Column(Float, nullable=True)
    work_pressure = Column(Float, nullable=True)
    blade_number = Column(SmallInteger, nullable=True)
    stage_number = Column(SmallInteger, nullable=True)

    asset_id = Column(Integer, ForeignKey("asset.id"))
    asset = relationship("Asset", uselist=False)
