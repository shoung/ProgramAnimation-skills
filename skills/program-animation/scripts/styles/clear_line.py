"""Pastel gouache flats, clean silhouette weights and clipped, form-following pen hatching."""

import math

from coast import BASE
from PIL import Image, ImageChops, ImageDraw

from styles import harbor_frame

SCALE = 2
INK = "#423442"
COLORS = {
    **BASE,
    "sun": "#ffe8ac",
    "cloud": "#ffe5d8",
    "mountain": "#dcbacf",
    "crest": "#f0d3df",
    "seam": "#9f6658",
    "lip": "#edbc8b",
    "ridge": "#997e99",
    "sea": "#6dbdb2",
    "stone": "#e5a477",
    "land": "#b3ac6a",
    "foam": "#b0d3b7",
    "pine": "#337e78",
    "leaf": "#65aaa0",
    "rail": "#785246",
    "step": "#ba7959",
    "wall": "#fff0cd",
    "red": "#d1684c",
    "roof": "#a34e41",
    "dark": "#423941",
    "hull": "#a14b42",
    "bird": "#4b5557",
}


def hatching(im, mark):
    # Work inside a face-local mask. Lines drift with the terrain, and their pitch
    # tightens toward the far edge. The existing flat color shows through each gap.
    xs, ys = zip(*mark.xy)
    left, top = math.floor(min(xs)), math.floor(min(ys))
    w, h = math.ceil(max(xs)) - left + 1, math.ceil(max(ys)) - top + 1
    mask = Image.new("L", (w, h))
    ImageDraw.Draw(mask).polygon([(x - left, y - top) for x, y in mark.xy], fill=255)
    strokes = Image.new("L", (w, h))
    pen = ImageDraw.Draw(strokes)
    if mark.role == "face":
        color = "#997795"
        bend, tilt, pitch, weight = 0.09, 0.72, 3.9, 1.65
    elif mark.role == "shade":
        color = "#724650"
        bend, tilt, pitch, weight = 0.047, -0.79, 3.7, 1.7
    else:
        color = "#796274"
        bend, tilt, pitch, weight = 0.09, -0.43, 3.3, 1.2
    x = -abs(tilt) * h - 2 * SCALE
    while x < w + abs(tilt) * h + 4 * SCALE:
        pts = []
        for i in range(9):
            u = i / 8
            offset = h * (tilt * u + bend * math.sin(math.pi * u))
            pts.append((x + offset, h * u))
        pen.line(pts, fill=255, width=round(weight * SCALE))
        compression = min(1, max(0, (x + h * tilt / 2) / w))
        x += SCALE * pitch * (1.28 - 0.49 * compression)
    if mark.role == "shade":
        # A shorter second family of marks nests in the deepest part of the cut.
        # Taper the reach so the terminator breaks into strokes rather than a new flat band.
        for j, start in enumerate(range(-h, w, 8 * SCALE)):
            reach = 0.40 + 0.14 * math.sin(j * 0.79)
            pen.line([(start, h), (start + h * 0.55 * reach, h * (1 - reach))], fill=220, width=SCALE)
    im.paste(color, (left, top), ImageChops.multiply(strokes, mask))


frame = harbor_frame("clear-line")
