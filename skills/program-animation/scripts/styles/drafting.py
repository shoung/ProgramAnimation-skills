"""Graphite field survey with two instrument plans, loose leaders and a worn paper edge."""

import math

import numpy as np
from coast import SIZE, H, Mark, W, draw_mark, grain
from headland import landscape
from lettering import titled
from PIL import Image, ImageDraw, ImageFont

INK = "#746044"
PALE = "#b39b74"
PAPER = "#e6d3a6"


@titled("drafting")
def frame(t):
    im = Image.new("RGB", SIZE, PAPER)
    d = ImageDraw.Draw(im)

    def note(x, y, s, n=9):
        d.text((x, y), s, fill=INK, font=ImageFont.load_default(size=n))

    def leader(points, s):
        d.line(points, fill=PALE)
        x, y = points[-1]
        note(x + 4, y - 6, s)

    # Large coastal elevation and a ray diagram. Leave the left margin free for measurements.
    coast = Image.new("RGB", SIZE, PAPER)
    pd = ImageDraw.Draw(coast)
    for m in landscape(t):
        if m.role in {"sun", "cloud", "sea", "foam", "crest", "leaf", "lip"}:
            continue
        pts = [(84 + x * 1.10, 8 + y * 1.03) for x, y in m.xy]
        xy = Mark(m.kind, m.role, pts, m.width)
        c = PALE if m.role in {"mountain", "face", "ridge", "seam"} else INK
        draw_mark(pd, xy, c if m.kind == "line" else PAPER, c)
        if m.role in {"shade", "shadow", "pine", "roof"}:
            mask = Image.new("L", SIZE)
            draw_mark(ImageDraw.Draw(mask), xy, 255)
            tone = coast.copy()
            q = ImageDraw.Draw(tone)
            xs, ys = zip(*pts)
            y0, y1 = min(ys), max(ys)
            for x in range(int(min(xs) - y1 + y0) - 2, int(max(xs) + 2), 4):
                q.line((x, y1, x + (y1 - y0) * 0.68, y0), fill="#a18a63", width=2)
            coast.paste(tone, (0, 0), mask)
    reveal = np.broadcast_to(np.clip((np.arange(W) - 330) / 66, 0, 1), (H, W))
    im.paste(coast, mask=Image.fromarray(np.uint8(reveal * 255)))
    for j in range(16):
        y = 451 + j * 3
        d.line((390 + (j * 61) % 131, y, 904 - (j * 41) % 140, y + 0.7), fill="#c8b68e")
    lamp = (773, 105)
    for angle in [-0.07 + 0.02 * math.sin(t), 0.16 + 0.04 * math.sin(t)]:
        d.line((464, lamp[1] + 309 * angle, *lamp), fill="#a58f6b")
    note(482, 64, "AA  /  OPTICAL AXIS", 9)
    # Measured elevation. The separate tower is larger than the profile view.
    x = 131
    d.line((x, 78, x, 493), fill=PALE)
    d.polygon([(x - 34, 462), (x - 20, 181), (x + 19, 181), (x + 36, 462)], outline=INK, width=2)
    for y in [182, 209, 263, 273, 337, 370, 451]:
        w = 20 + (y - 181) * 0.057
        d.line((x - w, y, x + w, y + 1), fill=INK)
    for y in [225, 304, 420]:
        d.rectangle((x - 5, y, x + 6, y + 15), outline=INK)
    for y, w, h in [(460, 42, 8), (468, 47, 6), (177, 33, 7), (157, 32, 19), (130, 17, 26), (125, 21, 5)]:
        d.rectangle((x - w, y, x + w, y + h), outline=INK, width=2)
    for xx in range(x - 28, x + 29, 7):
        d.line((xx, 158, xx, 176), fill=INK)
    d.polygon([(x - 22, 125), (x - 14, 117), (x, 102), (x + 15, 118), (x + 23, 125)], outline=INK)
    d.line((x, 102, x, 89), fill=INK)
    for i in range(50):
        y = 185 + i * 5
        w = 20 + (y - 181) * 0.057
        d.line((x + w - 9, y + 7, x + w - 1, y), fill=PALE)
    d.line((65, 104, 65, 470), fill=PALE)
    for y in [105, 178, 263, 337, 461, 474]:
        d.line((58, y, 99, y - 1), fill=PALE)
    leader([(160, 163), (202, 151), (216, 150)], "Gallery")
    leader([(153, 330), (196, 321), (218, 318)], "Masonry")
    leader([(170, 465), (202, 456), (219, 456)], "Plinth")
    # Lantern ring and lens section, retained at field-notebook scale.
    for cx, cy, r in [(351, 198, 49), (303, 418, 43)]:
        for f in [1.16, 1, 0.83, 0.78]:
            rad = r * f
            d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), outline=PALE if f > 1 else INK)
        for j in range(16):
            a = j * math.tau / 16
            d.line(
                (
                    cx + r * math.cos(a),
                    cy + r * math.sin(a),
                    cx + r * 1.10 * math.cos(a),
                    cy + r * 1.10 * math.sin(a),
                ),
                fill=INK,
            )
        d.line((cx - r - 12, cy, cx + r + 12, cy), fill=PALE)
        if cy > 300:
            for a in [t, t + math.pi / 2]:
                ox, oy = math.cos(a) * r * 0.68, math.sin(a) * r * 0.68
                d.line((cx - ox, cy - oy, cx + ox, cy + oy), fill=INK)
    d.line((167, 68, 373, 68), fill=PALE)
    note(265, 82, "01   Tower elevation")
    note(265, 95, "02   Lantern gallery")
    note(300, 270, "Horizontal section  /  A")
    note(305, 285, "Scale in metres")
    note(80, 494, "Elevation   1 : 160")
    d.rectangle((916, 475, 933, 503), fill="#995039")
    d.line((920, 480, 927, 480, 927, 492, 921, 492, 921, 499), fill="#dfc795", width=2)
    y, x = np.ogrid[:H, :W]
    edge = np.minimum(np.minimum(x, W - 1 - x), np.minimum(y, H - 1 - y))
    weather = np.exp(-edge / 25) * (0.15 + 0.055 * np.sin(x * 0.024 + y * 0.043))
    # Pressure and paper tooth vary the graphite independently of the aged ground.
    image = np.asarray(im, dtype=float)
    graphite = np.maximum(np.array([230, 211, 166]) - image, 0)
    ghost = np.roll(graphite, (1, 2), axis=(0, 1))
    tooth = 0.09 * np.sin(x * 0.37 + y * 0.41) + 0.07 * np.sin(x * 0.17 - y * 0.12)
    paper = (image + graphite * tooth[:, :, None] - ghost * 0.095) * (1 - weather[:, :, None])
    return grain(Image.fromarray(np.uint8(np.clip(paper, 0, 255))), 2.7, 0.95)
