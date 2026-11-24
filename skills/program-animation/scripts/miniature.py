"""Small orthographic mesh renderer for the isometric example (no 3-D engine)."""

import math
import random

from coast import SIZE, gradient, grain
from PIL import Image, ImageColor, ImageDraw, ImageFilter

TAU = math.tau


def shade(color, light):
    return tuple(round(min(255, max(0, c * light))) for c in ImageColor.getrgb(color))


class Set:
    def __init__(self, t):
        self.faces = []
        self.rng = random.Random(107)
        self.az = (0.65) + 0.055 * math.sin(t)
        self.el = 0.55
        self.scale = 61
        self.base = (478, 335)

    def camera(self, p):
        x, y, z = p
        a, e = self.az, self.el
        u = x * math.cos(a) - z * math.sin(a)
        towards = x * math.sin(a) + z * math.cos(a)
        v = y * math.cos(e) - towards * math.sin(e)
        depth = y * math.sin(e) + towards * math.cos(e)
        return (self.base[0] + u * self.scale, self.base[1] - v * self.scale), depth

    def face(self, pts, color, bias=0):
        proj = [self.camera(p) for p in pts]
        self.faces.append((sum(z for _, z in proj) / len(proj) + bias, [xy for xy, _ in proj], color))

    def lathe(self, x, y, z, rings, col, n=18, jitter=0):
        seq = []
        # All rings share radial imperfections, like finger-shaped clay.
        wobble = [1 + self.rng.uniform(-jitter, jitter) for _ in range(n)]
        for h, r in rings:
            seq.append(
                [
                    (
                        x + r * wobble[i] * math.cos(i * TAU / n),
                        y + h,
                        z + r * wobble[i] * math.sin(i * TAU / n),
                    )
                    for i in range(n)
                ]
            )
        for j in range(len(seq) - 1):
            for i in range(n):
                k = (i + 1) % n
                angle = (i + 0.5) * TAU / n
                light = 0.89 + 0.15 * math.cos(angle - 2.2) + 0.025 * j
                self.face([seq[j][i], seq[j][k], seq[j + 1][k], seq[j + 1][i]], shade(col, light))
        self.face(seq[-1], shade(col, 1.09))

    def box(self, x, y, z, w, h, d, col):
        for dx, dz, f in [(1, 0, 0.88), (-1, 0, 0.93), (0, 1, 1), (0, -1, 0.83)]:
            cx, cz = x + dx * w / 2, z + dz * d / 2
            ux, uz = dz * w / 2, dx * d / 2
            self.face(
                [
                    (cx - ux, y, cz - uz),
                    (cx + ux, y, cz + uz),
                    (cx + ux, y + h, cz + uz),
                    (cx - ux, y + h, cz - uz),
                ],
                shade(col, f),
            )
        self.face(
            [(x + i * w / 2, y + h, z + j * d / 2) for i, j in [(-1, -1), (-1, 1), (1, 1), (1, -1)]],
            shade(col, 1.05),
        )

    def blob(self, x, y, z, r, col, flat=1):
        self.lathe(
            x,
            y,
            z,
            [
                (r * h * flat, r * w)
                for h, w in [(-0.8, 0.42), (-0.45, 0.85), (0, 1), (0.48, 0.85), (0.83, 0.52), (0.98, 0.17)]
            ],
            col,
            14,
            0.02,
        )


