from pydantic import BaseModel


class ServerInfoSchema(BaseModel):
    table_volume: str
    disk_usage: float
    cpu_statu: float
    memory_statu: int
