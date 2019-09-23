from pydantic import BaseModel
from typing import Optional

class Station(BaseModel):
    id: int
    name: str
    location: str

