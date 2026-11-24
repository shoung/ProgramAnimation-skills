"""Directional broken color: broad ground strokes, fine loaded bristles and ridge highlights."""

import math
import random

import numpy as np
from coast import H, W, grain
from PIL import ImageDraw

from styles import harbor_frame

COLORS = {
    "sun": "#ffe3a4",
    "cloud": "#eba9a0",
    "distant": "#b28ab3",
    "mountain": "#b48dc2",
    "face": "#715eab",
    "snow": "#f1b9b4",
    "ridge": "#986caa",
    "sea": "#198fa3",
    "ripple": "#66b4bd",
    "stone": "#ad6749",
    "shade": "#75475d",
    "ochre": "#de9160",
    "land": "#aba55a",
    "red": "#c95038",
    "pine": "#315953",
    "leaf": "#547f61",
    "wall": "#f6ddce",
}


def paint_strokes(im, direction, brush_scale=None):
    """Lay the same three sizes of short, loaded strokes along a subject-specific field."""
    rgb = np.array(im, dtype=float)
    out = im.copy()
    d = ImageDraw.Draw(out)
    rng = random.Random(962)
    for count, base_len, base_w in [(9500, 17, 7), (16400, 9, 4), (8500, 6, 2)]:
        for _ in range(count):
            x = rng.randrange(W)
            y = rng.randrange(H)
            angle = direction(x, y)
            length = base_len * rng.uniform(0.55, 1.55)
            width = base_w * rng.uniform(0.55, 1.45)
            if brush_scale is not None:
                length *= brush_scale[y, x]
                width *= brush_scale[y, x]
            # Smaller strokes near a silhouette keep the architecture legible.
            near = rgb[min(H - 1, y + 3), min(W - 1, x + 3)]
            if np.max(abs(near - rgb[y, x])) > 30:
                length *= 0.48
                width *= 0.65
            dx, dy = math.cos(angle) * length * 0.5, math.sin(angle) * length * 0.5
            nx, ny = -math.sin(angle) * width * 0.5, math.cos(angle) * width * 0.5
            jitter = rng.uniform(-16, 16)
            col = tuple(
                np.clip(
                    rgb[y, x] + [jitter + rng.uniform(-7, 7), jitter, jitter + rng.uniform(-9, 9)], 0, 255
                ).astype(int)
            )
            d.polygon(
                [
                    (x - dx, y - dy),
                    (x - dx * 0.47 + nx, y - dy * 0.47 + ny),
                    (x + dx, y + dy),
                    (x + dx * 0.4 - nx, y + dy * 0.4 - ny),
                ],
                fill=col,
            )
            if width > 3.1 and rng.random() < 0.45:
                light = tuple(min(255, c + 13) for c in col)
                d.line(
                    (
                        x - dx * 0.38 + nx,
                        y - dy * 0.38 + ny,
                        x + dx * 0.67 + nx * 0.38,
                        y + dy * 0.67 + ny * 0.38,
                    ),
                    fill=light,
                )
    return grain(out, 1.8)


frame = harbor_frame("impasto")
