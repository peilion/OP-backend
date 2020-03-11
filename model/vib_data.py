from datetime import datetime
from typing import List

from pydantic import BaseModel

from model.base import SubSampledBinaryArray, SubSampledArray, SignalArray


class VibrationSignalSchema(BaseModel):
    id: int
    time: datetime
    vib: SubSampledArray
    spec: SignalArray


class VibrationSignalByidSchema(BaseModel):
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
    max: float


class VibrationWelchSchema(BaseModel):
    id: int
    time: datetime
    spec: SignalArray
    freq: SignalArray
    vib: SubSampledBinaryArray


class VibrationCumtrapzSchema(BaseModel):
    id: int
    time: datetime
    vel: SubSampledArray
    acc: SubSampledArray
    vel_spec: SignalArray
    acc_spec: SignalArray


class VibrationEMDSchema(BaseModel):
    id: int
    time: datetime
    emd: List
