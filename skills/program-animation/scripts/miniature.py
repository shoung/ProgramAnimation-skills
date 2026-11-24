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
        self.az = -0.76 + 0.045 * math.sin(t)
        self.el = 0.66
        self.scale = 63
        self.base = (547, 290)

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
    s.box(0, -0.57, 0, 9.4, 0.22, 6.1, "#c6a68b")
    s.box(0, -0.35, 0, 9.4, 0.34, 6.1, "#62b7b1")
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

    def terrace(cx, cz, rx, rz, height, grass, seed):
        rand = random.Random(seed)
        n = 11
        ring = [
            (
                math.cos(i * TAU / n) * rx * rand.uniform(0.89, 1.08),
                math.sin(i * TAU / n) * rz * rand.uniform(0.9, 1.09),
            )
            for i in range(n)
        ]

        def level(h, scale):
            return [(cx + dx * scale, h, cz + dz * scale) for dx, dz in ring]

        sand, foot, top = level(0.016, 1.14), level(0.095, 1.045), level(height, 0.91)
        for i in range(n):
            k = (i + 1) % n
            light = 0.86 + 0.17 * math.cos(i * TAU / n - 1.9)
            s.face([sand[i], sand[k], foot[k], foot[i]], shade("#f6d6b1", light + 0.05))
            s.face([foot[i], foot[k], top[k], top[i]], shade("#d78a70", light))
            s.face([(cx, height, cz), top[i], top[k]], grass, bias=-0.1)

    terrace(0.54, -0.52, 1.94, 1.37, 0.95, "#a5c8a1", 51)
    terrace(-0.93, 0.96, 1.08, 0.75, 0.46, "#a0c398", 52)
    terrace(-2.72, 0.59, 0.40, 0.36, 0.78, "#9dbd98", 53)
    terrace(-2.96, 1.62, 0.26, 0.22, 0.37, "#e2a18b", 54)
    terrace(2.53, 0.06, 0.47, 0.43, 0.27, "#dea38e", 56)
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
        (-1.25, 0.92, 0.73),
        (-0.81, 1.22, 0.87),
        (-2.72, 0.59, 0.55),
        (1.67, -0.64, 0.68),
        (1.82, 0.32, 0.5),
        (1.46, 0.72, 0.39),
    ]:
        soil = 0.78 if x < -2 else 0.46 if x < 0 else 0.95
        s.lathe(x, soil, z, [(0, 0.055 * sz), (0.22 * sz, 0.055 * sz)], "#8a7050", 8)
        for j in range(3):
            r = (0.29 - 0.052 * j) * sz
            s.lathe(
                x,
                soil + 0.11 + j * 0.19 * sz,
                z,
                [(0, r), (0.055 * sz, r * 1.04), (0.44 * sz, 0.03)],
                ["#52896f", "#5e9a72", "#70ab75"][j],
                7,
                0.045,
            )
    for j in range(12):
        s.box(-1.04, 0.06 + j * 0.033, 2.39 - j * 0.083, 0.26, 0.06, 0.08, "#cca580")
    for j in [0, 4, 9]:
        for x in [-1.16, -0.92]:
            s.box(x, 0.015, 2.39 - j * 0.083, 0.045, 0.14 + j * 0.033, 0.05, "#a57a5c")
    x, z = -3.95 + 0.15 * math.sin(t), 0.83
    s.lathe(x, 0.06, z, [(0, 0.11), (0.12, 0.21)], "#a7634d", 10)
    s.face([(x, 0.16, z), (x, 0.77, z), (x - 0.30, 0.18, z)], "#fff1cc")
    s.lathe(x, 0.13, z, [(0, 0.014), (0.68, 0.014)], "#685944", 6)
    # Puffy floating clouds are pinched from small overlapping ellipsoids.
    for cx, cy, cz, k in [(-3.6, 2.7, -1.4, 0.85), (2.14, 2.68, -2.86, 0.65)]:
        for dx, dy, r in [(-0.35, 0, 0.31), (-0.06, 0.12, 0.40), (0.22, 0.11, 0.33), (0.47, -0.01, 0.25)]:
            s.blob(cx + (dx + 0.17 * math.sin(t)) * k, cy + dy * k, cz, r * k, "#f5e8d2", 0.68)
    for _, xy, c in sorted(s.faces, key=lambda item: item[0]):
        d.polygon(xy, fill=c)
    return grain(im, 1.1)
