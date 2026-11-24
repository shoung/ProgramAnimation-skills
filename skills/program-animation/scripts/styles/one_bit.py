"""Two-ink maritime engraving with a fixed ordered screen and solid-color lettering."""

import numpy as np
from PIL import Image, ImageFilter

from styles import harbor_frame


def dither(image):
    """Engrave a luminance study with the gallery's fixed two-ink screen."""
    im = image.convert("L")
    intensity = np.array(im, dtype=float) / 255
    blurred = np.asarray(im.filter(ImageFilter.GaussianBlur(1.4)), dtype=float) / 255
    tone = np.clip((intensity - 0.078) * 1.22 + (intensity - blurred) * 0.95, 0, 1)
    bayer = np.array([[0.0]])
    for _ in range(3):
        bayer = np.block([[4 * bayer, 4 * bayer + 2], [4 * bayer + 3, 4 * bayer + 1]])
    threshold = np.tile((bayer + 0.5) / 64, ((im.height + 7) // 8, (im.width + 7) // 8))[
        : im.height, : im.width
    ]
    colors = np.array([[27, 33, 43], [235, 226, 195]], dtype="uint8")
    return Image.fromarray(colors[(tone > threshold).astype(int)])


frame = harbor_frame("one-bit")
