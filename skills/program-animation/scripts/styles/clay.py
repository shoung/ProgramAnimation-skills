"""Hand-modelled clay forms. Each lump is a smoothly lit ellipsoid with a pinched silhouette."""

import math
import random

import numpy as np
from coast import SIZE, gradient, grain
from PIL import Image, ImageColor, ImageDraw, ImageFilter


def lump(im, cx, cy, rx, ry, color, tilt=0, salt=0):
    """Shade an ellipsoid in its local tangent plane; deterministic small dents catch the light."""
    r = math.ceil(max(rx, ry) * 1.12) + 2
    x0, y0 = max(0, int(cx) - r), max(0, int(cy) - r)
    x1, y1 = min(SIZE[0], int(cx) + r + 1), min(SIZE[1], int(cy) + r + 1)
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    c, s = math.cos(tilt), math.sin(tilt)
    u = ((xx - cx) * c + (yy - cy) * s) / rx
    v = (-(xx - cx) * s + (yy - cy) * c) / ry
    ang = np.arctan2(v, u)
    radius = 1 + 0.021 * np.sin(ang * 3 + salt) + 0.014 * np.sin(ang * 5 + salt * 0.7)
    rad = np.sqrt(u * u + v * v) / radius
    alpha = np.clip((1 - rad) * min(rx, ry) + 0.5, 0, 1)
    z = np.sqrt(np.maximum(0, 1 - rad**2))
    lit = 0.76 + np.maximum(0, (-u * 0.43 - v * 0.72 + z * 0.54)) * 0.31
    lit += 0.014 * np.sin((xx + yy) * 0.9 + salt) * np.sin(yy * 0.13) + 0.008 * np.cos(yy * 0.73)
    base = np.array(ImageColor.getrgb(color))
    patch = lit[:, :, None] * base
    prior = np.asarray(im.crop((x0, y0, x1, y1)))
    mix = patch * alpha[:, :, None] + prior * (1 - alpha[:, :, None])
    im.paste(Image.fromarray(np.uint8(np.clip(mix, 0, 255))), (x0, y0))


