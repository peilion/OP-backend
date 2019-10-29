from typing import Optional

from pydantic import BaseModel


class StationSchema(BaseModel):
    id: int
    name: str
    location: str
    latitude: float
    longitude: float


class BranchSchema(BaseModel):
    id: int
    name: str
    telephone: Optional[str]


class RegionSchema(BaseModel):
    id: int
    name: str
    telephone: Optional[str]
