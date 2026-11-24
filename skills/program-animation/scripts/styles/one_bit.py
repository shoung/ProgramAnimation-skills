"""Ordered dithering on a deliberately coarse screen. Exactly two output colors."""

import numpy as np
from coast import SIZE
from night import night
from PIL import Image, ImageFilter


def frame(t):
    im = night(t).convert("L").resize((480, 270), Image.Resampling.LANCZOS)
    intensity = np.array(im, dtype=float) / 255
    blurred = np.asarray(im.filter(ImageFilter.GaussianBlur(1.4)), dtype=float) / 255
    tone = np.clip((intensity - 0.06) * 1.42 + (intensity - blurred) * 1.25, 0, 1)
    bayer = np.array([[0.0]])
    for _ in range(3):
        bayer = np.block([[4 * bayer, 4 * bayer + 2], [4 * bayer + 3, 4 * bayer + 1]])
    threshold = np.tile((bayer + 0.5) / 64, (34, 60))[:270, :480]
    colors = np.array([[27, 33, 43], [235, 226, 195]], dtype="uint8")
    return Image.fromarray(colors[(tone > threshold).astype(int)]).resize(SIZE, Image.Resampling.NEAREST)
