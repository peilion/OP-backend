import numpy as np
from .mixin import FaultPattenMixin

import abc
from services.signal.vibration.vibration_class import VibrationSignal


class MeasurePoint(metaclass=abc.ABCMeta):
    equip = None
    # should be specified in sub classes
    require_phase_diff = True

    def __init__(self, x: VibrationSignal, y: VibrationSignal, r: float, **kwargs):
        self.x = x
        self.y = y
        self.r = r
        self.fr = r / 60.0
        self._phase_diff = None
        for item in kwargs.items():
            self.__setattr__(item[0], item[1])
        self.validate_input()

    def validate_input(self):
        for parent_class in type(self).__bases__:
            grand_class = parent_class.__bases__[0]
            if grand_class is FaultPattenMixin:
                check_list = parent_class.check_list
                for check_item in check_list:
                    if (not hasattr(self, check_item)) | (
                        getattr(self, check_item) is None
                    ):
                        raise Exception(check_item + " undefined!")

    @property
    def phase_diff(self):
        if self._phase_diff is None:
            trimed_x = self.x.data[
                : int(self.x.sampling_rate / 4)
            ]  # 只取前 0.25秒! 的 加速度! 数据进行互相关计算,考虑计算量以及积分后的相位移动
            trimed_y = self.y.data[: int(self.x.sampling_rate / 4)]
            t = np.linspace(
                0.0, ((len(trimed_x) - 1) / self.x.sampling_rate), len(trimed_x)
            )
            cross_correlate = np.correlate(trimed_x, trimed_y, "full")
            dt = np.linspace(-t[-1], t[-1], (2 * len(trimed_x)) - 1)
            time_shift = dt[cross_correlate.argmax()]
            self._phase_diff = (
                (2.0 * np.pi) * ((time_shift / (1.0 / self.fr)) % 1.0)
            ) - np.pi
        return self._phase_diff

    @abc.abstractmethod
    def diagnosis(self):
        pass

    def compute_fault_num(self):
        self.fault_diag_result = {}

        for item in type(self).__bases__:
            if item.__bases__[0] is FaultPattenMixin:
                self.fault_diag_result[item.fault_name] = int(
                    getattr(self, item.fault_num_name)
                )

    def calibrate_fr(self, cali_base: tuple, tolerance: float):

        spec = cali_base[0]
        freq = cali_base[1]
        df = freq[1] - freq[0]

        upper_search = np.rint((self.fr + tolerance) / df).astype(np.int)
        lower_search = np.rint((self.fr - tolerance) / df).astype(np.int)

        cali_fr_index = (
            lower_search + np.argmax(spec[lower_search : upper_search + 1])
        ) * df
        self.fr = cali_fr_index
