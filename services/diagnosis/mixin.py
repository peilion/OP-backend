from services.signal.vibration.vibration_class import VibrationSignal
import numpy as np
from numpy import ndarray


class FaultPattenMixin:
    check_list = []
    fault_num_name = None


# 类名必须包含"Mixin"关键字
class UnbalanceMixin(FaultPattenMixin):
    ib_threshold = None
    pd_threshold = None
    thd_threshold = None
    check_list = ["ib_threshold", "pd_threshold", "thd_threshold"]
    fault_num_name = "ib_level"
    fault_name = "不平衡故障"

    def unbalance_diagnosis(self, blade_num: int, diag_obj: VibrationSignal):

        self.ib_indicator = (
            0.9 * diag_obj.harmonics[0]
            + 0.05 * diag_obj.harmonics[1]
            + 0.05
            * (
                diag_obj.harmonics[2:].sum()
                - (diag_obj.harmonics[blade_num - 1] if blade_num != 0 else 0)
            )
        )
        self.ib_level = np.searchsorted(self.ib_threshold, self.ib_indicator)

        if self.require_phase_diff:
            phase_diff = self.phase_diff
            if (abs(phase_diff) > (np.pi / 2 + self.pd_threshold)) | (
                abs(phase_diff) < (np.pi / 2 - self.pd_threshold)
            ):
                self.ib_level = 0

        if diag_obj.thd > self.thd_threshold:
            self.ib_level = 0


class MisalignmentMixin(FaultPattenMixin):
    ma_threshold = None
    check_list = ["ma_threshold"]
    fault_num_name = "ma_level"
    fault_name = "不对中故障"

    def misalignment_diagnosis(self, blade_num: int, diag_obj: VibrationSignal):
        self.ma_indicator = (
            0.5 * diag_obj.harmonics[0]
            + 0.4 * diag_obj.harmonics[1]
            + 0.1
            * (
                diag_obj.harmonics[2:].sum()
                - (diag_obj.harmonics[blade_num - 1] if blade_num != 0 else 0)
            )
        )

        self.ma_level = np.searchsorted(self.ma_threshold, self.ma_indicator)


class ALooseMixin(FaultPattenMixin):
    al_threshold = None
    pd_threshold = None
    check_list = ["al_threshold", "pd_threshold"]

    fault_num_name = "al_level"
    fault_name = "A类松动"

    def atype_loose_diagnosis(self, diag_obj: VibrationSignal):

        self.al_indicator = diag_obj.harmonics[0]
        self.al_level = np.searchsorted(self.al_threshold, self.al_indicator)

        if self.require_phase_diff:
            phase_diff = self.phase_diff
            if (abs(phase_diff) < (np.pi / 2 + self.pd_threshold)) & (
                abs(phase_diff) > (np.pi / 2 - self.pd_threshold)
            ):
                self.al_level = 0


class BLooseMixin(FaultPattenMixin):
    harmonic_threshold = None
    bl_threshold = None
    check_list = ["harmonic_threshold", "bl_threshold"]

    fault_num_name = "bl_level"
    fault_name = "B类松动"

    def btype_loose_diagnosis(self, blade_num: int, diag_obj: VibrationSignal):
        self.bl_indicator = diag_obj.half_fr_amp
        self.bl_level = np.searchsorted(self.bl_threshold, self.bl_indicator)

        harmonic_compare = diag_obj.harmonics >= self.harmonic_threshold
        hn = 0
        for index, item in enumerate(harmonic_compare):
            if item & ((index + 1) != blade_num):
                hn = hn + 1
        self.harmonic_number = hn


class RollBearingMixin(FaultPattenMixin):
    bw_threshold = None
    kurtosis_threshold = None
    bearing_ratio = None
    check_list = ["bw_threshold", "kurtosis_threshold", "bearing_ratio"]
    fault_num_name = "bw_level"
    fault_name = "滚动轴承故障"

    def roll_bearing_diagnosis(self, diag_obj: VibrationSignal):
        level_list = []
        obj: VibrationSignal = diag_obj
        bw_amps = obj.bearing_amp[:4]
        for item in bw_amps:
            level_list.append(np.searchsorted(self.bw_threshold, item))
        if obj.kurtosis > self.kurtosis_threshold:
            level_list.append(1)
        self.bw_level = np.array(level_list).max()


class GearMixin(FaultPattenMixin):
    gf_threshold = None
    kurtosis_threshold = None
    teeth_num = None
    check_list = ["gf_threshold", "kurtosis_threshold", "teeth_num"]
    sideband_order = 6
    fault_num_name = "gf_level"
    fault_name = "齿轮故障"

    def gear_diagnosis(self, diag_obj: VibrationSignal):
        self.sideband_energies = np.sum(diag_obj.sideband_amps, axis=1)
        self.gf_indicator = self.sideband_energies.max()
        self.gf_level = np.searchsorted(self.gf_threshold, self.gf_indicator)

        if (diag_obj.kurtosis > self.kurtosis_threshold) & (self.gf_level < 1):
            self.gf_level += 1


class OilWhirlMixin(FaultPattenMixin):
    wd_threshold = None  # type: ndarray
    check_list = ["wd_threshold"]

    fault_num_name = "ow_level"
    fault_name = "滑动轴承油膜涡动故障"

    def oil_whirl_diagnosis(self, diag_obj: VibrationSignal):
        self.ow_indicator = diag_obj.ow_amp
        self.ow_level = np.searchsorted(self.wd_threshold, self.ow_indicator)


class RubbingMixin(FaultPattenMixin):
    rb_threshold = None  # type:ndarray
    subharmonic_threshold = None  # type:ndarray
    check_list = ["rb_threshold", "subharmonic_threshold"]

    fault_num_name = "rb_level"
    fault_name = "碰磨故障"

    def rubbing_diagnosis(self, diag_obj: VibrationSignal, blade_num: int):

        harmonic_compare = diag_obj.harmonics >= self.harmonic_threshold
        hn = 0
        for index, item in enumerate(harmonic_compare):
            if item & ((index + 1) != blade_num):
                hn = hn + 1
        self.harmonic_number = hn

        sub_harmonic_compare = diag_obj.sub_harmonics >= self.subharmonic_threshold
        shn = 0
        for item in sub_harmonic_compare:
            shn = (shn + 1) if item else shn

        self.sub_har_num = shn
        self.rb_indicator = hn + shn
        self.rb_level = np.searchsorted(self.rb_threshold, self.rb_indicator)


class SurgeMixin(FaultPattenMixin):
    sg_threshold = None
    check_list = ["sg_threshold"]

    fault_num_name = "sg_level"
    fault_name = "喘振故障"

    def surge_diagnosis(self, diag_obj: VibrationSignal):
        low_index1, low_energy1 = diag_obj.get_band_energy(
            fr=self.fr, band_range=(0, 0.4)
        )
        low_index2, low_energy2 = diag_obj.get_band_energy(
            fr=self.fr, band_range=(0.6, 0.8)
        )

        self.sg_index = np.array([low_index1, low_index2])
        self.lt_fr_amp = np.array([low_energy1, low_energy2])

        self.sg_indicator = 0.45 * low_energy1 + 0.35 * low_energy2

        self.sg_level = np.searchsorted(self.sg_threshold, self.sg_indicator)
