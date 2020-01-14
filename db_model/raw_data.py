from sqlalchemy import Column, BigInteger, DateTime, LargeBinary, Integer, Float
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import relationship

from db import Base, table_args


class ElecData(object):
    _mapper = {}
    base_class_name = "elec_data"

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
                    ucur=Column(LargeBinary, nullable=False),
                    vcur=Column(LargeBinary, nullable=False),
                    wcur=Column(LargeBinary, nullable=False),
                    uvolt=Column(LargeBinary, nullable=False),
                    vvolt=Column(LargeBinary, nullable=False),
                    wvolt=Column(LargeBinary, nullable=False),
                    __table_args__=table_args,
                ),
            )
            cls._mapper[class_name] = ModelClass
        mapper = ModelClass
        return mapper


class VibData(object):
    _mapper = {}
    base_class_name = "vib_data"

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
                    ima=Column(LargeBinary, nullable=False),
                    __table_args__=table_args,
                ),
            )
            cls._mapper[class_name] = ModelClass
        mapper = ModelClass
        return mapper
