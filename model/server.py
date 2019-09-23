from pydantic import BaseModel


class ServerInfoSchema(BaseModel):
    table_volume: str
    table_count: int
    cpu_statu: float
    memory_statu: int
