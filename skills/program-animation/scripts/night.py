"""A moving beam and its water reflection for the two night studies."""

import numpy as np
from coast import H, W, gradient, paint, scene
from PIL import Image

NIGHT = {
    "sun": "#e4dec0",
    "cloud": "#394c63",
    "distant": "#233a4c",
    "mountain": "#304355",
    "face": "#263848",
    "snow": "#506171",
    "ridge": "#657180",
    "sea": "#203b50",
    "ripple": "#406379",
    "foam": "#7e9a9e",
    "stone": "#59606b",
    "shade": "#383c4a",
    "ochre": "#806e64",
    "land": "#687064",
    "pine": "#3a655e",
    "leaf": "#56927b",
    "wall": "#d4c3ac",
    "shadow": "#9a928d",
    "red": "#aa645a",
    "dark": "#383d49",
    "roof": "#85544d",
    "bird": "#81919c",
    "glass": "#b4aaa3",
}


def night(t):
    marks = scene(t)
    im = paint(marks, NIGHT, gradient([(0, "#101522"), (180, "#1c2c40"), (330, "#34495b")]))
    yy, xx = np.mgrid[:H, :W]
    dx, dy = xx - 671, yy - 98
    angle = 0.11 * np.sin(t)
    spread = 2 + np.abs(dx) * 0.041
    beam = np.exp(-(((dy - angle * dx) / spread) ** 2)) * np.exp(-np.abs(dx) / 530)
    lamp = np.exp(-(dx**2 + dy**2) / 182)
    reflection = np.exp(
        -(((xx - 270 - 10 * np.sin(yy * 0.13 + t)) / (9 + np.maximum(0, yy - 315) * 0.21)) ** 2)
    )
    reflection *= (yy > 315) * (0.5 + 0.5 * np.sin(yy * 0.83 + np.sin(yy * 0.3) + t)) ** 6
    add = (beam * 0.82 + lamp * 0.85 + reflection * 0.39)[:, :, None] * np.array([250, 218, 151])
    return Image.fromarray(np.uint8(np.clip(np.asarray(im) + add, 0, 255)))
