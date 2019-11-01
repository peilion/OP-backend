from sqlalchemy import Column, BigInteger, ForeignKey, Float, DateTime, VARBINARY
from sqlalchemy.ext.declarative.api import DeclarativeMeta

from db import table_args, Base


class VibFeature(object):
    _mapper = {}
    base_class_name = "vib_feature"

    @classmethod
    def model(cls, point_id: int, base: DeclarativeMeta = Base):
        class_name = cls.base_class_name + "_%d" % point_id
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
                    rms=Column(Float, default=0),
                    max=Column(Float, default=0),
                    p2p=Column(Float, default=0),
                    avg=Column(Float, default=0),
                    var=Column(Float, default=0),
                    kurtosis=Column(Float, default=0),
                    fr=Column(Float, default=0),
                    fr_amp=Column(VARBINARY),
                    thd=Column(Float, default=0),
                    bpfi=Column(Float, default=0),
                    bpfo=Column(Float, default=0),
                    bsf=Column(Float, default=0),
                    ftf=Column(Float, default=0),
                    sideband=Column(Float, default=0),
                    health_indicator=Column(Float, default=85),
                    data_id=Column(
                        BigInteger,
                        ForeignKey("vib_data_{0}.id".format(point_id)),
                        unique=True,
                    ),
                    __table_args__=table_args,
                ),
            )
            cls._mapper[class_name] = ModelClass
        mapper = ModelClass
        return mapper
