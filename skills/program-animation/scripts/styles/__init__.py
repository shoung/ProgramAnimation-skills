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


def harbor_frame(style):
    """Bind a style to the harbor scene while retaining frame(t, title, font_path)."""

    def frame(t, title=None, font_path=None):
        from lettering import STUDY_TITLE, letter

        if style in {"clay", "isometric"}:
            from harbor_model import model

            image = model(style, t)
        else:
            from harbor_plates import drafting, nocturne, print_plate

            if style in {"point-cloud", "one-bit"}:
                image = nocturne(style, t)
            elif style == "drafting":
                image = drafting(t)
            else:
                image = print_plate(style, t)
        return letter(image, style, STUDY_TITLE if title is None else title, font_path)

    return frame
