"""Rebuild all twelve PNGs and the labelled contact sheet from the example code."""

from pathlib import Path

from checked_render import checked_frame
from coast import SIZE
from PIL import Image, ImageDraw, ImageFont
from styles import CATALOG, renderer

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def main():
    folder = ASSETS / "previews"
    folder.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGB", (1600, 876), "#f6f2e9")
    d = ImageDraw.Draw(sheet)
    cjk = next(
        (
            p
            for p in [
                "/System/Library/Fonts/Supplemental/Songti.ttc",
                "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
            ]
            if Path(p).exists()
        ),
        None,
    )

    def font(size):
        return (
            ImageFont.truetype(cjk, size=size, index=2 if cjk.endswith("Songti.ttc") else 0)
            if cjk
            else ImageFont.load_default(size=size)
        )

    d.text(
        (33, 12), "燈塔的十二種畫法" if cjk else "Twelve lighthouse studies", font=font(42), fill="#273b3c"
    )
    for i, (key, (zh, en)) in enumerate(CATALOG.items()):
        im = checked_frame(0, lambda _, style=key: renderer(style)(0.85), SIZE)
        im.save(folder / (key + ".png"))
        x, y = 34 + (i % 4) * 388, 84 + (i // 4) * 260
        thumb = im.resize(
            (368, 207), Image.Resampling.BOX if key == "one-bit" else Image.Resampling.LANCZOS
        )
        sheet.paste(thumb, (x, y))
        label = zh if cjk else en
        d.text((x, y + 213), label, font=font(22), fill="#243b3c")
        print(key, flush=True)
    sheet.save(ASSETS / "gallery.jpg", quality=93, subsampling=0)


if __name__ == "__main__":
    main()
