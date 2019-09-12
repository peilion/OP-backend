from pydantic import BaseModel
from typing import List

class Token(BaseModel):
    roles: List[str]
    token: str
    introduction: str
    avatar: str
    name: str