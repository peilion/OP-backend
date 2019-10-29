from datetime import datetime

from pydantic import BaseModel

from model.base import SubSampledBinaryArray, SignalArray


class ElecSignalSchema(BaseModel):
    id: int
    time: datetime
    ucur: SubSampledBinaryArray
    vcur: SubSampledBinaryArray
    wcur: SubSampledBinaryArray
    ufft: SignalArray
    vfft: SignalArray
    wfft: SignalArray

class ElecSignalListSchema(BaseModel):
    id: int
    time: datetime