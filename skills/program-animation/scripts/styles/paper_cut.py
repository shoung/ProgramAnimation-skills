"""Stepped sunset, cut-paper headlands and overlapping scalloped paper sea strips."""

import math

from coast import SIZE, draw_mark, grain
from lettering import titled
from PIL import Image, ImageDraw, ImageFilter
from print_landscape import PALETTE, plate_scene

COLORS = {
    **PALETTE,
    "sky": "#efd8b4",
    "sun": "#e9654c",
    "cloud": "#fff5e5",
    "mountain": "#b4a0c9",
    "crest": "#e2cee4",
    "face": "#9680b7",
    "ridge": "#ad98c2",
    "sea": "#569a96",
    "foam": "#e6d6bb",
    "stone": "#c48165",
    "shade": "#ae6e59",
    "land": "#92b68c",
    "pine": "#518a79",
    "leaf": "#6da78a",
    "wall": "#f7ebdb",
    "red": "#dc6b56",
    "seam": "#b4745a",
}


@titled("paper-cut")
def frame(t):
    im = Image.new("RGB", SIZE, COLORS["sky"])
    d = ImageDraw.Draw(im)

    def surf(y, row, color, lip):
        points = []
        for x in range(-3, 965, 2):
            phase = (x + row * 27 + 3 * math.sin(t)) / 70
            # Convex cap of each paper scallop leaves a pointed junction.
            v = (phase % 1) * 2 - 1
            points.append((x, y - 14 * math.sqrt(max(0, 1 - v * v))))
        d.polygon(points + [(964, 544), (-3, 544)], fill=color)
        if lip:
            d.line([(px, py + 3) for px, py in points], fill="#396e79", width=6)
            d.line(points, fill=lip, width=4)

    for m in plate_scene(t, summit=231, horizon=373, cloud_style="puffs"):
        if m.role in {"ridge", "rail", "step", "lip"}:
            continue
        if m.role == "sun":
            for r, c in [(218, "#efc99e"), (159, "#efa97f"), (101, "#ec8969")]:
                shadow = Image.new("L", SIZE)
                ImageDraw.Draw(shadow).ellipse((333 - r, 228 - r, 333 + r, 228 + r), fill=62)
                im.paste("#a17f60", (0, 0), shadow.filter(ImageFilter.GaussianBlur(3)))
                d.ellipse((329 - r, 223 - r, 329 + r, 223 + r), fill=c)
        if m.role in {"cloud", "sun", "stone", "wall", "mountain", "roof"} and m.kind != "line":
            mask = Image.new("L", SIZE)
            draw_mark(ImageDraw.Draw(mask), m, 114, offset=(4, 7))
            im.paste("#816c67", (0, 0), mask.filter(ImageFilter.GaussianBlur(2.8)))
        draw_mark(d, m, COLORS[m.role])
        if m.role == "cloud":
            # The pale upper edge and darker underside suggest the thickness of stock.
            pts = m.xy
            d.line(pts[:23], fill="#fcf8ee", width=2)
            d.line(pts[38:52], fill="#d5c6b8", width=2)
        if m.role == "sea":
            surf(375, 0, "#589c99", None)
    for i, (y, c) in enumerate([(439, "#397f8a"), (478, "#336e84"), (517, "#305878")]):
        surf(y, i, c, "#e1e5d7")
    return grain(im, 2.0)
