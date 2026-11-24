"""Render twelve PNG previews and the contact sheet from the installed skill."""

from pathlib import Path

from checked_render import checked_frame
from coast import SIZE
from harbor_scene import PREVIEW_PHASE
from lettering import STUDY_TITLE, study_font, weighted_font
from PIL import Image, ImageDraw
from styles import CATALOG, renderer

ASSETS = Path(__file__).resolve().parents[1] / "assets"

CAPTIONS = {
    "paper-cut": "層層紙階與切邊投影",
    "ink-wash": "乾筆、濕墨與海上留白",
    "woodblock": "木紋、漸層刷色與刻線",
    "mineral": "金地上的石青、石綠",
    "clay": "圓角壓痕與柔光塑形",
    "riso": "色版偏移與細網點",
    "clear-line": "粉彩平塗與隨形排線",
    "drafting": "輪組剖面、尺寸與引線",
    "isometric": "平行投影的立體場景",
    "point-cloud": "粒子描出車燈與水面反光",
    "one-bit": "雙色網點與整塊暗面",
    "impasto": "順著物體走向疊上短筆觸",
}


def main():
    folder = ASSETS / "previews"
    folder.mkdir(parents=True, exist_ok=True)
    w, h = SIZE
    margin, gap, top, caption = 48, 24, 118, 65
    sheet = Image.new("RGB", (margin * 2 + 3 * w + 2 * gap, top + 4 * (h + caption) + 20), "#f7f3eb")
    d = ImageDraw.Draw(sheet)
    heading = weighted_font(study_font("Serif"), 57, 430)
    label = weighted_font(study_font("Sans"), 32, 540)
    blurb = weighted_font(study_font("Sans"), 23, 420)
    d.text((margin, 24), STUDY_TITLE, font=heading, anchor="lt", fill="#233a38")
    d.text((sheet.width - margin, 45), "同一座車站的十二種畫法", font=label, anchor="rt", fill="#52615c")
    d.line((margin, 94, sheet.width - margin, 94), fill="#9d9b88", width=2)
    for i, key in enumerate(CATALOG):
        draw = renderer(key)
        im = checked_frame(0, lambda _, render=draw: render(PREVIEW_PHASE), SIZE)
        if key == "one-bit" and len(im.getcolors(3) or []) != 2:
            raise ValueError("The night engraving requires exactly two inks.")
        im.save(folder / f"{key}.png")
        x = margin + (i % 3) * (w + gap)
        y = top + (i // 3) * (h + caption)
        sheet.paste(im, (x, y))
        d.text((x, y + h + 12), CATALOG[key][0], font=label, anchor="lt", fill="#243d38")
        d.text((x + w, y + h + 17), CAPTIONS[key], font=blurb, anchor="rt", fill="#55645c")
        print(key, flush=True)
    sheet.save(ASSETS / "gallery.png")


if __name__ == "__main__":
    main()
