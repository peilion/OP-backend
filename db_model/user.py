#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy import String
from sqlalchemy.orm import relationship

from db import Base, table_args


class User(Base):
    __tablename__ = 'user'
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    cr_time = Column(DateTime, nullable=True, default=func.now())
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())

    assets = relationship('Asset', back_populates='admin')