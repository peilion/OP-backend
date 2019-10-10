from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class MaintenanceRecord(BaseModel):
    id: int
    cr_time: datetime
    md_time: Optional[datetime]
    description: str
    asset_name: str
    statu: int
