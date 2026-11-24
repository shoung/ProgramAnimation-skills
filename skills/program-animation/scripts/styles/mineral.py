"""Stone-blue shadow planes and malachite pigment on a softly burnished gold ground."""

import numpy as np
from coast import H, W, draw_mark, gradient, grain
from lettering import titled
from PIL import Image, ImageDraw
from print_landscape import PALETTE, plate_scene, wavelets

COLORS = {
    **PALETTE,
    "sun": "#b44931",
    "cloud": "#ecdaa7",
    "mountain": "#73ad87",
    "face": "#147d91",
    "crest": "#aabd78",
    "ridge": "#579879",
    "sea": "#aaa981",
    "stone": "#63b69a",
    "shade": "#275985",
    "lip": "#d3ad54",
    "seam": "#459689",
    "land": "#a7a35f",
    "foam": "#c5ad67",
    "wall": "#ebdbaf",
    "red": "#aa4938",
    "shadow": "#b0a180",
    "pine": "#396853",
    "leaf": "#609261",
}


@titled("mineral")
def frame(t):
    im = gradient([(0, "#b29863"), (163, "#c3a26b"), (346, "#d9bd86")])
    d = ImageDraw.Draw(im)
    for m in plate_scene(t, summit=190, horizon=376):
        draw_mark(d, m, COLORS[m.role])
        if m.role == "mountain":
            points = m.xy
            top = min(points, key=lambda p: p[1])
            left, right = points[0], points[-1]
            span = right[0] - left[0]
            d.polygon(
                [top, (top[0] - 0.36 * span, left[1]), (top[0] - 0.12 * span, left[1])], fill="#50a491"
            )
            d.polygon(
                [top, (top[0] + 0.04 * span, right[1]), (top[0] + 0.19 * span, right[1])], fill="#288e94"
            )
            d.polygon(
                [top, (top[0] + 0.19 * span, right[1]), (top[0] + 0.31 * span, right[1])], fill="#386d91"
            )
        if m.role == "sea":
            wavelets(d, t, 376, ["#999871", "#b8b489", "#8f916d", "#c9bd91"], 720)
    y, x = np.ogrid[:H, :W]
    edge = np.maximum(abs((x - 480) / 480) ** 5, abs((y - 270) / 270) ** 6)
    fibers = 1.5 * np.sin(y * 2.5) + 1.4 * np.sin(0.031 * y + 0.9 * np.sin(x * 0.007))
    weave = 0.68 * np.sin(x * 2.4) + 0.83 * np.cos(y * 2.1 + x * 0.009)
    flakes = np.maximum(0, np.sin(x * 1.73 + y * 0.16) * np.cos(y * 1.91) - 0.95) * 98
    toned = (
        np.asarray(im).astype(float) * (1 - 0.14 * edge[:, :, None])
        + (fibers + weave)[:, :, None]
        + flakes[:, :, None] * [1.0, 0.84, 0.44]
    )
    return grain(Image.fromarray(np.uint8(np.clip(toned, 0, 255))), 2.8, 1.4)
