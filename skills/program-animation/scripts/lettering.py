"""Compose the title as a material in the scene. Coordinates refer to a 960 × 540 study."""

from functools import lru_cache, wraps
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

TYPE = Path(__file__).resolve().parents[1] / "assets/type"
# Face, nominal size, weight, position, ink. Sizes refer to the actual CJK em.
RECIPES = {
    "paper-cut": ("Sans", 61, 850, (40, 40), "#34314c"),
    "ink-wash": ("WenKai", 62, 470, (65, 43), "#272621"),
    "woodblock": ("Serif", 54, 730, (93, 49), "#fff0ce"),
    "mineral": ("WenKai", 56, 480, (74, 53), "#382e22"),
    "clay": ("Sans", 76, 820, (52, 52), "#fff0d5"),
    "riso": ("Sans", 78, 850, (44, 57), "#3e3658"),
    "clear-line": ("Serif", 48, 830, (65, 65), "#342d30"),
    "drafting": ("WenKai", 49, 500, (45, 33), "#4b3d28"),
    "isometric": ("Serif", 60, 370, (58, 56), "#52414b"),
    "point-cloud": ("Serif", 62, 340, (45, 32), "#f4ead1"),
    "one-bit": ("Sans", 67, 890, (57, 45), "#ebe2c3"),
    "impasto": ("Serif", 74, 750, (51, 45), "#fff0cc"),
}


def glyphs(text, family, size, weight, path, vertical):
    if path is None and not set(text) <= set("燈塔海岸風景研究"):
        raise ValueError(
            "For other titles, supply a full font with --font (the bundled study fonts are subsets)."
        )
    bundled = "WenKaiTC-study.ttf" if family == "WenKai" else f"Noto{family}TC-study.ttf"
    font = ImageFont.truetype(str(path or TYPE / bundled), size)
    try:
        axes = font.get_variation_axes()
    except OSError:  # Static faces already specify their weight.
        axes = []
    if axes:
        font.set_variation_by_axes(
            [
                min(max(weight, a["minimum"]), a["maximum"]) if a["name"] == b"Weight" else a["default"]
                for a in axes
            ]
        )
    missing = bytes(font.getmask("\U0010ffff"))
    if any(bytes(font.getmask(ch)) == missing for ch in text if not ch.isspace()):
        raise ValueError("The selected font lacks a title character")
    if vertical:
        box = Image.new("L", (size * 2, len(text) * (size + 6) + 8))
        d = ImageDraw.Draw(box)
        for i, ch in enumerate(text):
            d.text((size, 4 + i * (size + 6)), ch, anchor="mt", font=font, fill=255)
    else:
        bounds = font.getbbox(text)
        box = Image.new("L", (max(1, bounds[2] - bounds[0]), max(1, bounds[3] - bounds[1])))
        ImageDraw.Draw(box).text((-bounds[0], -bounds[1]), text, font=font, fill=255)
    box = box.crop(box.getbbox())
    scale = min(1, 210 / box.width, 159 / box.height if vertical else 81 / box.height)
    return box.resize(
        (max(1, round(box.width * scale)), max(1, round(box.height * scale))), Image.Resampling.LANCZOS
    )


def spaced(d, xy, text, size, gap, color):
    x, y = xy
    font = ImageFont.load_default(size=size)
    for ch in text:
        d.text((round(x), y), ch, font=font, fill=color, anchor="lt")
        x += font.getlength(ch) + gap


