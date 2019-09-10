from sqlalchemy import Column, Integer, SmallInteger, \
    ForeignKey, Float
from sqlalchemy.orm import relationship

from db import Base, table_args


class Motor(Base):
    __tablename__ = 'motor'
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    phase_number = Column(SmallInteger, nullable=True, default=3)
    pole_pairs_number = Column(SmallInteger, nullable=True, default=2)
    turn_number = Column(SmallInteger, nullable=True, default=50)
    rated_voltage = Column(Float, nullable=True, default=220)
    rated_speed = Column(Float, nullable=True, default=5000)

    asset_id = Column(Integer, ForeignKey('asset.id'))
    asset = relationship("Asset", uselist=False)
