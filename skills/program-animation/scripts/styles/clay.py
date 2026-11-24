"""Hand-modelled clay forms. Each lump is a smoothly lit ellipsoid with a pinched silhouette."""

import math

import numpy as np
from coast import SIZE
from PIL import Image, ImageColor

from styles import harbor_frame


def lump(im, cx, cy, rx, ry, color, tilt=0, salt=0):
    """Shade an ellipsoid in its local tangent plane; deterministic small dents catch the light."""
    r = math.ceil(max(rx, ry) * 1.12) + 2
    x0, y0 = max(0, int(cx) - r), max(0, int(cy) - r)
    x1, y1 = min(SIZE[0], int(cx) + r + 1), min(SIZE[1], int(cy) + r + 1)
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    c, s = math.cos(tilt), math.sin(tilt)
    u = ((xx - cx) * c + (yy - cy) * s) / rx
    v = (-(xx - cx) * s + (yy - cy) * c) / ry
    ang = np.arctan2(v, u)
    radius = 1 + 0.021 * np.sin(ang * 3 + salt) + 0.014 * np.sin(ang * 5 + salt * 0.7)
    rad = np.sqrt(u * u + v * v) / radius
    alpha = np.clip((1 - rad) * min(rx, ry) + 0.5, 0, 1)
    z = np.sqrt(np.maximum(0, 1 - rad**2))
    lit = 0.76 + np.maximum(0, (-u * 0.43 - v * 0.72 + z * 0.54)) * 0.31
    lit += 0.014 * np.sin((xx + yy) * 0.9 + salt) * np.sin(yy * 0.13) + 0.008 * np.cos(yy * 0.73)
    base = np.array(ImageColor.getrgb(color))
    patch = lit[:, :, None] * base
    prior = np.asarray(im.crop((x0, y0, x1, y1)))
    mix = patch * alpha[:, :, None] + prior * (1 - alpha[:, :, None])
    im.paste(Image.fromarray(np.uint8(np.clip(mix, 0, 255))), (x0, y0))


frame = harbor_frame("clay")
