import numpy as np
import pywt
from numpy import ndarray
from scipy import signal
from scipy.integrate import cumtrapz

from services.vibration_signal.thrid_party_lib.emd import EMD


def get_spectrum(data: ndarray) -> dict:
    # fft_size = int(Signal.shape[0])

    N = data.shape[0]
    spec = np.fft.fft(data)[0: int(N / 2)] / N  # FFT function from numpy
    spec[1:] = 2 * spec[1:]  # need to take the single-sided spectrum only
    spec = np.abs(spec)

    return {"spec": spec, "vib": data}


def get_hilbert_spectrum(data: ndarray) -> dict:
    start = int(data.shape[0] * 0.1)
    end = int(data.shape[0] * 0.9)
    data_envelope = np.abs(signal.hilbert(data)[start:end])

    N = data_envelope.shape[0]
    data_envelope_fft = (
            np.fft.fft(signal.detrend(data_envelope, type="constant"))[0: int(N / 2)] / N
    )  # FFT function from numpy
    data_envelope_fft[1:] = (
            2 * data_envelope_fft[1:]
    )  # need to take the single-sided spectrum only
    data_envelope_fft = np.abs(data_envelope_fft)

    data = data[start:end]

    return {"vib": data,
            "env_vib": data_envelope,
            "env_fft": data_envelope_fft}


def get_short_time_fournier_transform(data: ndarray) -> dict:
    f, t, z = signal.stft(data, 10240, nperseg=256)
    z = np.abs(z)
    stft = []
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            stft.append([j, i, float(z[i, j])])
    return {"t": t, "f": f, "stft": stft, "max": float(z.max())}


def get_multi_scale_envelope_spectrum(data: ndarray, n_Fs: int, n_Ssta: float, n_Send: float, n_Sint: float) -> dict:
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


def get_welch_spectrum_estimation(data: ndarray) -> dict:
    freq, spec = signal.welch(data, 10000, scaling="spectrum")
    return {"freq": freq, "spec": spec}


def get_acceleration_to_velocity(data: ndarray) -> dict:
    acc = signal.detrend(data, type="linear")
    time_vector = np.linspace(0.0, len(acc) / 10000, len(acc))
    vel = cumtrapz(acc, time_vector)

    x = np.arange(len(vel))
    fit = np.polyval(np.polyfit(x, vel, deg=10), x)
    vel -= fit
    vel = signal.detrend(vel, type="linear")

    N = acc.shape[0]
    acc_spec = np.fft.fft(acc)[0: int(N / 2)] / N  # FFT function from numpy
    acc_spec[1:] = 2 * acc_spec[1:]  # need to take the single-sided spectrum only
    acc_spec = np.abs(acc_spec)

    N = vel.shape[0]
    vel_spec = np.fft.fft(vel)[0: int(N / 2)] / N  # FFT function from numpy
    vel_spec[1:] = 2 * vel_spec[1:]  # need to take the single-sided spectrum only
    vel_spec = np.abs(vel_spec)

    return {"vel": vel, "acc": acc, "acc_spec": acc_spec, "vel_spec": vel_spec}


def get_empirical_mode_decomposition(data: ndarray) -> dict:
    decomposer = EMD(data)
    IMFs = decomposer.decompose()
    return {'emd': IMFs.round(3).tolist()}
