"""Parametric coastal elevation shared by the graphic print examples. Coordinates are in design pixels."""

import math
import random
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageColor, ImageDraw

W, H = 960, 540
SIZE = (W, H)


@dataclass
class Mark:
    kind: str
    role: str
    xy: list
    width: int = 1


BASE = {
    "sky": "#f8dcc0",
    "sun": "#ffc058",
    "cloud": "#ffedc9",
    "distant": "#a7bfc5",
    "mountain": "#6d91a7",
    "face": "#497387",
    "snow": "#eadfc9",
    "ridge": "#596d79",
    "sea": "#5b9d9e",
    "ripple": "#b7d5b7",
    "foam": "#f4e4c4",
    "stone": "#b46e50",
    "shade": "#865749",
    "ochre": "#d28b62",
    "crack": "#775447",
    "land": "#acaa71",
    "pine": "#355d55",
    "leaf": "#59846a",
    "trunk": "#775d4c",
    "wall": "#fff1ce",
    "shadow": "#d4cbbb",
    "red": "#bf503f",
    "roof": "#853e36",
    "dark": "#344852",
    "glass": "#a4c9bf",
    "lamp": "#ffe9ad",
    "sail": "#eed8ae",
    "hull": "#6c4940",
    "bird": "#53565c",
}


def draw_mark(d, m, fill, edge=None, width=1, offset=(0, 0)):
    x, y = offset
    pts = [(round(a + x), round(b + y)) for a, b in m.xy]
    if m.kind == "line":
        d.line(pts, fill=fill, width=m.width, joint="curve")
    elif m.kind == "oval":
        d.ellipse(pts, fill=fill, outline=edge, width=width)
    else:
        d.polygon(pts, fill=fill)
        if edge:
            d.line(pts + pts[:1], fill=edge, width=width, joint="curve")


def paint(marks, palette, sky=None, outlines=None):
    p = {**BASE, **palette}
    out = sky.copy() if sky is not None else Image.new("RGB", SIZE, p["sky"])
    d = ImageDraw.Draw(out)
    for m in marks:
        if p[m.role] is not None:
            edge = outlines(m) if outlines is not None and m.kind != "line" else None
            draw_mark(d, m, p[m.role], edge)
    return out


def gradient(stops):
    ys = np.arange(H)
    channels = np.array([ImageColor.getrgb(c) for _, c in stops])
    rows = np.stack([np.interp(ys, [v for v, _ in stops], ch) for ch in channels.T], axis=-1)
    return Image.fromarray(np.repeat(rows[:, None, :], W, axis=1).astype("uint8"))


def grain(im, amount=3, fibers=0):
    rng = np.random.default_rng(73)
    noise = rng.normal(0, amount, (H, W))
    if fibers:
        noise += rng.normal(0, fibers, (H, 1))
    return Image.fromarray(np.uint8(np.clip(np.asarray(im) + noise[:, :, None], 0, 255)))


