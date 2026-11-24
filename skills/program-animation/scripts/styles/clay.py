"""Hand-modelled clay forms. Each lump is a smoothly lit ellipsoid with a pinched silhouette."""

import math
import random
from functools import lru_cache

import numpy as np
from coast import SIZE, gradient, grain
from lettering import titled
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


@lru_cache(maxsize=1)
def tool_marks():
    # Three physical scales: thumb pressure, shaping tool and fine granules.
    rng = np.random.default_rng(143)
    height = np.zeros((540, 960), dtype=float)
    for w, h, amplitude in [(33, 25, 2.9), (135, 90, 1.1), (510, 270, 0.29)]:
        values = Image.fromarray(rng.integers(0, 256, (h, w), dtype=np.uint8))
        height += amplitude * np.asarray(values.resize(SIZE, Image.Resampling.BICUBIC), dtype=float) / 255
    gy, gx = np.gradient(height)
    return np.clip(0.58 * gx + 0.89 * gy, -0.17, 0.17)


def clay_slab(im, rim, depth, turf, salt):
    """Extrude an irregular top face, bevel its edges and catch light in pressed dents."""
    faces = []
    low = [
        (x + 4 + 5 * math.sin(i * 2.7 + salt), y + depth * (0.95 + 0.05 * math.sin(i)))
        for i, (x, y) in enumerate(rim)
    ]
    for i in range(len(rim)):
        j = (i + 1) % len(rim)
        # Front edges run right-to-left in the clockwise plan.
        if rim[j][0] < rim[i][0]:
            direction = (rim[j][1] - rim[i][1]) / max(18, abs(rim[j][0] - rim[i][0]))
            shade = 0.94 + 0.11 * np.clip(direction, -1, 1)
            faces.append(([rim[i], rim[j], low[j], low[i]], np.array([230, 185, 130]) * shade))
    faces.append((rim, np.array(turf)))
    for points, color in faces:
        l, t, r, b = (
            min(x for x, y in points),
            min(y for x, y in points),
            max(x for x, y in points),
            max(y for x, y in points),
        )
        l, t, r, b = math.floor(l) - 4, math.floor(t) - 4, math.ceil(r) + 5, math.ceil(b) + 5
        mask = Image.new("L", (r - l, b - t))
        ImageDraw.Draw(mask).polygon([(x - l, y - t) for x, y in points], fill=255)
        rounded = mask.filter(ImageFilter.GaussianBlur(2.8)).point(lambda v: min(255, max(0, (v - 97) * 7)))
        # A lightly wavy outline, small thumb-shaped dents and scattered pores break up machined edges.
        gy, gx = np.indices((b - t, r - l))
        wrinkle = np.rint(
            1.2 * np.sin((gx + l) * 0.14 + (gy + t) * 0.09) + 0.65 * np.cos((gy + t) * 0.21)
        ).astype(int)
        rounded = Image.fromarray(np.asarray(rounded)[np.clip(gy + wrinkle, 0, b - t - 1), gx])
        relief = np.asarray(rounded.filter(ImageFilter.GaussianBlur(3)), dtype=float) / 255
        dy, dx = np.gradient(relief)
        y, x = np.ogrid[t:b, l:r]
        light = (
            1
            + 0.42 * dy
            + 0.33 * dx
            + 0.018 * np.sin(x * 0.075 + y * 0.092 + salt)
            + 0.014 * np.sin(x * 0.23 - y * 0.08)
        )
        for ox, oy in [(0.25, 0.39), (0.64, 0.68), (0.79, 0.23)]:
            xx = (x - l - ox * (r - l)) / max(9, (r - l) * 0.12)
            yy = (y - t - oy * (b - t)) / max(6, (b - t) * 0.17)
            light += 0.045 * (yy + 0.6 * xx) * np.exp(-(xx**2) - yy**2)
        pores = (np.sin(x * 0.41 + y * 0.17) * np.sin(y * 0.33 - x * 0.07)) ** 8
        surface = tool_marks()[t:b, l:r]
        light += surface * (0.58 if points is rim else 1.15)
        pixels = np.uint8(np.clip(color * light[:, :, None] - 7 * pores[:, :, None], 0, 255))
        im.paste(Image.fromarray(pixels), (l, t), rounded)


