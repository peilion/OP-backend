from sqlalchemy import Column, Integer, SmallInteger, \
    ForeignKey, Float
from sqlalchemy.orm import relationship

from db import Base, table_args


class Bearing(Base):
    __tablename__ = 'bearing'
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    inner_race_diameter = Column(Float, nullable=True)
    inner_race_width = Column(Float, nullable=True)
    outter_race_diameter = Column(Float, nullable=True)
    outter_race_width = Column(Float, nullable=True)
    roller_diameter = Column(Float, nullable=True)
    roller_number = Column(SmallInteger, nullable=True)
    contact_angle = Column(Float, nullable=True)
    model = Column(Float, nullable=True)

    bpfi = Column(Float, nullable=True)
    bpfo = Column(Float, nullable=True)
    bsf = Column(Float, nullable=True)
    ftf = Column(Float, nullable=True)

    asset_id = Column(Integer, ForeignKey('asset.id'))
    asset = relationship("Asset", uselist=False)
