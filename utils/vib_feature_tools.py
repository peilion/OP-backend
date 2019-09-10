# ! /usr/bin/python
# -*- coding: utf-8 -*-


import numpy as np
import scipy.stats as sts


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
