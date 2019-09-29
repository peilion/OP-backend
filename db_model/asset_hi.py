from sqlalchemy import Column, BigInteger, DateTime, Float
from sqlalchemy.ext.declarative.api import DeclarativeMeta

from db import table_args, Base


class AssetHI(object):
    _mapper = {}
    base_class_name = 'asset_hi'

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
                health_indicator=Column(Float, default=85, nullable=True),

            __table_args__=table_args
            ))
            cls._mapper[class_name] = ModelClass
        mapper = ModelClass
        return mapper
