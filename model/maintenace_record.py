from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MaintenanceRecord(BaseModel):
    id: int
    cr_time: datetime
    md_time: Optional[datetime]
    description: str
    asset_name: str
    statu: int
