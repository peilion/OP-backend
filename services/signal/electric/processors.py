from services.signal.electric.electric_class import ElectricSignal
from utils.serializer import binary_deserializer


def three_phase_fast_fournier_transform(u: str, v: str, w: str) -> dict:
    res = {}
    for phase, phase_name in zip([u, v, w], ["u", "v", "w"]):
        x = ElectricSignal(
            data=binary_deserializer(phase), fs=20480, compute_axis=False
        )
        x.compute_spectrum(compute_axis=False)
        res[phase_name + "cur"] = x.data
        res[phase_name + "fft"] = x.spec[:300]
    return res
