#!/usr/bin/env python3

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "catalog"
OUTPUT_PNG = OUTPUT_DIR / "Prime-Variable-Covers-Poster.png"
OUTPUT_PDF = OUTPUT_DIR / "Prime-Variable-Covers-Catalog.pdf"

CANVAS_W = 3200
CANVAS_H = 2200

BG = "#F3F7FF"
GRID = "#DFE9FB"
BLUE = "#0F4FB3"
BLUE_DARK = "#0A2F76"
BLUE_MID = "#2F6FD4"
BLUE_LIGHT = "#5FA5FF"
TEXT = "#0E2858"
WHITE = "#FFFFFF"
MUTED = "#DCEAFF"

LOGO_PATH = ROOT / "images/PRIME VARIABLE.PNG.1.-06 (1).png"
DAM_HERO_PATH = ROOT / "images/1.png"

PRODUCTS = [
    {
        "title": "DAM LINERS",
        "image": ROOT / "images/products/damliner.webp",
        "badge": "FLAGSHIP PRODUCT",
        "desc": "Waterproof, durable liners for reservoirs, ponds, and bulk water storage.",
        "extra": ["0.3 MM", "0.5 MM", "0.75 MM", "1.00 MM"],
    },
    {
        "title": "SHADE NETS",
        "image": ROOT / "images/products/images-3shadenet.jpg",
        "badge": "CROP PROTECTION",
        "desc": "Controls heat and sunlight while protecting horticultural crops.",
    },
    {
        "title": "GREENHOUSES",
        "image": ROOT / "images/products/greenhouse.jpg",
        "badge": "PROTECTED FARMING",
        "desc": "Custom greenhouse systems designed to improve yield and crop consistency.",
    },
    {
        "title": "DRIP LINES",
        "image": ROOT / "images/products/irrigation-sys-600x368.jpg",
        "badge": "WATER EFFICIENCY",
        "desc": "Precision irrigation for cleaner water delivery and stronger field performance.",
    },
]


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


FONT_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def fit_crop(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    img = image.convert("RGB")
    src_ratio = img.width / img.height
    dst_ratio = size[0] / size[1]
    if src_ratio > dst_ratio:
        new_h = size[1]
        new_w = int(new_h * src_ratio)
    else:
        new_w = size[0]
        new_h = int(new_w / src_ratio)
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - size[0]) // 2
    top = (new_h - size[1]) // 2
    return img.crop((left, top, left + size[0], top + size[1]))


def paste_rounded(base: Image.Image, image: Image.Image, box: tuple[int, int, int, int], radius: int):
    x1, y1, x2, y2 = box
    panel = fit_crop(image, (x2 - x1, y2 - y1))
    mask = rounded_mask((x2 - x1, y2 - y1), radius)
    base.paste(panel, (x1, y1), mask)


