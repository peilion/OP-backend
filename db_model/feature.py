from sqlalchemy import (
    Column,
    BigInteger,
    DateTime,
    Float,
    LargeBinary,
    ForeignKey,
    Integer,
)
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import relationship

from db import Base, table_args


class ElecFeature(object):
    _mapper = {}
    base_class_name = "elec_feature"

    @classmethod
    def model(cls, station_id: int, inner_id: int, base: DeclarativeMeta = Base):
        class_name = cls.base_class_name + "_{0}_{1}".format(station_id, inner_id)
        ModelClass = cls._mapper.get(class_name, None)
        if ModelClass is None:
            ModelClass = type(
                class_name,
                (base,),
                dict(
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
                    data_id=Column(
                        BigInteger,
                        ForeignKey("elec_data_{0}_{1}.id".format(station_id, inner_id)),
                        unique=True,
                    ),
                    __table_args__=table_args,
                ),
            )
            cls._mapper[class_name] = ModelClass
        mapper = ModelClass
        return mapper


class VibFeature(object):
    _mapper = {}
    base_class_name = "vib_feature"

    @classmethod
    def model(cls, station_id: int, inner_id: int, base: DeclarativeMeta = Base):
        class_name = cls.base_class_name + "_{0}_{1}".format(station_id, inner_id)
        ModelClass = cls._mapper.get(class_name, None)
        if ModelClass is None:
            ModelClass = type(
                class_name,
                (base,),
                dict(
                    __module__=__name__,
                    __name__=class_name,
                    __tablename__=class_name,
                    id=Column(Integer, primary_key=True),
                    time=Column(DateTime, index=True),
                    rms=Column(Float, default=0),
                    max=Column(Float, default=0),
                    p2p=Column(Float, default=0),
                    avg=Column(Float, default=0),
                    var=Column(Float, default=0),
                    kurtosis=Column(Float, default=0),
                    fr=Column(Float, default=0),
                    fr_amp=Column(Float),
                    thd=Column(Float, default=0),
                    bpfi=Column(Float, default=0),
                    bpfo=Column(Float, default=0),
                    bsf=Column(Float, default=0),
                    ftf=Column(Float, default=0),
                    sideband=Column(Float, default=0),
                    health_indicator=Column(Float, default=85),
                    data_id=Column(
                        Integer,
                        ForeignKey("vib_data_{0}_{1}.id".format(station_id, inner_id)),
                        unique=True,
                    ),
                    __table_args__=table_args,
                ),
            )
            cls._mapper[class_name] = ModelClass
        mapper = ModelClass
        return mapper
