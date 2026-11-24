"""Colored surface particles, a volumetric beacon and broken reflections on a midnight sea."""

from functools import lru_cache

import numpy as np
from coast import SIZE, H, W, draw_mark
from headland import landscape
from PIL import Image, ImageDraw, ImageFilter

# Emitted sRGB color and projected surface coverage are independent: dark red paint
# carries just as many samples as a white band, even though it emits less light.
MATERIALS = {
    "crest": ((59, 82, 107), 0.20),
    "lip": ((251, 190, 111), 0.82),
    "seam": ((113, 74, 63), 0.44),
    "sky": ((12, 19, 30), 0.004),
    "sun": ((243, 227, 192), 0.90),
    "mountain": ((43, 69, 101), 0.20),
    "face": ((37, 53, 85), 0.17),
    "ridge": ((63, 89, 124), 0.32),
    "sea": ((43, 148, 175), 0.48),
    "stone": ((175, 100, 71), 0.60),
    "shade": ((108, 58, 52), 0.49),
    "land": ((140, 150, 97), 0.63),
    "pine": ((48, 136, 99), 0.61),
    "leaf": ((85, 184, 136), 0.70),
    "trunk": ((131, 88, 62), 0.48),
    "rail": ((187, 130, 83), 0.55),
    "step": ((225, 173, 108), 0.74),
    "foam": ((105, 194, 201), 0.72),
    "wall": ((239, 218, 183), 0.82),
    "shadow": ((168, 151, 146), 0.59),
    "red": ((243, 76, 50), 0.83),
    "roof": ((215, 102, 55), 0.70),
    "glass": ((149, 203, 191), 0.66),
    "lamp": ((255, 239, 191), 0.97),
    "dark": ((73, 76, 88), 0.53),
    "hull": ((205, 76, 50), 0.68),
    "sail": ((204, 191, 159), 0.60),
    "bird": ((144, 154, 154), 0.36),
}
ROLE = {name: i for i, name in enumerate(MATERIALS)}


@lru_cache(maxsize=1)
def samples():
    rng = np.random.default_rng(251)
    return tuple(rng.random((H, W), dtype=np.float32) for _ in range(3))


