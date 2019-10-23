from datetime import datetime

from pydantic import BaseModel


class WarningLogSchema(BaseModel):
    id: int
    cr_time: datetime
    description : str
    severity : int
    asset_name :str
    is_read : bool

class WarningAndMainteSchema(BaseModel):
    cr_time:datetime
    description: str
    t_name: str
    class Config:
        orm_mode = True