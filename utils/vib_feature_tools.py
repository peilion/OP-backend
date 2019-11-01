# ! /usr/bin/python
# -*- coding: utf-8 -*-


import numpy as np
import pywt
import scipy.stats as sts
from scipy import signal
from scipy.integrate import cumtrapz


def rms_fea(a):
    return np.sqrt(np.mean(np.square(a)))


def var_fea(a):
    return np.var(a)


def max_fea(a):
    return np.max(a)


def pp_fea(a):
    return np.max(a) - np.min(a)


def skew_fea(a):
    return sts.skew(a)


def kurt_fea(a):
    return sts.kurtosis(a)


def spectral_kurt(a):
    N = a.shape[0]
    mag = np.abs(np.fft.fft(a))
    mag = mag[1 : N / 2] * 2.00 / N
    return sts.kurtosis(mag)


def spectral_skw(a):
    N = a.shape[0]
    mag = np.abs(np.fft.fft(a))
    mag = mag[1 : N / 2] * 2.00 / N
    return sts.skew(mag)


def spectral_pow(a):
    N = a.shape[0]
    mag = np.abs(np.fft.fft(a))
    mag = mag[1 : N / 2] * 2.00 / N
    return np.mean(np.power(mag, 3))


def fftransform(Signal: str):
    # fft_size = int(Signal.shape[0])
    Signal = np.fromstring(Signal, dtype=np.float32)

    N = Signal.shape[0]
    spec = np.fft.fft(Signal)[0 : int(N / 2)] / N  # FFT function from numpy
    spec[1:] = 2 * spec[1:]  # need to take the single-sided spectrum only
    spec = np.abs(spec)

    return {"spec": spec, "vib": Signal}


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


def stft(data: str):
    Signal = np.fromstring(data, dtype=np.float32)
    Signal = signal.detrend(Signal, type="constant")
    f, t, Zxx = signal.stft(Signal, 10240, nperseg=256)
    Zxx = np.abs(Zxx)
    stft = []
    for i in range(Zxx.shape[0]):
        for j in range(Zxx.shape[1]):
            stft.append([j, i, float(Zxx[i, j])])
    return {"t": t, "f": f, "stft": stft, "max": float(Zxx.max())}


def musens(S: str, n_Fs: int, n_Ssta: float, n_Send: float, n_Sint: float):
    S = np.fromstring(S, dtype=np.float32)
    nLen = len(S)

    i = n_Ssta
    Sscal = []
    while i <= n_Send:
        Sscal.append(i)
        i = i + n_Sint
    Sscal.append(i)
    Sscal = np.array(Sscal).round(3).tolist()  # stupid
    C = pywt.cwt(S, Sscal, "cmor1-0.5")
    C = np.abs(C[0])

    z = []
    for j in range(len(Sscal)):
        tmp1 = C[j, :]
        tmp2 = np.fft.fft(tmp1)
        tmp2 = np.abs(tmp2 * np.conj(tmp2)) / len(tmp2)
        z.append(tmp2)

    z = np.array(z)
    z[:, 0:1] = 0

    FreqExt = np.round(
        (n_Fs * np.linspace(0, nLen / 2, int(nLen / 2)) / nLen), decimals=3
    ).tolist()
    Z = z[:, : len(FreqExt)]
    value = []
    for sIndex, scale in enumerate(Sscal):
        for fIndex, freq in enumerate(FreqExt):
            value.append([sIndex, fIndex, round(float(Z[sIndex][fIndex]), 3)])
    return {"scale": Sscal, "freq": FreqExt, "value": value}


def welch(data: str):
    Signal = np.fromstring(data, dtype=np.float32)
    Signal = signal.detrend(Signal, type="constant")
    freq, spec = signal.welch(Signal, 10000, scaling="spectrum")
    return {"freq": freq, "spec": spec}


def toVelocity(raw_data: str):
    acc = np.fromstring(raw_data, dtype=np.float32)
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
