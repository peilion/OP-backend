from services.signal.electric.electric_class import ElectricSignal, ThreePhaseElectric
from utils.serializer import binary_deserializer


def three_phase_fast_fournier_transform(u: str, v: str, w: str) -> dict:
    res = {}
    for phase, phase_name in zip([u, v, w], ["u", "v", "w"]):
        x = ElectricSignal(
            data=binary_deserializer(phase), fs=20480, compute_axis=False,type=0
        )
        x.compute_spectrum(compute_axis=False)
        res[phase_name + "cur"] = x.data
        res[phase_name + "fft"] = x.spec[:300]
    return res

def three_phase_hilbert_transform(u: str, v: str, w: str) -> dict:
    res = {}
    for phase, phase_name in zip([u, v, w], ["u", "v", "w"]):
        x = ElectricSignal(
            data=binary_deserializer(phase), fs=20480, compute_axis=False,type=0
        )

        env = x.to_envelope()
        env.compute_spectrum(compute_axis=False)

        res[phase_name + "env"] = env.data
        res[phase_name + "env_fft"] = env.spec[:300]
    return res

def dq_transform(u: str, v: str, w: str) -> dict:
    three_phase = ThreePhaseElectric(
        u=ElectricSignal(data=binary_deserializer(u), fs=20480, compute_axis=False, type=0),
        v=ElectricSignal(data=binary_deserializer(v), fs=20480, compute_axis=False, type=0),
        w=ElectricSignal(data=binary_deserializer(w), fs=20480, compute_axis=False, type=0)
    )
    d, q = three_phase.dq0_transform()
    return {'component_d':d,
            'component_q':q,}
