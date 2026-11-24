"""Bokashi sky, carved outlines and patterned waves of a relief print."""

import math

from coast import gradient, grain, paint, scene
from PIL import ImageDraw

COLORS = {
    "sun": "#c34e32",
    "cloud": "#fbedd0",
    "distant": "#a5b5ad",
    "mountain": "#5585a1",
    "face": "#355c79",
    "snow": "#f7e8c6",
    "ridge": "#55748a",
    "sea": "#416c82",
    "ripple": None,
    "foam": "#f2dec0",
    "stone": "#c59a58",
    "ochre": "#e3b866",
    "shade": "#9c7648",
    "land": "#98966a",
    "red": "#ad4733",
}


def frame(t):
    marks = scene(t)
    sky = gradient([(0, "#243f68"), (70, "#829eaf"), (181, "#e9cfaa"), (315, "#f2e1bb")])
    groups = next(i for i, m in enumerate(marks) if m.role == "sea") + 1
    edge = lambda m: (
        "#444b49" if m.role not in {"face", "snow", "shade", "ochre", "shadow", "distant"} else None
    )
    im = paint(marks[:groups], COLORS, sky, edge)
    d = ImageDraw.Draw(im)
    for row, y in enumerate(range(322, 554, 9)):
        pts = [
            (x, y + 2.6 * math.sin(0.057 * x + row * 0.7 + 0.65 * math.sin(t))) for x in range(-2, 965, 3)
        ]
        d.line(pts, fill="#a7bcc0" if row % 3 else "#d6d4bd", width=2)
        for x in range((row * 31) % 77 - 50, 960, 77):
            d.arc((x, y - 2, x + 41, y + 5), 0, 175, fill="#274f67", width=1)
    return grain(paint(marks[groups:], COLORS, im, edge), 3, 1.6)
