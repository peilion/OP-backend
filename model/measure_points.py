from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MeasurePointSchema(BaseModel):
    id: int
    name: str
    type: int
    md_time: Optional[datetime] = None
    staion_id: Optional[int]
    station_name: Optional[str]
    asset_id: Optional[int]
    asset_name: Optional[str]
    statu: Optional[int]
