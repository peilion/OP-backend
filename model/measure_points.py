from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MeasurePointSchema(BaseModel):
    id: Optional[int]
    name: str
    type: int
    md_time: Optional[datetime] = None
    sample_freq: Optional[int]
    sample_interval: Optional[int]
    sample_sensitive: Optional[float]
    statu: Optional[int]
    health_indicator: Optional[int]
    station_id: Optional[int]
    station_name: Optional[str]
    asset_id: Optional[int]
    asset_name: Optional[str]


class MeasurePointInputSchema(BaseModel):
    name: str
    type: int
    sample_freq: int
    sample_interval: int
    station_id: int
    asset_id: int
