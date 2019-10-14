# ! /usr/bin/python
# -*- coding: utf-8 -*-


import numpy as np
import scipy.stats as sts
from numpy import ndarray

import numba

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
    mag = mag[1:N / 2] * 2.00 / N
    return sts.kurtosis(mag)


def spectral_skw(a):
    N = a.shape[0]
    mag = np.abs(np.fft.fft(a))
    mag = mag[1:N / 2] * 2.00 / N
    return sts.skew(mag)


def spectral_pow(a):
    N = a.shape[0]
    mag = np.abs(np.fft.fft(a))
    mag = mag[1:N / 2] * 2.00 / N
    return np.mean(np.power(mag, 3))


def fftransform(Signal: str):
    # fft_size = int(Signal.shape[0])
    Signal = np.fromstring(Signal, dtype=np.float32)

    N = Signal.shape[0]
    spec = np.fft.fft(Signal)[0:int(N / 2)] / N  # FFT function from numpy
    spec[1:] = 2 * spec[1:]  # need to take the single-sided spectrum only
    spec = np.abs(spec)

    return {'spec': spec, 'vib': Signal}
