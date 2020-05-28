from datetime import datetime

from pydantic import BaseModel

from model.base import SubSampledBinaryArray, SignalArray, SubSampledArray, BinaryArray


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


class ElecSymSchema(BaseModel):
    id: int
    time: datetime
    A_pos_real: SubSampledArray
    B_pos_real: SubSampledArray
    C_pos_real: SubSampledArray
    A_neg_real: SubSampledArray
    B_neg_real: SubSampledArray
    C_neg_real: SubSampledArray
    zero_real: SubSampledArray
    A_pos_img: SubSampledArray
    B_pos_img: SubSampledArray
    C_pos_img: SubSampledArray
    A_neg_img: SubSampledArray
    B_neg_img: SubSampledArray
    C_neg_img: SubSampledArray
    zero_img: SubSampledArray


class ElecHarmonicSchema(BaseModel):
    id: int
    time: datetime
    uharmonics: BinaryArray
    vharmonics: BinaryArray
    wharmonics: BinaryArray