def add_shadow(base: Image.Image, box: tuple[int, int, int, int], radius: int = 36, offset: tuple[int, int] = (14, 14)):
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    x1, y1, x2, y2 = box
    dx, dy = offset
    draw.rounded_rectangle((x1 + dx, y1 + dy, x2 + dx, y2 + dy), radius=radius, fill=(23, 67, 148, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    base.alpha_composite(shadow)


def draw_grid(draw: ImageDraw.ImageDraw):
    step = 380
    for x in range(110, CANVAS_W, step):
        draw.line((x, 0, x, CANVAS_H), fill=GRID, width=18)
    for y in range(70, CANVAS_H, step):
        draw.line((0, y, CANVAS_W, y), fill=GRID, width=18)


def draw_badge(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fill: str, text_fill: str = WHITE):
    font = load_font(FONT_BOLD, 32)
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0] + 44
    h = 58
    draw.rounded_rectangle((x, y, x + w, y + h), radius=28, fill=fill)
    draw.text((x + 22, y + 11), text, font=font, fill=text_fill)
    return w


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_paragraph(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font: ImageFont.FreeTypeFont, fill: str, max_width: int, line_gap: int):
    yy = y
    for line in wrap_text(draw, text, font, max_width):
        draw.text((x, yy), line, font=font, fill=fill)
        yy += font.size + line_gap


def make_card(base: Image.Image, draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, product: dict):
    add_shadow(base, (x, y, x + w, y + h), radius=42)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=42, fill=WHITE, outline="#C7D9FA", width=4)

    image_h = 250 if h >= 500 else 220
    image_box = (x + 24, y + 24, x + w - 24, y + image_h)
    draw.rounded_rectangle(image_box, radius=30, fill="#E5F0FF")
    paste_rounded(base, Image.open(product["image"]), image_box, 30)

    draw_badge(draw, x + 30, y + image_h + 24, product["badge"], BLUE)
    if w >= 800:
        title_size = 66 if len(product["title"]) < 12 else 58
        desc_size = 34
        line_gap = 10
        title_y = y + image_h + 102
    else:
        title_size = 44 if len(product["title"]) < 12 else 38
        desc_size = 23
        line_gap = 6
        title_y = y + image_h + 94
    title_font = load_font(FONT_BLACK, title_size)
    desc_font = load_font(FONT_REG, desc_size)
    draw.text((x + 30, title_y), product["title"], font=title_font, fill=TEXT)
    draw_paragraph(draw, x + 30, title_y + (72 if w >= 800 else 58), product["desc"], desc_font, "#35507E", w - 60, line_gap)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    base = Image.new("RGBA", (CANVAS_W, CANVAS_H), BG)
    draw = ImageDraw.Draw(base)
    draw_grid(draw)

    # Soft geometric background similar to the reference poster
    draw.polygon([(1060, 70), (1840, 180), (2240, 0), (3200, 0), (3200, 580), (2140, 470)], fill="#EDF3FF")
    draw.polygon([(0, 1420), (530, 1100), (920, 1380), (650, 2200), (0, 2200)], fill="#EEF5FF")

    # Left hero image area
    hero_box = (0, 0, 1720, 2200)
    hero = fit_crop(Image.open(DAM_HERO_PATH), (hero_box[2], hero_box[3]))
    base.paste(hero, (hero_box[0], hero_box[1]))

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.polygon([(1400, 0), (1730, 0), (1480, 2200), (1150, 2200)], fill=(27, 84, 182, 210))
    overlay_draw.polygon([(1325, 0), (1455, 0), (1225, 2200), (1090, 2200)], fill=(106, 170, 255, 110))
    overlay_draw.rectangle((0, 1820, 3200, 2200), fill=(7, 35, 87, 160))
    base.alpha_composite(overlay)

    # Right blue poster panel
    draw.rounded_rectangle((1700, 0, 3200, 2200), radius=0, fill=BLUE)

    # Logo and heading
    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo.thumbnail((520, 250), Image.Resampling.LANCZOS)
        base.alpha_composite(logo, (2550, 30))

    big_font = load_font(FONT_BLACK, 150)
    sale_font = load_font(FONT_BLACK, 108)
    label_font = load_font(FONT_BOLD, 34)
    small_font = load_font(FONT_REG, 34)
    gauge_font = load_font(FONT_BLACK, 72)
    call_font = load_font(FONT_BLACK, 70)

    draw.text((2010, 290), "4 CORE", font=big_font, fill=WHITE)
    draw.text((2010, 430), "PRODUCTS", font=big_font, fill=WHITE)
    draw.text((2010, 610), "POSTER", font=sale_font, fill=MUTED)
    draw.text((2010, 748), "DAM LINERS | SHADE NETS", font=label_font, fill=MUTED)
    draw.text((2010, 798), "GREENHOUSES | DRIP LINES", font=label_font, fill=MUTED)

    draw.text((2060, 905), "Dam liner gauges", font=label_font, fill=WHITE)
    draw.text((2060, 970), "0.3 MM", font=gauge_font, fill=WHITE)
    draw.text((2480, 970), "0.5 MM", font=gauge_font, fill=WHITE)
    draw.text((2060, 1075), "0.75 MM", font=gauge_font, fill=WHITE)
    draw.text((2480, 1075), "1.00 MM", font=gauge_font, fill=WHITE)

    # Product cards
    cards = [
        (90, 1260, 730, 560, PRODUCTS[0]),
        (860, 1260, 730, 560, PRODUCTS[1]),
        (1630, 1260, 730, 560, PRODUCTS[2]),
        (2400, 1260, 710, 560, PRODUCTS[3]),
    ]
    for x, y, w, h, product in cards:
        make_card(base, draw, x, y, w, h, product)

    # Contact bar
    draw.rounded_rectangle((90, 1920, 3110, 2140), radius=80, fill=BLUE_DARK)
    draw.ellipse((140, 1962, 286, 2108), fill=WHITE)
    draw.rectangle((176, 1998, 250, 2072), fill=BLUE_DARK)
    draw.text((340, 1968), "CALL TODAY", font=call_font, fill=WHITE)
    draw.text((340, 2050), "0114 040 802   |   0722 607 359", font=load_font(FONT_BLACK, 54), fill=WHITE)
    draw.text((2160, 2048), "primevariablecovers.com", font=load_font(FONT_REG, 52), fill=MUTED)

    # Bottom line on left side
    draw.text((90, 1180), "Smart water solutions for modern farming.", font=load_font(FONT_BOLD, 44), fill=WHITE)

    poster = base.convert("RGB")
    poster.save(OUTPUT_PNG, quality=95)
    poster.save(OUTPUT_PDF, resolution=300.0)
    print(f"Created {OUTPUT_PNG}")
    print(f"Created {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
