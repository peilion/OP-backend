from typing import List

from pydantic import BaseModel


class Token(BaseModel):
    roles: List[str]
    token: str
    introduction: str
    avatar: str
    name: str
