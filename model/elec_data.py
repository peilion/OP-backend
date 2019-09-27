from datetime import datetime

from pydantic import BaseModel
from model.base import SubSampledBinaryArray


class ElecSignalSchema(BaseModel):
    id: int
    time: datetime
    ucur: SubSampledBinaryArray
    vcur: SubSampledBinaryArray
    wcur: SubSampledBinaryArray

class ElecSignalListSchema(BaseModel):
    id: int
    time: datetime