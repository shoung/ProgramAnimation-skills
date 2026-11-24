"""The default study fonts and the strict two-color title must survive copy installation."""

import sys
import unittest
from pathlib import Path

from PIL import ImageChops

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/program-animation/scripts"))
from lettering import glyphs
from styles import renderer


class LetteringTests(unittest.TestCase):
    def test_one_bit_title_stays_in_palette_and_can_be_replaced(self):
        draw = renderer("one-bit")
        background = draw(0.85, title="")
        title = draw(0.85)
        alternate = draw(0.85, title="海岸")
        colors = {color for _, color in background.getcolors(2)}
        for frame in (title, alternate):
            self.assertEqual({color for _, color in frame.getcolors(2)}, colors)
            box = ImageChops.difference(frame, background).getbbox()
            self.assertIsNotNone(box)
            self.assertLess(box[2], 400)
            self.assertLess(box[3], 200)
        self.assertIsNotNone(ImageChops.difference(title, alternate).getbbox())

    def test_packaged_faces_cover_traditional_characters(self):
        for family in ("Serif", "Sans", "WenKai"):
            a = glyphs("燈", family, 52, 550, None, False)
            b = glyphs("塔", family, 52, 550, None, False)
            self.assertTrue(a.getbbox() and b.getbbox())
            self.assertNotEqual(a.tobytes(), b.tobytes())
        with self.assertRaisesRegex(ValueError, "--font"):
            glyphs("山城夜雨", "Serif", 52, 550, None, False)
