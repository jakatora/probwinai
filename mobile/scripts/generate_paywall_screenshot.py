"""Generate a paywall screenshot (1284x2778) for App Store Connect
subscription Review Information.

Run: py -3.12 mobile/scripts/generate_paywall_screenshot.py
Output: mobile/store_assets/paywall_review.png
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "mobile" / "store_assets" / "paywall_review.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

W, H = 1284, 2778
BG = (15, 20, 25)
PANEL = (26, 33, 42)
ACCENT = (96, 165, 250)
ACCENT2 = (74, 222, 128)
TEXT = (230, 237, 243)
TEXT_DIM = (139, 155, 171)
PRICE = "24,99 zl"


def font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\seguibl.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def centered(d, text, y, f, color):
    bbox = d.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2 - bbox[0], y), text, fill=color, font=f)


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# Status bar
d.text((60, 50), "9:41", fill=TEXT, font=font(36, bold=True))

# Premium icon (crown-ish circle)
cx, cy, r = W // 2, 320, 70
d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ACCENT, width=6)
d.text((cx - 34, cy - 48), "P", fill=ACCENT, font=font(90, bold=True))

centered(d, "Darmowy okres zakonczony", 440, font(52, bold=True), TEXT)
centered(d, "Aby dalej korzystac z ProbWin AI,", 520, font(34), TEXT_DIM)
centered(d, "wykup subskrypcje miesieczna.", 565, font(34), TEXT_DIM)

# Benefits
benefits = [
    "Top 10 meczow dnia z analiza",
    "Prawdopodobienstwa wynikow",
    "Komentarz AI dla kazdego meczu",
    "Codzienne odswiezanie danych",
]
y = 720
for b in benefits:
    d.ellipse((110, y + 4, 150, y + 44), fill=ACCENT2)
    d.text((120, y + 4), "v", fill=BG, font=font(32, bold=True))
    d.text((180, y), b, fill=TEXT, font=font(36))
    y += 90

# Plan card
card_y = 1180
d.rounded_rectangle((90, card_y, W - 90, card_y + 320), radius=24,
                    fill=PANEL, outline=ACCENT, width=3)
centered(d, "Plan miesieczny", card_y + 40, font(40, bold=True), TEXT)
centered(d, f"{PRICE} / miesiac", card_y + 110, font(56, bold=True), ACCENT)
centered(d, "Odnawia sie automatycznie.", card_y + 200, font(30), TEXT_DIM)
centered(d, "Anuluj w kazdej chwili.", card_y + 245, font(30), TEXT_DIM)

# Subscribe button
btn_y = 1580
d.rounded_rectangle((90, btn_y, W - 90, btn_y + 130), radius=20, fill=ACCENT)
centered(d, f"Subskrybuj za {PRICE} / mies.", btn_y + 38, font(42, bold=True), BG)

# Restore
centered(d, "Przywroc zakup", btn_y + 200, font(34), TEXT_DIM)

# Legal links
centered(d, "Polityka prywatnosci      Warunki korzystania",
         btn_y + 320, font(28), ACCENT)

# Disclaimer
disclaimer = [
    "Platnosc zostanie pobrana z konta App Store.",
    "Subskrypcja odnawia sie automatycznie chyba ze",
    "zostanie anulowana min. 24h przed koncem okresu.",
    "Zarzadzaj subskrypcja w ustawieniach konta App Store.",
]
y = btn_y + 420
for line in disclaimer:
    centered(d, line, y, font(26), TEXT_DIM)
    y += 42

img.save(OUT, "PNG")
print(f"Wrote {OUT} ({img.size[0]}x{img.size[1]})")