@titled("clay")
def frame(t):
    im = gradient([(0, "#eec7b3"), (225, "#efccb8"), (230, "#78c0dd"), (295, "#66b5d7"), (540, "#459ccb")])
    rng = random.Random(180)
    # Low ridges on the soft blue tabletop catch sidelight like pressed clay.
    d = ImageDraw.Draw(im)
    for _ in range(4700):
        x, y = rng.uniform(-18, 961), rng.uniform(231, 542)
        phase = rng.uniform(0, 6)
        x += 2 * math.sin(t + phase)
        length = rng.uniform(2, 12) * (y / 360)
        col = rng.choice(["#81c5db", "#75bdd7", "#59afd0", "#559fc6", "#98cede"])
        d.arc((x, y, x + length, y + rng.uniform(1, 3)), 5, 165, fill=col, width=1)

    def rock(x, y, rx, ry, c, tilt=0):
        lump(im, x, y, rx, ry, c, tilt, rng.uniform(0, 9))

    for x, y, k in [(418, 44, 0.75), (786, 16, 1.10)]:
        x += 10 * math.sin(t)
        for dx, dy, r in [(-49, 5, 25), (-23, -3, 31), (2, -12, 36), (31, -2, 28), (52, 6, 21)]:
            rock(x + dx * k, y + dy * k, r * k, r * 0.6 * k, "#f7ead7")
    # A broad soft shadow connects the hand-built set to the blue tabletop.
    shade = Image.new("L", SIZE)
    ImageDraw.Draw(shade).polygon(
        [(319, 424), (409, 402), (737, 385), (819, 410), (790, 430), (466, 454), (346, 449)], fill=104
    )
    im.paste("#497e99", (0, 0), shade.filter(ImageFilter.GaussianBlur(10)))
    # Clay foam is pressed against the shore in uneven strips and short clumps.
    coasts = [
        [(106, 421), (129, 427), (169, 422), (178, 416)],
        [(178, 395), (203, 405), (239, 400), (248, 394)],
        [
            (326, 441),
            (349, 450),
            (407, 453),
            (424, 446),
            (474, 446),
            (500, 439),
            (550, 447),
            (594, 441),
            (643, 445),
            (677, 433),
            (726, 432),
            (754, 419),
            (806, 416),
            (844, 403),
        ],
    ]
    for shore in coasts:
        d.line(shore, fill="#eee9d6", width=12, joint="curve")
        for j, (x1, y1) in enumerate(shore[1:]):
            x0, y0 = shore[j]
            for _ in range(max(1, round((x1 - x0) / 10))):
                u = rng.random()
                rock(
                    x0 + (x1 - x0) * u,
                    y0 + (y1 - y0) * u + rng.uniform(-3, 3),
                    rng.uniform(6, 17),
                    rng.uniform(2.7, 7),
                    "#f6efdc",
                )
    clay_slab(
        im,
        [(111, 386), (140, 380), (161, 386), (157, 394), (124, 398), (108, 394)],
        26,
        (224, 189, 144),
        0.7,
    )
    clay_slab(
        im,
        [(179, 330), (201, 319), (230, 319), (242, 326), (235, 338), (208, 342), (181, 338)],
        58,
        (155, 187, 99),
        0.1,
    )
    clay_slab(
        im,
        [
            (331, 365),
            (402, 350),
            (510, 343),
            (621, 350),
            (688, 371),
            (665, 386),
            (585, 394),
            (484, 396),
            (427, 405),
            (358, 397),
            (324, 387),
        ],
        46,
        (151, 193, 105),
        1.8,
    )
    clay_slab(
        im,
        [
            (463, 312),
            (506, 300),
            (561, 301),
            (606, 293),
            (650, 297),
            (700, 304),
            (744, 303),
            (775, 315),
            (755, 330),
            (715, 335),
            (683, 343),
            (602, 344),
            (557, 340),
            (497, 340),
            (465, 333),
        ],
        79,
        (169, 199, 113),
        2.6,
    )
    clay_slab(
        im,
        [(713, 364), (744, 354), (788, 360), (804, 372), (788, 381), (743, 385), (710, 379)],
        34,
        (197, 176, 115),
        4.4,
    )
    clay_slab(im, [(301, 455), (324, 448), (346, 453), (337, 461), (303, 465)], 7, (227, 190, 143), 2)
    # Two rails of a little wooden landing lead from the lower terrace to the water.
    d.polygon([(395, 393), (413, 393), (386, 454), (367, 459)], fill="#936746")
    for i in range(12):
        x, y = 396 - i * 2.55, 395 + i * 5.0
        d.line((x, y, x + 15, y - 1.6), fill="#d4ab77", width=4)

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
    pad = Image.new("L", SIZE)
    ImageDraw.Draw(pad).ellipse((cx - 22, 311, cx + 43, 325), fill=97)
    im.paste("#72865b", (0, 0), pad.filter(ImageFilter.GaussianBlur(3.5)))
    rock(cx, 316, 27, 5, "#e2cca4")
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
        shadow = Image.new("L", SIZE)
        ImageDraw.Draw(shadow).ellipse((x - 7 * k, y - 3 * k, x + 22 * k, y + 4 * k), fill=123)
        im.paste("#687f54", (0, 0), shadow.filter(ImageFilter.GaussianBlur(1.7)))
        roll(x, y - 12 * k, y, 3 * k, 3.5 * k, "#977858")
        for level in range(3):
            ry = (13 - level * 1.7) * k
            cy = y - (14 + level * 8) * k
            radius = (14 - level * 2.8) * k
            roll(
                x,
                cy - ry,
                cy + ry * 0.25,
                max(1, radius * 0.15),
                radius,
                ["#39856a", "#50a87b", "#6abc84"][level],
            )

    for x, y, k in [
        (362, 381, 0.91),
        (392, 375, 1.17),
        (416, 378, 0.70),
        (475, 325, 0.78),
        (494, 319, 1.03),
        (715, 321, 0.72),
        (212, 334, 0.46),
    ]:
        pine(x, y, k)
    # Soft bevels retain the familiar geometry of the little keeper's house.
    pad = Image.new("L", SIZE)
    ImageDraw.Draw(pad).polygon([(496, 318), (573, 313), (588, 318), (527, 330), (492, 329)], fill=90)
    im.paste("#67855f", (0, 0), pad.filter(ImageFilter.GaussianBlur(3)))
    d.rounded_rectangle((491, 294, 548, 323), radius=4, fill="#f4d7a6")
    d.polygon([(547, 296), (564, 290), (564, 317), (548, 323)], fill="#cfaa7e")
    d.polygon([(487, 296), (498, 280), (551, 279), (558, 293)], fill="#d77550")
    d.polygon([(551, 279), (567, 287), (570, 293), (558, 293)], fill="#ac604c")
    d.line((492, 292, 500, 281, 550, 280), fill="#e6a170", width=3)
    for px in [501, 534]:
        d.rounded_rectangle((px, 304, px + 6, 312), radius=2, fill="#688487")
    d.rounded_rectangle((517, 308, 525, 323), radius=2, fill="#957352")
    d.rounded_rectangle((505, 273, 511, 285), radius=2, fill="#dba354")
    x = 49 + 6 * math.sin(t)
    rock(x, 421 + math.cos(t), 16, 5, "#bb6b54")
    d.polygon([(x, 415), (x, 388), (x - 15, 414)], fill="#f3dc9e")
    return grain(im.filter(ImageFilter.GaussianBlur(0.32)), 2.3)
