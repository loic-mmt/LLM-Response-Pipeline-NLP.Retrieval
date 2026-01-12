
from __future__ import annotations

from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont

# Classic meme fonts on macOS (Impact is ideal)
DEFAULT_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/Library/Fonts/Impact.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]


def _load_font(font_size: int, font_path: str | None = None) -> ImageFont.ImageFont:
    # User-provided font
    if font_path:
        p = Path(font_path)
        if p.exists():
            return ImageFont.truetype(str(p), font_size)

    # Try common system fonts
    for cand in DEFAULT_FONT_CANDIDATES:
        p = Path(cand)
        if p.exists():
            return ImageFont.truetype(str(p), font_size)

    # Last resort: DejaVu if available in Pillow
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except Exception:
        return ImageFont.load_default()


def draw_bottom_caption(
    img_path: str,
    caption: str,
    out_path: str,
    font_size: int = 52,
    stroke: int = 4,
    font_path: str | None = None,
):
    img = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # IMPORTANT: load a TrueType font so font_size is respected
    font = _load_font(font_size, font_path=font_path)

    # Wrap: estimate characters per line based on font size and image width
    max_chars = max(12, int(w / (font_size * 0.55)))
    lines = textwrap.wrap(caption, width=max_chars)
    text = "\n".join(lines)

    bbox = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        align="center",
        stroke_width=stroke,
    )
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    x = (w - tw) // 2
    y = h - th - int(0.06 * h)

    draw.multiline_text(
        (x, y),
        text,
        font=font,
        fill="white",
        align="center",
        stroke_width=stroke,
        stroke_fill="black",
    )

    img.save(out_path, "PNG")
