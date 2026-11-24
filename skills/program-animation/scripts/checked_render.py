"""Frame-level validation and atomic video encoding. Reusable with any pixel-producing backend."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


class InvalidFrame(ValueError):
    pass


def check_pixels(im, size, *, flat=None, probes=(), matte="white", min_contrast=3):
    """flat is the expected solid RGB for an intentional hold. Probes are exclusive-end XYXY boxes."""
    if not 0 <= min_contrast < 255:
        raise ValueError("min_contrast must fall within [0, 255)")
    if not isinstance(im, Image.Image) or im.size != size:
        raise InvalidFrame(f"Expected a {size} Pillow image")
    rgba = im.convert("RGBA")
    if rgba.getchannel("A").getextrema()[1] == 0:
        raise InvalidFrame("Fully transparent readback")
    background = Image.new("RGBA", size, matte)
    background.alpha_composite(rgba)
    rgb = background.convert("RGB")
    data = np.asarray(rgb, dtype=np.int16)
    if flat is not None:
        if np.max(np.abs(data - np.asarray(flat))) > 3:
            raise InvalidFrame(f"Expected a deliberate hold in {flat}")
        return rgb
    for box in [(0, 0, *size), *probes]:
        x, y, r, b = box
        if not (0 <= x < r <= size[0] and 0 <= y < b <= size[1]):
            raise ValueError(f"Invalid content probe {box}")
        patch = data[y:b, x:r]
        # Per-channel comparison also catches a fully saturated, single-color frame.
        # Ignore isolated noisy pixels in an otherwise empty buffer.
        base = np.median(patch[:: max(1, (b - y) // 9), :: max(1, (r - x) // 9)], axis=(0, 1))
        varied = np.any(np.abs(patch - base) > min_contrast, axis=2)
        need = min(24, max(1, patch.shape[0] * patch.shape[1] // 1000))
        if np.max(np.ptp(patch, axis=(0, 1))) <= min_contrast or varied.sum() < need:
            raise InvalidFrame(f"Empty or near-uniform pixels in {box}")
    return rgb


def checked_frame(
    index, render, size, *, restart=None, attempts=3, flat=None, probes=(), verify=None, min_contrast=3
):
    """render(index) must seek explicitly. restart() must restore the renderer at the same time."""
    if attempts < 1:
        raise ValueError("Need at least one attempt")
    for attempt in range(1, attempts + 1):
        try:
            raw = render(index)
            pixels = check_pixels(raw, size, flat=flat, probes=probes, min_contrast=min_contrast)
            if verify is not None and not verify(index, pixels):
                raise InvalidFrame("Scene content check failed")
            return pixels
        except (InvalidFrame, OSError, RuntimeError) as exc:
            if attempt == attempts:
                raise InvalidFrame(f"Frame {index} failed after {attempts} attempts: {exc}") from exc
            print(f"Frame {index}, attempt {attempt}: {exc}; rerendering", file=sys.stderr)
            if restart is not None:
                restart()


def encode(path, frames, *, count, size, fps, audio=None):
    """Consume checked RGB frames. Publish only a complete, decodable file of the promised length."""
    path = Path(path)
    if count <= 0 or fps <= 0 or any(n <= 0 or n % 2 for n in size):
        raise ValueError("Need positive count, fps and even image dimensions")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=path.parent) as work:
        temp = Path(work) / "film.mp4"
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-xerror",
            "-nostdin",
            "-y",
            "-f",
            "rawvideo",
            "-pixel_format",
            "rgb24",
            "-video_size",
            f"{size[0]}x{size[1]}",
            "-framerate",
            str(fps),
            "-i",
            "pipe:0",
        ]
        if audio:
            seconds = float(
                subprocess.check_output(
                    [
                        "ffprobe",
                        "-v",
                        "error",
                        "-show_entries",
                        "format=duration",
                        "-of",
                        "default=nw=1:nk=1",
                        str(audio),
                    ],
                    text=True,
                )
            )
            if seconds > count / fps + 0.001:
                raise ValueError(f"Audio lasts {seconds:.3f} s but the film lasts {count / fps:.3f} s")
            cmd += [
                "-i",
                str(audio),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-af",
                "apad",
                "-c:a",
                "aac",
                "-t",
                str(count / fps),
            ]
        cmd += [
            "-c:v",
            "libx264",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(temp),
        ]
        with subprocess.Popen(cmd, stdin=subprocess.PIPE) as proc:
            written = 0
            try:
                for im in frames:
                    if im.size != size or im.mode != "RGB":
                        raise InvalidFrame(f"Unexpected format at frame {written}")
                    proc.stdin.write(im.tobytes())
                    written += 1
                proc.stdin.close()
                if proc.wait() != 0 or written != count:
                    raise RuntimeError(f"Encode failed or frame count mismatch: {written}/{count}")
            except BaseException:
                proc.kill()
                raise
        subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i", str(temp), "-f", "null", "-"], check=True)
        found = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-count_frames",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=nb_read_frames",
                "-of",
                "csv=p=0",
                str(temp),
            ],
            text=True,
        ).strip()
        if found != str(count):
            raise RuntimeError(f"Decoded {found} frames, expected {count}")
        os.replace(temp, path)