@lru_cache(maxsize=32)
def title_layer(style, title, font_path):
    family, size, weight, (x, y), ink = RECIPES[style]
    vertical = style in {"ink-wash", "mineral", "woodblock"}
    mask = glyphs(title, family, size, weight, font_path, vertical)
    w, h = mask.size
    plate = Image.new("RGBA", (960, 540))
    d = ImageDraw.Draw(plate)
    paper = title == "燈塔"

    def stamp(dx, dy, color, stencil=mask):
        # Source-over preserves the underlying plaque behind antialiased edges.
        overlay = (
            color.convert("RGBA")
            if isinstance(color, Image.Image)
            else Image.new("RGBA", stencil.size, color)
        )
        overlay.putalpha(stencil)
        plate.alpha_composite(overlay, (x + dx, y + dy))

    rng = np.random.default_rng(893)
    yy, xx = np.indices((h, w))
    if style == "paper-cut":
        d.rounded_rectangle((x - 18, y - 13, x + w + 31, y + h + 45), 4, fill="#9b816e")
        d.rounded_rectangle((x - 21, y - 18, x + w + 26, y + h + 40), 4, fill="#faf2e0")
    elif style in {"ink-wash", "mineral"}:
        # Slightly ragged, dry strokes, with a small vermilion intaglio seal.
        shift = np.rint(1.3 * np.sin(yy * 0.078) + 0.7 * np.cos(xx * 0.13 + yy * 0.15)).astype(int)
        arr = np.asarray(mask)[yy, np.clip(xx + shift, 0, w - 1)]
        mask = Image.fromarray(np.uint8(arr * (0.64 + 0.36 * rng.random((h, w)) ** 0.35)))
        sx, sy = x - 26, y + h - 6
        d.rounded_rectangle((sx, sy, sx + 19, sy + 23), 2, fill="#aa4937")
        d.line(
            [
                (sx + 4, sy + 4),
                (sx + 4, sy + 18),
                (sx + 9, sy + 18),
                (sx + 9, sy + 6),
                (sx + 15, sy + 6),
                (sx + 15, sy + 19),
            ],
            fill="#eee0bd",
            width=2,
        )
        if paper:
            small = glyphs("海岸風景", family, 12, 440, None, True)
            stamp(-24, 3, "#69563e", small)
    elif style == "woodblock":
        d.rectangle((x - 18, y - 17, x + w + 16, y + h + 20), fill="#443831")
        d.rectangle((x - 16, y - 15, x + w + 14, y + h + 18), fill="#ad4836")
        d.rectangle((x - 10, y - 9, x + w + 8, y + h + 12), outline="#d98a62", width=2)
        if paper:
            small = glyphs("海岸風景研究", "Serif", 14, 650, None, True)
            d.rectangle(
                (x - 47, y - 8, x - 19, y + small.height + 8), fill="#f3e5c6", outline="#595044", width=2
            )
            stamp(-41, 0, "#594838", small)
    elif style == "clear-line":
        right = x + w + (111 if paper else 22)
        d.rectangle((x - 19, y - 14, right + 4, y + h + 29), fill="#3c3540")
        d.rectangle((x - 23, y - 19, right, y + h + 24), fill="#ffe5a2", outline="#40383f", width=3)
        if paper:
            spaced(d, (x + w + 13, y + 8), "THE LIGHTHOUSE", 9, 0.45, ink)
            d.line((x + w + 13, y + 24, right - 11, y + 24), fill=ink)
    elif style == "drafting" and paper:
        spaced(d, (x + w + 18, y - 1), "PHAROS", 14, 2.8, ink)
        spaced(d, (x + w + 18, y + 24), "coastal light station", 9, 0.65, ink)
    elif style == "clay":
        stamp(4, 7, "#9c6156")
        stamp(1, 4, "#c97964")
        bevel = np.asarray(mask.filter(ImageFilter.GaussianBlur(1.25)), dtype=float) / 255
        dy, dx = (a[1:-1, 1:-1] for a in np.gradient(np.pad(bevel, 1, mode="edge")))
        raised = np.clip(np.array([250, 229, 202]) * (1 + 0.58 * dy + 0.34 * dx)[:, :, None], 0, 255)
        ink = Image.fromarray(raised.astype("uint8"))
    elif style == "riso":
        padded = Image.new("L", (w + 14, h + 14))
        padded.paste(mask, (7, 7))
        stamp(-7, -7, "#f3e9d6", padded.filter(ImageFilter.MaxFilter(13)))
        stamp(-4, 2, "#ed4c76")
        stamp(4, -1, "#4994b8")
        mask = Image.fromarray(np.uint8(np.asarray(mask) * (0.83 + 0.17 * rng.random((h, w)))))
    elif style == "point-cloud":
        padded = Image.new("L", (w + 22, h + 22))
        padded.paste(mask, (11, 11))
        stamp(
            -11, -9, "#171a1c", padded.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(2))
        )
        stamp(-11, -11, "#dac6a0", padded.filter(ImageFilter.GaussianBlur(2.7)))
        mask = Image.fromarray(np.uint8(np.asarray(mask) * (0.48 + 0.52 * rng.random((h, w)))))
    elif style == "one-bit":
        d.rectangle(
            (x - 24, y - 20, x + w + (97 if paper else 22), y + h + 38),
            fill="#1b212b",
            outline=ink,
            width=2,
        )
        if paper:
            for i, word in enumerate(("THE", "LIGHT", "HOUSE")):
                spaced(d, (x + w + 15, y + i * 15), word, 12, 1.6, ink)
    elif style == "impasto":
        stamp(1, 2, "#c89086")
        # Paint drag leaves ridges along the diagonal nib and small breaks at stroke ends.
        drag = 0.5 + 0.5 * np.sin(xx * 0.94 + yy * 0.81 + 1.4 * np.cos(yy * 0.084))
        strength = np.clip(0.77 + 0.18 * drag + 0.07 * rng.random((h, w)), 0, 1)
        mask = Image.fromarray(np.uint8(np.asarray(mask) * strength))
        oily = np.array([243, 224, 187]) + drag[:, :, None] * [12, 13, 17]
        ink = Image.fromarray(oily.astype("uint8"))
    stamp(0, 0, ink, mask)
    if paper and style in {"clay", "paper-cut", "riso", "isometric", "impasto", "point-cloud"}:
        sub = {"paper-cut": "#514957", "riso": "#343967", "clay": "#8e4d44", "impasto": "#ffebd2"}.get(
            style, ink
        )
        spaced(d, (x, y + h + 8), "THE LIGHTHOUSE", 12, 2.1, sub)
        if style == "riso":
            d.line((x, y + h + 28, x + w + 8, y + h + 28), fill="#367eaa", width=3)
    if paper and style in {"one-bit", "clear-line"}:
        small = glyphs("海岸風景研究", "Sans", 12, 690, None, False)
        stamp(0, h + 9, ink, small)
    bounds = plate.getbbox()
    plate = plate.crop(bounds)
    if style == "one-bit":
        plate.putalpha(plate.getchannel("A").point(lambda n: 255 if n >= 128 else 0))
        alpha = plate.getchannel("A")
        flat = Image.new("RGB", plate.size, (27, 33, 43))
        flat.paste(plate, mask=alpha)
        solid = Image.new("RGBA", plate.size, (27, 33, 43))
        solid.paste((235, 226, 195, 255), mask=flat.convert("L").point(lambda n: 255 if n > 126 else 0))
        solid.putalpha(alpha)
        plate = solid
    return bounds[:2], plate


def letter(im, style, title="燈塔", font_path=None):
    """Apply the title at 960 × 540. An empty string returns the clean artwork."""
    if not title.strip():
        return im
    pos, plate = title_layer(style, title, font_path)
    im.paste(plate, pos, plate.getchannel("A"))
    return im


def titled(style):
    """Give a frame renderer reusable title and font arguments."""

    def decorate(draw_scene):
        @wraps(draw_scene)
        def frame(t, title="燈塔", font_path=None):
            return letter(draw_scene(t), style, title, font_path)

        return frame

    return decorate
