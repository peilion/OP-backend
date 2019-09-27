from pydantic import BaseModel


class StationSchema(BaseModel):
    id: int
    name: str
    location: str

