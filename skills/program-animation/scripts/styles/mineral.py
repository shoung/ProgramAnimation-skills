"""Blue-green mineral pigments and angular planes on gold silk."""

import random

from coast import BASE, SIZE, draw_mark, gradient, grain, scene
from PIL import Image, ImageDraw

COLORS = {
    "sun": "#bd533a",
    "cloud": "#e6ce99",
    "distant": "#b1ad80",
    "mountain": "#609785",
    "face": "#397584",
    "snow": "#9bb797",
    "ridge": "#899f7d",
    "sea": "#a2b69a",
    "ripple": "#c8c398",
    "foam": "#d8cda1",
    "stone": "#609080",
    "ochre": "#61a59b",
    "shade": "#316e79",
    "land": "#899756",
    "wall": "#e7d4a0",
    "shadow": "#b9a67a",
    "red": "#ae5237",
    "roof": "#754d37",
    "pine": "#416c52",
    "leaf": "#68905d",
}


def frame(t):
    sky = gradient([(0, "#a88954"), (180, "#c6ab72"), (355, "#e0c48a")])
    marks = scene(t)
    rng = random.Random(39)
    for m in marks:
        draw_mark(ImageDraw.Draw(sky), m, COLORS.get(m.role, BASE[m.role]))
        if m.role not in {"mountain", "stone"}:
            continue
        mask = Image.new("L", SIZE)
        draw_mark(ImageDraw.Draw(mask), m, 255)
        tile = sky.copy()
        d = ImageDraw.Draw(tile)
        xs, ys = zip(*m.xy)
        for _ in range(27):
            x, y = rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys))
            s = rng.uniform(14, 80)
            d.polygon(
                [(x, y), (x + s * 0.77, y + s), (x - s * 0.2, y + s * 0.7)],
                fill=rng.choice(["#48877a", "#739f83", "#61999b", "#48828a", "#94ac7e"]),
            )
        sky.paste(tile, (0, 0), mask)
    d = ImageDraw.Draw(sky)
    for x in range(10, 960, 13):
        for y in range(8, 536, 18):
            if rng.random() < 0.12:
                d.line((x, y, x + 2, y + 1), fill="#d6bd87")
    return grain(sky, 3.3, 1.4)
