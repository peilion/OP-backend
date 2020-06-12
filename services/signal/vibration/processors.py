import numpy as np

from services.diagnosis.base import MeasurePoint
from services.signal.vibration.vibration_class import VibrationSignal
from utils.serializer import binary_deserializer


def fast_fournier_transform(signal: str) -> dict:
    signal = VibrationSignal(
        data=binary_deserializer(signal), fs=10000, compute_axis=False
    )
    signal.compute_spectrum(compute_axis=False)
    return {"spec": signal.spec, "vib": signal.data}


def hilbert(data: str) -> dict:
    signal = VibrationSignal(
        data=binary_deserializer(data), fs=10000, compute_axis=False
    )
    env = signal.to_envelope()
    env.compute_spectrum(compute_axis=False)
    return {"vib": signal.data, "env_vib": env.data, "env_fft": env.spec}


def short_time_fournier_transform(data: str) -> dict:
    signal = VibrationSignal(
        data=binary_deserializer(data), fs=10000, compute_axis=False
    )
    res = signal.get_short_time_fournier_transform()
    return res


def multi_scale_envelope_spectrum(data: str) -> dict:
    signal = VibrationSignal(
        data=binary_deserializer(data), fs=10000, compute_axis=False
    )
    res = signal.get_multi_scale_envelope_spectrum(n_Ssta=1.0, n_Send=8.0, n_Sint=0.2)
    return res


def welch_spectrum_estimation(data: str) -> dict:
    signal = VibrationSignal(
        data=binary_deserializer(data), fs=10000, compute_axis=False
    )
    res = signal.get_welch_spectrum_estimation()
    return {"vib": signal.data, **res}


def acceleration_to_velocity(data: str) -> dict:
    acc = VibrationSignal(data=binary_deserializer(data), fs=10000)
    vel = acc.to_velocity()
    acc.compute_spectrum(compute_axis=False)
    vel.compute_spectrum(compute_axis=False)
    return {
        "vel": vel.data,
        "acc": acc.data,
        "acc_spec": acc.spec,
        "vel_spec": vel.spec,
    }


def empirical_mode_decomposition(data: str) -> dict:
    signal = VibrationSignal(
        data=binary_deserializer(data), fs=10000, compute_axis=False
    )
    res = signal.get_empirical_mode_decomposition()
    return res
