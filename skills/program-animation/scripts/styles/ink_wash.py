"""Pooled black ink, dry splits and untouched paper in a shore-and-mountains study."""

from functools import lru_cache

import numpy as np
from coast import SIZE
from PIL import Image
from print_landscape import PALETTE

from styles import harbor_frame

COLORS = {
    **PALETTE,
    "sun": "#ba5846",
    "mountain": "#cac8bc",
    "face": "#62635e",
    "crest": "#e6e4d6",
    "ridge": "#aaa99f",
    "sea": "#e9e7d9",
    "stone": "#dedacb",
    "shade": "#282925",
    "seam": "#484741",
    "foam": "#676861",
    "land": "#383932",
    "rail": "#30332e",
    "step": "#737269",
    "lip": "#c6c3b3",
    "pine": "#232724",
    "leaf": "#383c36",
    "trunk": "#393931",
    "wall": "#f3ecdb",
    "red": "#242725",
    "roof": "#1e211f",
    "dark": "#292c29",
    "shadow": "#545650",
    "glass": "#9b9687",
    "lamp": "#e7ca91",
    "hull": "#262a29",
    "sail": "#6d6f69",
    "bird": "#545550",
}


@lru_cache(maxsize=1)
def damp_sheet():
    rng = np.random.default_rng(114)

    def noise(w, h):
        im = Image.fromarray(rng.integers(0, 255, (h, w), dtype="uint8")).resize(
            SIZE, Image.Resampling.BICUBIC
        )
        return (np.asarray(im, dtype=float) - 128) / 128

    return 0.52 * noise(37, 22) + 0.29 * noise(113, 68) + 0.19 * noise(470, 180)


frame = harbor_frame("ink-wash")
