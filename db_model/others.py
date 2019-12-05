from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from db import Base, table_args


class User(Base):
    __tablename__ = "user"
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    cr_time = Column(DateTime, nullable=True, default=func.now())
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())

    assets = relationship("Asset", back_populates="admin")


class Manufacturer(Base):
    __tablename__ = "manufacturer"
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    telephone = Column(String(30), nullable=True)
    cr_time = Column(DateTime, nullable=True, default=func.now())
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())

    assets = relationship("Asset", back_populates="manufacturer")
