"""Survey sheet with an orthographic elevation, lantern plan and measured coastal profile."""

import math

from coast import SIZE, draw_mark, grain, scene
from PIL import Image, ImageDraw, ImageFont

INK = "#745e46"
FAINT = "#ad9978"
PAPER = "#eddfbd"


def frame(t):
    im = Image.new("RGB", SIZE, PAPER)
    d = ImageDraw.Draw(im)
    font = ImageFont.load_default(size=12)
    small = ImageFont.load_default(size=10)

    def label(x, y, s, face=small, color=INK):
        d.text((x, y), s, fill=color, font=face)

    def dim(x, y, x2, y2):
        d.line((x, y, x2, y2), fill=FAINT)
        for a, b in [(x, y), (x2, y2)]:
            d.line((a - 3, b + 4, a + 3, b - 4), fill=INK)

    d.rectangle((18, 17, 942, 522), outline=FAINT)
    d.line((38, 68, 921, 68), fill=INK)
    label(38, 28, "PHAROS", ImageFont.load_default(size=29))
    label(181, 45, "COASTAL SURVEY   /   LIGHT STATION", font)
    label(790, 45, "PLATE  VII     1 : 160", font)
    # Architectural elevation is drawn at its own scale.
    x = 160
    d.line((x, 90, x, 451), fill=FAINT)
    d.line((55, 445, 264, 445), fill=INK)
    d.polygon([(x - 36, 430), (x - 19, 169), (x + 19, 169), (x + 36, 430)], outline=INK)
    for y in [184, 204, 250, 276, 341, 370, 425]:
        w = 19 + (y - 169) * 17 / 261
        d.line((x - w, y, x + w, y), fill=INK)
        for i in range(4):
            d.line((x + w - 8 + i * 2, y + 1, x + w - 10 + i * 2, y + 9), fill=FAINT)
    for y in [218, 294, 388]:
        d.rectangle((x - 5, y, x + 4, y + 12), outline=INK)
    d.rectangle((x - 43, 430, x + 43, 438), outline=INK)
    d.rectangle((x - 47, 438, x + 47, 444), outline=INK)
    for y, w, h in [(166, 30, 5), (151, 29, 15), (128, 17, 22), (123, 22, 5)]:
        d.rectangle((x - w, y, x + w, y + h), outline=INK)
    for xx in range(x - 27, x + 29, 7):
        d.line((xx, 152, xx, 165), fill=FAINT)
    d.polygon(
        [(x - 23, 123), (x - 17, 117), (x - 7, 109), (x, 101), (x + 9, 110), (x + 22, 123)], outline=INK
    )
    d.line((x, 101, x, 91), fill=INK)
    dim(77, 102, 77, 444)
    label(41, 271, "28.60")
    dim(123, 458, 196, 458)
    label(141, 462, "5.40")
    label(90, 488, "A   /   TOWER ELEVATION", font)
    # Lantern floor plan. Rotating rays make the survey sheet an animation.
    cx, cy = 374, 166
    for r in [51, 42, 36, 12, 7]:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=FAINT if r in {51, 7} else INK)
    for j in range(12):
        a = j * math.tau / 12
        d.line(
            (cx + 36 * math.cos(a), cy + 36 * math.sin(a), cx + 43 * math.cos(a), cy + 43 * math.sin(a)),
            fill=INK,
        )
    for a in [t - 0.18, t + 0.18]:
        d.line((cx, cy, cx + 48 * math.cos(a), cy + 48 * math.sin(a)), fill="#a86946")
    label(312, 226, "B   /   LANTERN PLAN", font)
    # Plot the same island in pencil, with stipple and hatching on the cliff.
    profile = Image.new("RGB", SIZE, PAPER)
    pd = ImageDraw.Draw(profile)
    for i, m in enumerate(scene(t)):
        if m.role in {"sea", "sun", "cloud", "distant", "mountain", "face", "snow", "ridge"} or (
            m.role == "ripple" and i % 8
        ):
            continue
        color = FAINT if m.role in {"ripple", "foam", "leaf", "ochre"} else INK
        draw_mark(pd, m, color if m.kind == "line" else PAPER, color)
        if m.role == "shade":
            a, b, c = m.xy
            for n in range(1, 10):
                f = n / 10
                pd.line(
                    [
                        (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f),
                        (a[0] + (c[0] - a[0]) * f, a[1] + (c[1] - a[1]) * f),
                    ],
                    fill=FAINT,
                )
    profile = profile.crop((30, 49, 940, 475)).resize((634, 297), Image.Resampling.LANCZOS)
    im.paste(profile, (283, 247))
    # Reestablish the sheet's lower margin after inserting the coastal section.
    d.rectangle((283, 487, 942, 522), fill=PAPER)
    d.line((18, 522, 942, 522), fill=FAINT)
    d.line((942, 247, 942, 522), fill=FAINT)
    label(540, 490, "C   /   SOUTHERN APPROACH", font)
    for j in range(5):
        d.rectangle((753 + j * 26, 208, 779 + j * 26, 213), fill=INK if j % 2 == 0 else PAPER, outline=INK)
    label(752, 218, "0          5         10         15 m")
    label(556, 119, "OPTICAL ASSEMBLY", font)
    label(556, 143, "01   Fresnel lens")
    label(556, 163, "02   Lantern gallery")
    d.line((426, 155, 479, 134, 538, 134), fill=FAINT)
    return grain(im, 3.2, 0.8)
