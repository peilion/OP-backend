from datetime import datetime

from pydantic import BaseModel

from model.base import SubSampledBinaryArray, SignalArray,SubSampledArray


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


class ElecEnvelopeSchema(BaseModel):
    id: int
    time: datetime

    uenv: SubSampledArray
    venv: SubSampledArray
    wenv: SubSampledArray

    uenv_fft: SignalArray
    venv_fft: SignalArray
    wenv_fft: SignalArray


class ElecDQSchema(BaseModel):
    id: int
    time: datetime
    component_d: SubSampledArray
    component_q: SubSampledArray