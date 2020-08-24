import numpy as np
from scipy import signal, optimize


def cal_samples(phaseAOmega, phaseBOmega, phaseCOmega, end_time):
    """
    Calculate the number of samples needed.
    """
    max_omega = max(abs(phaseAOmega), abs(phaseBOmega), abs(phaseCOmega))
    max_freq = max_omega / (2 * np.pi)
    samples = (max_freq ** 2) * 6 * end_time
    return samples


def make_phase(mag, omega, phi, samples, end_time):
    """
    Create the phase signal in complex form.
    """

    array_time = np.linspace(0, end_time, samples)

    x = omega * array_time + phi

    return to_complex(mag, x), array_time


def parameter_estimation(wave, sampling_rate, initailization):
    fitfunc = lambda p, x: p[0] * np.sin(2 * np.pi * p[1] * x + p[2])  # Target function
    errfunc = lambda p, x, y: fitfunc(p, x) - y  # Distance to the target function
    size = int(wave.shape[0])
    Tx = np.linspace(0, size / sampling_rate, size)
    p1, success = optimize.leastsq(errfunc, initailization[:], args=(Tx, wave))
    return p1


def cal_symm(a, b, c):
    # 120 degree rotator
    ALPHA = np.exp(1j * 2 / 3 * np.pi)

    # Positive sequence
    a_pos = 1 / 3 * (a + b * ALPHA + c * (ALPHA ** 2))

    b_pos = 1 / 3 * (a * (ALPHA ** 2) + b + c * ALPHA)

    c_pos = 1 / 3 * (a * ALPHA + b * (ALPHA ** 2) + c)

    # Negative sequence
    a_neg = 1 / 3 * (a + b * (ALPHA ** 2) + c * ALPHA)

    b_neg = 1 / 3 * (a * ALPHA + b + c * (ALPHA ** 2))

    c_neg = 1 / 3 * (a * (ALPHA ** 2) + b * ALPHA + c)

    # zero sequence
    zero = 1 / 3 * (a + b + c)

    return a_pos, b_pos, c_pos, a_neg, b_neg, c_neg, zero


def fftransform(Signal):
    # fft_size = int(Signal.shape[0])
    spec = np.fft.rfft(Signal)
    # freq = np.linspace(0, 10240 / 2, fft_size / 2 + 1)
    spec = np.abs(spec)
    return spec


def to_complex(r, x, real_offset=0, imag_offset=0):
    real = r * np.cos(x) + real_offset

    imag = r * np.sin(x) + imag_offset

    return real + 1j * imag


def threephase_deserialize(u, v, w):
    return (
        np.fromstring(u, dtype=np.float32),
        np.fromstring(v, dtype=np.float32),
        np.fromstring(w, dtype=np.float32),
    )


def feature_calculator(u, v, w):
    RATE = 10000
    LENGTH = u.shape[0]
    FREQ_INTERVAL = RATE / 2 / (LENGTH / 2)
    PSF_list = []
    complex_list = []
    max_list = []
    harmonics_list = []
    THD_list = []
    rms_list = []
    min_list = []
    brb_list = []
    for phase in [u, v, w]:
        # FFt
        phase = signal.detrend(phase, type="constant")
        phase_fft = fftransform(phase)
        phase_fft_axis = np.linspace(0, RATE / 2, len(phase) / 2 + 1)

        # Power supply frequency
        PSF = phase_fft_axis[np.argmax(phase_fft[: int(60 / FREQ_INTERVAL)])]

        harmonics_index = [i * PSF / FREQ_INTERVAL for i in range(2, 20)]
        total = 0
        harmonics = []
        fundamental = phase_fft[int(PSF / FREQ_INTERVAL)]
        for hm in harmonics_index:
            nth_harmonic = phase_fft[int(hm)] / fundamental
            total = total + nth_harmonic ** 2
            harmonics.append(nth_harmonic)
        harmonics = np.array(harmonics)
        # total = np.sqrt(total)
        THD = np.sqrt(total)
        # Hilbert transform
        Shiftted = np.abs(signal.hilbert(phase))
        phase_envelope = signal.detrend(Shiftted[1024 : 1024 + 4096])
        # Hilebert spectrum
        phase_envelope_fft = fftransform(phase_envelope)
        brb_list.append(phase_envelope_fft[:10])

        # RMS
        rms = np.sqrt(np.dot(phase, phase) / phase.size)

        # Maximum and minimum
        maximum = np.max(phase)
        minimum = np.min(phase)
        PSF_list.append(PSF)
        max_list.append(maximum)
        harmonics_list.append(harmonics)
        THD_list.append(THD)
        rms_list.append(rms)
        min_list.append(minimum)
    i = 0
    p = []
    for phase in [u, v, w]:
        # Estimate parameters
        p0 = [
            max_list[i],
            PSF_list[i],
            np.pi * PSF_list[i],
        ]  # Initial guess for the parameters
        p1 = parameter_estimation(phase, RATE, initailization=p0)
        p.append(p1)
        i = i + 1
        # Calculate complex data

    samples = cal_samples(
        2 * np.pi * p[0][1],
        2 * np.pi * p[1][1],
        2 * np.pi * p[2][1],
        end_time=LENGTH / RATE,
    )

    i = 0
    for phase in [u, v, w]:
        complex_phase, _ = make_phase(
            p[i][0],
            2 * np.pi * p[i][1],
            p[i][2],
            samples=int(samples),
            end_time=LENGTH / RATE,
        )
        # Append to the list
        complex_list.append(complex_phase)
        i = i + 1

    (
        phaseA_pos,
        phaseB_pos,
        phaseC_pos,
        phaseA_neg,
        phaseB_neg,
        phaseC_neg,
        phaseZero,
    ) = cal_symm(complex_list[0], complex_list[1], complex_list[2])

    return (
        rms_list,
        THD_list,
        harmonics_list,
        max_list,
        min_list,
        brb_list,
        p,
        np.sqrt(np.dot(phaseA_neg.real, phaseA_neg.real) / phase.size),
        np.sqrt(np.dot(phaseA_pos.real, phaseA_pos.real) / phase.size),
        np.sqrt(np.dot(phaseZero.real, phaseZero.real) / phase.size),
        fundamental,
    )
