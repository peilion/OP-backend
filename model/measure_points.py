from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MeasurePointSchema(BaseModel):
    id: int
    name: str
    type: int
    md_time: Optional[datetime] = None
    sample_freq: Optional[int]
    sample_interval: Optional[int]
    statu: Optional[int]