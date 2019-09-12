from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import IntEnum


class LevelEnum(IntEnum):
    unit = 0
    equip = 1
    component = 2


class StatuEnum(IntEnum):
    excellent = 0
    good = 1
    moderate = 2
    poor = 3
    offline = 4


class StationEnum(IntEnum):
    hhht = 0
    etkq = 1
    bt = 2


class Asset(BaseModel):
    id: int
    name: str
    sn: str
    lr_time: Optional[datetime] = None
    cr_time: Optional[datetime] = None
    md_time: Optional[datetime] = None
    asset_level: int
    memo: Optional[str] = None
    health_indicator: float
    statu: int
    parent_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    station_id: int
    admin_id: int
    station_name: Optional[str] = None

    # class Config:
    #     orm_mode = True
