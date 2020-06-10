from datetime import datetime
from typing import Optional

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
    measure_point_name: str
    data_id: int


class WarningAndMainteSchema(BaseModel):
    cr_time: datetime
    description: str
    t_name: str
    asset_name: Optional[str]
    severity: Optional[int]

    class Config:
        orm_mode = True
