"""Material plates for the harbor tram. Colors refer to the actual painted surfaces."""

import math
import random
from functools import lru_cache

import numpy as np
from coast import BASE, SIZE, H, W, draw_mark, gradient, grain
from harbor_scene import PREVIEW_PHASE, station
from lettering import RECIPES, STUDY_TITLE, study_font, weighted_font
from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFilter, ImageFont
from print_landscape import PALETTE, wavelets
from styles import (
    clear_line,
    impasto,
    ink_wash,
    mineral,
    one_bit,
    paper_cut,
    riso,
    woodblock,
)

PIGMENTS = {
    # Roof, train body, car shadow, glazing, platform, steel, lamp, lining.
    "paper-cut": ("#657f74", "#ce644e", "#aa5849", "#53767a", "#d8b08f", "#627472", "#ffdb86", "#f9d89b"),
    "ink-wash": ("#494943", "#282925", "#52544e", "#77796e", "#e2dece", "#5a5b50", "#efe2b3", "#d9d3bc"),
    "woodblock": ("#657971", "#bb5138", "#963d32", "#456276", "#d2b680", "#536070", "#fee3a0", "#e9c47e"),
    "mineral": ("#49897b", "#367d73", "#255889", "#496f83", "#bba66e", "#776948", "#ffdf9b", "#d8b15d"),
    "riso": ("#667f84", "#dd6759", "#a45160", "#686781", "#e7b17e", "#68637e", "#ffdda1", "#fac681"),
    "clear-line": ("#609492", "#d86c51", "#ad665c", "#608d9b", "#e3b994", "#786d75", "#ffdf89", "#f3c980"),
    "impasto": ("#528f8a", "#d86443", "#924f50", "#527e8a", "#cf9673", "#7f6d73", "#ffe2a2", "#efc07c"),
    "point-cloud": ("#5ba697", "#f37c58", "#bd5d4a", "#aed2c0", "#937f6d", "#94a1a2", "#ffe7ae", "#edc88d"),
    "one-bit": ("#82908b", "#90918b", "#575c5f", "#a9b3af", "#606565", "#858a83", "#f7f5df", "#c9cabe"),
}
MODULE = {
    "paper-cut": paper_cut,
    "ink-wash": ink_wash,
    "woodblock": woodblock,
    "mineral": mineral,
    "riso": riso,
    "clear-line": clear_line,
    "impasto": impasto,
}
SKIES = {
    "paper-cut": [(0, "#f2d9bb"), (539, "#f4d8b8")],
    "ink-wash": [(0, "#efede1"), (539, "#eeebde")],
    "woodblock": [(0, "#29466a"), (65, "#6c889d"), (171, "#e5d4b3"), (307, "#f3e3bf")],
    "mineral": [(0, "#b49a67"), (175, "#d2b47c"), (450, "#e1c792")],
    "riso": [(0, "#9eacb6"), (118, "#e8c3a0"), (276, "#f2ceac")],
    "clear-line": [(0, "#78b5bd"), (210, "#ebddba"), (540, "#f8e5bc")],
    "impasto": [(0, "#615894"), (111, "#bf83a3"), (218, "#efa392"), (325, "#f5c58d")],
    "drafting": [(0, "#e8d9b7"), (539, "#e4d3ab")],
}
ygrid, xgrid = np.mgrid[:H, :W]


def palette(style):
    p = {**BASE, **PALETTE, **getattr(MODULE.get(style), "COLORS", {})}
    copper, body, bodyshade, window, ground, metal, lamp, trim = PIGMENTS[style]
    p.update(
        copper=copper,
        body=body,
        bodyshade=bodyshade,
        window=window,
        ground=ground,
        metal=metal,
        lamp=lamp,
        trim=trim,
        eave=p["dark"],
        frame=p["dark"],
        wire=p["dark"],
        bumper=metal,
        undercar=p["dark"],
        cream=p["wall"],
        stripe=trim,
        glint=p["wall"],
        joint=p["seam"],
        signboard=p["dark"],
        signink=p["wall"],
    )
    if style == "ink-wash":
        p.update(
            distant="#d6d4c9",
            joint="#c6c3b5",
            wire="#7d7c71",
            foam="#bebbae",
            lip="#bebbac",
            signboard="#43453f",
            signink="#f0eddf",
        )
    if style == "mineral":
        p.update(distant="#96a884", window="#436b74", signboard="#475844")
    return p


