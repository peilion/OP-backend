from datetime import datetime

from pydantic import BaseModel
from model.base import SubSampledBinaryArray,SubSampledArray,SignalArray
from typing import List

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

class VibrationEnvelopeSchema(BaseModel):
    id: int
    time: datetime
    vib: SubSampledArray
    env_vib: SubSampledArray
    env_fft: SignalArray

class VibrationSTFTSchema(BaseModel):
    id: int
    time: datetime
    f: SignalArray
    t: SignalArray
    stft: List
    max:float

class VibrationMUSENSSchema(BaseModel):
    id: int
    time: datetime
    scale: List
    freq: SignalArray
    value: List
