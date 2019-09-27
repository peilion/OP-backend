from datetime import datetime

from pydantic import BaseModel
from model.base import SubSampledBinaryArray


class VibrationSignalSchema(BaseModel):
    id: int
    time: datetime
    vib: SubSampledBinaryArray

class VibrationSignalListSchema(BaseModel):
    id: int
    time: datetime