@lru_cache(maxsize=64)
def fitted_text(text, width, height, font):
    face = weighted_font(font, 72, 580)
    l, t, r, b = face.getbbox(text)
    tile = Image.new("L", (r - l, b - t))
    ImageDraw.Draw(tile).text((-l, -t), text, font=face, fill=255)
    s = min(width / tile.width, height / tile.height)
    return tile.resize(
        (max(1, round(tile.width * s)), max(1, round(tile.height * s))), Image.Resampling.LANCZOS
    )


def glyph_mark(im, m, color, font):
    (x, y), (r, b) = m.xy
    stencil = fitted_text(STUDY_TITLE if m.kind == "sign" else "07", r - x, b - y, font)
    im.paste(color, (int((x + r - stencil.width) / 2), int((y + b - stencil.height) / 2)), stencil)


def paper_shadow(im, m):
    xs, ys = zip(*m.xy)
    l, t, r, b = int(min(xs)) - 5, int(min(ys)) - 5, int(max(xs)) + 11, int(max(ys)) + 13
    mask = Image.new("L", (r - l + 1, b - t + 1))
    draw_mark(ImageDraw.Draw(mask), m, 115, offset=(3 - l, 4 - t))
    im.paste("#78685e", (l, t), mask.filter(ImageFilter.GaussianBlur(2)))


def waves(im, style, t):
    d = ImageDraw.Draw(im)
    rng = random.Random(2259)
    if style == "paper-cut":
        for i, (py, fill) in enumerate(
            [(286, "#79b1a7"), (317, "#609ea1"), (354, "#4f8e98"), (398, "#437c90"), (450, "#326780")]
        ):
            pts = []
            for x in range(-2, 966, 2):
                k = ((x + 22 * i) % (53 + i * 4)) / (53 + i * 4) * 2 - 1
                pts.append((x, py - (5 + i) * math.sqrt(max(0, 1 - k * k))))
            d.polygon(pts + [(965, 542), (-2, 542)], fill=fill)
            d.line(pts, fill="#d9e2cc", width=2)
    elif style in ("woodblock", "mineral", "riso"):
        colors = {
            "woodblock": ["#96a9a7", "#304e6a", "#d6ceaf"],
            "mineral": ["#9c9b73", "#c3ba8a", "#8e946f"],
            "riso": ["#9898b2", "#7984a3", "#c6a5a3"],
        }[style]
        wavelets(d, t - PREVIEW_PHASE, 270, colors, 1350 if style == "woodblock" else 730)
    else:
        colors = {
            "clear-line": ["#65a99f", "#91c6af"],
            "ink-wash": ["#b4b6ab", "#cccbbf", "#9b9c91"],
            "impasto": ["#4ca59f", "#89c2ad", "#eab78f"],
        }[style]
        for _ in range(230 if style != "impasto" else 760):
            x = rng.uniform(-41, 960)
            y = rng.uniform(270, 455)
            depth = (y - 269) / 180
            w = rng.uniform(4, 35) * (0.5 + 1.9 * depth)
            rise = rng.uniform(0.3, 2)
            d.line(
                [(x, y), (x + 0.3 * w, y - rise), (x + 0.88 * w, y - 0.4 * rise), (x + w, y)],
                fill=rng.choice(colors),
                width=1 + int(style == "impasto" and depth > 0.3),
            )