def render_set(t):
    s = Set(t)
    rng = random.Random(406)
    im = gradient([(0, "#fae5cc"), (540, "#ecc2aa")])
    corners = [(-4.7, -0.35, -3.05), (-4.7, -0.35, 3.05), (4.7, -0.35, 3.05), (4.7, -0.35, -3.05)]
    shadow = Image.new("L", SIZE)
    ImageDraw.Draw(shadow).polygon(
        [(s.camera(p)[0][0] + 11, s.camera(p)[0][1] + 17) for p in corners], fill=110
    )
    im.paste("#ac8977", (0, 0), shadow.filter(ImageFilter.GaussianBlur(10)))
    s.box(0, -0.34, 0, 9.4, 0.32, 6.1, "#66b3ad")
    # Water surface is a backplate, so small objects always sort in front.
    for _, xy, c in sorted(s.faces, key=lambda item: item[0]):
        ImageDraw.Draw(im).polygon(xy, fill=c)
    s.faces.clear()
    d = ImageDraw.Draw(im)
    for _ in range(220):
        x, z = rng.uniform(-4.55, 4.55), rng.uniform(-2.96, 2.96)
        x += 0.04 * math.sin(t + z * 4)
        (u, v), _ = s.camera((x, 0.002, z))
        length = rng.uniform(2, 10)
        d.line(
            [(u - length, v), (u, v - 1), (u + length, v)],
            fill=rng.choice(["#a2d6ce", "#7bbbc2", "#92c9c2"]),
            width=1,
        )
    # Ring-shaped cliff mesh. Each face is split into two geological planes.
    radii = [1 + rng.uniform(-0.16, 0.17) for _ in range(25)]
    rings = []
    for h, rad in [(-0.06, 1.12), (0.13, 1.08), (0.66, 0.91), (0.95, 0.80)]:
        rings.append(
            [
                (
                    3.16 * radii[i] * rad * math.cos(i * TAU / 25),
                    h,
                    1.70 * radii[i] * rad * math.sin(i * TAU / 25),
                )
                for i in range(25)
            ]
        )
    for j in range(3):
        for i in range(25):
            k = (i + 1) % 25
            a, b, c, e = rings[j][i], rings[j][k], rings[j + 1][k], rings[j + 1][i]
            col = "#d7896b" if j else "#f4d6ac"
            light = 0.8 + 0.17 * math.sin((i + 0.5) * TAU / 25 + 1)
            s.face([a, b, c], shade(col, light))
            s.face([a, c, e], shade(col, light + 0.07))
    # Split the turf into sectors to avoid a single long polygon crossing every prop's depth.
    for i in range(25):
        s.face([(0, 0.95, 0), rings[-1][i], rings[-1][(i + 1) % 25]], "#a5bf79", bias=-0.12)
    x, z = 0.82, -0.32
    for y, r1, r2, h, col in [
        (0, 0.42, 0.39, 0.22, "#ece1bc"),
        (0.22, 0.35, 0.33, 0.47, "#faf2d7"),
        (0.69, 0.33, 0.31, 0.28, "#ca604c"),
        (0.97, 0.31, 0.29, 0.42, "#f8ebce"),
        (1.39, 0.29, 0.27, 0.28, "#c65a46"),
        (1.67, 0.27, 0.25, 0.43, "#f6e9ca"),
        (2.10, 0.31, 0.35, 0.11, "#574f50"),
        (2.21, 0.25, 0.25, 0.29, "#a2c5c3"),
        (2.50, 0.36, 0.27, 0.085, "#aa4f41"),
        (2.585, 0.27, 0.035, 0.18, "#ce604b"),
    ]:
        s.lathe(x, 0.95 + y, z, [(0, r1), (h, r2)], col)
    s.lathe(x, 3.71, z, [(0, 0.035), (0.15, 0.017)], "#544a49", 8)
    for i in range(10):
        a = i * TAU / 10
        s.lathe(
            x + 0.317 * math.cos(a),
            3.14,
            z + 0.317 * math.sin(a),
            [(0, 0.009), (0.13, 0.009)],
            "#514e4f",
            6,
        )
    for i in range(24):
        a = i * TAU / 24
        b = (i + 1) * TAU / 24
        ring = [
            (x + 0.324 * math.cos(theta), h, z + 0.324 * math.sin(theta))
            for theta, h in [(a, 3.255), (a, 3.273), (b, 3.273), (b, 3.255)]
        ]
        s.face(ring, "#5b5551")
    for h, r in [(1.1, 0.348), (1.96, 0.292), (2.69, 0.259)]:
        s.box(x + 0.08, h, z + r, 0.096, 0.14, 0.034, "#504f50")
    # Gabled keeper's cottage with a chimney, painted door and window frames.
    x, z = -0.79, 0.02
    s.box(x, 0.95, z, 1.05, 0.44, 0.59, "#f3d7a5")
    for side in [-1, 1]:
        s.face(
            [
                (x - 0.62, 1.39, z + side * 0.37),
                (x + 0.62, 1.39, z + side * 0.37),
                (x + 0.62, 1.70, z),
                (x - 0.62, 1.70, z),
            ],
            shade("#c96649", 1 if side == 1 else 0.84),
        )
    for side in [-1, 1]:
        s.face(
            [
                (x + side * 0.526, 1.39, z - 0.29),
                (x + side * 0.526, 1.39, z + 0.29),
                (x + side * 0.526, 1.67, z),
            ],
            "#efd8af",
        )
    s.box(x - 0.28, 1.58, z - 0.04, 0.14, 0.29, 0.12, "#ae725c")
    for dx in [-0.34, 0, 0.32]:
        s.box(x + dx, 0.98 if not dx else 1.12, z + 0.304, 0.13, 0.29 if not dx else 0.12, 0.028, "#51767a")
    for x, z, sz in [
        (-2.25, 0.06, 0.73),
        (-1.75, -0.49, 0.87),
        (-1.92, 0.58, 0.55),
        (1.67, -0.64, 0.68),
        (1.82, 0.32, 0.5),
        (1.46, 0.72, 0.39),
    ]:
        s.lathe(x, 0.95, z, [(0, 0.055 * sz), (0.22 * sz, 0.055 * sz)], "#8a7050", 8)
        for j in range(3):
            r = (0.29 - 0.052 * j) * sz
            s.lathe(
                x,
                1.06 + j * 0.19 * sz,
                z,
                [(0, r), (0.055 * sz, r * 1.04), (0.44 * sz, 0.03)],
                ["#52896f", "#5e9a72", "#70ab75"][j],
                7,
                0.045,
            )
    for i in range(8):
        s.box(-1.45 + i * 0.105, 0.08 + i * 0.103, 1.63 - i * 0.095, 0.35, 0.10, 0.20, "#c8a77b")
    for x, z, sz in [
        (-3.18, 1.71, 0.43),
        (2.87, 0.95, 0.37),
        (-2.71, -1.64, 0.25),
        (3.24, 0.85, 0.26),
        (-3.32, 1.68, 0.22),
    ]:
        s.blob(x, 0.07, z, sz, "#c9997e", 0.83)
    x, z = -2.85 + 0.15 * math.sin(t), 2.33
    s.lathe(x, 0.06, z, [(0, 0.11), (0.12, 0.21)], "#a7634d", 10)
    s.face([(x, 0.16, z), (x, 0.77, z), (x - 0.30, 0.18, z)], "#fff1cc")
    s.lathe(x, 0.13, z, [(0, 0.014), (0.68, 0.014)], "#685944", 6)
    # Foam at the cliff's shoreline follows the irregular mesh perimeter.
    for i in range(115):
        a = rng.uniform(0, TAU)
        u = a / TAU * 25
        r = radii[int(u)] * (1 - u % 1) + radii[(int(u) + 1) % 25] * (u % 1)
        f = r * 1.13 + rng.uniform(0.00, 0.08) + 0.02 * math.sin(t + a * 3)
        x, z = 3.16 * f * math.cos(a), 1.7 * f * math.sin(a)
        s.blob(x, 0.014, z, rng.uniform(0.035, 0.079), "#ede8cc", 0.35)
    # Puffy floating clouds are pinched from small overlapping ellipsoids.
    for cx, cy, cz, k in [(-3.6, 2.7, -1.4, 0.85), (2.14, 3.8, -2.86, 0.91)]:
        for dx, dy, r in [(-0.35, 0, 0.31), (-0.06, 0.12, 0.40), (0.22, 0.11, 0.33), (0.47, -0.01, 0.25)]:
            s.blob(cx + (dx + 0.17 * math.sin(t)) * k, cy + dy * k, cz, r * k, "#f5e8d2", 0.68)
    for _, xy, c in sorted(s.faces, key=lambda item: item[0]):
        d.polygon(xy, fill=c)
    return grain(im, 1.1)
