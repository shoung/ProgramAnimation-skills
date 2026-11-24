"""Broad coastal planes used by the ink and particle studies, ordered back to front."""

import math

from coast import Mark, scene


def cloud(x, y, scale):
    # Overlapping lobes traced as one continuous silhouette.
    arcs = [
        ((-53, 3), (-52, -9), (-42, -15), (-31, -13)),
        ((-31, -13), (-22, -26), (-6, -24), (-1, -19)),
        ((-1, -19), (6, -28), (24, -26), (30, -18)),
        ((30, -18), (53, -24), (62, -6), (53, 6)),
        ((53, 6), (48, 15), (36, 16), (27, 13)),
        ((27, 13), (9, 17), (-3, 12), (-11, 13)),
        ((-11, 13), (-21, 17), (-36, 12), (-38, 12)),
        ((-38, 12), (-49, 13), (-54, 10), (-53, 3)),
    ]
    points = []
    for arc in arcs:
        for i in range(8):
            u = i / 8
            weights = ((1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u**3)
            bx, by = (sum(weight * p[k] for weight, p in zip(weights, arc)) for k in (0, 1))
            points.append((x + scale * bx, y + scale * by))
    return Mark("poly", "cloud", points)


def landscape(t):
    marks = []

    def polygon(role, *points):
        marks.append(Mark("poly", role, points))

    def stroke(role, *points, width=1):
        marks.append(Mark("line", role, points, width))

    marks.append(Mark("oval", "sun", [(278, 146), (380, 248)]))
    for x, y, s in [(15, 181, 0.95), (548, 128, 1.1), (715, 54, 1.85), (947, 165, 0.76)]:
        marks.append(cloud(x + 6 * math.sin(t), y, s))
    # A ridge front is a continuous contour; only the crests rise above the haze.
    for x, y, w, h in [
        (333, 208, 240, 168),
        (733, 218, 273, 158),
        (1015, 232, 230, 144),
        (131, 168, 292, 209),
        (292, 302, 142, 76),
        (828, 294, 193, 84),
    ]:

        def peak(u, v, x=x, y=y, w=w, h=h):
            return x + u * w, y + v * h

        left = [
            (-1, 1),
            (-0.78, 0.78),
            (-0.64, 0.69),
            (-0.49, 0.50),
            (-0.34, 0.39),
            (-0.19, 0.23),
            (-0.08, 0.145),
            (0, 0),
        ]
        right = [(0.13, 0.20), (0.31, 0.39), (0.48, 0.52), (0.58, 0.61), (0.74, 0.72), (1, 1)]
        polygon("mountain", *(peak(a, b) for a, b in left + right))
        polygon(
            "crest",
            *(
                peak(a, b)
                for a, b in [
                    (-0.66, 0.69),
                    (-0.34, 0.39),
                    (-0.19, 0.23),
                    (-0.08, 0.145),
                    (0, 0),
                    (0.13, 0.20),
                    (0.31, 0.39),
                    (0.48, 0.52),
                    (0.34, 0.46),
                    (0.12, 0.26),
                    (0.007, 0.09),
                    (-0.10, 0.22),
                    (-0.27, 0.35),
                    (-0.35, 0.46),
                ]
            ),
        )
        polygon(
            "face",
            *(
                peak(a, b)
                for a, b in [
                    (0, 0),
                    *right,
                    (0.64, 0.89),
                    (0.43, 0.76),
                    (0.40, 0.80),
                    (0.25, 0.64),
                    (0.24, 0.70),
                    (0.13, 0.49),
                    (0.08, 0.46),
                    (0.045, 0.28),
                ]
            ),
        )
        stroke(
            "ridge",
            *(
                peak(a, b)
                for a, b in [
                    (-0.60, 0.73),
                    (-0.28, 0.49),
                    (-0.09, 0.31),
                    (0.008, 0.15),
                    (0.12, 0.34),
                    (0.32, 0.53),
                ]
            ),
        )
    polygon("sea", (-4, 376), (964, 376), (964, 545), (-4, 545))

    def rock(top, toe, shadow, grass=True):
        polygon("stone", *top, *reversed(toe))
        polygon("shade", *shadow)
        stroke("foam", *toe, width=2)
        if grass:
            polygon("land", *((x, y - 4) for x, y in top), *reversed(top))

    rock(
        [(104, 378), (144, 378)],
        [(99, 424), (151, 425)],
        [(135, 378), (144, 378), (151, 425), (135, 424)],
        False,
    )
    rock(
        [(198, 329), (237, 328), (275, 327)],
        [(183, 421), (223, 425), (284, 421)],
        [(246, 328), (275, 327), (273, 365), (284, 421), (247, 423), (241, 396)],
    )
    rock(
        [(471, 326), (497, 316), (610, 315), (668, 317), (736, 320)],
        [(418, 429), (495, 436), (594, 432), (687, 438), (780, 430)],
        [
            (610, 315),
            (668, 317),
            (736, 320),
            (728, 343),
            (740, 372),
            (712, 373),
            (739, 421),
            (675, 433),
            (647, 402),
            (612, 403),
            (626, 375),
            (612, 365),
        ],
    )
    rock(
        [(718, 358), (755, 359), (805, 361)],
        [(703, 433), (764, 438), (828, 433)],
        [(771, 360), (805, 361), (828, 433), (797, 431), (784, 395)],
    )
    rock(
        [(341, 383), (407, 379), (519, 378)],
        [(319, 434), (422, 438), (533, 434)],
        [(455, 379), (519, 378), (512, 397), (533, 434), (470, 435), (479, 411), (452, 413)],
    )
    rock(
        [(538, 425), (585, 420), (657, 420)],
        [(521, 442), (590, 446), (669, 443)],
        [(647, 420), (657, 420), (669, 443), (648, 443)],
        False,
    )
    rock(
        [(769, 412), (846, 413)],
        [(747, 437), (866, 437)],
        [(829, 413), (846, 413), (866, 437), (849, 437)],
        False,
    )
    rock(
        [(272, 428), (302, 427)],
        [(262, 440), (303, 440)],
        [(293, 427), (302, 427), (303, 440), (294, 440)],
        False,
    )

    # Weathering interrupts the large planes: a few chipped lips, bedding seams
    # and clefts are enough to explain a rock's volume without outlining every facet.
    for pts in [
        [(199, 374), (209, 363), (217, 361), (222, 355)],
        [(205, 378), (208, 372), (213, 370)],
        [(352, 398), (358, 397), (366, 389)],
        [(372, 426), (375, 420), (382, 416), (384, 408)],
        [(479, 346), (486, 335), (492, 331)],
        [(515, 418), (523, 411), (537, 407), (545, 400)],
        [(541, 412), (553, 409), (558, 405)],
        [(645, 399), (658, 392), (660, 383)],
        [(787, 410), (780, 399), (780, 393)],
        [(608, 433), (620, 428), (627, 428)],
    ]:
        stroke("seam", *pts)
    for pts in [
        [(472, 327), (499, 319), (565, 318)],
        [(343, 385), (408, 382), (445, 382)],
        [(578, 422), (611, 421), (644, 421)],
        [(201, 331), (226, 330), (240, 330)],
    ]:
        stroke("lip", *pts, width=2)

    def pine(x, y, h):
        polygon("trunk", (x - 1.4, y), (x - 1, y - h * 0.3), (x + 1.5, y - h * 0.3), (x + 2, y))
        profile = [
            (0, -1),
            (0.12, -0.69),
            (0.08, -0.68),
            (0.19, -0.43),
            (0.14, -0.43),
            (0.245, -0.16),
            (0.12, -0.135),
            (0, -0.15),
            (-0.22, -0.13),
            (-0.15, -0.43),
            (-0.20, -0.42),
            (-0.08, -0.69),
            (-0.13, -0.68),
        ]
        polygon("pine", *((x + h * a, y + h * b) for a, b in profile))
        polygon("leaf", (x, y - h * 0.91), (x - 1, y - h * 0.51), (x - h * 0.125, y - h * 0.46))

    for x, y, h in [
        (224, 326, 26),
        (239, 326, 15),
        (364, 379, 33),
        (385, 380, 55),
        (406, 379, 36),
        (423, 379, 68),
        (443, 378, 28),
        (457, 378, 47),
        (709, 316, 22),
        (744, 358, 34),
        (757, 358, 19),
    ]:
        pine(x, y, h)

    for i in range(5):
        x = 322 + i * 14
        stroke("rail", (x, 435), (x + 2, 419 - i * 0.5), width=3)
    stroke("rail", (322, 426), (376, 423), width=2)
    for x, y in [(388, 410), (395, 404), (402, 398), (409, 392)]:
        stroke("step", (x, y), (x + 10, y - 1), width=2)

    # Reuse the keeper's cottage, beacon, boat and birds without the other study's terrain.
    shared = scene(t)
    start = next(i for i, m in enumerate(shared) if m.role == "wall")
    for m in shared[start:]:
        if m.kind == "line" and m.role == "wall":  # stairs on the original cliff
            continue
        points = m.xy
        if m.role == "red" and min(x for x, _ in points) > 638:
            y0 = points[0][1]
            if y0 == 265:
                continue
            start, end = (147, 176) if y0 == 143 else (217, 247)
            r1, r2 = 13 + (start - 117) * 0.064, 13 + (end - 117) * 0.064
            points = [(671 - r1, start), (671 + r1, start), (671 + r2, end), (671 - r2, end)]
        if m.role == "bird":
            marks.append(m)
            continue
        if max(x for x, _ in points) < 300:
            if min(x for x, _ in points) > 150:
                continue
            points = [(x - 25, y + 34) for x, y in points]
        else:
            # Set both buildings on the high terrace and enlarge them slightly.
            points = [(626 + (x - 671) * 1.22, 315 + (y - 294) * 1.12) for x, y in points]
        marks.append(Mark(m.kind, m.role, points, m.width))
    return marks
