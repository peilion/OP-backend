from datetime import datetime

from pydantic import BaseModel
from model.base import SubSampledBinaryArray,SubSampledArray,SignalArray


class VibrationSignalSchema(BaseModel):
    id: int
    time: datetime
    vib: SubSampledArray
    spec: SignalArray

class VibrationSignalListSchema(BaseModel):
    id: int
    time: datetime