"""Stacked cardstock with a stepped sunset and down-right cast shadows."""

import math

from coast import BASE, SIZE, draw_mark, grain, scene
from PIL import Image, ImageDraw, ImageFilter

PALETTE = {
    "sky": "#f4d6af",
    "sun": "#f67b60",
    "distant": "#c5b4d5",
    "mountain": "#a696cd",
    "face": "#8273af",
    "snow": "#e8dcec",
    "sea": "#3e849d",
    "ripple": "#89bac1",
    "stone": "#c0765d",
    "shade": "#a36253",
    "land": "#89ae89",
    "cloud": "#fff3dc",
}


def frame(t):
    colors = {**BASE, **PALETTE}
    im = Image.new("RGB", SIZE, colors["sky"])
    d = ImageDraw.Draw(im)
    for m in scene(t):
        if m.role == "sun":
            x, y = m.xy[0][0] + 57, m.xy[0][1] + 57
            for r, c in [(132, "#f5c397"), (104, "#f4ad83"), (78, "#f49473")]:
                d.ellipse((x - r, y - r, x + r, y + r), fill=c)
        if m.role in {"cloud", "sun", "mountain", "stone", "pine", "wall", "roof"} and m.kind != "line":
            shadow = Image.new("L", SIZE)
            draw_mark(ImageDraw.Draw(shadow), m, 91, offset=(3, 5))
            im.paste("#775c61", (0, 0), shadow.filter(ImageFilter.GaussianBlur(2)))
        if m.role == "ripple":
            continue
        draw_mark(d, m, colors[m.role])
        if m.role == "sea":
            # Interlocking strips read as hand-cut scallops, even in a still.

            for row in range(8):
                y = 341 + row * 29
                pts = [
                    (x, y - 6 * abs(math.sin(x / 28 + row * 0.74 + 0.3 * math.sin(t))))
                    for x in range(-2, 965, 3)
                ]
                d.polygon(
                    pts + [(966, 542), (-3, 542)],
                    fill=[
                        "#4d9ba6",
                        "#47919e",
                        "#428599",
                        "#3c7991",
                        "#376f88",
                        "#316580",
                        "#2c5c76",
                        "#28556f",
                    ][row],
                )
                d.line(pts, fill="#c5dbd4", width=3)
    return grain(im, 2.1)
