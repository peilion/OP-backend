from datetime import datetime

from pydantic import BaseModel
from model.base import SubSampledBinaryArray,SignalArray


class ElecSignalSchema(BaseModel):
    id: int
    time: datetime
    ucur: SignalArray
    vcur: SignalArray
    wcur: SignalArray
    ufft: SignalArray
    vfft: SignalArray
    wfft: SignalArray

class ElecSignalListSchema(BaseModel):
    id: int
    time: datetime