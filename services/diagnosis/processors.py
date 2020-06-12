import MySQLdb

from .base import MeasurePoint
from .mixin import (
    UnbalanceMixin,
    MisalignmentMixin,
    RollBearingMixin,
    ALooseMixin,
    BLooseMixin,
    SurgeMixin,
    RubbingMixin,
)
import numpy as np

from ..signal.vibration.vibration_class import VibrationSignal


class MotorDriven(
    MeasurePoint,
    UnbalanceMixin,
    MisalignmentMixin,
    RollBearingMixin,
    ALooseMixin,
    BLooseMixin,
    RubbingMixin,
):
    # Mixin的继承顺序必须与故障代码的顺序完全一致
    require_phase_diff = False

    def diagnosis(self):
        self.x.compute_spectrum()
        self.calibrate_fr(cali_base=(self.x.spec, self.x.freq), tolerance=20)
        self.x_vel = self.x.to_velocity(detrend_type="poly").to_filted_signal(
            filter_type="lowpass", co_frequency=2 * 10 * self.fr / self.x.sampling_rate
        )
        self.x_vel.compute_spectrum()
        self.x_vel.compute_sub_harmonic(fr=self.fr)
        self.x_vel.compute_harmonics(fr=self.fr, upper=11)
        self.x_vel.compute_half_harmonic(fr=self.fr)

        self.unbalance_diagnosis(blade_num=0, diag_obj=self.x_vel)
        self.misalignment_diagnosis(blade_num=0, diag_obj=self.x_vel)
        self.atype_loose_diagnosis(diag_obj=self.x_vel)
        self.btype_loose_diagnosis(blade_num=0, diag_obj=self.x_vel)
        self.rubbing_diagnosis(diag_obj=self.x_vel, blade_num=0)

        self.x_env = self.x.to_filted_signal(
            filter_type="highpass", co_frequency=2 * 1000 / self.x.sampling_rate
        ).to_envelope()
        self.x_env.compute_spectrum()
        self.x_env.compute_bearing_frequency(
            bpfi=self.bearing_ratio["bpfi"],
            bpfo=self.bearing_ratio["bpfo"],
            bsf=self.bearing_ratio["bsf"],
            ftf=self.bearing_ratio["ftf"],
            fr=self.fr,
            upper=3,
        )
        self.roll_bearing_diagnosis(diag_obj=self.x_env)

        self.compute_fault_num()


class MotorNonDriven(
    MeasurePoint, UnbalanceMixin, RollBearingMixin, ALooseMixin, BLooseMixin
):
    require_phase_diff = False

    def diagnosis(self):
        self.x.compute_spectrum()
        self.calibrate_fr(cali_base=(self.x.spec, self.x.freq), tolerance=20)
        self.x_vel = self.x.to_velocity(detrend_type="poly").to_filted_signal(
            filter_type="lowpass", co_frequency=2 * 10 * self.fr / self.x.sampling_rate
        )
        self.x_vel.compute_spectrum()
        self.x_vel.compute_harmonics(fr=self.fr, upper=11)

        self.unbalance_diagnosis(blade_num=0, diag_obj=self.x_vel)
        self.atype_loose_diagnosis(diag_obj=self.x_vel)

        self.x_vel.compute_half_harmonic(fr=self.fr)
        self.btype_loose_diagnosis(blade_num=0, diag_obj=self.x_vel)

        self.x_env = self.x.to_filted_signal(
            filter_type="highpass", co_frequency=2 * 1000 / self.x.sampling_rate
        ).to_envelope()
        self.x_env.compute_spectrum()
        self.x_env.compute_bearing_frequency(
            bpfi=self.bearing_ratio["bpfi"],
            bpfo=self.bearing_ratio["bpfo"],
            bsf=self.bearing_ratio["bsf"],
            ftf=self.bearing_ratio["ftf"],
            fr=self.fr,
            upper=3,
        )

        self.roll_bearing_diagnosis(diag_obj=self.x_env)
        self.compute_fault_num()


