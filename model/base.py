import numpy as np
from numpy import ndarray
import orjson
from core.config import TIME_DOMAIN_SUB_SAMPLED_RATIO, TIME_DOMAIN_DECIMAL


class SubSampledBinaryArray(list):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        raw = np.fromstring(v, dtype=np.float32)
        axis = np.linspace(
            0, raw.size, int(raw.size / TIME_DOMAIN_SUB_SAMPLED_RATIO), endpoint=False
        )
        return [
            round(float(item), TIME_DOMAIN_DECIMAL)
            for item in np.take(raw, axis.astype(np.int))
        ]


class BinaryArray(list):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        raw = np.fromstring(v, dtype=np.float32)
        return [round(float(item), TIME_DOMAIN_DECIMAL) for item in raw]


class BinaryArrayMax(list):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        raw = np.fromstring(v, dtype=np.float32)
        return float(raw.max())


class SubSampledArray(list):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: ndarray):
        axis = np.linspace(
            0, v.size, int(v.size / TIME_DOMAIN_SUB_SAMPLED_RATIO), endpoint=False
        )
        return [
            round(float(item), TIME_DOMAIN_DECIMAL)
            for item in np.take(v, axis.astype(np.int))
        ]


class SignalArray(list):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: ndarray):
        return [round(float(item), TIME_DOMAIN_DECIMAL) for item in v]


class SignalArrayWithoutRound(list):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: ndarray):
        return [float(item) for item in v]


class JsonString(list):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str):
        return orjson.loads(v)
