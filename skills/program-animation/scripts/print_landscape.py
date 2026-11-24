"""Compose printed coastal plates with tiered rocks, a fixed horizon, and registerable ink shapes."""

import math
import random

from coast import BASE, Mark
from headland import landscape

PALETTE = {
    **BASE,
    "crest": "#e9d6c3",
    "rail": "#705142",
    "step": "#c38c65",
    "seam": "#a77359",
    "lip": "#d9b481",
}
RIDGES = {"mountain", "face", "crest", "ridge"}


def ribbon(x, y, width, thickness):
    # A long mist band folds back on itself; rounded ends approximate the carved key block.
    pts = []
    # Trace a single non-self-intersecting outline around two connected cloud banks.
    for u, v in [
        (0.018, 0),
        (0.64, 0),
        (0.654, 0.045),
        (0.66, 0.14),
        (0.654, 0.245),
        (0.64, 0.30),
        (0.49, 0.30),
        (0.48, 0.36),
        (0.48, 0.48),
        (0.49, 0.54),
        (0.98, 0.54),
        (0.994, 0.60),
        (1, 0.74),
        (0.994, 0.89),
        (0.98, 0.96),
        (0.32, 0.96),
        (0.305, 0.89),
        (0.30, 0.75),
        (0.305, 0.61),
        (0.32, 0.54),
        (0.38, 0.54),
        (0.39, 0.48),
        (0.39, 0.36),
        (0.38, 0.30),
        (0.018, 0.30),
        (0.005, 0.24),
        (0, 0.15),
        (0.005, 0.05),
    ]:
        pts.append((x + u * width, y + v * thickness))
    return Mark("poly", "cloud", pts)


def plate_scene(t, *, summit=201, horizon=365, cloud_style="ribbon"):
    marks = landscape(t)
    result = []
    for m in marks:
        if m.role == "cloud":
            if cloud_style == "puffs":
                result.append(m)
            continue
        if m.role in RIDGES:
            result.append(
                Mark(
                    m.kind,
                    m.role,
                    [(x, summit + (y - 168) * (horizon - summit) / 208) for x, y in m.xy],
                    m.width,
                )
            )
            continue
        if m.role == "sea":
            if cloud_style == "ribbon":
                drift = 8 * math.sin(t)
                result.extend(
                    [
                        ribbon(318 + drift, 130, 391, 33),
                        ribbon(-140 + drift, 285, 657, 36),
                        ribbon(681 - drift, 270, 418, 34),
                    ]
                )
            result.append(Mark("poly", "sea", [(0, horizon), (960, horizon), (960, 540), (0, 540)]))
        else:
            result.append(m)
    return result


def wavelets(draw, t, horizon, colors, count=1300):
    rng = random.Random(393)
    for _ in range(count):
        y = rng.uniform(horizon + 1, 542)
        depth = (y - horizon) / (540 - horizon)
        x = rng.uniform(-45, 966) + math.sin(t + y * 0.09) * 2
        w = rng.uniform(4, 27) * (1 + depth)
        h = rng.uniform(0.2, 2) * (1 + depth)
        draw.line(
            [(x, y), (x + w * 0.25, y - h), (x + w * 0.70, y - h * 0.6), (x + w, y)],
            fill=rng.choice(colors),
            width=1 + int(depth > 0.65 and w > 34),
        )
