from sqlalchemy import (
    Column,
    Integer,
    SmallInteger,
    ForeignKey,
    Float,
    DateTime,
    func,
    BigInteger,
    JSON,
)
from sqlalchemy import String, Text
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import relationship

from db import Base, table_args


class Asset(Base):
    LEVELS = {0: "Unit", 1: "Equip", 2: "Component"}
    STATUS = {0: "Excellent", 1: "Good", 2: "Moderate", 3: "Poor", 4: "Offline"}
    MPCONFIGURATION = {1: "4振动", 2: "10振动加电流电压", 3: "8振动加电流电压"}
    TYPES = {
        0: "PumpUnit",
        1: "Pump",
        2: "Motor",
        3: "Rotor",
        4: "Stator",
        5: "Bearing",
    }  # should have the same name as the models been defined in .asset_info.py

    id = Column(Integer, primary_key=True)
    name = Column(String(64))  # 轴承命名规则 以N（非驱动端） 或D（驱动端） 开头
    sn = Column(String(128), unique=True)
    lr_time = Column(DateTime, nullable=True)
    cr_time = Column(DateTime, nullable=True, default=func.now())
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())
    st_time = Column(DateTime, nullable=False)
    asset_type = Column(SmallInteger, nullable=False)  # 值含义见 TYPES
    asset_level = Column(SmallInteger, nullable=False)  # 值含义见 LEVELS
    repairs = Column(SmallInteger, nullable=False)
    memo = Column(Text, nullable=True)
    health_indicator = Column(Float, default=85, nullable=True)
    statu = Column(SmallInteger, default=4)  # 值含义见 STATUS
    mp_configuration = Column(SmallInteger, nullable=True)

    parent_id = Column(Integer, ForeignKey("asset.id"), nullable=True)
    manufacturer_id = Column(Integer, ForeignKey("manufacturer.id"))
    station_id = Column(Integer, ForeignKey("station.id"))
    admin_id = Column(Integer, ForeignKey("user.id"), nullable=True)

    children = relationship("Asset", join_depth=2)
    manufacturer = relationship("Manufacturer", back_populates="assets")
    station = relationship("Station", back_populates="assets")
    admin = relationship("User", back_populates="assets")
    warninglogs = relationship("WarningLog", back_populates="asset")
    measure_points = relationship("MeasurePoint", back_populates="asset")
    maintlogs = relationship("MaintenanceRecord", back_populates="asset")

    __tablename__ = "asset"
    __table_args__ = table_args


class AssetHI(object):
    _mapper = {}
    base_class_name = "asset_hi"

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
                    health_indicator=Column(Float, default=85, nullable=True),
                    similarity=Column(Float, nullable=True),
                    threshold=Column(Float, nullable=True),
                    est=Column(JSON),
                    data_id=Column(Integer, index=True),
                    __table_args__=table_args,
                ),
            )
            cls._mapper[class_name] = ModelClass
        mapper = ModelClass
        return mapper