class PumpDriven(
    MeasurePoint,
    UnbalanceMixin,
    MisalignmentMixin,
    RollBearingMixin,
    ALooseMixin,
    BLooseMixin,
    SurgeMixin,
    RubbingMixin,
):
    # Mixin的继承顺序必须与故障代码的顺序完全一致
    require_phase_diff = False

    def diagnosis(self):
        self.x.compute_spectrum()
        self.calibrate_fr(cali_base=(self.x.spec, self.x.freq), tolerance=20)
        self.x_vel = self.x.to_velocity(detrend_type="poly").to_filted_signal(
            filter_type="lowpass", co_frequency=2 * 10 * self.fr / self.x.sampling_rate
        )
        self.x_vel.compute_spectrum()
        self.x_vel.compute_harmonics(fr=self.fr, upper=11)
        self.x_vel.compute_half_harmonic(fr=self.fr)
        self.x_vel.compute_sub_harmonic(fr=self.fr)

        self.unbalance_diagnosis(blade_num=0, diag_obj=self.x_vel)
        self.misalignment_diagnosis(blade_num=0, diag_obj=self.x_vel)
        self.atype_loose_diagnosis(diag_obj=self.x_vel)
        self.btype_loose_diagnosis(blade_num=0, diag_obj=self.x_vel)
        self.rubbing_diagnosis(diag_obj=self.x_vel, blade_num=0)

        self.x_env = self.x.to_filted_signal(
            filter_type="highpass", co_frequency=2 * 1000 / self.x.sampling_rate
        ).to_envelope()
        self.x_env.compute_spectrum()
        self.x_env.compute_bearing_frequency(
            bpfi=self.bearing_ratio["bpfi"],
            bpfo=self.bearing_ratio["bpfo"],
            bsf=self.bearing_ratio["bsf"],
            ftf=self.bearing_ratio["ftf"],
            fr=self.fr,
            upper=3,
        )
        self.roll_bearing_diagnosis(diag_obj=self.x_env)
        self.surge_diagnosis(diag_obj=self.x)

        self.compute_fault_num()


class PumpNonDriven(
    MeasurePoint, UnbalanceMixin, RollBearingMixin, ALooseMixin, BLooseMixin, SurgeMixin
):
    require_phase_diff = False

    def diagnosis(self):
        self.x.compute_spectrum()
        self.calibrate_fr(cali_base=(self.x.spec, self.x.freq), tolerance=20)
        self.x_vel = self.x.to_velocity(detrend_type="poly").to_filted_signal(
            filter_type="lowpass", co_frequency=2 * 10 * self.fr / self.x.sampling_rate
        )
        self.x_vel.compute_spectrum()
        self.x_vel.compute_harmonics(fr=self.fr, upper=11)

        self.unbalance_diagnosis(blade_num=0, diag_obj=self.x_vel)
        self.atype_loose_diagnosis(diag_obj=self.x_vel)
        self.surge_diagnosis(diag_obj=self.x)

        self.x_vel.compute_half_harmonic(fr=self.fr)
        self.btype_loose_diagnosis(blade_num=0, diag_obj=self.x_vel)

        self.x_env = self.x.to_filted_signal(
            filter_type="highpass", co_frequency=2 * 1000 / self.x.sampling_rate
        ).to_envelope()
        self.x_env.compute_spectrum()
        self.x_env.compute_bearing_frequency(
            bpfi=self.bearing_ratio["bpfi"],
            bpfo=self.bearing_ratio["bpfo"],
            bsf=self.bearing_ratio["bsf"],
            ftf=self.bearing_ratio["ftf"],
            fr=self.fr,
            upper=3,
        )

        self.roll_bearing_diagnosis(diag_obj=self.x_env)
        self.compute_fault_num()


