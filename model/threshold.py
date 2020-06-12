from datetime import datetime
from typing import Optional, List
from .base import JsonString
from pydantic import BaseModel, validator


class ThresholdSchema(BaseModel):
    id: int
    mp_pattern: str
    diag_threshold: JsonString
    md_time: datetime


class MotorDrivenEndPostSchema(BaseModel):
    thd: float
    ALoose: List[float]
    BLoose: List[float]
    Rubbing: List[float]
    kurtosis: float
    Unbalance: List[float]
    RollBearing: List[float]
    Misalignment: List[float]
    harmonic_threshold: List[float]
    subharmonic_threshold: List[float]

    @validator("ALoose")
    def ALoose_must_have_a_size_of_three(cls, v):
        if len(v) != 3:
            raise ValueError("must have a size of 3")
        return v

    @validator("BLoose")
    def BLoose_must_have_a_size_of_three(cls, v):
        if len(v) != 3:
            raise ValueError("must have a size of 3")
        return v

    @validator("Rubbing")
    def Rubbing_must_have_a_size_of_three(cls, v):
        if len(v) != 3:
            raise ValueError("must have a size of 3")
        return v

    @validator("Unbalance")
    def Unbalance_must_have_a_size_of_three(cls, v):
        if len(v) != 3:
            raise ValueError("must have a size of 3")
        return v

    @validator("RollBearing")
    def RollBearing_must_have_a_size_of_three(cls, v):
        if len(v) != 3:
            raise ValueError("must have a size of 3")
        return v

    @validator("Misalignment")
    def Misalignment_must_have_a_size_of_three(cls, v):
        if len(v) != 3:
            raise ValueError("must have a size of 3")
        return v

    @validator("harmonic_threshold")
    def harmonic_threshold_must_have_a_size_of_11(cls, v):
        if len(v) != 11:
            raise ValueError("must have a size of 11")
        return v

    @validator("subharmonic_threshold")
    def sub_harmonic_threshold_must_have_a_size_of_5(cls, v):
        if len(v) != 5:
            raise ValueError("must have a size of 5")
        return v
