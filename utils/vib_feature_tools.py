# ! /usr/bin/python
# -*- coding: utf-8 -*-


import numpy as np
import pywt
import scipy.stats as sts
from scipy import signal
from scipy.integrate import cumtrapz


def rms_fea(signal):
    return np.sqrt(np.mean(np.square(signal)))


def var_fea(signal):
    return np.var(signal)


def max_fea(signal):
    return np.max(signal)


def pp_fea(signal):
    return np.max(signal) - np.min(signal)


def skew_fea(signal):
    return sts.skew(signal)


def kurt_fea(signal):
    return sts.kurtosis(signal)


def spectral_kurt(signal):
    N = signal.shape[0]
    mag = np.abs(np.fft.fft(signal))
    mag = mag[1 : N / 2] * 2.00 / N
    return sts.kurtosis(mag)


def spectral_skw(signal):
    N = signal.shape[0]
    mag = np.abs(np.fft.fft(signal))
    mag = mag[1 : N / 2] * 2.00 / N
    return sts.skew(mag)


def spectral_pow(signal):
    N = signal.shape[0]
    mag = np.abs(np.fft.fft(signal))
    mag = mag[1 : N / 2] * 2.00 / N
    return np.mean(np.power(mag, 3))


def fast_fournier_transform(signal: str):
    # fft_size = int(Signal.shape[0])
    signal = np.fromstring(signal, dtype=np.float32)

    N = signal.shape[0]
    spec = np.fft.fft(signal)[0 : int(N / 2)] / N  # FFT function from numpy
    spec[1:] = 2 * spec[1:]  # need to take the single-sided spectrum only
    spec = np.abs(spec)

    return {"spec": spec, "vib": signal}


def hilbert(data: str):
    data = np.fromstring(data, dtype=np.float32)
    start = int(data.shape[0] * 0.1)
    end = int(data.shape[0] * 0.9)
    data_envelope = np.abs(signal.hilbert(data)[start:end])

    N = data_envelope.shape[0]
    data_envelope_fft = (
        np.fft.fft(signal.detrend(data_envelope, type="constant"))[0 : int(N / 2)] / N
    )  # FFT function from numpy
    data_envelope_fft[1:] = (
        2 * data_envelope_fft[1:]
    )  # need to take the single-sided spectrum only
    data_envelope_fft = np.abs(data_envelope_fft)

    data = data[start:end]

    return {"vib": data, "env_vib": data_envelope, "env_fft": data_envelope_fft}


def short_time_fournier_transform(data: str):
    data = np.fromstring(data, dtype=np.float32)
    data = signal.detrend(data, type="constant")
    f, t, z = signal.stft(data, 10240, nperseg=256)
    z = np.abs(z)
    stft = []
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            stft.append([j, i, float(z[i, j])])
    return {"t": t, "f": f, "stft": stft, "max": float(z.max())}


def multi_scale_envelope_spectrum(data: str, n_Fs: int, n_Ssta: float, n_Send: float, n_Sint: float):
    data = np.fromstring(data, dtype=np.float32)
    length = len(data)

    i = n_Ssta
    scal = []
    while i <= n_Send:
        scal.append(i)
        i = i + n_Sint
    scal.append(i)
    scal = np.array(scal).round(3).tolist()  # stupid
    coef = pywt.cwt(data, scal, "cmor1-0.5")
    coef = np.abs(coef[0])

    z = []
    for j in range(len(scal)):
        tmp1 = coef[j, :]
        tmp2 = np.fft.fft(tmp1)
        tmp2 = np.abs(tmp2 * np.conj(tmp2)) / len(tmp2)
        z.append(tmp2)

    z = np.array(z)
    z[:, 0:1] = 0

    FreqExt = np.round(
        (n_Fs * np.linspace(0, length / 2, int(length / 2)) / length), decimals=3
    ).tolist()
    z = z[:, : len(FreqExt)]
    value = []
    for sIndex, scale in enumerate(scal):
        for fIndex, freq in enumerate(FreqExt):
            value.append([sIndex, fIndex, round(float(z[sIndex][fIndex]), 3)])
    return {"scale": scal, "freq": FreqExt, "value": value}


def welch_spectrum_estimation(data: str):
    data = np.fromstring(data, dtype=np.float32)
    data = signal.detrend(data, type="constant")
    freq, spec = signal.welch(data, 10000, scaling="spectrum")
    return {"freq": freq, "spec": spec}


def acceleration_to_velocity(data: str):
    acc = np.fromstring(data, dtype=np.float32)
    acc = signal.detrend(acc, type="linear")
    time_vector = np.linspace(0.0, len(acc) / 10000, len(acc))
    vel = cumtrapz(acc, time_vector)

    x = np.arange(len(vel))
    fit = np.polyval(np.polyfit(x, vel, deg=10), x)
    vel -= fit
    vel = signal.detrend(vel, type="linear")

    N = acc.shape[0]
    acc_spec = np.fft.fft(acc)[0 : int(N / 2)] / N  # FFT function from numpy
    acc_spec[1:] = 2 * acc_spec[1:]  # need to take the single-sided spectrum only
    acc_spec = np.abs(acc_spec)

    N = vel.shape[0]
    vel_spec = np.fft.fft(vel)[0 : int(N / 2)] / N  # FFT function from numpy
    vel_spec[1:] = 2 * vel_spec[1:]  # need to take the single-sided spectrum only
    vel_spec = np.abs(vel_spec)

    return {"vel": vel, "acc": acc, "acc_spec": acc_spec, "vel_spec": vel_spec}
