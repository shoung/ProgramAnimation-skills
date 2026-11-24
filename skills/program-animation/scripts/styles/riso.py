"""Three displaced ink screens. Their overlap builds the darker print colors."""

import numpy as np
from coast import H, W, paint, scene
from PIL import Image

COLORS = {
    "sky": "#ffe5b9",
    "sun": "#ff6374",
    "cloud": "#eedbec",
    "distant": "#c7b4d9",
    "mountain": "#958cce",
    "face": "#756fb0",
    "snow": "#ead3db",
    "sea": "#8d99bf",
    "stone": "#e4a26b",
    "shade": "#b58279",
    "ochre": "#f3bd68",
    "land": "#a4a77c",
    "red": "#ee655f",
    "dark": "#514f7c",
}
INKS = [([0.16, 0.59, 0.64], 0.31), ([0.64, 0.56, 0.11], 1.14), ([0.06, 0.21, 0.60], 0.73)]


def frame(t):
    im = np.array(paint(scene(t), COLORS)).astype(float) / 255
    r, g, b = im.transpose(2, 0, 1)
    plates = [
        np.clip(1 - g + 0.24 * (r - b), 0, 1),
        np.clip(1 - r + 0.3 * (b - r), 0, 1),
        np.clip(r - b + 0.15 * (1 - b), 0, 1),
    ]
    yy, xx = np.mgrid[:H, :W]
    paper = np.empty_like(im)
    paper[:] = [0.992, 0.955, 0.854]
    grains = np.random.default_rng(382).normal(0, 0.045, (H, W))
    for (absorption, angle), density, shift in zip(INKS, plates, [(1, -2), (-1, 1), (2, 2)]):
        density = np.roll(density, shift, axis=(0, 1))
        a = np.cos(angle) * xx + np.sin(angle) * yy
        b = -np.sin(angle) * xx + np.cos(angle) * yy
        screen = 0.5 + 0.25 * (np.cos(a * 1.22) + np.cos(b * 1.22))
        coverage = np.clip((density + grains - screen) * 4 + 0.48, 0, 1)
        paper *= 1 - coverage[:, :, None] * np.array(absorption)
    return Image.fromarray(np.uint8(np.clip((paper + grains[:, :, None] * 0.19) * 255, 0, 255)))
