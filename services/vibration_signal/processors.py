from services.vibration_signal.transformers import *
from utils.serializer import binary_deserializer


def fast_fournier_transform(signal: str):
    signal = binary_deserializer(signal)
    res = get_spectrum(data=signal)
    return res


def hilbert(data: str):
    signal = binary_deserializer(data)
    res = get_hilbert_spectrum(data=signal)
    return res


def short_time_fournier_transform(data: str):
    signal = binary_deserializer(data)
    res = get_short_time_fournier_transform(data=signal)
    return res


def multi_scale_envelope_spectrum(data: str):
    signal = binary_deserializer(data)
    res = get_multi_scale_envelope_spectrum(data=signal, n_Fs=10000, n_Ssta=1.0, n_Send=8.0, n_Sint=0.2)
    return res


def welch_spectrum_estimation(data: str):
    signal = binary_deserializer(data)
    res = get_welch_spectrum_estimation(data=signal)
    return res


def acceleration_to_velocity(data: str):
    signal = binary_deserializer(data)
    res = get_acceleration_to_velocity(data=signal)
    return res


def empirical_mode_decomposition(data: str):
    signal = binary_deserializer(data)
    res = get_empirical_mode_decomposition(data=signal)
    return res