def scene(t):
    marks = []

    def add(kind, role, pts, width=1):
        marks.append(Mark(kind, role, pts, width))

    def poly(role, *pts):
        add("poly", role, pts)

    def line(role, *pts, width=1):
        add("line", role, pts, width)

    def oval(role, x, y, rx, ry):
        add("oval", role, [(x - rx, y - ry), (x + rx, y + ry)])

    def rect(role, x, y, w, h):
        poly(role, (x, y), (x + w, y), (x + w, y + h), (x, y + h))

    rng = random.Random(805)
    oval("sun", 271, 159 + 8 * math.cos(t), 57, 57)
    for x, y, s in [(67, 97, 0.77), (482, 78, 0.94), (814, 126, 0.65), (370, 203, 0.42)]:
        x += 14 * math.sin(t)
        # One closed, scalloped cloud silhouette.
        contour = [
            (0, 8),
            (8, 1),
            (23, 0),
            (28, -8),
            (37, -11),
            (45, -8),
            (52, -20),
            (65, -24),
            (77, -19),
            (82, -11),
            (94, -12),
            (104, -8),
            (107, -3),
            (121, -1),
            (130, 7),
            (122, 10),
            (5, 10),
        ]
        poly("cloud", *((x + a * s, y + b * s) for a, b in contour))
    back = [
        (-12, 244),
        (53, 219),
        (85, 236),
        (135, 204),
        (172, 221),
        (231, 189),
        (297, 241),
        (371, 209),
        (451, 247),
        (504, 221),
        (590, 245),
        (691, 200),
        (754, 238),
        (822, 207),
        (913, 239),
        (969, 215),
    ]
    poly("distant", *back, (970, 330), (-12, 330))
    for x, y, s in [
        (378, 237, 0.73),
        (733, 210, 0.98),
        (866, 155, 1.18),
        (93, 149, 1.33),
        (271, 190, 1.13),
    ]:

        def pt(a, b, ox=x, oy=y, scale=s):
            return ox + a * scale, oy + b * scale

        left = [(-160, 145), (-110, 104), (-76, 84), (-57, 58), (-39, 48), (-25, 27), (-10, 16), (0, 0)]
        right = [(17, 16), (33, 40), (45, 47), (67, 72), (91, 84), (130, 125), (165, 145)]
        poly("mountain", *(pt(a, b) for a, b in left + right + [(165, 196), (-160, 196)]))
        poly(
            "face",
            *(
                pt(a, b)
                for a, b in [
                    (0, 0),
                    *right,
                    (128, 146),
                    (83, 117),
                    (51, 107),
                    (42, 88),
                    (27, 85),
                    (29, 68),
                    (10, 44),
                    (16, 42),
                ]
            ),
        )
        poly(
            "snow",
            *(
                pt(a, b)
                for a, b in [
                    (-43, 53),
                    (-22, 26),
                    (0, 0),
                    (17, 16),
                    (34, 42),
                    (19, 32),
                    (12, 34),
                    (5, 23),
                    (0, 20),
                    (-18, 40),
                    (-15, 31),
                ]
            ),
        )
        for a, b in [(-62, 71), (-38, 58), (-82, 94), (42, 61), (63, 86)]:
            line("ridge", pt(a, b), pt(a - 8, b + 12), pt(a - 19, b + 20), pt(a - 27, b + 29))
    rect("sea", -2, 315, W + 4, H - 314)
    for i in range(424):
        x, y = rng.uniform(-50, 960), rng.uniform(318, 555)
        length = rng.uniform(5, 26) * (0.7 + (y - 315) / 120)
        x += (3 + (y - 315) * 0.02) * math.sin(t + rng.uniform(0, 6.28))
        line(
            "ripple", (x, y), (x + length * 0.3, y - 1), (x + length, y), width=1 + (y > 476 and i % 5 == 0)
        )

    def cliff(top, bottom, main=True):
        poly("foam", *((x - 4, y + 3) for x, y in top), *((x + 4, y + 4) for x, y in reversed(bottom)))
        poly("stone", *top, *reversed(bottom))
        for i in range(len(top) - 1):
            a, b, c, e = top[i], top[i + 1], bottom[i], bottom[i + 1]
            mid = ((a[0] + e[0]) * 0.5 + 4, (a[1] + e[1]) * 0.5)
            poly("ochre" if i % 3 == 0 else "shade", a, mid, c)
            if i % 2:
                poly("shade", b, e, mid)
            if main:
                line("crack", (a[0] + 8, a[1] + 7), (mid[0] - 5, mid[1]), (mid[0] - 7, mid[1] + 7))
        poly(
            "land",
            *((x, y - 3 - i % 3) for i, (x, y) in enumerate(top)),
            *((x + 3, y + 3 + i % 2 * 2) for i, (x, y) in enumerate(reversed(top))),
        )

    cliff(
        [(132, 336), (148, 325), (172, 327), (188, 332)],
        [(122, 381), (150, 384), (178, 383), (199, 379)],
        False,
    )
    cliff(
        [(242, 323), (262, 307), (293, 307), (301, 314)],
        [(224, 367), (251, 370), (285, 369), (312, 367)],
        False,
    )
    top = [
        (300, 391),
        (332, 377),
        (355, 359),
        (398, 354),
        (427, 331),
        (469, 323),
        (486, 309),
        (543, 309),
        (571, 300),
        (618, 299),
        (643, 292),
        (702, 295),
        (731, 304),
        (762, 305),
        (777, 321),
        (803, 331),
        (822, 350),
        (845, 355),
        (873, 373),
        (905, 383),
    ]
    bottom = [
        (280, 408),
        (326, 409),
        (348, 416),
        (398, 417),
        (421, 408),
        (467, 412),
        (492, 419),
        (531, 422),
        (574, 425),
        (618, 425),
        (642, 420),
        (701, 419),
        (721, 412),
        (752, 414),
        (787, 407),
        (809, 405),
        (836, 399),
        (856, 400),
        (881, 395),
        (917, 395),
    ]
    cliff(top, bottom)

    def tree(x, y, s):
        rect("trunk", x - s * 0.055, y - s * 0.20, s * 0.11, s * 0.22)
        for level in range(3):
            offset = level * 0.17
            half = (0.25 - level * 0.051) * s
            base = y - (0.1 + offset) * s
            tip = y - (0.57 + offset) * s
            poly(
                "pine",
                (x, tip),
                (x + half, base - 2),
                (x + half * 0.4, base - 1),
                (x, base + 1),
                (x - half, base),
            )
            poly("leaf", (x, tip), (x + 2, base - 5), (x - half, base))

    for x, y, s in [
        (440, 329, 20),
        (454, 326, 29),
        (471, 324, 23),
        (495, 308, 27),
        (507, 310, 36),
        (718, 301, 30),
        (737, 306, 19),
        (753, 307, 27),
    ]:
        tree(x, y, s)
    # Keeper's house and the attached shed.
    rect("wall", 529, 277, 59, 32)
    poly("shadow", (588, 276), (605, 267), (605, 299), (588, 309))
    poly("red", (522, 279), (536, 258), (589, 258), (600, 279))
    poly("roof", (589, 258), (607, 265), (614, 280), (600, 279))
    rect("roof", 545, 249, 6, 13)
    for x in (535, 550, 578):
        rect("dark", x, 285, 6, 10)
    rect("roof", 564, 290, 8, 19)
    rect("wall", 610, 283, 25, 15)
    poly("roof", (606, 284), (616, 274), (638, 275), (642, 284))
    # Tapered beacon body, with bands conforming to the taper.
    cx, top_y, base_y = 671, 117, 294

    def half(y):
        return 13 + (y - top_y) * 0.064

    def slab(role, y1, y2):
        poly(role, (cx - half(y1), y1), (cx + half(y1), y1), (cx + half(y2), y2), (cx - half(y2), y2))

    slab("wall", top_y, base_y)
    for a, b in [(143, 166), (201, 226), (265, 285)]:
        slab("red", a, b)
    poly("shadow", (cx + 7, top_y), (cx + 13, top_y), (cx + half(base_y), base_y), (cx + 14, base_y))
    for y in (132, 187, 247):
        rect("dark", cx - 4, y, 5, 9)
        rect("glass", cx - 3, y + 1, 2, 4)
    rect("dark", cx - 5, 279, 10, 15)
    rect("wall", cx - 27, 294, 54, 4)
    poly("dark", (650, 111), (692, 111), (688, 118), (654, 118))
    rect("glass", 658, 86, 26, 25)
    oval("lamp", cx, 97, 4 + 1.5 * math.cos(t), 7)
    for x in (658, 665, 677, 684):
        line("dark", (x, 86), (x, 110), width=2)
    for x in range(649, 694, 7):
        line("dark", (x, 103), (x, 112))
    line("dark", (648, 103), (694, 103), width=2)
    poly("roof", (652, 86), (657, 82), (661, 75), (670, 69), (678, 74), (684, 83), (690, 86))
    line("dark", (670, 69), (670, 60), width=2)
    oval("lamp", 670, 60, 2, 2)
    for i in range(16):
        x = 374 + i * 6
        y = 358 - i * 1.75
        line("wall", (x, y), (x + 5, y + 1), width=2)

    def boat(x, y, s):
        rect("dark", x, y - 42 * s, max(1, 1.7 * s), 43 * s)
        poly("sail", (x - 3 * s, y - 40 * s), (x - 4 * s, y - 4 * s), (x - 24 * s, y - 4 * s))
        poly("wall", (x + 2 * s, y - 32 * s), (x + 18 * s, y - 5 * s), (x + 2 * s, y - 5 * s))
        poly("hull", (x - 28 * s, y), (x + 24 * s, y), (x + 17 * s, y + 6 * s), (x - 20 * s, y + 6 * s))

    boat(90 + 6 * math.sin(t), 382 + 1.5 * math.cos(t), 0.86)
    boat(210 + 3 * math.sin(t), 350 + 0.7 * math.cos(t), 0.38)
    for x, y, s in [(370, 130, 1), (395, 123, 0.65), (791, 78, 0.8), (821, 83, 0.55), (184, 87, 0.5)]:
        x += 9 * math.sin(t)
        wing = 4 + 2 * math.sin(t * 2 + x)
        line(
            "bird",
            (x - 10 * s, y - wing * s),
            (x - 5 * s, y - 3 * s),
            (x, y + 1 * s),
            (x + 5 * s, y - 2 * s),
            (x + 10 * s, y - wing * s),
            width=2,
        )
    return marks
