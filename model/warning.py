from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WarningLogSchema(BaseModel):
    id: int
    cr_time: datetime
    description : str
    severity : int
    asset_name :str

