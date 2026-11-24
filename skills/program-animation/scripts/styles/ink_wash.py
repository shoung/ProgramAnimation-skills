"""Pooled black ink, dry splits and untouched paper in a shore-and-mountains study."""

import math
import random
from functools import lru_cache

import numpy as np
from coast import SIZE, H, W, draw_mark, grain
from lettering import titled
from PIL import Image, ImageDraw
from print_landscape import PALETTE, plate_scene

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


@titled("ink-wash")
def frame(t):
    wash = damp_sheet()
    y, x = np.mgrid[:H, :W]
    im = Image.new("RGB", SIZE, "#eeebde")
    d = ImageDraw.Draw(im)
    rng = random.Random(934)
    for m in plate_scene(t, summit=221, horizon=322, cloud_style="none"):
        if m.role == "ridge":
            continue
        color = COLORS[m.role]
        if m.role in {"mountain", "face", "crest"}:
            peak = min(m.xy, key=lambda p: p[1])
            mask = Image.new("L", SIZE)
            draw_mark(ImageDraw.Draw(mask), m, 255)
            near = peak[0] < 210
            f = np.clip((338 - y) / 95, 0, 1)
            strength = (0.35 + 0.6 * near) * f * (0.89 + 0.22 * wash)
            if m.role == "face" and near:
                color = "#262923"
            im.paste(color, (0, 0), Image.fromarray(np.uint8(np.clip(np.asarray(mask) * strength, 0, 255))))
            continue
        draw_mark(d, m, color)
        if m.role == "sea":
            for i in range(140):
                py = rng.uniform(325, 539)
                px = rng.uniform(-80, 960) + 3 * math.sin(t + py)
                length = rng.uniform(3, 72) * (1 + (py - 320) / 310)
                d.polygon(
                    [
                        (px, py),
                        (px + length * 0.28, py - rng.uniform(0.3, 1.8)),
                        (px + length, py),
                        (px + length * 0.36, py + 0.4),
                    ],
                    fill=rng.choice(["#cac8bc", "#d3d1c4", "#acaba1"]),
                )
        if m.role == "stone":
            xs, ys = zip(*m.xy)
            w = max(xs) - min(xs)
            if w < 45:
                continue
            mask = Image.new("L", SIZE)
            draw_mark(ImageDraw.Draw(mask), m, 255)
            strokes = im.copy()
            q = ImageDraw.Draw(strokes)
            for _ in range(max(2, int(w / 27))):
                px = rng.uniform(min(xs), max(xs))
                py = rng.uniform(min(ys) - 9, max(ys))
                a = rng.uniform(4, 16)
                q.polygon(
                    [
                        (px, py),
                        (px + a, py - 2),
                        (px + a * 0.7, py + 12),
                        (px + a * 1.3, py + 24),
                        (px + a * 0.65, py + 31),
                        (px - 2, py + 14),
                    ],
                    fill=rng.choice(["#32342e", "#56564f", "#808078"]),
                )
            im.paste(strokes, (0, 0), mask)
        if m.role == "foam":
            d.line([(px + 2, py + 3) for px, py in m.xy], fill="#74736a", width=2)
            xs, ys = zip(*m.xy)
            left, right = min(xs), max(xs)
            y0 = max(ys) + 5
            # The brush pools at touchdown and dries into separated hairs across the water.
            for j in range(3):
                a = left + rng.uniform(-17, 7)
                b = a + (right - left) * rng.uniform(0.28, 1.15)
                yy = y0 + j * 3.3
                d.polygon(
                    [
                        (a, yy),
                        (a + (b - a) * 0.17, yy - 1.1),
                        (b, yy - 0.7),
                        (a + (b - a) * 0.32, yy + 0.9),
                    ],
                    fill=["#5b5e55", "#989990", "#c0bfb4"][j],
                )
    # Directional dry fibers lift small flecks only from the dark ink deposits.
    offset = np.rint(3.8 * wash).astype(int)
    ink = np.asarray(im)[np.clip(y + offset, 0, H - 1), np.clip(x - offset, 0, W - 1)].astype(float)
    fiber = 0.5 + 0.5 * np.sin(x * 0.63 + y * 0.105 + wash * 5)
    dry = np.maximum(0, wash + 0.18) * (244 - ink[:, :, 0]) * (0.13 + 0.19 * fiber)
    dry += (
        np.clip((fiber - 0.93) * 8, 0, 1)
        * np.clip((wash - 0.18) * 3, 0, 1)
        * np.clip(109 - ink[:, :, 0], 0, 100)
        * 0.62
    )
    return grain(Image.fromarray(np.uint8(np.clip(ink + dry[:, :, None], 0, 255))), 2.1, 0.7)
