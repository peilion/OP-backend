import numpy as np
from numpy import ndarray
from scipy.integrate import cumtrapz

from services.signal.base import DigitalSignal


class VibrationSignal(DigitalSignal):
    type_mapper = {0: "Displacement", 1: "Velocity", 2: "Acceleration", 3: "Envelope"}

    def __init__(
        self, data: ndarray, fs: int, type=2, isdetrend=False, compute_axis: bool = True
    ):
        """

        :param data:
        :param fs:
        :param type: 0:位移 1:速度 2:加速度 3:加速度包络
        :param isdetrend:默认未消除趋势
        """
        self.type = type
        super().__init__(data, fs, isdetrend, compute_axis)

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

    def to_velocity(self, detrend_type="poly"):
        data = cumtrapz(self.data, self.time_vector)
        detrend_meth = getattr(self, detrend_type + "_detrend")
        return VibrationSignal(
            detrend_meth(data), fs=self.sampling_rate, type=self.type - 1
        )

    def compute_mesh_frequency(
        self, fr, mesh_ratio, sideband_order=6, upper_order=3, tolerance=None
    ):
        tolerance = (
            self.sampling_rate * 1.0 / self.N / 2 if tolerance is None else tolerance
        )

        spec = self.spec
        freq = self.freq
        df = freq[1] - freq[0]
        mesh_frequencies = [mesh_ratio * fr * i for i in range(1, upper_order + 1)]
        self.sideband_amps = []
        self.sideband_indexes = []
        for mesh_frequency in mesh_frequencies:

            for i in range(-sideband_order, sideband_order + 1):
                frequecy = mesh_frequency + i * fr

                if frequecy > self.sampling_rate / 2:
                    self.sideband_indexes.append(0)
                    self.sideband_amps.append(0)
                    continue

                upper_search = np.rint(
                    (frequecy + (frequecy / fr) * tolerance) / df
                ).astype(np.int)
                lower_search = np.rint(
                    (frequecy - (frequecy / fr) * tolerance) / df
                ).astype(np.int)

                sideband_index = lower_search + np.argmax(
                    spec[lower_search : upper_search + 1]
                )
                sideband_amp = spec[sideband_index]
                self.sideband_indexes.append(sideband_index)
                self.sideband_amps.append(sideband_amp)

        self.sideband_amps = np.reshape(
            self.sideband_amps, (upper_order, sideband_order * 2 + 1)
        )
        self.sideband_indexes = np.reshape(
            self.sideband_indexes, (upper_order, sideband_order * 2 + 1)
        )

    def compute_oilwhirl_frequency(self, fr):
        spec = self.spec
        freq = self.freq
        df = freq[1] - freq[0]

        ow_frequency_lower = fr * 0.45
        ow_frequency_upper = fr * 0.48

        lower_search = np.rint(ow_frequency_lower / df).astype(np.int)
        upper_search = np.rint(ow_frequency_upper / df).astype(np.int)

        self.ow_index = lower_search + np.argmax(spec[lower_search:upper_search])

        self.ow_amp = spec[self.ow_index]

    def __sub__(self, other):  # minus method
        assert isinstance(other, VibrationSignal), "Unsupport Type."
        assert self.sampling_rate == other.sampling_rate, "Unequal Sampling Rate"
        trimed_x = self.data[
            : int(self.data.sampling_rate / 4)
        ]  # 只取前 0.25秒! 的 加速度! 数据进行互相关计算,考虑计算量以及积分后的相位移动
        trimed_y = other.data[: int(self.data.sampling_rate / 4)]
        t = np.linspace(
            0.0, ((len(trimed_x) - 1) / self.data.sampling_rate), len(trimed_x)
        )
        cross_correlate = np.correlate(trimed_x, trimed_y, "full")
        dt = np.linspace(-t[-1], t[-1], (2 * len(trimed_x)) - 1)
        time_shift = dt[cross_correlate.argmax()]
        _phase_diff = np.abs(
            ((2.0 * np.pi) * ((time_shift / (1.0 / self.fr)) % 1.0)) - np.pi
        )
        return _phase_diff
