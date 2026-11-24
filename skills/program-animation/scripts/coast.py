"""Parametric coastal elevation shared by the graphic print examples. Coordinates are in design pixels."""

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
