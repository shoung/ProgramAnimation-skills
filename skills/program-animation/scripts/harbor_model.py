"""Two orthographic sets. A depth-tested mesh carries relief, glazing and the station sign."""

import math
import random

import numpy as np
from coast import H, W, gradient, grain
from harbor_plates import fitted_text
from harbor_scene import PREVIEW_PHASE
from lettering import STUDY_TITLE, study_font
from miniature import OrthographicCamera
from PIL import Image, ImageColor, ImageDraw, ImageFilter
from styles.clay import lump


class Mesh:
    def __init__(self, style):
        self.clay = style == "clay"
        self.camera = (
            OrthographicCamera(-0.52, 0.26, 82, (504, 347))
            if self.clay
            else OrthographicCamera(-0.73, 0.56, 69, (500, 321))
        )
        self.eye = np.array(
            [
                math.sin(self.camera.az) * math.cos(self.camera.el),
                math.sin(self.camera.el),
                math.cos(self.camera.az) * math.cos(self.camera.el),
            ]
        )
        self.sun = np.array([-0.43, 0.80, 0.42])
        self.depth = np.full((H, W), -1e5)
        self.im = gradient(
            [(0, "#edbfae" if self.clay else "#fae7d2"), (540, "#f4d7ad" if self.clay else "#efd2be")]
        )
        for cx, cy, s in [(350, 110, 0.85), (625, 62, 0.64), (861, 110, 0.53)]:
            for dx, dy, rx, ry in [(-35, 2, 30, 14), (-12, -8, 31, 23), (16, -6, 27, 20), (37, 4, 23, 12)]:
                lump(self.im, cx + dx * s, cy + dy * s, rx * s, ry * s, "#fff1da", salt=dx)
        if self.clay:
            # The clay sea runs behind the whole set to a soft horizon.
            d = ImageDraw.Draw(self.im)
            d.rectangle((0, 258, W, H), fill="#69afb6")
            rng = random.Random(83)
            for i in range(1020):
                x = rng.randrange(-12, 960)
                y = rng.randrange(259, 540)
                size = 2 + (y - 258) * 0.045
                d.arc(
                    (x - size, y, x + size * 2, y + 2 + size * 0.24),
                    10,
                    170,
                    fill=rng.choice(["#83c3c3", "#65a7b1", "#a3cfc6"]),
                    width=1 + (y > 420),
                )
        else:
            shadow = Image.new("L", (W, H))
            d = ImageDraw.Draw(shadow)
            d.polygon(
                [
                    (x + 10, y + 16)
                    for x, y in [
                        self.camera.camera((a, -0.4, b))[0]
                        for a, b in [(-4.9, -2.6), (4.9, -2.6), (4.9, 2.6), (-4.9, 2.6)]
                    ]
                ],
                fill=108,
            )
            self.im.paste("#a98574", (0, 0), shadow.filter(ImageFilter.GaussianBlur(9)))
        self.pixels = np.array(self.im)

    def face(self, pts, color, normal=None):
        pts = np.asarray(pts, float)
        n = np.cross(pts[1] - pts[0], pts[2] - pts[0]) if normal is None else np.asarray(normal, float)
        # Interpolated vertex lighting keeps hand-shaped clay smooth across mesh edges.
        n = n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-8)
        if n.ndim == 1 and n @ self.eye < 0:
            n = -n
        diffuse = np.maximum(0, n @ self.sun)
        light = 0.61 + 0.43 * diffuse if self.clay else 0.74 + 0.29 * diffuse
        if self.clay:
            half = (self.sun + self.eye) / np.linalg.norm(self.sun + self.eye)
            light += 0.065 * np.maximum(0, n @ half) ** 9
        rgb = np.asarray(light)[..., None] * np.array(ImageColor.getrgb(color))
        proj = []
        for p in pts:
            (x, y), z = self.camera.camera(p)
            proj.append((x, y, z))
        for i in range(1, len(pts) - 1):
            self.triangle([proj[0], proj[i], proj[i + 1]], rgb if rgb.ndim == 1 else rgb[[0, i, i + 1]])

    def triangle(self, pts, color):
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = pts
        l = max(0, math.floor(min(x0, x1, x2)))
        r = min(W, math.ceil(max(x0, x1, x2)) + 1)
        t = max(0, math.floor(min(y0, y1, y2)))
        b = min(H, math.ceil(max(y0, y1, y2)) + 1)
        det = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if l >= r or t >= b or abs(det) < 0.00001:
            return
        yy, xx = np.ogrid[t:b, l:r]
        u = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / det
        v = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / det
        w = 1 - u - v
        z = z0 * u + z1 * v + z2 * w
        view = self.depth[t:b, l:r]
        sel = (u >= -1e-6) & (v >= -1e-6) & (w >= -1e-6) & (z > view - 0.00001)
        if color.ndim == 2:
            color = u[sel, None] * color[0] + v[sel, None] * color[1] + w[sel, None] * color[2]
        self.pixels[t:b, l:r][sel] = np.uint8(np.clip(color, 0, 255))
        view[sel] = z[sel]

    def box(self, x, y, z, w, h, d, color):
        p = [
            (x + a * w / 2, y + b * h, z + c * d / 2)
            for b in [0, 1]
            for a, c in [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        ]
        for face in [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)]:
            self.face([p[i] for i in face], color)

    def rod(self, a, b, r, color, n=10):
        a, b = np.array(a), np.array(b)
        axis = b - a
        axis = axis / np.linalg.norm(axis)
        ref = np.array([0.0, 1.0, 0.0]) if abs(axis[1]) < 0.90 else np.array([1.0, 0.0, 0.0])
        u = np.cross(axis, ref)
        u /= np.linalg.norm(u)
        v = np.cross(axis, u)
        ring = [r * (u * math.cos(i * math.tau / n) + v * math.sin(i * math.tau / n)) for i in range(n)]
        self.face([a + k for k in ring], color)
        self.face([b + k for k in ring], color)
        for i, j in zip(range(n), list(range(1, n)) + [0]):
            self.face([a + ring[i], b + ring[i], b + ring[j], a + ring[j]], color)

    def rounded(self, x, y, z, w, h, d, r, col):
        """Rounded rectangle in plan with turned-under edges, like a molded tram or plinth."""
        n = 5 if self.clay else 3

        def ring(hh, inset):
            pts = []
            for a, c, start in [(1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)]:
                for j in range(n + 1):
                    angle = math.radians(start + 90 * j / n)
                    pts.append(
                        (
                            x + a * (w / 2 - r) + (r - inset) * math.cos(angle),
                            y + hh,
                            z + c * (d / 2 - r) + (r - inset) * math.sin(angle),
                        )
                    )
            return pts

        bevel = min(r * 0.65, h * 0.22)
        levels = [ring(0, bevel), ring(bevel, 0), ring(h - bevel, 0), ring(h, bevel)]
        for index, low in enumerate(levels[:-1]):
            hi = levels[index + 1]
            for i in range(len(low)):
                j = (i + 1) % len(low)
                self.face([low[i], low[j], hi[j], hi[i]], col)
        self.face(levels[-1], col, normal=(0, 1, 0))

    def blob(self, x, y, z, rx, ry, rz, col, seed=0):
        """Pinched lumps with an irregular silhouette and gently varying normals."""
        rows = []
        for j in range(11):
            v = math.pi * (j + 0.02) / 10.04
            ring = []
            for i in range(20):
                u = math.tau * i / 20
                wobble = (
                    1 + 0.035 * math.sin(3 * u + seed) * math.sin(v) + 0.023 * math.cos(5 * u - 2 * v + seed)
                )
                ring.append(
                    (
                        x + rx * math.sin(v) * math.cos(u) * wobble,
                        y + ry * math.cos(v) * wobble,
                        z + rz * math.sin(v) * math.sin(u) * wobble,
                    )
                )
            rows.append(ring)
        for index, low in enumerate(rows[:-1]):
            hi = rows[index + 1]
            for i in range(20):
                j = (i + 1) % 20
                pts = [low[i], low[j], hi[j], hi[i]]
                normals = (np.array(pts) - [x, y, z]) / np.square([rx, ry, rz]) if self.clay else None
                self.face(pts, col, normals)

    def contact_shadows(self):
        # March rays from visible surfaces toward a small area light in screen space.
        # The Z buffer distinguishes a nearby bumper from ground behind the same pixel.
        depth = self.depth
        valid = depth > -100
        yy, xx = np.mgrid[:H, :W]
        shade = np.zeros((H, W))
        for light in [(-0.51, 0.77, 0.36), (-0.37, 0.86, 0.40), (-0.48, 0.80, 0.53)]:
            ray = np.array(light)
            (u, v), dz = self.camera.camera(ray)
            u -= self.camera.base[0]
            v -= self.camera.base[1]
            occluded = np.zeros((H, W))
            for dist in np.geomspace(0.06, 2.2, 18):
                ox, oy = round(float(u * dist)), round(float(v * dist))
                nx, ny = np.clip(xx + ox, 0, W - 1), np.clip(yy + oy, 0, H - 1)
                blocked = depth[ny, nx] > depth + dz * dist + 0.036
                occluded = np.maximum(occluded, blocked * np.exp(-0.27 * dist))
            shade += occluded / 3
        shade = (
            np.asarray(Image.fromarray(np.uint8(shade * 255)).filter(ImageFilter.GaussianBlur(1.35))) / 255
        )
        strength = 0.27 if self.clay else 0.15
        return Image.fromarray(np.uint8(self.pixels * (1 - strength * (valid * shade)[:, :, None])))

    def oval(self, x, y, z, rx, rz, col):
        self.face(
            [
                (x + rx * math.cos(i * math.tau / 36), y, z + rz * math.sin(i * math.tau / 36))
                for i in range(36)
            ],
            col,
            normal=(0, 1, 0),
        )

    def decal(self, text, x, y, z, w, h, font):
        mask = np.asarray(fitted_text(text, 240, 64, font))
        # Screen-to-plane inversion keeps the sign on the front wall with proper occlusion.
        o = np.array(self.camera.camera((x - w / 2, y + h, z))[0])
        u = np.array(self.camera.camera((x + w / 2, y + h, z))[0]) - o
        v = np.array(self.camera.camera((x - w / 2, y, z))[0]) - o
        yy, xx = np.mgrid[:H, :W]
        inv = np.linalg.inv(np.column_stack([u, v]))
        ax = inv[0, 0] * (xx - o[0]) + inv[0, 1] * (yy - o[1])
        ay = inv[1, 0] * (xx - o[0]) + inv[1, 1] * (yy - o[1])
        sel = (ax >= 0) & (ax <= 1) & (ay >= 0) & (ay <= 1)
        zbuf = (x - w / 2 + w * ax) * self.eye[0] + (y + h - h * ay) * self.eye[1] + z * self.eye[2]
        sel &= zbuf > self.depth - 0.014
        a = (
            mask[(ay[sel] * (mask.shape[0] - 1)).astype(int), (ax[sel] * (mask.shape[1] - 1)).astype(int)][
                :, None
            ]
            / 255
        )
        self.pixels[sel] = self.pixels[sel] * (1 - a) + a * [255, 231, 178]


