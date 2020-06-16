import numpy as np

from services.signal.electric.electric_class import ElectricSignal, ThreePhaseElectric
from services.signal.electric.electric_class import make_phase, cal_symm
from utils.serializer import binary_deserializer


def three_phase_fast_fournier_transform(
    u: str, v: str, w: str, if_return_raw: bool = True
) -> dict:
    res = {}
    for phase, phase_name in zip([u, v, w], ["u", "v", "w"]):
        x = ElectricSignal(
            data=binary_deserializer(phase), fs=10000, compute_axis=False, type=0
        )
        x.compute_spectrum(compute_axis=False)
        if if_return_raw:
            res[phase_name + "cur"] = x.data
        res[phase_name + "fft"] = x.spec[:300]
    return res


def three_phase_hilbert_transform(u: str, v: str, w: str) -> dict:
    res = {}
    for phase, phase_name in zip([u, v, w], ["u", "v", "w"]):
        x = ElectricSignal(
            data=binary_deserializer(phase), fs=10000, compute_axis=False, type=0
        )

        env = x.to_envelope()
        env.compute_spectrum(compute_axis=False)

        res[phase_name + "env"] = env.data
        res[phase_name + "env_fft"] = env.spec[:300]
    return res


def dq_transform(u: str, v: str, w: str) -> dict:
    three_phase = ThreePhaseElectric(
        u=ElectricSignal(
            data=binary_deserializer(u), fs=10000, compute_axis=False, type=0
        ),
        v=ElectricSignal(
            data=binary_deserializer(v), fs=10000, compute_axis=False, type=0
        ),
        w=ElectricSignal(
            data=binary_deserializer(w), fs=10000, compute_axis=False, type=0
        ),
    )
    d, q = three_phase.dq0_transform()
    return {"component_d": d, "component_q": q}


def sym_analyze(res):
    complex_list = []
    for item in ["u", "v", "w"]:
        complex_phase, _ = make_phase(
            res[item + "amplitude"],
            2 * np.pi * res[item + "frequency"],
            res[item + "initial_phase"],
            samples=1024,
            end_time=1024 / 10000,
        )
        # Append to the list
        complex_list.append(complex_phase)

    (
        phaseA_pos,
        phaseB_pos,
        phaseC_pos,
        phaseA_neg,
        phaseB_neg,
        phaseC_neg,
        phaseZero,
    ) = cal_symm(complex_list[0], complex_list[1], complex_list[2])
    return {
        "A_pos_real": phaseA_pos.real,
        "B_pos_real": phaseB_pos.real,
        "C_pos_real": phaseC_pos.real,
        "A_neg_real": phaseA_neg.real,
        "B_neg_real": phaseB_neg.real,
        "C_neg_real": phaseC_neg.real,
        "zero_real": phaseZero.real,
        "A_pos_img": phaseA_pos.imag,
        "B_pos_img": phaseB_pos.imag,
        "C_pos_img": phaseC_pos.imag,
        "A_neg_img": phaseA_neg.imag,
        "B_neg_img": phaseB_neg.imag,
        "C_neg_img": phaseC_neg.imag,
        "zero_img": phaseZero.imag,
    }
