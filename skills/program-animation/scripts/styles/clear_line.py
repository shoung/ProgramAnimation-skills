"""Even pen contours, pastel flats and clipped, parallel pen shading."""

from coast import BASE, SIZE, draw_mark, scene
from PIL import Image, ImageDraw

COLORS = {
    "sky": "#a5d9cf",
    "sun": "#fbe8a2",
    "cloud": "#ffeadb",
    "distant": "#ddd1d4",
    "mountain": "#d2b4cf",
    "face": "#c9a7c5",
    "snow": "#efd8de",
    "ridge": "#947f99",
    "sea": "#87c9bc",
    "ripple": "#609e95",
    "foam": "#f9ebd3",
    "stone": "#d7a188",
    "shade": "#d7a188",
    "ochre": "#dfae94",
    "crack": "#97746c",
    "land": "#bdc796",
    "shadow": "#f6dfbc",
    "red": "#d8795d",
    "dark": "#494350",
    "pine": "#65877b",
    "leaf": "#8eb09a",
}


def frame(t):
    colors = {**BASE, **COLORS}
    im = Image.new("RGB", SIZE, colors["sky"])
    d = ImageDraw.Draw(im)
    ruled = Image.new("L", SIZE)
    rd = ImageDraw.Draw(ruled)
    for x in range(-550, 980, 6):
        rd.line((x, 540, x + 350, 0), fill=180)
    from PIL import ImageChops

    for m in scene(t):
        edge = (
            "#584c57"
            if m.kind != "line" and m.role not in {"sea", "shade", "shadow", "ochre", "foam", "leaf"}
            else None
        )
        draw_mark(d, m, colors[m.role], edge, 2 if m.role in {"stone", "wall", "roof"} else 1)
        if m.role in {"shade", "face", "shadow"}:
            mask = Image.new("L", SIZE)
            draw_mark(ImageDraw.Draw(mask), m, 255)
            im.paste("#917a86", (0, 0), ImageChops.multiply(mask, ruled))
    return im