def motor_driven_end_diagnosis(data, fs, R, bearing_ratio: dict, th: dict):
    data = np.fromstring(data, dtype=np.float32)
    x = VibrationSignal(data=data, fs=fs, type=2)
    mp_instance = MotorDriven(
        x=x,
        y=x,
        r=R,
        bearing_ratio=bearing_ratio,
        ib_threshold=th["Unbalance"],
        ma_threshold=th["Misalignment"],
        bw_threshold=th["RollBearing"],
        al_threshold=th["ALoose"],
        bl_threshold=th["BLoose"],
        rb_threshold=th["Rubbing"],
        thd_threshold=th["thd"],
        pd_threshold=0,
        kurtosis_threshold=th["kurtosis"],
        harmonic_threshold=th["harmonic_threshold"],
        subharmonic_threshold=th["subharmonic_threshold"],
    )
    mp_instance.diagnosis()
    return (
        mp_instance.fault_diag_result,
        {
            "ib_mark": int(mp_instance.x_vel.harmonics_index[1]),
            "ma_mark": int(mp_instance.x_vel.harmonics_index[2]),
            "al_mark": int(mp_instance.x_vel.harmonics_index[1]),
            "bl_mark": [int(item) for item in mp_instance.x_vel.harmonics_index],
            "rb_mark": [int(item) for item in mp_instance.x_vel.harmonics_index[:5]]
            + [int(item) for item in mp_instance.x_vel.sub_harmonics_index],
            "bw_mark": [int(item) for item in mp_instance.x_env.bearing_index],
        },
        {
            "ib_indicator": float(mp_instance.ib_indicator),
            "ma_indicator": float(mp_instance.ma_indicator),
            "bw_indicator": MySQLdb.Binary(
                mp_instance.x_env.bearing_amp.astype(np.float32)
            ),
            "al_indicator": float(mp_instance.al_indicator),
            "bl_indicator": float(mp_instance.bl_indicator),
            "rb_indicator": float(mp_instance.rb_indicator),
            "env_kurtosis": float(mp_instance.x_env.kurtosis),
            "vel_thd": float(mp_instance.x_vel.thd),
        },
    )


def motor_non_driven_end_diagnosis(data, fs, R, bearing_ratio: dict, th: dict):
    data = np.fromstring(data, dtype=np.float32)
    x = VibrationSignal(data=data, fs=fs, type=2)
    mp_instance = MotorNonDriven(
        x=x,
        y=x,
        r=R,
        bearing_ratio=bearing_ratio,
        ib_threshold=th["Unbalance"],
        bw_threshold=th["RollBearing"],
        al_threshold=th["ALoose"],
        bl_threshold=th["BLoose"],
        thd_threshold=th["thd"],
        pd_threshold=0,
        kurtosis_threshold=th["kurtosis"],
        harmonic_threshold=th["harmonic_threshold"],
    )
    mp_instance.diagnosis()
    return (
        mp_instance.fault_diag_result,
        {
            "ib_mark": int(mp_instance.x_vel.harmonics_index[1]),
            "al_mark": int(mp_instance.x_vel.harmonics_index[1]),
            "bl_mark": [int(item) for item in mp_instance.x_vel.harmonics_index],
            "bw_mark": [int(item) for item in mp_instance.x_env.bearing_index],
        },
        {
            "ib_indicator": float(mp_instance.ib_indicator),
            "bw_indicator": MySQLdb.Binary(
                mp_instance.x_env.bearing_amp.astype(np.float32)
            ),
            "al_indicator": float(mp_instance.al_indicator),
            "bl_indicator": float(mp_instance.bl_indicator),
            "env_kurtosis": float(mp_instance.x_env.kurtosis),
            "vel_thd": float(mp_instance.x_vel.thd),
        },
    )


