"""Stable surface samples and contour points, plus a sparse drifting star field."""

import numpy as np
from coast import H, W
from night import night
from PIL import Image, ImageFilter


def frame(t):
    src = night(t)
    rgb = np.asarray(src).astype(float)
    edge = np.asarray(src.convert("L").filter(ImageFilter.FIND_EDGES)).astype(float) / 255
    edge[[0, -1], :] = 0
    edge[:, [0, -1]] = 0
    y = np.arange(H)[:, None]
    rng = np.random.default_rng(251)
    brightness = rgb.max(2) / 255
    prob = 0.009 + 0.48 * brightness**1.8 + 0.57 * edge
    picked = rng.random((H, W)) < prob
    py, px = np.nonzero(picked)
    # Depth-dependent displacement moves the samples in the beam without crawling noise.
    drift = np.sin(t + py * 0.018) * (0.4 + brightness[py, px])
    px2 = np.clip(np.rint(px + drift).astype(int), 0, W - 1)
    stars = (rng.random((H, W)) < 0.0006) & (y < 230)
    field = np.zeros((H, W, 3), dtype=float) + [9, 17, 29]
    field[stars] = [130, 143, 149]
    field[py, px2] = np.clip(rgb[py, px] * (1.3 + edge[py, px, None]) + [12, 17, 16], 0, 255)
    dots = Image.fromarray(field.astype("uint8"))
    glow = np.asarray(dots.filter(ImageFilter.GaussianBlur(2.6))).astype(float)
    return Image.fromarray(np.uint8(np.clip(field + glow * 0.32, 0, 255)))
