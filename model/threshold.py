from datetime import datetime
from typing import Optional
from .base import JsonString
from pydantic import BaseModel


class ThresholdSchema(BaseModel):
    id: int
    mp_pattern: str
    diag_threshold: JsonString
    md_time: datetime
