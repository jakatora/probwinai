"""Generate ProbWin AI app icon + foreground + splash from scratch via PIL.
Run: py -3.12 mobile/scripts/generate_icon.py
Outputs to mobile/assets/
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

BG = (15, 20, 25)        # #0F1419
PANEL = (24, 32, 41)
ACCENT = (96, 165, 250)  # blue
ACCENT2 = (74, 222, 128) # green
TEXT = (230, 237, 243)


def rounded_rect(draw, xy, radius, fill):
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def find_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\seguibl.ttf" if bold else r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def make_icon(size=1024, transparent_bg=False, with_text=True):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0) if transparent_bg else BG + (255,))
    d = ImageDraw.Draw(img)
    if not transparent_bg:
        # rounded background already filled; replace with rounded mask
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), radius=int(size*0.234), fill=255)
        bg = Image.new("RGBA", (size, size), BG + (255,))
        img = Image.composite(bg, Image.new("RGBA", (size, size), (0, 0, 0, 0)), mask)
        d = ImageDraw.Draw(img)

    # 3 ascending probability bars
    bar_w = int(size * 0.156)
    gap = int(size * 0.078)
    total_w = bar_w * 3 + gap * 2
    x0 = (size - total_w) // 2
    y_base = int(size * 0.62)
    heights = [int(size * 0.20), int(size * 0.34), int(size * 0.46)]
    colors = [ACCENT, ACCENT2, ACCENT]
    for i, (h, c) in enumerate(zip(heights, colors)):
        x = x0 + i * (bar_w + gap)
        y = y_base - h
        rounded_rect(d, (x, y, x + bar_w, y_base), radius=int(size*0.02), fill=c + (255,))

    if with_text:
        font = find_font(int(size * 0.18), bold=True)
        text = "P"
        bbox = d.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        d.text(((size - tw) // 2 - bbox[0], int(size * 0.72) - bbox[1]),
               text, fill=TEXT + (255,), font=font)

    return img


def make_splash(width=1242, height=2688):
    img = Image.new("RGBA", (width, height), BG + (255,))
    d = ImageDraw.Draw(img)
    # Centered icon-like graphic
    icon_size = int(min(width, height) * 0.36)
    icon = make_icon(icon_size, transparent_bg=True, with_text=True)
    img.paste(icon, ((width - icon_size) // 2, (height - icon_size) // 2 - int(height*0.04)), icon)
    # Title
    font = find_font(int(width * 0.078), bold=True)
    title = "ProbWin AI"
    bbox = d.textbbox((0, 0), title, font=font)
    tw = bbox[2] - bbox[0]
    d.text(((width - tw) // 2 - bbox[0], int(height * 0.72)), title, fill=TEXT + (255,), font=font)
    sub_font = find_font(int(width * 0.034))
    sub = "Statystyki + AI"
    sb = d.textbbox((0, 0), sub, font=sub_font)
    sw = sb[2] - sb[0]
    d.text(((width - sw) // 2 - sb[0], int(height * 0.78)), sub, fill=(155, 167, 178, 255), font=sub_font)
    return img


if __name__ == "__main__":
    icon = make_icon(1024)
    icon.save(ASSETS / "icon.png")
    print(f"Wrote {ASSETS / 'icon.png'}")

    fg = make_icon(1024, transparent_bg=True, with_text=True)
    fg.save(ASSETS / "icon_foreground.png")
    print(f"Wrote {ASSETS / 'icon_foreground.png'}")

    splash = make_splash()
    splash.save(ASSETS / "splash.png")
    print(f"Wrote {ASSETS / 'splash.png'}")
