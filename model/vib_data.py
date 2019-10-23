from datetime import datetime

from pydantic import BaseModel
from model.base import SubSampledBinaryArray,SubSampledArray,SignalArray


class VibrationSignalSchema(BaseModel):
    id: int
    time: datetime
    vib: SubSampledArray
    spec: SignalArray

class VibrationSignalSchemaByid(BaseModel):
    id: int
    time: datetime
    vib: SubSampledBinaryArray

class VibrationSignalListSchema(BaseModel):
    id: int
    time: datetime