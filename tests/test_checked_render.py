"""Regressions for readbacks that succeed but contain no scene, and for partial video delivery."""

import io
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/program-animation/scripts"))
from checked_render import InvalidFrame, check_pixels, checked_frame, encode


class FrameGuardTest(unittest.TestCase):
    size = (80, 60)

    def picture(self):
        im = Image.new("RGB", self.size, "#456789")
        ImageDraw.Draw(im).rectangle((31, 20, 51, 42), fill="#fff3da")
        return im

    def test_restarts_and_renders_same_index_after_loss(self):
        calls = []
        restarts = []

        def renderer(index):
            calls.append(index)
            return self.picture() if restarts else Image.new("RGB", self.size, "#456789")

        with redirect_stderr(io.StringIO()):
            im = checked_frame(57, renderer, self.size, restart=lambda: restarts.append(True))
        self.assertEqual(calls, [57, 57])
        self.assertEqual(restarts, [True])
        self.assertEqual(im.tobytes(), self.picture().tobytes())

    def test_subject_missing_even_with_caption_remaining(self):
        im = self.picture()
        with self.assertRaises(InvalidFrame):
            check_pixels(im, self.size, probes=[(0, 0, 20, 20)])

    def test_dim_fade_keeps_content_requirement(self):
        dim = Image.new("RGB", self.size)
        ImageDraw.Draw(dim).ellipse((19, 13, 60, 47), fill=(2, 2, 2))
        with self.assertRaises(InvalidFrame):
            check_pixels(dim, self.size)
        checked_frame(5, lambda _: dim, self.size, min_contrast=0)
        with self.assertRaises(InvalidFrame):
            check_pixels(Image.new("RGB", self.size), self.size, min_contrast=0)

    def test_transparency_flat_holds_and_stuck_pixel(self):
        im = Image.new("RGBA", self.size, (25, 100, 200, 0))
        with self.assertRaises(InvalidFrame):
            check_pixels(im, self.size, flat=(255, 255, 255))
        black = Image.new("RGB", self.size)
        check_pixels(black, self.size, flat=(0, 0, 0))
        with self.assertRaises(InvalidFrame):
            check_pixels(black, self.size, flat=(255, 255, 255))
        black.putpixel((0, 0), (255, 255, 255))
        with self.assertRaises(InvalidFrame):
            check_pixels(black, self.size)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "video tools required")
    def test_persistent_loss_preserves_previous_delivery(self):
        def frames():
            for i in range(3):
                yield checked_frame(
                    i, lambda n: self.picture() if n < 2 else Image.new("RGB", self.size), self.size
                )

        with tempfile.TemporaryDirectory() as work:
            dest = Path(work) / "film.mp4"
            encode(dest, [self.picture()], count=1, size=self.size, fps=4)
            previous = dest.read_bytes()
            with (
                redirect_stderr(io.StringIO()),
                self.assertRaisesRegex(InvalidFrame, "Frame 2 failed after 3"),
            ):
                encode(dest, frames(), count=3, size=self.size, fps=4)
            self.assertEqual(dest.read_bytes(), previous)
