import numpy as np
from numpy import ndarray
from scipy import optimize, signal

from services.signal.base import DigitalSignal


class ElectricSignal(DigitalSignal):
    # def acc2vel_fd(self):
    #     data = self.data
    #     N = len(data)
    #     df = 1.0/(N*1/self.sampling_rate)
    #     nyq = 1/(2*1/self.sampling_rate)
    #     iomega_array = 1j*2*np.pi*np.linspace(-nyq,nyq,int(2*nyq/df))
    #     A = fftshift(fft(data))
    #     A = A * iomega_array
    #     A = ifftshift(A)
    #     self.v_data = np.real(ifft(A))
    #
    # def acc2vel_wj(self):
    #     data = self.data
    #     dt = self.time_vector[1] - self.time_vector[0]
    #     baseline = np.mean(data)
    #     datafft = np.fft.fft(data - baseline)
    #     datafreq = np.fft.fftfreq(len(data), dt)
    #     datafreq = [(i + 1) * datafreq[1] for i in range(len(datafft))]
    #     self.v_data = np.real(np.fft.ifft(datafft / (2. * np.pi * np.abs(datafreq)))) + baseline
    type_mapper = {0: "Raw", 1: "Envelope"}

    def __init__(
        self,
        data: ndarray,
        fs: int,
        type: int,
        isdetrend=False,
        compute_axis: bool = True,
    ):
        super().__init__(data, fs, isdetrend, compute_axis)
        self._fundamental = None
        self.type = type

    def to_envelope(self):
        cutoff = int(self.N * 0.1)
        return self.__class__(
            data=np.abs(signal.hilbert(self.data)[cutoff:-cutoff]),
            fs=self.sampling_rate,
            type=1
            # eliminate endpoint effect
        )

    def compute_brb_component(self):
        assert self.type == 1, "This method should be applied to envelope signal"
        brb_range = int(10 / self.df)
        self.brb_list = self.spec[:brb_range]

    def estimate_fundamental(self):
        if self.spec is None:
            self.compute_spectrum(compute_axis=True)
        self._fundamental = self.freq[np.argmax(self.spec)]

    def estimate_params(self):
        fitfunc = lambda p, x: p[0] * np.sin(
            2 * np.pi * p[1] * x + p[2]
        )  # Target function
        errfunc = lambda p, x, y: fitfunc(p, x) - y  # Distance to the target function
        size = int(self.data.shape[0])
        Tx = np.linspace(0, size / self.sampling_rate, size)
        p1 = optimize.leastsq(
            func=errfunc,
            x0=np.array([self.max_fea, self.fundamental, np.pi * self.fundamental]),
            args=(Tx, self.data),
        )
        self.amplitude = p1[0]
        self._fundamental = p1[1]
        self.phase = p1[2]

    def make_phase(self, samples):
        array_time = np.linspace(0, self.data.shape[0] / self.sampling_rate, samples)
        x = self.fundamental * array_time + self.phase
        return self.to_complex(self.amplitude, x), array_time

    @staticmethod
    def to_complex(r, x, real_offset=0, imag_offset=0):
        real = r * np.cos(x) + real_offset
        imag = r * np.sin(x) + imag_offset
        return real + 1j * imag

    @property
    def fundamental(self):
        if self._fundamental is None:
            self.estimate_fundamental()
        return self._fundamental


class ThreePhaseElectric(object):
    def __init__(self, u: ElectricSignal, v: ElectricSignal, w: ElectricSignal):
        if (u.sampling_rate != v.sampling_rate != w.sampling_rate) | (
            u.data.shape[0] != v.data.shape[0] != w.data.shape[0]
        ):
            raise Exception("Unmatched sampling rate")
        self.u = u
        self.v = v
        self.w = w

    def estimate_three_params(self):
        self.u.estimate_params()
        self.v.estimate_params()
        self.w.estimate_params()

    def dq0_transform(self):
        d = (
            np.sqrt(2 / 3) * self.u.data
            - (1 / (np.sqrt(6))) * self.v.data
            - (1 / (np.sqrt(6))) * self.w.data
        )
        q = (1 / (np.sqrt(2))) * self.v.data - (1 / (np.sqrt(2))) * self.w.data
        return d, q

    def cal_symm(self, require_sym_comps: bool = False):
        # 120 degree rotator
        self.cal_samples()
        b, _ = self.u.make_phase(samples=self.fake_samples_number)
        a, _ = self.v.make_phase(samples=self.fake_samples_number)
        c, _ = self.w.make_phase(samples=self.fake_samples_number)

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
        self.p_rms = np.sqrt(np.mean(np.square(a_pos)))
        self.n_rms = np.sqrt(np.mean(np.square(a_neg)))
        self.imbanlance = self.n_rms / self.p_rms

        if require_sym_comps:
            return a_pos, b_pos, c_pos, a_neg, b_neg, c_neg, zero

    def cal_samples(self):
        """
        Calculate the number of samples needed.
        """
        max_omega = max(
            abs(2 * np.pi * self.u.fundamental),
            abs(2 * np.pi * self.v.fundamental),
            abs(2 * np.pi * self.w.fundamental),
        )
        max_freq = max_omega / (2 * np.pi)
        self.fake_samples_number = (
            (max_freq ** 2) * 6 * self.u.data.shape[0] / self.u.sampling_rate
        )


def to_complex(r, x, real_offset=0, imag_offset=0):
    real = r * np.cos(x) + real_offset

    imag = r * np.sin(x) + imag_offset

    return real + 1j * imag


def make_phase(mag, omega, phi, samples, end_time):
    """
    Create the phase signal in complex form.
    """

    array_time = np.linspace(0, end_time, samples)

    x = omega * array_time + phi

    return to_complex(mag, x), array_time


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