def frame(t):
    im = gradient([(0, "#eec7b3"), (238, "#f2d7bd"), (251, "#82c9ce"), (270, "#64b6c4"), (540, "#458fa9")])
    rng = random.Random(180)
    # Low ridges on the soft blue tabletop catch sidelight like pressed clay.
    d = ImageDraw.Draw(im)
    for _ in range(4700):
        x, y = rng.uniform(-18, 961), rng.uniform(252, 542)
        phase = rng.uniform(0, 6)
        x += 2 * math.sin(t + phase)
        length = rng.uniform(2, 12) * (y / 360)
        col = rng.choice(["#76bfc9", "#77c3cc", "#66b6c4", "#60adbd", "#9acece"])
        d.arc((x, y, x + length, y + rng.uniform(1, 3)), 5, 165, fill=col, width=1)

    def rock(x, y, rx, ry, c, tilt=0):
        lump(im, x, y, rx, ry, c, tilt, rng.uniform(0, 9))

    for x, y, k in [(178, 89, 0.76), (725, 73, 0.92)]:
        x += 10 * math.sin(t)
        for dx, dy, r in [(-49, 5, 25), (-23, -3, 31), (2, -12, 36), (31, -2, 28), (52, 6, 21)]:
            rock(x + dx * k, y + dy * k, r * k, r * 0.6 * k, "#f7ead7")
    # Individual sandy cliff tiers overlap the ring of white surf.
    for j in range(38):
        a = j * math.tau / 38
        x, y = 515 + 270 * math.cos(a), 397 + 45 * math.sin(a)
        rock(x, y, 20 + rng.random() * 9, 5 + rng.random() * 4, "#f7edcc", 0.06 * math.cos(a + t))
    rock(517, 373, 257, 55, "#d5ab7b")
    for x, y, rx, ry, a in [
        (340, 368, 74, 49, -0.31),
        (398, 356, 95, 54, -0.32),
        (515, 362, 132, 60, 0),
        (631, 357, 96, 53, 0.19),
        (705, 379, 72, 39, 0.21),
    ]:
        rock(x, y, rx, ry, "#deb689", a)
    rock(523, 324, 211, 31, "#a3c782", -0.026)
    for x, y, rx, ry in [(177, 369, 36, 27), (219, 338, 28, 24), (767, 395, 27, 17)]:
        rock(x, y + 16, rx * 1.13, 6, "#eee8cc")
        rock(x, y, rx, ry, "#d4ac83")
        rock(x, y - ry * 0.66, rx * 0.78, ry * 0.28, "#9dbb7d")

    # Smoothed horizontal rolls and a curved endcap form each striped tower band.
    def roll(cx, y0, y1, w0, w1, color):
        y0, y1 = int(y0), int(y1)
        for y in range(y0, y1 + 1):
            f = (y - y0) / max(1, y1 - y0)
            r = w0 + (w1 - w0) * f + 1.1 * math.sin(f * math.pi)
            x0 = int(cx - r)
            xs = np.arange(x0, int(cx + r) + 1)
            n = (xs - cx) / r
            light = (
                0.82 + 0.19 * np.sqrt(np.maximum(0, 1 - n * n)) - 0.11 * n + 0.016 * math.sin(f * math.pi)
            )
            vals = np.asarray(ImageColor.getrgb(color)) * light[:, None]
            im.paste(Image.fromarray(np.uint8(np.clip(vals[None, :, :], 0, 255))), (x0, y))
        rock(cx, y1, w1, 4.5, color)

    cx = 607
    rock(cx + 3, 319, 40, 8, "#89a16a")
    for y0, y1, w0, w1, col in [
        (274, 314, 20, 23, "#f5e5ca"),
        (253, 275, 19, 20, "#c95d49"),
        (219, 254, 18, 19, "#f7e7ca"),
        (196, 220, 17, 18, "#cc6149"),
        (160, 197, 15, 17, "#f7e9ce"),
    ]:
        roll(cx, y0, y1, w0, w1, col)
    for y in [178, 238, 293]:
        rock(cx - 4, y, 3.1, 5, "#61655e")
    rock(cx, 157, 23, 6, "#555953")
    roll(cx, 132, 153, 13, 14, "#abc5bb")
    rock(cx, 144, 4, 6, "#ffe3a2")
    for x in [cx - 13, cx + 11]:
        d.line((x, 132, x, 154), fill="#6d7268", width=2)
    rock(cx, 131, 21, 6, "#ab5342")
    rock(cx, 126, 17, 10, "#c7634e")
    rock(cx, 116, 3, 4, "#98705a")

    def pine(x, y, k):
        rock(x, y + 1, 12 * k, 3 * k, "#8ca875")
        roll(x, y - 12 * k, y, 3 * k, 3.5 * k, "#977858")
        for level in range(3):
            ry = (13 - level * 1.7) * k
            rock(
                x,
                y - (14 + level * 10) * k,
                (13 - level * 2.6) * k,
                ry,
                ["#519b79", "#69ab80", "#86b683"][level],
            )

    for x, y, k in [(385, 325, 0.82), (405, 320, 1.19), (675, 318, 0.82), (702, 324, 0.7)]:
        pine(x, y, k)
    # Soft bevels retain the familiar geometry of the little keeper's house.
    d.rounded_rectangle((451, 281, 527, 314), radius=5, fill="#f6d6a2")
    d.polygon([(525, 282), (548, 276), (548, 307), (526, 314)], fill="#d9b37f")
    d.polygon([(447, 284), (460, 266), (529, 265), (539, 281)], fill="#cc7155")
    d.polygon([(529, 265), (550, 274), (553, 281), (539, 281)], fill="#ac604c")
    d.line((452, 281, 462, 268, 529, 267), fill="#e18e6d", width=3)
    for x in [463, 505]:
        d.rounded_rectangle((x, 291, x + 7, 299), radius=2, fill="#638a8a")
    d.rounded_rectangle((484, 295, 493, 314), radius=2, fill="#9e785b")
    for i in range(9):
        rock(431 - i * 5.3, 328 + i * 8, 9, 2.4, "#c89f70")
    x = 133 + 6 * math.sin(t)
    rock(x, 421 + math.cos(t), 16, 5, "#bb6b54")
    d.polygon([(x, 415), (x, 388), (x - 15, 414)], fill="#f3dc9e")
    return grain(im.filter(ImageFilter.GaussianBlur(0.32)), 2.3)
