import numpy as np
from numpy import ndarray
from scipy import signal
from scipy import stats
from scipy.integrate import cumtrapz
from scipy.signal import detrend


class VibrationSignal:
    type_mapper = {0: "Displacement", 1: "Velocity", 2: "Acceleration", 3: "Envelope"}

    def __init__(self, data: ndarray, fs: int, type=2, isdetrend=False):
        """

        :param data:
        :param fs:
        :param type: 0:位移 1:速度 2:加速度 3:加速度包络
        :param isdetrend:默认未消除趋势
        """
        if not isdetrend:
            self.data = self.linear_detrend(data)
        else:
            self.data = data
        self.sampling_rate = fs
        self.time_vector = np.linspace(
            0.0, len(self.data) / self.sampling_rate, len(self.data)
        )
        self.N = len(data)
        self.nyq = 1 / 2 * self.sampling_rate
        self.type = type
        self._kurtosis = None

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

    def to_filted_signal(self, filter_type: str, co_frequency):
        b, a = signal.butter(8, co_frequency, filter_type)
        data = signal.filtfilt(b, a, self.data)
        return VibrationSignal(data=data, fs=self.sampling_rate, type=self.type)

    def to_envelope(self):
        return VibrationSignal(
            data=np.abs(signal.hilbert(self.data)), fs=self.sampling_rate, type=3
        )

    # def visualize(self, *args):
    #     """
    #     :param args: 'data','v_data' 中的一个或多个
    #     """
    #     for item in args:
    #         data = getattr(self, item)
    #         if data is not None:
    #             plt.plot(data)
    #             plt.show()

    def compute_harmonics(self, fr: float, upper: int, tolerance=0.025):
        assert self.spec is not None, "需先计算频谱"
        spec = self.spec
        freq = self.freq
        df = freq[1] - freq[0]

        nfrs = [i * fr for i in range(1, upper)]
        harmonics = []
        harmonics_index = []

        for index, nfr in enumerate(nfrs):
            upper_search = np.rint((nfr + nfr / fr * tolerance) / df).astype(np.int)
            lower_search = np.rint((nfr - nfr / fr * tolerance) / df).astype(np.int)

            nfr_index = lower_search + np.argmax(spec[lower_search : upper_search + 1])
            nfr_amp = spec[nfr_index]

            harmonics_index.append(nfr_index)
            harmonics.append(nfr_amp)

        self.harmonics = np.array(harmonics)
        self.harmonics_index = np.array(harmonics_index)

        self.thd = np.sqrt((self.harmonics[1:] ** 2).sum()) / self.harmonics[0]

    def compute_sub_harmonic(self, fr: float, upper=10, tolerance=0.025):
        assert self.spec is not None, "需先计算频谱"
        spec = self.spec
        freq = self.freq
        df = freq[1] - freq[0]

        subhar_frequencies = [i * fr / 2 for i in range(1, upper, 2)]
        harmonics = []
        harmonics_index = []

        for subhar_frequency in subhar_frequencies:
            upper_search = np.rint(
                (subhar_frequency + tolerance * (subhar_frequency / fr)) / df
            ).astype(np.int)
            lower_search = np.rint(
                (subhar_frequency - tolerance * (subhar_frequency / fr)) / df
            ).astype(np.int)

            nth_harmonic_index = lower_search + np.argmax(
                spec[lower_search : upper_search + 1]
            )
            nth_harmonic = spec[nth_harmonic_index]

            harmonics_index.append(nth_harmonic_index)
            harmonics.append(nth_harmonic)

        self.sub_harmonics = np.array(harmonics)
        self.sub_harmonics_index = np.array(harmonics_index)

    def compute_spectrum(self):
        spec = np.fft.fft(self.data)[0 : int(self.N / 2)] / self.N
        spec[1:] = 2 * spec[1:]
        self.spec = np.abs(spec)
        self.freq = np.fft.fftfreq(self.N, 1.0 / self.sampling_rate)[
            0 : int(self.N / 2)
        ]

    def compute_bearing_frequency(
        self, bpfi, bpfo, bsf, ftf, fr, upper=3, tolerance=0.025
    ):
        assert self.spec is not None, "需先计算频谱"
        spec = self.spec
        freq = self.freq
        df = freq[1] - freq[0]

        bearing_index = []
        bearing_amp = []
        for component in [ftf, bsf, bpfo, bpfi]:
            for i in range(1, upper + 1):
                characteristic_fr = component * fr * i
                upper_search = np.rint(
                    (characteristic_fr + tolerance * (characteristic_fr / fr)) / df
                ).astype(np.int)
                lower_search = np.rint(
                    (characteristic_fr - tolerance * (characteristic_fr / fr)) / df
                ).astype(np.int)

                tmp_index = lower_search + np.argmax(
                    spec[lower_search : upper_search + 1]
                )
                tmp_amp = spec[tmp_index]

                bearing_index.append(tmp_index)
                bearing_amp.append(tmp_amp)
        self.bearing_index = np.array(bearing_index)
        self.bearing_amp = np.array(bearing_amp)

    def compute_half_harmonic(self, fr, tolerance=0.025):
        spec = self.spec
        freq = self.freq
        df = freq[1] - freq[0]

        half_fr_indexes = fr / 2

        upper_search = np.rint(
            (half_fr_indexes + tolerance * (half_fr_indexes / fr)) / df
        ).astype(np.int)
        lower_search = np.rint(
            (half_fr_indexes - tolerance * (half_fr_indexes / fr)) / df
        ).astype(np.int)

        self.half_fr_indexes = lower_search + np.argmax(
            spec[lower_search : upper_search + 1]
        )
        self.half_fr_amp = spec[self.half_fr_indexes]

    def compute_mesh_frequency(
        self, fr, mesh_ratio, sideband_order=6, upper_order=3, tolerance=0.025
    ):
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

    def get_band_energy(self, fr: float, band_range: tuple):
        assert self.spec is not None, "需先计算频谱"
        assert len(band_range) == 2, "频带设置错误"
        df = self.freq[1] - self.freq[0]
        upper_search = np.rint(band_range[1] * fr / df).astype(np.int)
        lower_search = np.rint(band_range[0] * fr / df).astype(np.int)
        search_range = self.spec[lower_search : upper_search + 1]
        return lower_search + np.argmax(search_range), np.max(search_range)

    @staticmethod
    def linear_detrend(data):
        return detrend(data, type="linear")

    @staticmethod
    def const_detrend(data):
        return detrend(data, type="const")

    @staticmethod
    def poly_detrend(data):
        x = np.arange(len(data))
        fit = np.polyval(np.polyfit(x, data, deg=10), x)
        data -= fit
        return data

    @staticmethod
    def diff_detrend(data):
        return np.diff(data)

    @property
    def kurtosis(self):
        if self._kurtosis is None:
            self._kurtosis = stats.kurtosis(self.data)
        return self._kurtosis

    @property
    def rms_fea(self):
        return np.sqrt(np.mean(np.square(self.data)))

    @property
    def var_fea(self):
        return np.var(self.data)

    @property
    def max_fea(self):
        return np.max(self.data)

    @property
    def pp_fea(self):
        return np.max(self.data) - np.min(self.data)

    @property
    def skew_fea(self):
        return stats.skew(self.data)

    @property
    def spectral_kurt(self):
        return stats.kurtosis(self.spec)

    @property
    def spectral_skw(self):
        return stats.skew(self.spec)

    @property
    def spectral_pow(self):
        return np.mean(np.power(self.spec, 3))

    def __repr__(self):
        return "{0} Signal with a size of {1}, and the sampling rate is {2}.".format(
            self.type_mapper[type], len(self.data), self.sampling_rate
        )