def print_plate(style, t):
    font = study_font(RECIPES[style][0])
    im = gradient(SKIES[style])
    p = palette(style)
    marks = station(style, t)
    d = ImageDraw.Draw(im)
    for m in marks:
        role = m.role
        if m.kind in ("sign", "route"):
            glyph_mark(im, m, p[role], font)
            continue
        if style == "ink-wash" and (role == "glint" or (m.group == "sky" and role == "cloud")):
            continue
        if style == "paper-cut" and role == "sun":
            for rad, col in [(135, "#f1c79f"), (94, "#eba885"), (67, "#e88b73")]:
                d.ellipse((332 - rad, 103 - rad, 332 + rad, 103 + rad), fill=col)
        if (
            style == "paper-cut"
            and m.kind == "poly"
            and role in ("cloud", "body", "roof", "wall", "cream", "copper", "mountain", "sun")
        ):
            paper_shadow(im, m)
        color = p[role]
        edge = None
        width = 1
        if (
            style == "woodblock"
            and m.kind == "poly"
            and role not in ("ground", "sea", "glint", "distant", "trim")
        ):
            edge = "#464b49"
        if (
            style == "clear-line"
            and m.kind == "poly"
            and role not in ("sea", "ground", "glint", "distant", "face", "shadow", "bodyshade")
        ):
            edge = clear_line.INK if m.group in ("hall", "tram", "ferry") else "#797281"
            width = 3 if role in ("body", "copper", "roof", "wall", "hull") else 1
        draw_mark(d, m, color, edge, width)
        if role == "sea":
            waves(im, style, t)
        if style == "ink-wash" and m.group == "hills":
            xs, ys = zip(*m.xy)
            top = min(ys)
            mask = Image.new("L", SIZE)
            draw_mark(ImageDraw.Draw(mask), m, 255)
            fade = np.clip(0.19 + 0.89 * (ygrid - top) / (272 - top) + 0.31 * ink_wash.damp_sheet(), 0, 1)
            im.paste("#efede1", (0, 0), Image.fromarray(np.uint8(np.asarray(mask) * fade)))
        if style == "clear-line" and m.kind == "poly" and role in ("bodyshade", "shadow", "face"):
            # The source pen routine takes double-resolution face-local coordinates.
            from coast import Mark

            xs, ys = zip(*m.xy)
            l, t = math.floor(min(xs)), math.floor(min(ys))
            w, h = math.ceil(max(xs)) - l + 1, math.ceil(max(ys)) - t + 1
            tile = im.crop((l, t, l + w, t + h)).resize((w * 2, h * 2))
            mm = Mark(
                "poly",
                "shade" if role == "bodyshade" else role,
                [(2 * (x - l), 2 * (y - t)) for x, y in m.xy],
            )
            clear_line.hatching(tile, mm)
            im.paste(tile.resize((w, h), Image.Resampling.LANCZOS), (l, t))
        if style == "mineral" and role == "mountain":
            top = min(m.xy, key=lambda xy: xy[1])
            tx = top[0]
            for off, col in [(14, "#40978c"), (38, "#337b89")]:
                d.polygon([top, (tx + off, 267), (tx + off + 21, 267)], fill=col)
    if style == "ink-wash":
        wash = ink_wash.damp_sheet()
        shift = np.rint(4 * wash).astype(int)
        a = np.asarray(im)[np.clip(ygrid + shift, 0, H - 1), np.clip(xgrid - shift, 0, W - 1)].astype(float)
        tooth = (0.5 + 0.5 * np.cos(xgrid * 0.79 + ygrid * 0.12 + 6 * wash)) ** 7
        dry = np.maximum(0, 239 - a[:, :, 0]) * np.maximum(0, wash + 0.19) * (0.17 + 0.46 * tooth)
        im = grain(Image.fromarray(np.uint8(np.clip(a + dry[:, :, None], 0, 255))), 2.3, 0.6)
    elif style == "mineral":
        a = np.asarray(im, float)
        fleck = np.maximum(0, np.sin(xgrid * 1.49 + ygrid * 0.23) * np.cos(ygrid * 0.76) - 0.91) * 108
        edge = np.maximum(abs((xgrid - 480) / 480) ** 6, abs((ygrid - 270) / 270) ** 6)
        light = np.sin(ygrid * 2.4) + np.sin(xgrid * 1.7) * 0.63 + 2 * np.cos(xgrid * 0.009 + ygrid * 0.012)
        im = grain(
            Image.fromarray(
                np.uint8(
                    np.clip(
                        a * (1 - 0.12 * edge[:, :, None])
                        + light[:, :, None]
                        + fleck[:, :, None] * [1, 0.86, 0.48],
                        0,
                        255,
                    )
                )
            ),
            2,
            1,
        )
    elif style == "woodblock":
        a = np.asarray(im, float)
        grainline = (0.5 + 0.5 * np.sin(ygrid * 1.79 + 1.44 * np.sin(xgrid * 0.012 + ygrid * 0.041))) ** 7
        im = grain(Image.fromarray(np.uint8(a + (248 - a) * (0.059 * grainline[:, :, None]))), 2.8, 1)
    elif style == "riso":
        im = riso.print_sheet(im)
    elif style == "impasto":

        def direction(x, y):
            if y > 440 - 0.167 * x:
                return -0.22 + 0.10 * math.sin(y * 0.06)
            if 312 < x < 695 and 197 < y < 437:
                return -1.22 if y < 340 else -0.26
            if y > 268:
                return -0.02 + 0.11 * math.sin(y * 0.12)
            return -0.6 + 0.44 * math.sin(0.013 * x + 0.023 * y)

        # Keep fine lettering and the traveler's gestures legible with a small finishing brush.
        detail = np.ones((H, W))
        detail[207:249, 735:867] = 0.23
        detail[248:278, 355:435] = 0.32
        detail[289:386, 789:854] = 0.38
        im = impasto.paint_strokes(im, direction, detail)
    elif style == "paper-cut":
        im = grain(im, 2.2, 0.4)
    return im


