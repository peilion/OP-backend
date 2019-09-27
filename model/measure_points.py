from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MeasurePointSchema(BaseModel):
    id: int
    name: str
    type: int
    md_time: Optional[datetime] = None
    staion_id: int
    station_name: str
    asset_id: int
    asset_name: str
    statu: int
