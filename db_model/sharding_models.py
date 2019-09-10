#!/usr/bin/env python
# -*- coding: utf-8 -*-
# these model are used to get
from sqlalchemy import Column, BigInteger, ForeignKey, Float, DateTime, LargeBinary, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from db_config import session_make
from db.conn import meta_engine
from db_model.meta_models import MeasurePoint
import copy
from db.conn import station_engines

from db_config import table_args

Base = declarative_base()

class ElecData(object):
    _mapper = {}
    base_class_name = 'elec_data'

    @classmethod
    def model(cls, point_id: int, base: DeclarativeMeta = Base):
        class_name = cls.base_class_name + '_%d' % point_id
        ModelClass = cls._mapper.get(class_name, None)
        if ModelClass is None:
            ModelClass = type(class_name, (base,), dict(
                __module__=__name__,
                __name__=class_name,
                __tablename__=class_name,
                id=Column(BigInteger, primary_key=True),
                time=Column(DateTime, index=True),
                ucur=Column(LargeBinary, nullable=False),
                vcur=Column(LargeBinary, nullable=False),
                wcur=Column(LargeBinary, nullable=False),
                uvolt=Column(LargeBinary, nullable=False),
                vvolt=Column(LargeBinary, nullable=False),
                wvolt=Column(LargeBinary, nullable=False),
                __table_args__=table_args
            ))
            cls._mapper[class_name] = ModelClass
        mapper = ModelClass
        return mapper


class ElecFeature(object):
    _mapper = {}
    base_class_name = 'elec_feature'

    @classmethod
    def model(cls, point_id: int, base: DeclarativeMeta = Base):
        class_name = cls.base_class_name + '_%d' % point_id
        ModelClass = cls._mapper.get(class_name, None)
        if ModelClass is None:
            ModelClass = type(class_name, (base,), dict(
                __module__=__name__,
                __name__=class_name,
                __tablename__=class_name,
                id=Column(BigInteger, primary_key=True),
                time=Column(DateTime, index=True),
                urms=Column(Float, default=0),
                uthd=Column(Float, default=0),
                uharmonics=Column(LargeBinary, default=0),
                umax_current=Column(Float, default=0),
                umin_current=Column(Float, default=0),
                ufbrb=Column(LargeBinary, nullable=True),
                ufrequency=Column(Float, default=0),
                uamplitude=Column(Float, default=0),
                uinitial_phase=Column(Float, default=0),

                vrms=Column(Float, default=0),
                vthd=Column(Float, default=0),
                vharmonics=Column(LargeBinary, default=0),
                vmax_current=Column(Float, default=0),
                vmin_current=Column(Float, default=0),
                vfbrb=Column(LargeBinary, nullable=True),
                vfrequency=Column(Float, default=0),
                vamplitude=Column(Float, default=0),
                vinitial_phase=Column(Float, default=0),

                wrms=Column(Float, default=0),
                wthd=Column(Float, default=0),
                wharmonics=Column(LargeBinary, default=0),
                wmax_current=Column(Float, default=0),
                wmin_current=Column(Float, default=0),
                wfbrb=Column(LargeBinary, nullable=True),
                wfrequency=Column(Float, default=0),
                wamplitude=Column(Float, default=0),
                winitial_phase=Column(Float, default=0),

                n_rms=Column(Float, default=0),
                p_rms=Column(Float, default=0),
                z_rms=Column(Float, default=0),
                imbalance=Column(Float, default=0),

                health_indicator=Column(Float, default=85),

                data_id=Column(BigInteger, ForeignKey('elec_data_{0}.id'.format(point_id)), unique=True),

                __table_args__=table_args
            ))
            cls._mapper[class_name] = ModelClass
        mapper = ModelClass
        return mapper


class VibData(object):
    _mapper = {}
    base_class_name = 'vib_data'

    @classmethod
    def model(cls, point_id: int, base: DeclarativeMeta = Base):
        class_name = cls.base_class_name + '_%d' % point_id
        ModelClass = cls._mapper.get(class_name, None)
        if ModelClass is None:
            ModelClass = type(class_name, (base,), dict(
                __module__=__name__,
                __name__=class_name,
                __tablename__=class_name,
                id=Column(BigInteger, primary_key=True),
                time=Column(DateTime, index=True),
                vib=Column(LargeBinary, nullable=False),

                __table_args__=table_args
            ))
            cls._mapper[class_name] = ModelClass
        mapper = ModelClass
        return mapper


class VibFeature(object):
    _mapper = {}
    base_class_name = 'vib_feature'

    @classmethod
    def model(cls, point_id: int, base: DeclarativeMeta = Base):
        class_name = cls.base_class_name + '_%d' % point_id
        ModelClass = cls._mapper.get(class_name, None)
        if ModelClass is None:
            ModelClass = type(class_name, (base,), dict(
                __module__=__name__,
                __name__=class_name,
                __tablename__=class_name,
                id=Column(BigInteger, primary_key=True),
                time=Column(DateTime, index=True),
                rms=Column(Float, default=0),
                max=Column(Float, default=0),
                p2p=Column(Float, default=0),
                avg=Column(Float, default=0),
                var=Column(Float, default=0),
                kurtosis=Column(Float, default=0),

                data_id=Column(BigInteger, ForeignKey('vib_data_{0}.id'.format(point_id)), unique=True),

                __table_args__=table_args
            ))
            cls._mapper[class_name] = ModelClass
        mapper = ModelClass
        return mapper


# mps = session.query(MeasurePoint).all()

def make_shard_base(index):
    session = session_make(meta_engine)
    mps = session.query(MeasurePoint).filter(MeasurePoint.station_id == index + 1).all()
    for mp in mps:
        if mp.type == 0:
            VibDataModel = VibData.model(point_id=mp.id_inner_station, base=Base)
            VibFeatureModel = VibFeature.model(point_id=mp.id_inner_station, base=Base)
        elif mp.type == 1:
            ElectricalDataModel = ElecData.model(point_id=mp.id_inner_station, base=Base)
            ElecFeatureModel = ElecFeature.model(point_id=mp.id_inner_station, base=Base)
    return copy.deepcopy(Base)


if __name__ == '__main__':

    bases = [make_shard_base(i) for i in range(3)]

    for index, base in enumerate(bases):
        base.metadata.drop_all(bind=station_engines[index])
        base.metadata.create_all(bind=station_engines[index])
