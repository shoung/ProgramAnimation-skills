"""Orthographic projection shared by the two harbor models."""

import math


class OrthographicCamera:
    def __init__(self, azimuth, elevation, scale, origin):
        self.az = azimuth
        self.el = elevation
        self.scale = scale
        self.base = origin

    def camera(self, p):
        x, y, z = p
        a, e = self.az, self.el
        u = x * math.cos(a) - z * math.sin(a)
        towards = x * math.sin(a) + z * math.cos(a)
        v = y * math.cos(e) - towards * math.sin(e)
        depth = y * math.sin(e) + towards * math.cos(e)
        return (self.base[0] + u * self.scale, self.base[1] - v * self.scale), depth
