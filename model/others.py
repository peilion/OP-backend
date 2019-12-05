from typing import List

from pydantic import BaseModel


class TokenSchema(BaseModel):
    roles: List[str]
    token: str
    introduction: str
    avatar: str
    name: str


class ServerInfoSchema(BaseModel):
    table_volume: str
    disk_usage: float
    cpu_statu: float
    memory_statu: int


class MsgSchema(BaseModel):
    msg: str
