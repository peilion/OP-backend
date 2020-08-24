import enum

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    func,
    Text,
    Binary,
    ForeignKey,
    SmallInteger,
    Float,
    Boolean,
    JSON,
    UniqueConstraint,
    Enum,
    String)
from sqlalchemy.orm import relationship

from db import Base, table_args


class FaultPatternEnum(enum.Enum):
    不平衡故障 = 1
    不对中故障 = 2
    A类松动 = 3
    B类松动 = 4
    滚动轴承故障 = 5
    喘振故障 = 6
    碰磨故障 = 7


class LogTypeEnum(enum.Enum):
    mset = 1
    diagnosis = 2
    vib = 3
    elec = 4


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_record"
    __table_args__ = table_args

    STATUS = {0: "awaiting", 1: "working", 2: "finished"}

    id = Column(Integer, primary_key=True)
    cr_time = Column(DateTime, nullable=True, default=func.now(), index=True)
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())

    description = Column(Text, nullable=False)
    asset_id = Column(Integer, ForeignKey("asset.id"))
    statu = Column(SmallInteger)

    asset = relationship("Asset", back_populates="maintlogs")


class WarningLog(Base):
    __tablename__ = "warning_log"
    __table_args__ = (
        UniqueConstraint("mp_id", "data_id", name="uix_mpid_dataid"),
        table_args,
    )
    SEVERITIES = {0: "轻微", 1: "较严重", 2: "严重"}

    id = Column(Integer, primary_key=True)
    cr_time = Column(DateTime, nullable=True, default=func.now(), index=True)
    description = Column(JSON, nullable=False)
    marks = Column(JSON, nullable=False)
    threshold_id = Column(Integer, ForeignKey("threshold.id"), index=True)
    severity = Column(SmallInteger, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    asset_id = Column(Integer, ForeignKey("asset.id"))
    mp_id = Column(Integer, ForeignKey("measure_point.id"))
    data_id = Column(Integer, index=True)
    ib_indicator = Column(Float, server_default="0")
    ma_indicator = Column(Float, server_default="0")
    bw_indicator = Column(Binary, server_default="")
    al_indicator = Column(Float, server_default="0")
    bl_indicator = Column(Float, server_default="0")
    rb_indicator = Column(Float, server_default="0")
    sg_indicator = Column(Float, server_default="0")
    env_kurtosis = Column(Float, server_default="0")
    vel_thd = Column(Float)

    asset = relationship("Asset", back_populates="warninglogs")


class MsetWarningLog(Base):
    __tablename__ = "mset_warning_log"
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    cr_time = Column(DateTime, nullable=True, default=func.now(), index=True)
    md_time = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())

    description = Column(Text, nullable=False)
    asset_id = Column(Integer, ForeignKey("asset.id"))
    reporter_id = Column(Integer, index=True)

    # asset = relationship("Asset", back_populates="MsetWarningLogs")


class MaintenanceSuggestion(Base):
    __tablename__ = "maintenance_suggestion"
    __table_args__ = table_args

    id = Column(Integer, primary_key=True)
    fault_pattern = Column(Enum(FaultPatternEnum), nullable=False)
    severity = Column(SmallInteger, nullable=False)
    suggestion = Column(Text, nullable=False)


class logs(Base):
    __tablename__ = "logs"
    __table_args__ = table_args
    id = Column(Integer, primary_key=True)
    type = Column(Enum(LogTypeEnum), nullable=False, index=True)
    time = Column(DateTime, nullable=True, index=True)
    asset_id = Column(Integer, ForeignKey("asset.id"))
    description = Column(String(256))
    mp_name = Column(String(64))
    detail = Column(JSON, nullable=False)
    md_code = Column(String(32))  # hashlib.md5(string.encode(encoding='UTF-8')).hexdigest()
    '''
        mset类型应包含如下字段：
            reporter_id     int        对应asset_hi_x 中的mset评估记录id
        diagnosis类型应包含如下字段：
            marks           jsonobj    标识线位置
            description     jsonobj    结构化的报警描述
            threshold_id    int        使用的阈值设定id
            severity        int        严重程度 {0: "轻微", 1: "较严重", 2: "严重"}
            mp_id           int        对应的测点id
            data_id         int        对应的设备数据id
            ib_indicator    float      不平衡故障指标
            ma_indicator    float      不对中故障指标
            bw_indicator    array      轴承故障指标数组
            al_indicator    float      a型松动故障指标
            bl_indicator    float      b型松动故障指标
            rb_indicator    float      转子碰磨故障指标
            sg_indicator    float      喘振故障指标
            env_kurtosis    float      包络峭度
            vel_thd         float      速度谱谐波畸变率
        vib类型应包含如下字段：
            rms             float      超标的均方根值
            severity        int        严重程度 {0: "轻微", 1: "较严重", 2: "严重"}
        elec类型应包含如下字段：
            brb             float      超标的转子断条能量值
            imbalance       float      超标的不平衡度
            thd             float      超标的谐波畸变率
            severity        int        严重程度 {0: "轻微", 1: "较严重", 2: "严重"}
    '''
