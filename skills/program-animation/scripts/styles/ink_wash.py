"""Wet mountain washes, broken dry-brush marks and vermilion on warm paper."""

import random

import numpy as np
from coast import BASE, SIZE, H, W, draw_mark, grain, scene
from PIL import Image, ImageDraw, ImageFilter

COLORS = {
    "sky": "#f0ecdd",
    "sun": "#bd5a47",
    "cloud": None,
    "distant": "#c5c4b8",
    "mountain": "#8c9086",
    "face": "#5e635f",
    "snow": "#e5e4d5",
    "ridge": "#787c74",
    "sea": "#e4e3d7",
    "ripple": "#a4a69a",
    "foam": "#f5f0df",
    "stone": "#565c54",
    "shade": "#373e39",
    "ochre": "#97988a",
    "crack": "#333b35",
    "land": "#74796c",
    "pine": "#28322d",
    "leaf": "#4b554c",
    "trunk": "#4b5048",
    "wall": "#f3edda",
    "shadow": "#c4c2b1",
    "red": "#3a403a",
    "roof": "#292e2c",
    "dark": "#232b29",
    "glass": "#bcbfaf",
    "lamp": "#ede2bd",
    "sail": "#d4d0bd",
    "hull": "#474c42",
    "bird": "#64685d",
}


def pigment():
    # Broad blooms follow the damp sheet, while dry fibers break the deposited ink.
    rng = np.random.default_rng(114)

    def field(w, h):
        noise = Image.fromarray(rng.integers(0, 255, (h, w), dtype="uint8"))
        return np.asarray(noise.resize(SIZE, Image.Resampling.BICUBIC), dtype=float) / 255

    return 0.56 * field(25, 14) + 0.32 * field(110, 58) + 0.12 * field(530, 110)


def frame(t):
    colors = {**BASE, **COLORS}
    im = Image.new("RGB", SIZE, colors["sky"])
    rng = random.Random(25)
    blooms = pigment()
    yy, xx = np.mgrid[:H, :W]
    for i, m in enumerate(scene(t)):
        if colors[m.role] is None or (m.role == "ripple" and i % 4):
            continue
        if m.role in {"distant", "mountain", "face", "snow"}:
            mask = Image.new("L", SIZE)
            draw_mark(ImageDraw.Draw(mask), m, 255)
            a = np.array(mask.filter(ImageFilter.GaussianBlur(1.6)), dtype=float)
            wet = np.clip(0.98 - (np.arange(H) - 150) * 0.004, 0.22, 1)
            # Mountain feet dissolve into mist; feather pigment down the slopes.
            wet = np.clip((332 - np.arange(H)) / 132, 0.04, 1) * wet
            strokes = 0.5 + 0.5 * np.sin(
                0.47 * xx + 0.40 * yy + 9 * np.sin(yy * 0.037 + xx * 0.011) + 22 * blooms
            )
            wash = np.clip(0.20 + 1.10 * blooms + 0.24 * strokes, 0, 1)
            if m.role == "snow":
                wash *= 0.8
            mask = Image.fromarray(np.uint8(a * wet[:, None] * wash))
            im.paste(colors[m.role], (0, 0), mask)
            continue
        if m.role == "ridge":
            continue
        if m.role in {"shade", "ochre"}:
            wash = Image.new("L", SIZE)
            draw_mark(ImageDraw.Draw(wash), m, 255)
            opacity = np.clip(0.20 + (blooms - 0.32) * 1.4, 0.1, 0.82)
            im.paste(colors[m.role], (0, 0), Image.fromarray(np.uint8(np.asarray(wash) * opacity)))
        else:
            draw_mark(ImageDraw.Draw(im), m, colors[m.role])
        if m.role in {"stone", "shade", "ochre"}:
            mask = Image.new("L", SIZE)
            draw_mark(ImageDraw.Draw(mask), m, 255)
            scratch = im.copy()
            d = ImageDraw.Draw(scratch)
            x0, y0, x1, y1 = mask.getbbox() or (0, 0, 1, 1)
            for _ in range(max(4, (x1 - x0) * (y1 - y0) // 255)):
                x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
                d.line(
                    (x, y, x - 6, y + rng.uniform(4, 20)),
                    fill=rng.choice(["#353b35", "#a5a495", "#707368"]),
                    width=rng.choice([1, 1, 2]),
                )
            im.paste(scratch, (0, 0), mask)
    # A small carved collector's seal in the margin.
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((46, 72, 69, 99), radius=2, outline="#ac5043", width=3)
    for line in [
        [(51, 76), (51, 94), (56, 94), (56, 77)],
        [(59, 77), (64, 77), (64, 83), (60, 83), (60, 93), (65, 93)],
    ]:
        d.line(line, fill="#ac5043", width=2)
    # Ragged, ink-wicked edges survive reduction better than uniform digital contours.
    offsets = np.rint((blooms - 0.5) * 5).astype(int)
    ink = np.asarray(im)[np.clip(yy + offsets, 0, H - 1), np.clip(xx - offsets, 0, W - 1)].astype(float)
    absorb = (blooms - 0.49) * (0.19 * (241 - ink[:, :, 1]) + 5)
    im = Image.fromarray(np.uint8(np.clip(ink + absorb[:, :, None], 0, 255)))
    return grain(im, 3.2, 1)
