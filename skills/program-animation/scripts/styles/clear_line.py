"""Pastel gouache flats, clean silhouette weights and clipped, form-following pen hatching."""

import math

from coast import BASE, SIZE, H, Mark, W, draw_mark
from headland import landscape
from lettering import titled
from PIL import Image, ImageChops, ImageDraw

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


@titled("clear-line")
def frame(t):
    size = (W * SCALE, H * SCALE)
    im = Image.new("RGB", size)
    pen = ImageDraw.Draw(im)
    # Broad pastel bands in the sky and short tide lines leave the silhouettes legible.
    for i in range(60):
        f = i / 59
        rgb = tuple(round(a + (b - a) * f) for a, b in zip((93, 168, 179), (250, 232, 189)))
        pen.rectangle((0, i * 7 * SCALE, size[0], (i + 1) * 7 * SCALE), fill=rgb)
    for original in landscape(t):
        role = original.role
        m = Mark(
            original.kind, role, [(x * SCALE, y * SCALE) for x, y in original.xy], original.width * SCALE
        )
        if role in {"face", "shade", "shadow"}:
            if role == "shadow" and min(x for x, _ in original.xy) < 570:  # gable projects beyond the house
                draw_mark(pen, m, COLORS["wall"], INK, 2 * SCALE)
            hatching(im, m)
            continue
        heavy = role in {"stone", "wall", "roof", "red", "pine", "hull"}
        weight = 3.5 if heavy else 2.2
        if role in {"dark", "glass", "lamp", "leaf", "land"}:
            weight = 1.35
        edge = None if role == "sea" else (INK if heavy else "#645064")
        if role == "crest":
            edge = None
        if role == "sun":
            edge, weight = "#b0a082", 1.7
        draw_mark(pen, m, COLORS[role], edge, round(weight * SCALE))
        if role == "cloud":
            xs, ys = zip(*m.xy)
            left, right, top, bottom = min(xs), max(xs), min(ys), max(ys)
            w, h = right - left, bottom - top
            # The underside only picks up a few curved strokes; the tops stay open.
            cloud_mask = Image.new("L", (math.ceil(w) + 2, math.ceil(h) + 2))
            ImageDraw.Draw(cloud_mask).polygon([(x - left, y - top) for x, y in m.xy], fill=255)
            strokes = Image.new("L", cloud_mask.size)
            brush = ImageDraw.Draw(strokes)
            for x in range(0, math.ceil(w), 4 * SCALE):
                u = x / w
                start = h * (0.79 + 0.06 * math.cos(5 * math.pi * u))
                brush.line(
                    [(x, start), (x + 2 * SCALE, start + h * 0.08), (x + 6 * SCALE, h)],
                    fill=180,
                    width=SCALE,
                )
            im.paste("#ba98a3", (int(left), int(top)), ImageChops.multiply(strokes, cloud_mask))
            for u, lean in [(0.27, -1), (0.68, 1)]:
                # Two short curved interior pen marks describe the puffy lobes.
                pen.line(
                    [
                        (left + w * (u + lean * 0.055 * v * v), top + h * (0.83 - 0.32 * v))
                        for v in (0, 0.2, 0.4, 0.6, 0.8, 1)
                    ],
                    fill="#b796a0",
                    width=SCALE,
                )
        if role == "sea":
            for i in range(220):
                y = 379 + (i * 29) % 166
                x = (i * i * 57 + i * 79) % 1031 - 43 + 4 * math.sin(t + i)
                length = 7 + (i * 11) % 43
                pen.line(
                    [
                        (x * SCALE, y * SCALE),
                        ((x + length * 0.4) * SCALE, (y - 0.55) * SCALE),
                        ((x + length) * SCALE, y * SCALE),
                    ],
                    fill="#579d98",
                    width=SCALE if i % 4 else 2 * SCALE,
                )
    return im.resize(SIZE, Image.Resampling.LANCZOS)
