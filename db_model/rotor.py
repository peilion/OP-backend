from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from db import Base, table_args


class Rotor(Base):
    __tablename__ = "rotor"
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)

    length = Column(Float, nullable=True)
    outer_diameter = Column(Float, nullable=True)
    inner_diameter = Column(Float, nullable=True)
    slot_number = Column(Integer, nullable=True)

    asset_id = Column(Integer, ForeignKey("asset.id"))
    asset = relationship("Asset", uselist=False)
