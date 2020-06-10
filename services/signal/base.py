import abc

import numpy as np
import pywt
from numpy import ndarray
from scipy import signal
from scipy import stats
from scipy.signal import detrend

from services.signal.thrid_party_lib.emd import EMD


class DigitalSignal:  # Base class for vibration signal and electric signal
    def __init__(
        self, data: ndarray, fs: int, isdetrend=False, compute_axis: bool = True
    ):
        """
        :param data:
        :param fs:
        :param isdetrend:默认未消除趋势
        """
        if not isdetrend:
            self.data = self.linear_detrend(data)
        else:
            self.data = data
        self.sampling_rate = fs
        if compute_axis:
            self.time_vector = np.linspace(
                0.0, len(self.data) / self.sampling_rate, len(self.data)
            )
        self.N = len(data)
        self.nyq = 1 / 2 * self.sampling_rate
        self._kurtosis = None

    def to_filted_signal(self, filter_type: str, co_frequency):
        b, a = signal.butter(8, co_frequency, filter_type)
        data = signal.filtfilt(b, a, self.data)
        return self.__class__(data=data, fs=self.sampling_rate)

    def to_envelope(self):
        return self.__class__(
            data=np.abs(signal.hilbert(self.data)), fs=self.sampling_rate
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

    def calibrate_fr(self, basic_fr: float, tolerance: float = 0.5):

        df = self.freq[1] - self.freq[0]

        upper_search = np.rint((basic_fr + tolerance) / df).astype(np.int)
        lower_search = np.rint((basic_fr - tolerance) / df).astype(np.int)

        cali_fr = (
            lower_search + np.argmax(self.spec[lower_search : upper_search + 1])
        ) * df
        self.fr = cali_fr

    def compute_harmonics(self, fr: float, upper: int, tolerance=None):
        assert self.spec is not None, "需先计算频谱"
        tolerance = (
            self.sampling_rate * 1.0 / self.N / 2 if tolerance is None else tolerance
        )
        spec = self.spec
        freq = self.freq
        df = freq[1] - freq[0]

        nfrs = [0.5 * fr] + [i * fr for i in range(1, upper)]
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

    def compute_sub_harmonic(self, fr: float, upper=10, tolerance=None):
        assert self.spec is not None, "需先计算频谱"
        tolerance = (
            self.sampling_rate * 1.0 / self.N / 2 if tolerance is None else tolerance
        )
        df = self.df

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
                self.spec[lower_search : upper_search + 1]
            )
            nth_harmonic = self.spec[nth_harmonic_index]

            harmonics_index.append(nth_harmonic_index)
            harmonics.append(nth_harmonic)

        self.sub_harmonics = np.array(harmonics)
        self.sub_harmonics_index = np.array(harmonics_index)

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

    def compute_spectrum(self, compute_axis: bool = True):
        spec = np.fft.fft(self.data)[0 : int(self.N / 2)] / self.N
        spec[1:] = 2 * spec[1:]
        self.spec = np.abs(spec)
        if compute_axis:
            self.freq = np.fft.fftfreq(self.N, 1.0 / self.sampling_rate)[
                0 : int(self.N / 2)
            ]
            self.df = self.freq[1] - self.freq[0]

    def compute_bearing_frequency(
        self, bpfi, bpfo, bsf, ftf, fr, upper=3, tolerance=None
    ):
        assert self.spec is not None, "需先计算频谱"
        tolerance = (
            self.sampling_rate * 1.0 / self.N / 2 if tolerance is None else tolerance
        )
        df = self.df

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
                    self.spec[lower_search : upper_search + 1]
                )
                tmp_amp = self.spec[tmp_index]

                bearing_index.append(tmp_index)
                bearing_amp.append(tmp_amp)
        self.bearing_index = np.array(bearing_index)
        self.bearing_amp = np.array(bearing_amp)

    def get_band_energy(self, fr: float, band_range: tuple):
        assert self.spec is not None, "需先计算频谱"
        assert len(band_range) == 2, "频带设置错误"
        df = self.df
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
        return np.diff(data)  # Detrend Method Region

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
        return np.mean(np.power(self.spec, 3))  # Feature Property Region

    def get_short_time_fournier_transform(self) -> dict:
        f, t, z = signal.stft(self.data, self.sampling_rate, nperseg=256)
        z = np.abs(z)
        stft = []
        for i in range(z.shape[0]):
            for j in range(z.shape[1]):
                stft.append([j, i, round(float(z[i, j]), 3)])
        return {"t": t, "f": f, "stft": stft, "max": float(z.max())}

    def get_multi_scale_envelope_spectrum(
        self, n_Ssta: float, n_Send: float, n_Sint: float
    ) -> dict:
        length = len(self.data)

        i = n_Ssta
        scal = []
        while i <= n_Send:
            scal.append(i)
            i = i + n_Sint
        scal.append(i)
        scal = np.array(scal).round(3).tolist()  # stupid
        coef = pywt.cwt(self.data, scal, "cmor1-0.5")
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
            (self.sampling_rate * np.linspace(0, length / 2, int(length / 2)) / length),
            decimals=3,
        ).tolist()
        z = z[:, : len(FreqExt)]
        value = []
        for sIndex, scale in enumerate(scal):
            for fIndex, freq in enumerate(FreqExt):
                value.append([sIndex, fIndex, round(float(z[sIndex][fIndex]), 3)])
        return {"scale": scal, "freq": FreqExt, "value": value}

    def get_welch_spectrum_estimation(self) -> dict:
        freq, spec = signal.welch(self.data, self.sampling_rate, scaling="spectrum")
        return {"freq": freq, "spec": spec}

    def get_empirical_mode_decomposition(self) -> dict:
        decomposer = EMD(self.data)
        IMFs = decomposer.decompose()
        return {"emd": IMFs.round(3).tolist()}  # Advanced Transfrom Region

    def __repr__(self):
        return "Signal with a size of {0}, and the sampling rate is {1}.".format(
            len(self.data), self.sampling_rate
        )


class MeasurePoint(metaclass=abc.ABCMeta):
    fault_num_mapper = {0: [0, 0, 0], 1: [1, 0, 0], 2: [0, 1, 0], 3: [0, 0, 1]}
    equip = None
    # should be specified in sub classes
    require_phase_diff = True

    def __init__(self, data: dict, r: float):
        self.data = data
        self.r = r
        self.fr = r / 60.0

    @abc.abstractmethod
    def diagnosis(self):
        pass

    def compute_fault_num(self):
        self.fault_num = []

        for item in type(self).__bases__:
            if str(item).__contains__("Mixin"):
                self.fault_num += self.fault_num_mapper[
                    getattr(self, item.fault_num_name)
                ]
        self.fault_num = np.array(self.fault_num)