def nocturne(style, t):
    font = study_font(RECIPES[style][0])
    marks = station(style, t)
    p = palette(style)
    colors = {
        "sky": "#0c1321",
        "sun": "#e7ddbc",
        "distant": "#34475c",
        "mountain": "#425c78",
        "face": "#304157",
        "ridge": "#678595",
        "sea": "#489aa4",
        "foam": "#a5ceca",
        "shade": "#6e575a",
        "dark": "#485760",
        "red": "#e58868",
        "wall": "#f5cfaa",
        "glass": "#d0bda1",
        "roof": "#bc7b5b",
        "shadow": "#8a7371",
        "hull": "#de876d",
        "lip": "#d4bf9b",
        "bird": "#889fa6",
        "step": "#c5ae8c",
    }
    p.update(
        colors,
        cream="#efcda7",
        wire="#81969d",
        frame="#566566",
        glint="#e9dec1",
        eave="#5e6764",
        signboard="#273840",
        signink="#ffe8b6",
        joint="#8d7c74",
    )
    keys = ["sky"] + sorted({m.role for m in marks})
    lookup = {k: i for i, k in enumerate(keys)}
    surf = Image.new("L", SIZE)
    pen = ImageDraw.Draw(surf)
    for m in marks:
        if m.kind in ("sign", "route"):
            # Role ids are discrete labels; use a binary stencil here.
            (x, y), (r, b) = m.xy
            mask = fitted_text(STUDY_TITLE if m.kind == "sign" else "07", r - x, b - y, font).point(
                lambda a: 255 if a >= 115 else 0
            )
            surf.paste(lookup[m.role], (int((x + r - mask.width) / 2), int((y + b - mask.height) / 2)), mask)
        else:
            draw_mark(pen, m, lookup[m.role])
    ids = np.asarray(surf)
    rng = np.random.default_rng(211)
    h, w = ids.shape
    sky = ids == 0
    water = ids == lookup["sea"]
    ground = ids == lookup["ground"]
    hills = np.isin(ids, [lookup[k] for k in ("mountain", "distant", "face")])
    rim = (ids != np.roll(ids, 1, 0)) | (ids != np.roll(ids, 1, 1))
    rim[0, :] = False
    rim[:, 0] = False
    xx, yy = xgrid, ygrid
    dep = np.maximum(0, (yy - 269) / 200)
    wave = (
        0.5 + 0.5 * np.cos(76 * np.log1p(2 * dep) + t - PREVIEW_PHASE + 2 * np.sin(xx * 0.027 + yy * 0.061))
    ) ** 5
    moonpath = np.exp(-(((xx - 332 - 9 * np.sin(yy * 0.075)) / (20 + 50 * dep)) ** 2))
    streetlamp = np.exp(-(((xx - 397) / 34) ** 2))
    wave *= 0.35 + 0.65 * (0.5 + 0.5 * np.sin(xx * 0.043 + yy * 0.074))
    light = np.full((h, w), 0.74)
    light[sky] = 0.052
    light[water] = (0.13 + wave * (0.49 + 1.25 * moonpath))[water]
    light[hills] = (0.21 + 0.4 * (0.5 + 0.5 * np.cos(yy * 0.8 + xx * 0.031)) ** 4)[hills]
    light[ground] = (0.34 + 0.055 * np.sin(yy * 0.095 + xx * 0.029) + 0.31 * streetlamp)[ground]
    for k in ("lamp", "signink", "trim", "window"):
        light[ids == lookup[k]] *= 1.24
    if style == "point-cloud":
        # Motorcar windows reflect cool skylight above warmer interior lamps. Particles
        # on the painted nose follow its curve; the side darkens toward the trailing bogie.
        cab = ids == lookup["body"]
        light[cab] *= (0.48 + 0.57 * np.exp(-(((xx - 390) / 54) ** 2)))[cab]
        side = ids == lookup["bodyshade"]
        light[side] *= np.clip(0.93 - (xx - 468) * 0.0015, 0.5, 1)[side]
        glass = ids == lookup["window"]
        cabin = np.clip((yy - 251 + 0.18 * np.maximum(0, xx - 465)) / 74, 0, 1)
        light[glass] = (0.32 + 0.52 * cabin + 0.16 * (0.5 + 0.5 * np.cos(xx * 0.092)) ** 6)[glass]
        p["window"] = "#82c5c5"
        hall = (ids == lookup["wall"]) & (xx > 620)
        light[hall] *= (0.49 + 0.43 * np.exp(-(((xx - 800) / 88) ** 2)))[hall]
        light[ground] *= 0.73
    pick, energy = rng.random((2, h, w))
    palette_rgb = np.array([ImageColor.getrgb(p[k]) for k in keys])
    cov = np.where(sky, 0.004, np.where(hills, 0.27, np.where(water, 0.43, 0.63)))
    scalar = light * (0.18 + (pick < cov) * (0.32 + 1.07 * energy)) + 0.56 * rim * (0.36 + energy)
    field = palette_rgb[ids] * scalar[:, :, None] + [6, 11, 19]
    field[sky & (pick > 0.9987)] += np.array([135, 159, 185])
    moon = ids == lookup["sun"]
    radius = np.hypot(xx - 332, yy - 103) / 45
    field[moon] = (
        0.53 + 0.37 * np.exp(-(((radius - 0.94) / 0.085) ** 2)) + 0.07 * np.sin(xx * 0.11 + np.cos(yy * 0.12))
    )[moon, None] * [231, 220, 188]
    # The tram headlights throw a shallow pool of light along the curving rail.
    for cx, cy, sz in [(397, 368, 13), (337, 393, 4), (453, 389, 4), (801, 163, 6)]:
        glow = np.exp(-(((xx - cx) / sz) ** 2) - ((yy - cy) / sz) ** 2)
        field += glow[:, :, None] * [188, 155, 93]
    spill = (
        np.exp(-(((yy - 374 - (397 - xx) * 0.14) / (2 + np.maximum(0, 397 - xx) * 0.064)) ** 2))
        * np.exp(-np.abs(397 - xx) / 108)
        * (xx < 397)
    )
    field += spill[:, :, None] * [147, 109, 59]
    if style == "one-bit":
        # Sketch lit boundaries and rail reflections into the tonal master before screening.
        tone = light * 0.59 + 0.41 * rim
        tone[sky] = 0.035 + 0.22 * (pick[sky] > 0.9985)
        tone[hills] = (0.10 + 0.23 * rim)[hills]
        tone[water] = (0.075 + wave * (0.40 + 0.98 * moonpath))[water]
        tone[ground] = (0.16 + 0.065 * np.sin(yy * 0.32 + xx * 0.073) + 0.13 * streetlamp)[ground]
        for k, base in [
            ("body", 0.32),
            ("bodyshade", 0.19),
            ("window", 0.51),
            ("lamp", 0.95),
            ("cream", 0.72),
            ("dark", 0.12),
            ("frame", 0.10),
            ("signboard", 0.11),
            ("signink", 0.95),
            ("trim", 0.75),
        ]:
            region = ids == lookup[k]
            tone[region] = (base + 0.31 * rim)[region]
        tone[moon] = (0.70 + 0.26 * np.exp(-(((radius - 0.91) / 0.11) ** 2)))[moon]
        tone += 0.53 * spill
        im = one_bit.dither(Image.fromarray(np.uint8(255 * np.clip(tone, 0, 1))))
    else:
        im = Image.fromarray(np.uint8(np.clip(field, 0, 255)))
        smooth = np.asarray(im.filter(ImageFilter.GaussianBlur(0.85)), float)
        bloom = np.asarray(im.filter(ImageFilter.GaussianBlur(3.8)), float)
        im = Image.fromarray(np.uint8(np.clip(field * 0.75 + 0.26 * smooth + 0.30 * bloom, 0, 255)))
    return im


