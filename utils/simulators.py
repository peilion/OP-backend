import numpy as np


def unbalance(AMP, FN, FS=51200, T=10):
    t = np.linspace(0, T, FS * T)
    x = AMP * np.sin(2 * np.pi * FN * t) + np.random.normal(
        scale=AMP * 0.1, size=len(t)
    )
    y = AMP * np.sin(2 * np.pi * FN * t + np.pi / 2) + np.random.normal(
        scale=AMP * 0.1, size=len(t)
    )

    return x, y


def misalignment(AMP, FN, FS=51200, T=10):
    t = np.linspace(0, T, FS * T)
    x = (
        AMP * 0.5 * np.sin(2 * np.pi * FN * t)
        + AMP * np.sin(2 * np.pi * 2 * FN * t)
        + AMP * 0.25 * np.sin(2 * np.pi * 4 * FN * t)
        + np.random.normal(scale=AMP * 0.1, size=len(t))
    )

    y = (
        AMP * 0.5 * np.sin(2 * np.pi * FN * t + np.pi / 2)
        + AMP * np.sin(2 * np.pi * 2 * FN * t + np.pi / 2)
        + AMP * 0.25 * np.sin(2 * np.pi * 4 * FN * t + np.pi / 2)
        + np.random.normal(scale=AMP * 0.1, size=len(t))
    )

    return x, y


def a_loose(AMP, FN, FS=51200, T=10):
    t = np.linspace(0, T, FS * T)
    x = AMP * np.sin(2 * np.pi * FN * t) + np.random.normal(
        scale=AMP * 0.1, size=len(t)
    )
    y = 0.5 * AMP * np.sin(2 * np.pi * FN * t + np.pi / 2 * 0.1) + np.random.normal(
        scale=0.5 * AMP * 0.1, size=len(t)
    )

    return x, y


def b_loose(AMP, FN, FS=51200, T=10):
    t = np.linspace(0, T, FS * T)
    x = (
        AMP * np.sin(2 * np.pi * FN * 0.5 * t)
        + AMP * 0.5 * np.sin(2 * np.pi * FN * t)
        + AMP * 0.25 * np.sin(2 * np.pi * 2 * FN * t)
        + AMP * 0.1 * np.sin(2 * np.pi * 3 * FN * t)
        + np.random.normal(scale=AMP * 0.1, size=len(t))
    )

    y = (
        AMP * np.sin(2 * np.pi * FN * 0.5 * t + np.pi / 2)
        + AMP * np.sin(2 * np.pi * FN * t + np.pi / 2)
        + AMP * 0.5 * np.sin(2 * np.pi * 2 * FN * t + np.pi / 2)
        + AMP * 0.25 * np.sin(2 * np.pi * 3 * FN * t + np.pi / 2)
        + np.random.normal(scale=AMP * 0.1, size=len(t))
    )
    return x, y


def rolling_bearing(AMP, FN, bearing_ratios, FS=51200, T=10, FRES=2000):
    t = np.linspace(0, T, FS * T)
    x = AMP * np.sin(2 * np.pi * FN * t) + AMP * np.sin(2 * np.pi * FRES * t)
    for bearing_ratio in bearing_ratios:
        for order in (1, 2, 3):
            x = (
                x
                + 0.01
                * AMP
                * np.sin(2 * np.pi * (FRES + order * bearing_ratio * FN) * t)
                + 0.01
                * AMP
                * np.sin(2 * np.pi * (FRES - order * bearing_ratio * FN) * t)
            )

    return x, x


def oil_whirl(AMP, FN, FS=51200, T=10):
    t = np.linspace(0, T, FS * T)
    x = (
        0.8 * AMP * np.sin(2 * np.pi * FN * 0.46 * t)
        + AMP * np.sin(2 * np.pi * FN * t)
        + np.random.normal(scale=AMP * 0.1, size=len(t))
    )

    y = (
        0.8 * AMP * np.sin(2 * np.pi * FN * 0.46 * t + np.pi / 2)
        + AMP * np.sin(2 * np.pi * FN * t + np.pi / 2)
        + np.random.normal(scale=AMP * 0.1, size=len(t))
    )
    return x, y


def gear(AMP, FN, MESH_RATIO, FS=51200, T=10):
    t = np.linspace(0, T, FS * T)
    MESH_FREQ = MESH_RATIO * FN
    x = 0.5 * AMP * np.sin(2 * np.pi * FN * t)

    for central_order in (1, 2, 3):
        for side_order in (1, 2, 3, 4, 5, 6):
            x = x + (1 - 0.3 * central_order) * AMP * (
                0.2 * np.sin(2 * np.pi * central_order * MESH_FREQ * t)
                + 0.1
                * np.sin(2 * np.pi * (central_order * MESH_FREQ - side_order * FN) * t)
                + 0.1
                * np.sin(2 * np.pi * (central_order * MESH_FREQ + side_order * FN) * t)
            )
    return x, x


def rubbing(AMP, FN, FS=51200, T=10):
    t = np.linspace(0, T, FS * T)
    x = np.random.normal(scale=AMP * 0.1, size=len(t))
    y = np.random.normal(scale=AMP * 0.1, size=len(t))
    for i in range(2, 10):
        x = (
            x
            + 0.1 * i * AMP * np.sin(2 * np.pi * FN * (i + 0.5) * t)
            + 0.2 * i * AMP * np.sin(2 * np.pi * FN * (i + 1) * t)
        )

        y = (
            y
            + 0.1 * i * AMP * np.sin(2 * np.pi * FN * (i + 0.5) * t + np.pi / 2)
            + 0.2 * i * AMP * np.sin(2 * np.pi * FN * (i + 1) * t + np.pi / 2)
        )

    return x, y


def surge(AMP, FN, FS=51200, T=10):
    t = np.linspace(0, T, FS * T)
    x = AMP * np.sin(2 * np.pi * FN * t) + np.random.normal(
        scale=AMP * 0.1, size=len(t)
    )
    y = AMP * np.sin(2 * np.pi * FN * t + np.pi / 2) + np.random.normal(
        scale=AMP * 0.1, size=len(t)
    )
    for i in (1, 2, 3, 4, 6, 7, 8, 9):
        x = x + AMP * 0.5 * (np.sin(2 * np.pi * FN * 0.1 * i * t))
        y = y + AMP * 0.5 * (np.sin(2 * np.pi * FN * 0.1 * i * t + np.pi / 2))

    return x, y
