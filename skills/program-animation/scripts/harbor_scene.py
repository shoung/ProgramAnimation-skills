"""Elevation of a fictional seaside tram terminus, in a 960 × 540 picture plane."""

import math
import random
from dataclasses import dataclass, replace

from coast import Mark
from print_landscape import ribbon


@dataclass
class Element(Mark):
    group: str = ""


def arch(x, y, width, height, rise):
    """A semicircular window head with straight reveals down to its sill."""
    return (
        [(x, y + height)]
        + [
            (
                x + width / 2 + width / 2 * math.cos(a * math.pi / 16),
                y + rise - rise * math.sin(a * math.pi / 16),
            )
            for a in range(16, -1, -1)
        ]
        + [(x + width, y + height)]
    )


def oval(x, y, rx, ry, count=48):
    return [
        (x + rx * math.cos(i * math.tau / count), y + ry * math.sin(i * math.tau / count))
        for i in range(count)
    ]


PREVIEW_PHASE = 0.85


def station(style, t):
    marks = []
    group = "sky"

    def poly(role, *pts):
        marks.append(Element("poly", role, list(pts), group=group))

    def line(role, *pts, w=1):
        marks.append(Element("line", role, list(pts), w, group))

    def rect(role, x, y, w, h):
        poly(role, (x, y), (x + w, y), (x + w, y + h), (x, y + h))

    def disk(role, x, y, rx, ry):
        poly(role, *oval(x, y, rx, ry))

    disk("sun", 332, 103, 45, 45)
    if style in ("woodblock", "mineral"):
        for box in [(346, 91, 241, 24), (65, 178, 294, 19), (715, 75, 166, 22)]:
            poly("cloud", *ribbon(*box).xy)
    elif style not in ("ink-wash", "one-bit", "point-cloud"):
        for x, y, scale in [(442, 82, 0.87), (179, 163, 0.55), (721, 59, 0.67)]:
            pts = [
                (-69, 12),
                (-66, 5),
                (-55, 1),
                (-45, 2),
                (-39, -8),
                (-30, -12),
                (-19, -10),
                (-11, -20),
                (0, -25),
                (13, -23),
                (22, -18),
                (28, -10),
                (40, -13),
                (51, -7),
                (56, -1),
                (67, 0),
                (77, 5),
                (80, 10),
                (72, 13),
            ]
            poly("cloud", *((x + a * scale, y + b * scale) for a, b in pts))
    group = "hills"
    hills = [
        (-4, 222),
        (52, 206),
        (88, 217),
        (142, 187),
        (169, 180),
        (206, 196),
        (251, 209),
        (301, 214),
        (360, 197),
        (394, 184),
        (419, 191),
        (445, 178),
        (486, 165),
        (521, 184),
        (558, 183),
        (610, 207),
        (647, 199),
        (721, 216),
        (775, 205),
        (812, 210),
        (872, 189),
        (966, 208),
    ]
    poly("distant", *hills, (966, 282), (-4, 282))
    for x, y, s in [(-38, 215, 1.14), (140, 204, 0.83), (468, 193, 1.15), (600, 221, 0.85)]:
        ridge = [
            (-144, 67),
            (-113, 58),
            (-78, 37),
            (-60, 33),
            (-37, 19),
            (-27, 20),
            (-5, 3),
            (0, 0),
            (11, 4),
            (29, 11),
            (39, 23),
            (64, 26),
            (83, 39),
            (127, 55),
            (152, 67),
        ]
        poly("mountain", *((x + a * s, y + b * s) for a, b in ridge), (x + 152 * s, 279), (x - 144 * s, 279))
        poly(
            "face",
            (x, y),
            (x + 29 * s, y + 11 * s),
            (x + 64 * s, y + 26 * s),
            (x + 123 * s, 269),
            (x + 78 * s, 270),
            (x + 37 * s, y + 33 * s),
        )
    group = "port"
    # Container cranes on the opposite shore, their open trusses let the sky through.
    for x, y, s in [(29, 228, 0.84), (74, 221, 0.95), (264, 241, 0.60)]:

        def c(a, b, ox=x, oy=y, scale=s):
            return (ox + a * scale, oy + b * scale)

        for a in (-12, 8):
            line("ridge", c(a - 5, 47), c(a, 7), c(a + 4, 47), w=2)
        line("ridge", c(-19, 10), c(43, -11), c(18, -8), c(4, -2), c(-17, 5), c(-19, 10), w=2)
        line("ridge", c(-9, 3), c(0, -18), c(7, 0), c(39, -10))
        line("ridge", c(36, -8), c(36, 8))
    group = "water"
    rect("sea", -3, 269, 966, 274)
    group = "ferry"
    # The double-ended harbor ferry has a wheelhouse, two decks, and a mast.
    poly("hull", (72, 325), (85, 331), (199, 331), (224, 321), (215, 336), (195, 342), (93, 342), (79, 337))
    line("foam", (87, 340), (105, 342), (191, 342), (214, 337), w=2)
    poly("wall", (89, 314), (192, 313), (207, 323), (83, 325))
    rect("red", 100, 309, 86, 4)
    for x in range(101, 190, 12):
        rect("dark", x, 316, 7, 5)
    rect("wall", 123, 300, 42, 11)
    for x in range(128, 161, 9):
        rect("glass", x, 302, 5, 5)
    rect("roof", 118, 297, 52, 3)
    rect("red", 174, 298, 6, 13)
    line("dark", (142, 296), (142, 280), w=2)
    poly("red", (143, 280), (156, 282), (143, 286))
    group = "quay"
    poly("shade", (-3, 454), (966, 284), (966, 543), (-3, 543))
    poly("ground", (-3, 440), (966, 279), (966, 543), (-3, 543))
    line("lip", (-3, 441), (966, 279), w=5)
    rng = random.Random(471)
    for i in range(110):
        x, y = rng.randrange(978) - 12, rng.randrange(291, 550)
        if y > 447 - 0.166 * x:
            line("joint", (x, y), (x + 10 + rng.randrange(24), y - 2 - rng.randrange(4)))
    # The rails follow the same grade as the wheels, converging into the siding.
    for left, grade in [(532, 0.249), (566, 0.272)]:
        for off, role, weight in [(3, "shade", 5), (0, "metal", 3), (-2, "lip", 1)]:
            line(role, (-8, left + 2 + off), (969, left - grade * 969 + off), w=weight)
    for x in range(5, 960, 60):
        y = 438 - 0.166 * x
        if x < 300 or x > 923:
            rect("dark", x, y - 11, 5, 12)
            disk("rail", x + 2, y - 11, 5, 2)
    group = "hall"
    # Ferry terminal: copper mansard, gabled clock bay and a glazed train shed.
    poly("shadow", (625, 238), (690, 207), (697, 320), (628, 333))
    rect("wall", 690, 210, 231, 99)
    poly("shadow", (921, 211), (950, 222), (950, 302), (921, 309))
    poly("roof", (613, 239), (648, 210), (699, 193), (710, 203), (687, 231))
    poly("roof", (677, 215), (707, 169), (898, 168), (932, 213))
    poly("copper", (707, 169), (730, 156), (889, 156), (898, 168))
    for x in range(710, 904, 17):
        line("seam", (x, 173), (x - 12, 207))
    rect("eave", 672, 210, 264, 8)
    for x in [698, 735, 854, 891]:
        poly("trim", *arch(x - 4, 248, 27, 52, 13))
        poly("glass", *arch(x, 252, 19, 46, 10))
        line("frame", (x + 9, 254), (x + 9, 297), w=2)
        line("frame", (x, 267), (x + 17, 267), w=2)
        rect("step", x - 3, 298, 26, 3)
    poly("wall", (761, 212), (761, 168), (801, 130), (839, 169), (839, 213))
    poly("trim", (755, 168), (801, 122), (846, 168), (841, 171), (801, 135), (760, 172))
    poly("roof", (749, 165), (798, 116), (803, 115), (851, 163), (845, 168), (800, 128), (755, 170))
    line("copper", (798, 117), (801, 99), (804, 115), w=2)
    disk("roof", 801, 163, 18, 18)
    disk("lamp", 801, 163, 14, 14)
    for k in range(12):
        a = math.tau * k / 12
        line(
            "frame",
            (801 + 11 * math.sin(a), 163 - 11 * math.cos(a)),
            (801 + 13 * math.sin(a), 163 - 13 * math.cos(a)),
        )
    line("dark", (793, 159), (801, 163), (805, 154), w=2)
    for x in (763, 832):
        rect("trim", x, 182, 5, 123)
    rect("eave", 681, 225, 246, 4)
    rect("signboard", 747, 217, 109, 26)
    marks.append(Element("sign", "signink", [(752, 220), (851, 239)], group=group))
    poly("trim", *arch(782, 250, 35, 57, 18))
    poly("dark", *arch(786, 254, 27, 53, 14))
    line("seam", (799, 258), (799, 306), w=2)
    for i in range(3):
        rect("step", 773 - i * 4, 305 + i * 4, 54 + i * 8, 3)
    # Canopy, braces and platform bench.
    poly("copper", (578, 272), (669, 243), (736, 243), (649, 275))
    poly("eave", (578, 272), (649, 275), (736, 243), (735, 249), (650, 282), (579, 278))
    for x, y in [(591, 278), (647, 282), (714, 256)]:
        line("frame", (x, y), (x, y + 43), w=3)
        line("frame", (x, y + 10), (x + 9, y - 1), w=2)
    for x in (869, 898):
        line("frame", (x, 297), (x - 3, 309), w=2)
    rect("roof", 861, 293, 49, 4)
    rect("roof", 860, 287, 48, 3)
    group = "wire"
    line("wire", (270, 133), (450, 168), (592, 194), (717, 211), (944, 221), w=1)
    line("wire", (283, 144), (468, 173), (593, 194), (754, 210), (965, 214), w=1)
    # The near support is behind the car; its cantilever frames the sea.
    line("frame", (265, 131), (265, 395), w=4)
    line("wire", (265, 139), (317, 144), (265, 158), w=2)
    rect("trim", 261, 161, 8, 3)
    group = "tram"

    # Three-quarter streetcar. Near cab is broad. Far windows diminish along the body.
    def side(u, v):
        return (467 + u * 221, 255 - 40 * u + v * (162 - 36 * u))

    def panel(role, u0, u1, v0, v1):
        poly(role, side(u0, v0), side(u1, v0), side(u1, v1), side(u0, v1))

    poly("undercar", (325, 415), (469, 401), (694, 328), (697, 344), (477, 425), (348, 439))
    for x, y, r in [
        (489, 414, 12),
        (509, 408, 11),
        (647, 365, 9),
        (664, 359, 8),
        (347, 432, 10),
        (446, 428, 11),
    ]:
        disk("dark", x, y, r, r)
        disk("metal", x, y, 0.49 * r, 0.49 * r)
    panel("bodyshade", 0, 1, 0.02, 0.96)
    panel("cream", 0, 1, 0.06, 0.56)
    panel("stripe", 0, 1, 0.565, 0.595)
    panel("trim", 0, 1, 0.83, 0.848)
    for i in range(9):
        u = (i / 9) ** 0.85 + 0.016
        end = min(0.982, ((i + 1) / 9) ** 0.85 - 0.013)
        panel("frame", u, end, 0.117, 0.515)
        panel("window", u + 0.008, end - 0.007, 0.14, 0.481)
        if i % 3 != 1:
            panel("glint", u + 0.012, min(u + 0.026, end - 0.009), 0.16, 0.46)
        if i in (0, 8):
            panel("seam", u - 0.008, u, 0.1, 0.91)
            panel("seam", end, end + 0.006, 0.1, 0.91)
    panel("bumper", 0, 1, 0.937, 0.98)
    poly(
        "copper",
        (324, 271),
        (328, 249),
        (346, 238),
        (535, 206),
        (667, 201),
        (687, 211),
        (692, 219),
        (473, 275),
    )
    poly("roof", (333, 247), (354, 236), (543, 205), (660, 200), (677, 204), (481, 247))
    poly("trim", (373, 240), (391, 225), (542, 199), (610, 198), (618, 205), (474, 239))
    poly("roof", (387, 228), (397, 219), (549, 194), (604, 193), (613, 199), (541, 203))
    line("dark", (502, 210), (540, 179), (585, 195), (553, 209), w=3)
    line("frame", (511, 209), (542, 185), (572, 197), w=2)
    line("frame", (533, 178), (553, 181), w=3)
    cab = [
        (322, 273),
        (325, 260),
        (334, 251),
        (349, 247),
        (449, 245),
        (461, 247),
        (469, 255),
        (473, 269),
        (473, 396),
        (468, 412),
        (457, 420),
        (344, 427),
        (329, 421),
        (323, 408),
    ]
    poly("body", *cab)
    poly(
        "cream",
        (324, 273),
        (329, 258),
        (341, 253),
        (452, 250),
        (463, 255),
        (468, 269),
        (470, 338),
        (323, 344),
    )
    line("stripe", (324, 345), (391, 344), (470, 338), w=5)
    poly("frame", *arch(332, 275, 129, 61, 17))
    for i, (x, w) in enumerate([(337, 36), (378, 36), (419, 36)]):
        poly("window", *arch(x, 279, w, 51, 8))
        poly("glint", (x + 4, 289), (x + 9, 285), (x + 6, 324), (x + 3, 325))
        line("seam", (x, 315), (x + w - 1, 313))
    rect("signboard", 363, 256, 66, 15)
    marks.append(Element("route", "signink", [(366, 256), (426, 271)], group=group))
    # Side spears and brass headlight make the nose readable even with tiny brushstrokes.
    for j in (0, 7, 14):
        line("stripe", (329, 362 + j), (350, 368 + j), (379, 369 + j * 0.45), w=2)
        line("stripe", (462, 355 + j), (437, 366 + j), (414, 367 + j * 0.45), w=2)
    disk("dark", 397, 369, 15, 15)
    disk("trim", 397, 368, 12, 12)
    disk("lamp", 397, 368, 8, 8)
    poly(
        "bumper",
        (320, 407),
        (343, 414),
        (451, 410),
        (475, 399),
        (474, 409),
        (454, 421),
        (342, 428),
        (322, 422),
    )
    line("trim", (327, 411), (347, 416), (449, 413), (468, 405), w=2)
    for x, y in [(337, 393), (453, 389)]:
        disk("lamp", x, y, 4, 4)
    # A waiting passenger faces the approaching cab, holding a small valise.
    group = "traveler"
    poly("shade", (800, 376), (838, 368), (848, 370), (821, 380), (797, 381))
    poly("dark", (805, 345), (814, 346), (812, 373), (808, 377), (803, 375))
    poly("frame", (815, 346), (823, 344), (825, 369), (821, 373), (816, 372))
    poly("dark", (803, 372), (812, 372), (811, 378), (798, 379), (797, 376))
    poly("dark", (817, 368), (825, 368), (827, 373), (815, 375))
    poly(
        "trim",
        (804, 319),
        (810, 315),
        (818, 315),
        (824, 322),
        (825, 337),
        (829, 346),
        (815, 352),
        (800, 350),
        (803, 332),
    )
    poly("step", (818, 318), (823, 322), (825, 339), (828, 346), (820, 349))
    poly("wall", (807, 304), (816, 302), (819, 308), (817, 315), (809, 316), (804, 311))
    disk("roof", 811, 303, 8, 7)
    poly("roof", (799, 307), (808, 301), (821, 300), (826, 303), (819, 306), (803, 309))
    poly(
        "red", (807, 313), (817, 312), (820, 316), (827, 316), (836, 311), (831, 318), (822, 321), (811, 317)
    )
    line("frame", (818, 322), (822, 332), (824, 340), w=3)
    line("rail", (824, 341), (831, 341), (832, 349), w=2)
    poly("roof", (818, 349), (834, 346), (837, 361), (822, 365))
    line("trim", (822, 350), (825, 362), w=2)
    line("trim", (831, 348), (834, 359), w=2)
    group = "birds"
    for x, y, s in [(491, 95, 0.85), (518, 88, 0.55), (556, 103, 0.44), (74, 192, 0.48), (103, 185, 0.6)]:
        line(
            "bird",
            (x - 12 * s, y - 3 * s),
            (x - 6 * s, y - 4 * s),
            (x, y),
            (x + 5 * s, y - 5 * s),
            (x + 12 * s, y - 8 * s),
            w=2,
        )
    phase = t - PREVIEW_PHASE
    # Move the ferry and birds on separate cycles. The registered ink and brush
    # passes stay fixed in image space, so surface grain does not flicker.
    drift = {
        "ferry": (17 * math.sin(phase), 2 * math.sin(phase * 2)),
        "birds": (10 * math.sin(phase), 3 * math.sin(phase * 2)),
    }
    return [
        replace(m, xy=[(x + drift[m.group][0], y + drift[m.group][1]) for x, y in m.xy])
        if m.group in drift
        else m
        for m in marks
    ]