def drafting(t):
    font = study_font("WenKai")
    im = gradient(SKIES["drafting"])
    p = ImageDraw.Draw(im)
    paper = "#e8d9b7"
    lead = "#6c5d45"
    fine = "#a3906b"
    fills = {
        "window": "#b4ab91",
        "frame": "#766c55",
        "dark": "#776b55",
        "signboard": "#77694f",
        "lamp": "#eee1bd",
        "ground": "#dfceaa",
        "sea": "#e6d7b3",
        "bodyshade": "#bcaf8f",
        "trim": "#e7d5ae",
        "face": "#d1c3a1",
        "distant": "#e1d3b2",
        "mountain": "#dbccab",
        "underbody": "#7a7059",
        "roof": "#beb193",
        "shadow": "#c2b496",
        "glint": "#ede1c4",
        "undercar": "#94866d",
    }
    for m in station("drafting", t):
        if m.kind in ("sign", "route"):
            glyph_mark(im, m, "#f6e5c3", font)
            continue
        col = fills.get(m.role, paper)
        old = m.group in ("sky", "hills", "port")
        if m.role == "cloud":
            continue
        if m.kind == "line":
            draw_mark(p, m, "#b4a581" if old or m.role == "joint" else "#8a795c")
        else:
            draw_mark(p, m, col, "#b5a786" if old or m.group == "water" else lead)
        if m.role == "sea":
            wavelets(p, t - PREVIEW_PHASE, 270, ["#c7ba97", "#d2c4a2"], 400)
        if m.role in ("bodyshade", "shadow", "roof") and m.kind == "poly":
            mask = Image.new("L", SIZE)
            draw_mark(ImageDraw.Draw(mask), m, 255)
            h = Image.new("L", SIZE)
            pen = ImageDraw.Draw(h)
            for px in range(-H, W, 7):
                pen.line((px, 539, px + 540, 0), fill=110)
            im.paste("#8d8064", (0, 0), ImageChops.multiply(h, mask))

    def note(x, y, s):
        p.text((x, y), s, font=ImageFont.load_default(size=11), fill=lead)

    def dim(a, b):
        p.line((a, b), fill=fine)
        for x, y in [a, b]:
            p.line((x - 4, y + 4, x + 4, y - 4), fill=lead)

    # Wheel section and pantograph detail have their own datums, separate from the perspective.
    cx, cy = 111, 149
    for r in [43, 36, 32, 12, 8]:
        p.ellipse((cx - r, cy - r, cx + r, cy + r), outline=lead if r in [36, 12] else fine)
    for k in range(12):
        a = k * math.tau / 12
        p.line(
            (
                cx + 12 * math.cos(a),
                cy + 12 * math.sin(a),
                cx + 32 * math.cos(a + 0.19),
                cy + 32 * math.sin(a + 0.19),
            ),
            fill=fine,
        )
    for k in range(4):
        a = k * math.pi / 2
        p.line(
            (cx + 38 * math.cos(a), cy + 38 * math.sin(a), cx + 50 * math.cos(a), cy + 50 * math.sin(a)),
            fill=lead,
        )
    p.line((146, 137, 168, 117, 197, 117), fill=fine)
    note(171, 101, "Wheel section")
    p.line((460, 196, 438, 155, 397, 155), fill=fine)
    note(363, 137, "Contact wire")
    p.line((842, 145, 883, 117, 921, 117), fill=fine)
    note(861, 100, "Clock bay")
    p.line((477, 431, 489, 453), fill=fine)
    p.line((691, 351, 702, 375), fill=fine)
    dim((485, 449), (701, 373))
    note(560, 419, "Carriage elevation")
    dim((61, 493), (241, 493))
    note(68, 498, "PLATFORM SECTION    /    B")
    for i in range(9):
        p.line((62 + i * 22, 489, 62 + i * 22, 494), fill=lead)
    a = np.asarray(im, float)
    edge = np.minimum(np.minimum(xgrid, W - 1 - xgrid), np.minimum(ygrid, H - 1 - ygrid))
    weather = np.exp(-edge / 31) * (0.095 + 0.025 * np.cos(xgrid * 0.032 + ygrid * 0.057))
    im = grain(Image.fromarray(np.uint8(np.clip(a * (1 - weather[:, :, None]), 0, 255))), 2.7, 0.9)
    return im
