from datetime import datetime
from typing import Optional, List
from .base import SignalArray, JsonString, BinaryArrayMax, SignalArrayWithoutRound
from pydantic import BaseModel


class MaintenanceRecordSchema(BaseModel):
    id: int
    cr_time: datetime
    md_time: Optional[datetime]
    description: str
    asset_name: str
    statu: int


class WarningLogSchema(BaseModel):
    id: int
    cr_time: datetime
    description: str
    severity: int
    asset_name: str
    asset_id: int
    is_read: bool
    measure_point_name: Optional[str]
    data_id: int
    mp_id: int


class WarningDetailSchema(BaseModel):
    id: int
    cr_time: datetime
    description: JsonString
    marks: JsonString
    severity: int
    data_id: int
    ib_indicator: Optional[float]
    ma_indicator: Optional[float]
    bw_indicator: BinaryArrayMax
    al_indicator: Optional[float]
    bl_indicator: Optional[float]
    rb_indicator: Optional[float]
    sg_indicator: Optional[float]
    env_kurtosis: Optional[float]
    vel_thd: Optional[float]
    thres: JsonString
    suggestions: List[str]


class WarningData(BaseModel):
    spec: SignalArrayWithoutRound
    freq: SignalArrayWithoutRound


class WarningAndMainteSchema(BaseModel):
    cr_time: datetime
    description: str
    t_name: str
    asset_name: Optional[str]
    severity: Optional[int]

    class Config:
        orm_mode = True


class WarningTableSchema(BaseModel):
    description: str
    id: int
    asset_id: int
    mp_id: Optional[int]
    cr_time: datetime
    severity: int
    is_read: bool
    mp_name: Optional[str]
    data_id: int
    asset_name: Optional[str]
    t_name: str
    mp_configuration: int
