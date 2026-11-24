"""Layered sunset and sea strips with cast shadows along the cut edges."""

from print_landscape import PALETTE

from styles import harbor_frame

COLORS = {
    **PALETTE,
    "sky": "#efd8b4",
    "sun": "#e9654c",
    "cloud": "#fff5e5",
    "mountain": "#b4a0c9",
    "crest": "#e2cee4",
    "face": "#9680b7",
    "ridge": "#ad98c2",
    "sea": "#569a96",
    "foam": "#e6d6bb",
    "stone": "#c48165",
    "shade": "#ae6e59",
    "land": "#92b68c",
    "pine": "#518a79",
    "leaf": "#6da78a",
    "wall": "#f7ebdb",
    "red": "#dc6b56",
    "seam": "#b4745a",
}


frame = harbor_frame("paper-cut")