def frame(t):
    surface = Image.new("L", SIZE, ROLE["sky"])
    pen = ImageDraw.Draw(surface)
    for mark in landscape(t):
        if mark.role != "cloud":
            draw_mark(pen, mark, ROLE[mark.role])
    ids = np.asarray(surface)
    y, x = np.ogrid[:H, :W]
    pick, energy, dust = samples()
    colors = np.array([rgb for rgb, _ in MATERIALS.values()], dtype=np.float32)
    coverage = np.array([density for _, density in MATERIALS.values()], dtype=np.float32)[ids]
    intensity = np.full(SIZE[::-1], 0.80, dtype=np.float32)
    sky = ids == ROLE["sky"]
    sea = ids == ROLE["sea"]
    hills = np.isin(ids, [ROLE[key] for key in ("mountain", "face", "ridge", "crest")])
    # Mountain scan lines and strata on the cliffs contour the surfaces in depth.
    intensity[hills] = np.broadcast_to(
        0.17 + 0.58 * (0.5 + 0.5 * np.cos(y * 0.83 + x * 0.018)) ** 5, (H, W)
    )[hills]
    rock = np.isin(ids, [ROLE["stone"], ROLE["shade"]])
    strata = 0.45 + 0.16 * np.cos(x * 0.033 + y * 0.056) + 0.11 * np.sin(x * 0.1 - y * 0.078)
    intensity[rock] = strata[rock]
    tower = (x > 591) & (x < 657) & (y < 316) & (~sky) & (~hills)
    cylinder = np.clip((x - 626) / 25, -1, 1)
    lambert = 0.34 + 0.65 * np.sqrt(1 - cylinder**2) - 0.26 * cylinder
    intensity[tower] *= np.broadcast_to(lambert, (H, W))[tower]

    # Cyan water crests and two narrow, interrupted reflections; wavelength increases toward camera.
    depth = np.maximum(0, (y - 376) / 164)
    waves = 0.5 + 0.5 * np.sin(
        71 * np.log1p(depth * 2.5)
        + 1.7 * np.sin(x * 0.018 + y * 0.063)
        + 1.4 * np.cos(x * 0.015 - y * 0.033 - t)
        + t
    )
    swells = 0.5 + 0.5 * np.cos(y * 0.113 + 1.1 * np.sin(x * 0.014 - t))
    moon_path = np.exp(-(((x - 329 - 8 * np.sin(y * 0.1 + t)) / (15 + 43 * depth)) ** 2))
    lamp_path = np.exp(-(((x - 626) / (10 + 23 * depth)) ** 2))
    glints = 0.53 + 0.47 * np.sin(x * 0.034 + y * 0.081 + np.cos(x * 0.012 + t))
    waterlight = (
        waves**4 * (0.14 + 0.37 * swells + 1.12 * moon_path + 0.30 * lamp_path) * (0.33 + 0.67 * glints)
    )
    waterlight *= 1 - 0.52 * depth
    intensity[sea] = (0.10 + 0.75 * np.exp(-15 * depth) + 1.03 * waterlight)[sea]

    # Per-material boundaries light the actual tower bands and tree crowns in their own hue.
    above = np.vstack([ids[:1], ids[:-1]])
    left = np.column_stack([ids[:, :1], ids[:, :-1]])
    rim = ((ids != above) | (ids != left)) & ~sky & ~hills
    coverage = np.minimum(0.99, coverage + 0.29 * rim)
    hit = pick < coverage
    light = intensity * (0.34 + 0.94 * energy) * hit
    light += 0.52 * rim * (0.42 + energy)
    # Low energy from adjacent points gives the densely sampled surfaces visible mass at thumbnail size.
    light += np.where(sky, 0, 0.28) * intensity
    field = colors[ids] * light[:, :, None]
    field += np.array([5, 10, 18])
    field += (
        sea[:, :, None] * (0.16 + 0.54 * np.exp(-depth * 4) + 0.65 * waterlight)[:, :, None] * [9, 45, 53]
    )
    field += sea[:, :, None] * (waterlight * (0.10 + 0.9 * moon_path))[:, :, None] * [84, 103, 94]

    # The surface of the moon has mottled dust and a luminous near rim.
    moon = ids == ROLE["sun"]
    radius = np.sqrt(((x - 329) / 51) ** 2 + ((y - 197) / 51) ** 2)
    lunar = np.exp(-(((radius - 0.97) / 0.066) ** 2))
    marbling = 0.06 * np.sin(x * 0.095 + 1.5 * np.sin(y * 0.071)) + 0.05 * np.cos(y * 0.18 - x * 0.042)
    field[moon] = field[moon] * 0.22 + (0.47 + 0.37 * lunar + marbling)[moon, None] * [211, 204, 183]
    field += sky[:, :, None] * np.exp(-(((radius - 1) / 0.095) ** 2))[:, :, None] * [58, 56, 45]
    star = (dust > 0.9989) & sky
    field += star[:, :, None] * energy[:, :, None] * [187, 206, 223]

    # Gold dust occupies two opposing cones; the flare, falloff and water are separate light sources.
    dx = x - 626
    axis = 94 + dx * 0.024 * np.sin(t)
    width = 2.2 + np.abs(dx) * (0.046 + 0.014 * np.cos(t))
    cone = np.exp(-(((y - axis) / width) ** 2)) * np.exp(-np.abs(dx) / 920)
    core = np.exp(-(((y - axis) / (1.8 + np.abs(dx) * 0.012)) ** 2)) * np.exp(-np.abs(dx) / 370)
    airborne = cone * (0.61 + 0.56 * energy) * (0.68 + 0.65 * (dust < 0.46))
    field += airborne[:, :, None] * [183, 159, 113] + core[:, :, None] * [109, 98, 77]
    field += np.exp(-((dx / 13) ** 2 + ((y - 94) / 14) ** 2))[:, :, None] * [231, 212, 155]
    field += np.exp(-((dx / 77) ** 2 + ((y - 94) / 75) ** 2))[:, :, None] * [21, 18, 11]
    emitted = Image.fromarray(np.uint8(np.clip(field, 0, 255)))
    bloom = np.asarray(emitted.filter(ImageFilter.GaussianBlur(4)), dtype=np.float32)
    # Subpixel splats overlap at output resolution, especially across the water.
    # Some light remains at each point core so the night keeps its particulate texture.
    scatter = np.asarray(emitted.filter(ImageFilter.GaussianBlur(1.05)), dtype=np.float32)
    return Image.fromarray(np.uint8(np.clip(field * 0.67 + 0.39 * scatter + 0.32 * bloom, 0, 255)))
