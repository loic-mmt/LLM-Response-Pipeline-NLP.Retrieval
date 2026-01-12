from PIL import Image, ImageDraw, ImageFont
import textwrap

def draw_bottom_caption(img_path: str, caption: str, out_path: str, font_size=52, stroke=4):
    img = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size

    font = ImageFont.load_default()

    max_chars = max(14, int(w / (font_size * 0.55)))
    lines = textwrap.wrap(caption, width=max_chars)
    text = "\n".join(lines)

    bbox = draw.multiline_textbbox((0, 0) , text, font=font, align="center", stroke_width=stroke)
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