def pump_driven_end_diagnosis(data, fs, R, bearing_ratio: dict, th: dict):
    data = np.fromstring(data, dtype=np.float32)
    x = VibrationSignal(data=data, fs=fs, type=2)
    mp_instance = PumpDriven(
        x=x,
        y=x,
        r=R,
        bearing_ratio=bearing_ratio,
        ib_threshold=th["Unbalance"],
        ma_threshold=th["Misalignment"],
        bw_threshold=th["RollBearing"],
        al_threshold=th["ALoose"],
        bl_threshold=th["BLoose"],
        sg_threshold=th["Surge"],
        rb_threshold=th["Rubbing"],
        thd_threshold=th["thd"],
        pd_threshold=0,
        kurtosis_threshold=th["kurtosis"],
        harmonic_threshold=th["harmonic_threshold"],
        subharmonic_threshold=th["subharmonic_threshold"],
    )
    mp_instance.diagnosis()
    return (
        mp_instance.fault_diag_result,
        {
            "ib_mark": int(mp_instance.x_vel.harmonics_index[1]),
            "ma_mark": int(mp_instance.x_vel.harmonics_index[2]),
            "al_mark": int(mp_instance.x_vel.harmonics_index[1]),
            "bl_mark": [int(item) for item in mp_instance.x_vel.harmonics_index],
            "rb_mark": [int(item) for item in mp_instance.x_vel.harmonics_index[:5]]
            + [int(item) for item in mp_instance.x_vel.sub_harmonics_index],
            "bw_mark": [int(item) for item in mp_instance.x_env.bearing_index],
            "sg_mark": [int(item) for item in mp_instance.sg_index],
        },
        {
            "ib_indicator": float(mp_instance.ib_indicator),
            "ma_indicator": float(mp_instance.ma_indicator),
            "bw_indicator": MySQLdb.Binary(
                mp_instance.x_env.bearing_amp.astype(np.float32)
            ),
            "al_indicator": float(mp_instance.al_indicator),
            "bl_indicator": float(mp_instance.bl_indicator),
            "sg_indicator": float(mp_instance.sg_indicator),
            "rb_indicator": float(mp_instance.rb_indicator),
            "env_kurtosis": float(mp_instance.x_env.kurtosis),
            "vel_thd": float(mp_instance.x_vel.thd),
        },
    )


def pump_non_driven_end_diagnosis(data, fs, R, bearing_ratio: dict, th: dict):
    data = np.fromstring(data, dtype=np.float32)
    x = VibrationSignal(data=data, fs=fs, type=2)
    mp_instance = PumpNonDriven(
        x=x,
        y=x,
        r=R,
        bearing_ratio=bearing_ratio,
        ib_threshold=th["Unbalance"],
        bw_threshold=th["RollBearing"],
        al_threshold=th["ALoose"],
        bl_threshold=th["BLoose"],
        sg_threshold=th["Surge"],
        thd_threshold=th["thd"],
        pd_threshold=0,
        kurtosis_threshold=th["kurtosis"],
        harmonic_threshold=th["harmonic_threshold"],
    )
    mp_instance.diagnosis()
    return (
        mp_instance.fault_diag_result,
        {
            "ib_mark": int(mp_instance.x_vel.harmonics_index[1]),
            "al_mark": int(mp_instance.x_vel.harmonics_index[1]),
            "bl_mark": [int(item) for item in mp_instance.x_vel.harmonics_index],
            "bw_mark": [int(item) for item in mp_instance.x_env.bearing_index],
            "sg_mark": [int(item) for item in mp_instance.sg_index],
        },
        {
            "ib_indicator": float(mp_instance.ib_indicator),
            "bw_indicator": MySQLdb.Binary(
                mp_instance.x_env.bearing_amp.astype(np.float32)
            ),
            "al_indicator": float(mp_instance.al_indicator),
            "bl_indicator": float(mp_instance.bl_indicator),
            "sg_indicator": float(mp_instance.sg_indicator),
            "env_kurtosis": float(mp_instance.x_env.kurtosis),
            "vel_thd": float(mp_instance.x_vel.thd),
        },
    )
