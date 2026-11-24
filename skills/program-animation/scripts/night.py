"""Luminance master for the two-ink maritime engraving."""

import numpy as np
from coast import SIZE, H, W, draw_mark
from headland import landscape
from PIL import Image, ImageDraw

VALUES = {
    "sun": 185,
    "cloud": 17,
    "mountain": 21,
    "crest": 34,
    "face": 15,
    "ridge": 156,
    "sea": 18,
    "stone": 88,
    "shade": 30,
    "land": 123,
    "seam": 50,
    "lip": 165,
    "foam": 117,
    "pine": 51,
    "leaf": 92,
    "trunk": 45,
    "rail": 79,
    "step": 108,
    "wall": 171,
    "shadow": 100,
    "red": 64,
    "roof": 62,
    "dark": 40,
    "glass": 124,
    "lamp": 235,
    "sail": 115,
    "hull": 65,
    "bird": 98,
}


def night(t):
    paper = Image.new("L", SIZE, 21)
    d = ImageDraw.Draw(paper)
    for m in landscape(t):
        outline = (
            193
            if m.role in {"mountain", "cloud"}
            else 175
            if m.role in {"stone", "land", "wall", "roof", "pine"}
            else None
        )
        draw_mark(d, m, VALUES[m.role], outline, 2)
    v = np.asarray(paper, dtype=float)
    y, x = np.ogrid[:H, :W]
    dx = x - 626
    beam = np.exp(-(((y - 94 - 0.025 * dx * np.sin(t)) / (2.8 + abs(dx) * 0.055)) ** 2)) * np.exp(
        -abs(dx) / 830
    )
    r = np.hypot((x - 329) / 51, (y - 197) / 51)
    moon = v == 185
    v += moon * (
        24 * np.cos(x * 0.14 + y * 0.06) + 16 * np.sin(y * 0.18) + 46 * np.exp(-(((r - 0.97) / 0.06) ** 2))
    )
    tower = (x > 592) & (x < 658) & (y > 103) & (y < 315) & (np.asarray(paper) > 35)
    v *= np.where(tower, 0.55 + 0.56 * np.exp(-(((x - 616) / 15) ** 2)), 1.0)
    v += beam * 176 + np.exp(-((dx / 14) ** 2 + ((y - 94) / 13) ** 2)) * 90
    water = (np.asarray(paper) == 18) & (y >= 376)
    wake = (0.5 + 0.5 * np.cos(y * 0.62 + 0.85 * np.sin(x * 0.022 + y * 0.061) + t)) ** 4
    v += (
        water
        * wake
        * (
            23
            + 165
            * np.exp(-(((x - 329 - 6 * np.sin(y * 0.16 + t)) / (14 + np.maximum(y - 376, 0) * 0.28)) ** 2))
        )
    )
    return Image.fromarray(np.uint8(np.clip(v, 0, 255)))
