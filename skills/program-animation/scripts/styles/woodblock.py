"""Indigo bokashi, vermilion sun and carved ribbons of cloud above short printed waves."""

import numpy as np
from coast import draw_mark, gradient, grain
from lettering import titled
from PIL import Image, ImageDraw
from print_landscape import PALETTE, plate_scene, wavelets

COLORS = {
    **PALETTE,
    "sun": "#b54632",
    "cloud": "#f4e8c8",
    "mountain": "#87a9b8",
    "face": "#375e84",
    "crest": "#f7e8d0",
    "ridge": "#567c91",
    "sea": "#476e8a",
    "stone": "#d5ac69",
    "shade": "#b58554",
    "pine": "#43776c",
    "land": "#9e995d",
    "red": "#b54734",
    "wall": "#f1e4ca",
    "roof": "#914c3a",
}


@titled("woodblock")
def frame(t):
    im = gradient([(0, "#253f63"), (58, "#607895"), (152, "#dfc7a4"), (316, "#f1dfbb")])
    d = ImageDraw.Draw(im)
    for m in plate_scene(t, summit=196, horizon=378):
        edge = (
            "#42494b"
            if m.role in {"cloud", "mountain", "stone", "roof", "wall", "pine", "land", "red"}
            else None
        )
        draw_mark(d, m, COLORS[m.role], edge, 2 if m.role == "cloud" else 1)
        if m.role == "sea":
            wavelets(d, t, 378, ["#a0b0ac", "#99a8a2", "#dacfaa", "#324d6a", "#314c6b"], 1900)
    y, x = np.ogrid[:540, :960]
    # Low ridges of longitudinal wood grain show through the colored impressions.
    fiber = (
        0.5 + 0.5 * np.sin(y * 1.81 + 1.45 * np.sin(x * 0.008 + y * 0.034) + 0.44 * np.sin(x * 0.023))
    ) ** 9
    rgb = np.asarray(im, dtype=float)
    ink = (246 - rgb) * (0.045 * fiber[:, :, None])
    return grain(Image.fromarray(np.uint8(np.clip(rgb + ink, 0, 255))), 2.6, 1.1)
