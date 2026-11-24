"""Render a still or a full loop from one of the twelve executable studies."""

import argparse
import math
from pathlib import Path

from checked_render import checked_frame, encode
from coast import SIZE
from harbor_scene import PREVIEW_PHASE
from lettering import STUDY_TITLE
from styles import CATALOG, renderer


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--style", choices=CATALOG, required=True)
    out = p.add_mutually_exclusive_group(required=True)
    out.add_argument("--png", type=Path)
    out.add_argument("--video", type=Path)
    p.add_argument("--seconds", type=float, default=4)
    p.add_argument("--fps", type=int, default=24)
    p.add_argument("--audio", type=Path, help="Optional pre-mixed audio track for the MP4")
    p.add_argument("--phase", type=float, default=PREVIEW_PHASE, help="Still image phase in radians")
    p.add_argument(
        "--title",
        default=STUDY_TITLE,
        help="Text styled within the scene; pass an empty string to omit the title overlay",
    )
    p.add_argument("--font", type=Path, help="Full font covering a custom title (TTF, OTF, or TTC)")
    args = p.parse_args()
    if not math.isfinite(args.seconds) or args.seconds <= 0 or args.fps <= 0 or not math.isfinite(args.phase):
        p.error("seconds and fps must be positive and phase must be finite")
    if args.png and args.audio:
        p.error("--audio requires --video")
    art = renderer(args.style)
    if args.png:
        im = checked_frame(0, lambda _: art(args.phase, args.title, args.font), SIZE)
        args.png.parent.mkdir(parents=True, exist_ok=True)
        im.save(args.png, format="PNG")
    else:
        count = max(1, round(args.seconds * args.fps))

        def frame(i):
            return art(math.tau * i / count, args.title, args.font)

        encode(
            args.video,
            (checked_frame(i, frame, SIZE) for i in range(count)),
            count=count,
            size=SIZE,
            fps=args.fps,
            audio=args.audio,
        )


if __name__ == "__main__":
    main()