def model(style, t):
    font = study_font("Sans" if style == "clay" else "Serif")
    m = Mesh(style)
    soft = m.clay
    sea = "#71bec0"
    earth = "#d69c74"
    top = "#ebc792"
    rail = "#7a7368"
    wood = "#996e51"
    if not soft:
        m.rounded(0, -0.50, 0, 9.9, 0.24, 5.28, 0.17, "#c4aa8d")
        m.rounded(0, -0.28, 0, 9.9, 0.32, 5.28, 0.17, sea)
    rng = random.Random(101)
    if not soft:
        for _ in range(56):
            x, z = rng.uniform(-4.75, 4.75), rng.uniform(1.10, 2.42)
            m.oval(x, 0.046, z, rng.uniform(0.05, 0.27), 0.012, "#b2dbd1")
    if soft:
        for j in range(29):
            sx = -4.50 + j * 0.323
            m.blob(
                sx,
                0.07,
                1.08 + rng.uniform(-0.035, 0.055),
                0.28 + rng.random() * 0.13,
                0.19 + rng.random() * 0.09,
                0.19 + rng.random() * 0.10,
                rng.choice(["#bd8b6c", "#ce9b78", "#d2a785"]),
                j,
            )
        for sx in (-3.94, -3.74, 3.28, 3.53, 3.87):
            m.blob(sx, -0.015, 1.46 + rng.random() * 0.14, 0.18, 0.10, 0.14, "#bca48a", int(sx * 12))
        m.rounded(0, -0.12, -0.73, 9.62, 0.47, 3.70, 0.28, earth)
    else:
        m.rounded(0, 0.032, -0.73, 9.62, 0.32, 3.71, 0.17, earth)
    m.rounded(0, 0.34, -0.73, 9.64, 0.09, 3.75, 0.12, top)
    for x in np.arange(-4.72, 4.58, 0.22):
        m.box(x, 0.43, 0.40, 0.06, 0.026, 0.98, wood)
    for z in (0.08, 0.72):
        m.box(0, 0.456, z, 9.53, 0.044, 0.055, rail)
    for x in [-4.14, -3.35, 3.38, 4.32]:
        m.rod((x, 0.42, 1.03), (x, 0.62, 1.03), 0.045, "#5b7369")
    for x, z, sx, sz in [(-0.82, 0.36, 1.82, 0.57), (2.25, -1.4, 1.75, 1.02)]:
        m.oval(x + 0.11, 0.434, z + 0.13, sx, sz, "#ba9c79")
    # Copper-roofed station house and its central clock dormer.
    x, z = 2.08, -1.40
    m.rounded(x, 0.43, z, 3.20, 1.29, 1.42, 0.09, "#f0d3a0")
    m.box(x, 0.44, z, 3.31, 0.12, 1.48, "#c38d66")
    m.box(x, 1.64, z, 3.39, 0.13, 1.57, "#a86d4f")
    for side, col in [(1, "#75a397"), (-1, "#4b817e")]:
        m.face(
            [
                (x - 1.77, 1.77, z + side * 0.86),
                (x + 1.77, 1.77, z + side * 0.86),
                (x + 1.52, 2.22, z),
                (x - 1.51, 2.22, z),
            ],
            col,
        )
    for side in [-1, 1]:
        m.face(
            [
                (x + side * 1.58, 1.77, z - 0.76),
                (x + side * 1.58, 1.77, z + 0.76),
                (x + side * 1.58, 2.20, z),
            ],
            "#edd5a3",
        )
    for wx in [x - 1.26, x - 0.80, x + 0.80, x + 1.26]:
        m.box(wx, 0.72, z + 0.725, 0.28, 0.53, 0.04, "#528183")
        m.box(wx, 0.72, z + 0.758, 0.033, 0.53, 0.025, "#e9c590")
        m.box(wx, 0.985, z + 0.75, 0.28, 0.03, 0.025, "#e9c590")
    m.box(x, 0.55, z + 0.726, 0.4, 0.77, 0.05, "#685b4d")
    for i in range(3):
        m.box(x, 0.43 + i * 0.043, z + 0.83 + (2 - i) * 0.087, 0.7 - i * 0.06, 0.05, 0.23, "#d5b18b")
    for xx in [x - 0.48, x + 0.48]:
        m.box(xx, 0.56, z + 0.75, 0.11, 1.13, 0.10, "#f3dbb0")
    m.box(x + 0.27, 1.29, z + 0.79, 1.66, 0.33, 0.07, "#365951")
    m.decal(STUDY_TITLE, x + 0.27, 1.335, z + 0.836, 1.52, 0.22, font)
    m.box(x, 1.71, z + 0.38, 0.95, 0.50, 0.70, "#efcda0")
    m.face([(x - 0.48, 2.20, z + 0.738), (x + 0.48, 2.20, z + 0.738), (x, 2.63, z + 0.738)], "#eed3aa")
    for k in [-1, 1]:
        m.face(
            [
                (x + k * 0.57, 2.16, z + 0.83),
                (x, 2.69, z + 0.83),
                (x, 2.69, z - 0.10),
                (x + k * 0.57, 2.16, z - 0.10),
            ],
            "#54867e",
        )
    m.rod((x, 2.13, z + 0.73), (x, 2.13, z + 0.79), 0.222, "#896c52", 24)
    m.rod((x, 2.13, z + 0.788), (x, 2.13, z + 0.804), 0.180, "#ffe7ae", 24)
    m.rod((x - 0.095, 2.17, z + 0.81), (x, 2.13, z + 0.81), 0.011, "#485957")
    m.rod((x, 2.13, z + 0.81), (x + 0.042, 2.24, z + 0.81), 0.012, "#485957")
    # Rounded electric car with side glazing, brass wheel hubs and a diamond collector.
    x, z = -1.02, 0.43
    for wx in (x - 1.12, x + 1.10):
        for wz in [z - 0.38, z + 0.38]:
            m.rod((wx, 0.69, wz - 0.065), (wx, 0.69, wz + 0.065), 0.193, "#4d5050", 18)
            m.rod((wx, 0.69, wz + 0.069), (wx, 0.69, wz + 0.077), 0.086, "#b3a37f", 16)
    m.rounded(x, 0.70, z, 3.46, 0.15, 1.04, 0.17, "#656865")
    m.rounded(x, 0.81, z, 3.48, 0.56, 1.09, 0.21, "#cc684b")
    m.rounded(x, 1.32, z, 3.47, 0.53, 1.08, 0.20, "#f2d6a0")
    m.rounded(x, 1.83, z, 3.61, 0.13, 1.16, 0.22, "#698b84")
    m.rounded(x, 1.953, z, 2.80, 0.11, 0.80, 0.18, "#b6ad87")
    for k in range(8):
        wx = x - 1.38 + k * 0.39
        m.rounded(wx, 1.395, z + 0.544, 0.31, 0.36, 0.048, 0.021, "#487580")
        m.box(wx - 0.10, 1.43, z + 0.575, 0.019, 0.27, 0.012, "#9ebeb3")
    for side in [-1, 1]:
        xx = x + side * 1.743
        for wz in [z - 0.18, z + 0.18]:
            m.box(xx, 1.39, wz, 0.030, 0.35, 0.286, "#507984")
        for wz in [z - 0.32, z + 0.32]:
            m.rod((xx, 1.09, wz), (xx + side * 0.032, 1.09, wz), 0.07, "#f7d78e", 16)
        m.box(xx, 0.89, z, 0.038, 0.04, 0.93, "#e8b879")
    m.box(x, 1.29, z + 0.55, 3.14, 0.037, 0.02, "#f1bd75")
    for ax, ay, bx, by in [(-0.58, 2.07, 0, 2.43), (0, 2.43, 0.58, 2.14), (0.58, 2.14, 0.30, 2.07)]:
        m.rod((x + ax, ay, z), (x + bx, by, z), 0.026, "#535b5c")
    m.rod((x - 0.12, 2.43, z), (x + 0.13, 2.43, z), 0.029, "#575d58")
    for px in [-3.55, 3.96]:
        m.rod((px, 0.43, -0.15), (px, 2.66, -0.15), 0.045, "#8a745e")
        m.rod((px, 2.56, -0.15), (px, 2.51, 0.48), 0.021, "#776b5d")
    m.rod((-3.55, 2.51, 0.48), (x, 2.43, z), 0.008, "#817461", 6)
    m.rod((x, 2.43, z), (3.96, 2.51, 0.48), 0.008, "#817461", 6)
    # A harbor launch moored below the platform and a short floating pier.
    drift = t - PREVIEW_PHASE
    bx, bz = -2.55 + 0.18 * math.sin(drift), 1.91 + 0.047 * math.sin(2 * drift)
    m.rounded(bx, 0.10, bz, 1.66, 0.20, 0.52, 0.245, "#ab6550")
    m.rounded(bx, 0.27, bz, 1.32, 0.08, 0.46, 0.16, "#e3c798")
    m.rounded(bx, 0.34, bz, 0.73, 0.20, 0.35, 0.07, "#f3dbba")
    m.box(bx, 0.39, bz + 0.18, 0.57, 0.09, 0.03, "#5f8c91")
    m.rounded(bx, 0.54, bz, 0.85, 0.07, 0.43, 0.065, "#76988e")
    m.rod((bx - 0.51, 0.34, bz), (bx - 0.51, 0.85, bz), 0.019, "#7c7160")
    for j in range(7):
        m.box(3.31, 0.24, 1.25 + j * 0.106, 0.57, 0.07, 0.09, "#bd9871")
    # A waiting passenger, scarf and suitcase, next to the platform bench.
    px, pz, gy = 2.66, 0.94, 0.44
    for dx in (-0.062, 0.060):
        m.rod((px + dx, gy + 0.03, pz), (px + dx, gy + 0.27, pz), 0.040, "#535b5c")
        m.rounded(px + dx - 0.023, gy, pz, 0.15, 0.075, 0.11, 0.045, "#514b48")
    m.blob(px, gy + 0.37, pz, 0.129, 0.217, 0.112, "#e2b461", 4)
    m.blob(px - 0.021, gy + 0.614, pz, 0.087, 0.108, 0.085, "#d89f77", 6)
    m.blob(px - 0.025, gy + 0.685, pz, 0.119, 0.061, 0.115, "#a7614a", 7)
    m.rod((px + 0.11, gy + 0.475, pz), (px + 0.19, gy + 0.25, pz), 0.034, "#d3a055")
    m.rounded(px + 0.21, gy + 0.12, pz, 0.18, 0.15, 0.10, 0.033, "#b16848")
    m.rod((px + 0.12, gy + 0.54, pz), (px - 0.06, gy + 0.53, pz + 0.035), 0.029, "#b55f49")
    for ax in (-4.15, -3.90, 3.90):
        m.rod((ax, 0.43, -1.19), (ax, 1.05, -1.19), 0.04, "#98784f")
        for k in range(3):
            m.blob(
                ax + (0.11 if k == 1 else -0.04),
                1.03 + 0.17 * k,
                -1.19 + (0.08 if k == 1 else 0),
                0.23 - 0.03 * k,
                0.23,
                0.20,
                "#83a17b" if k != 1 else "#6d9677",
                k + int(ax * 2),
            )
    if soft:
        # Overlapping copper tiles and glazing bars leave thumb-sized surface relief.
        for tx in np.arange(0.56, 3.72, 0.25):
            if abs(tx - 2.08) > 0.54 and 0.52 < tx < 3.7:
                m.rod((tx, 1.80, -0.59), (tx, 2.22, -1.39), 0.028, "#76a89b", 8)
        for wx in np.arange(-2.35, 0.38, 0.39):
            m.rod((wx, 1.75, 0.997), (wx + 0.25, 1.75, 0.997), 0.018, "#dfc69c", 8)
        for wx in [-2.17, -0.24]:
            m.rod((wx, 1.11, 0.985), (wx + 0.35, 1.11, 0.985), 0.014, "#e8b778", 8)
    im = m.contact_shadows()
    if soft:
        yy, xx = np.mgrid[:H, :W]
        arr = np.asarray(im, float)
        tool = np.sin(0.73 * xx + 0.28 * yy + 3 * np.sin(0.053 * yy)) * np.sin(0.10 * yy - 0.04 * xx)
        im = grain(
            Image.fromarray(np.uint8(np.clip(arr + 1.55 * tool[:, :, None], 0, 255))).filter(
                ImageFilter.GaussianBlur(0.48)
            ),
            1.8,
        )
    else:
        im = grain(im, 1)
    return im
