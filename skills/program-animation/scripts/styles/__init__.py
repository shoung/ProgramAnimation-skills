"""Order follows the visual reference, left to right, top to bottom."""

from importlib import import_module

CATALOG = {
    "paper-cut": ("層疊剪紙", "Layered paper"),
    "ink-wash": ("山水水墨", "Ink wash"),
    "woodblock": ("浮世繪木版", "Woodblock"),
    "mineral": ("青綠金箋", "Mineral landscape"),
    "clay": ("黏土微縮", "Clay miniature"),
    "riso": ("孔版套色", "Risograph"),
    "clear-line": ("莫比烏斯式清線", "Ligne claire"),
    "drafting": ("復古工程圖", "Survey drawing"),
    "isometric": ("等角場景模型", "Isometric diorama"),
    "point-cloud": ("粒子點雲", "Particle cloud"),
    "one-bit": ("1-bit 抖動", "One-bit dither"),
    "impasto": ("厚塗油畫", "Impasto"),
}


def renderer(style):
    return import_module("styles." + style.replace("-", "_")).frame
