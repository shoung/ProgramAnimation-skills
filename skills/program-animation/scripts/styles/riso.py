"""Registered ink solids with soft screens, a paper border and printer's color controls."""

import numpy as np
from coast import SIZE, H, W, draw_mark, gradient
from lettering import titled
from PIL import Image, ImageDraw, ImageFont
from print_landscape import PALETTE, plate_scene, wavelets

COLORS = {
    **PALETTE,
    "sun": "#ed637c",
    "cloud": "#efcfdb",
    "mountain": "#a695ba",
    "face": "#71649a",
    "crest": "#c3b2cf",
    "ridge": "#8f7fa8",
    "sea": "#69749c",
    "stone": "#e7a05d",
    "shade": "#815f53",
    "seam": "#b87c54",
    "foam": "#e3b689",
    "land": "#a5a061",
    "pine": "#556856",
    "leaf": "#7b8960",
    "red": "#dc675e",
    "wall": "#eee1c6",
}


@titled("riso")
def frame(t):
    base = gradient([(0, "#aeb9bb"), (90, "#e3cf9e"), (201, "#edc398"), (345, "#f0cfb4")])
    d = ImageDraw.Draw(base)
    for m in plate_scene(t, summit=211, horizon=370, cloud_style="puffs"):
        draw_mark(d, m, COLORS[m.role])
        if m.role == "sea":
            wavelets(d, t, 370, ["#626e99", "#9294ac", "#8791b0", "#cca49a"], 1000)
    y, x = np.mgrid[:H, :W]
    rgb = np.asarray(base, dtype=float) / 255
    paper = np.array([0.979, 0.955, 0.885])
    density = np.clip(1 - rgb / paper, 0, 1)
    rng = np.random.default_rng(829)
    fiber = rng.normal(0, 0.015, (H, W))
    result = np.empty_like(rgb)
    for k, (angle, shift) in enumerate([(0.26, (0, -1)), (1.12, (1, 0)), (0.69, (-1, 1))]):
        ink = np.roll(density[:, :, k], shift, axis=(0, 1))
        u = np.cos(angle) * x + np.sin(angle) * y
        v = -np.sin(angle) * x + np.cos(angle) * y
        cell = 0.50 + 0.24 * (np.cos(u * 1.42) + np.cos(v * 1.42))
        screened = np.clip((ink + fiber - cell) * 3.4 + 0.5, 0, 1)
        # A solid ink deposit plus its porous screen leaves the silhouette readable.
        result[:, :, k] = paper[k] * (1 - 0.89 * ink - 0.11 * screened) + fiber
    sheet = Image.new("RGB", SIZE, "#f4efe2")
    sheet.paste(Image.fromarray(np.uint8(np.clip(result * 255, 0, 255))).resize((938, 510)), (11, 10))
    d = ImageDraw.Draw(sheet)
    for px, py in [(7, 7), (952, 7), (7, 531), (952, 531)]:
        d.ellipse((px - 2, py - 2, px + 2, py + 2), outline="#737484")
    for j, c in enumerate(["#e9af42", "#db5e82", "#487d9f", "#514c6c"]):
        d.rectangle((28 + j * 12, 525, 36 + j * 12, 530), fill=c)
    d.text((85, 522), "INK PROOF", font=ImageFont.load_default(size=8), fill="#716a76")
    return sheet
