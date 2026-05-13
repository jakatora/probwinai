"""Generate App Store screenshots (1290x2796 - iPhone 6.7") for ProbWin AI.
Renderuje 4 mockupy na bazie prawdziwych danych z docs/data/top10.json
oraz przykladowego match insight.

Run: py -3.12 mobile/scripts/generate_screenshots.py
Output: mobile/store_assets/screenshots/ios_67/*.png
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs" / "data" / "top10.json"
OUT = ROOT / "mobile" / "store_assets" / "screenshots" / "ios_67"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1290, 2796

BG = (15, 20, 25)
PANEL = (24, 32, 41)
PANEL_HI = (32, 42, 53)
BORDER = (45, 58, 71)
ACCENT = (96, 165, 250)
ACCENT2 = (74, 222, 128)
DANGER = (248, 113, 113)
TEXT = (230, 237, 243)
TEXT_DIM = (155, 167, 178)
TEXT_FAINT = (107, 119, 130)


def font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\seguibl.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def draw_status_bar(d, time_text="9:41"):
    # iOS-like status bar
    d.text((60, 30), time_text, fill=TEXT, font=font(36, bold=True))
    # right side: signal + battery indicators (simplified)
    bx = W - 220
    d.text((bx, 30), "100%", fill=TEXT, font=font(32))
    # battery rect
    d.rounded_rectangle((bx + 130, 38, bx + 200, 70), radius=6, outline=TEXT, width=2)
    d.rounded_rectangle((bx + 134, 42, bx + 196, 66), radius=4, fill=TEXT)


def draw_app_bar(d, title, subtitle=None, back=False):
    y = 130
    if back:
        d.text((50, y + 10), "<", fill=ACCENT, font=font(64, bold=True))
        x_title = 110
    else:
        x_title = 50
    d.text((x_title, y), title, fill=TEXT, font=font(56, bold=True))
    if subtitle:
        d.text((x_title, y + 80), subtitle, fill=TEXT_DIM, font=font(32))


def card(d, x, y, w, h, hi=False):
    d.rounded_rectangle((x, y, x + w, y + h), radius=20,
                         fill=PANEL_HI if hi else PANEL, outline=BORDER, width=2)


def prob_from_odds(o):
    if not o:
        return None
    inv = [1/x for x in o]
    s = sum(inv)
    return [round(100 * v / s) for v in inv]


def screenshot_home():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_status_bar(d)
    draw_app_bar(d, "ProbWin AI", "Top 10 mecz\u00f3w \u2022 13 maja")

    matches = json.loads(DATA.read_text(encoding="utf-8"))["matches"][:6]
    y = 320
    for m in matches:
        x, w, h = 50, W - 100, 200
        card(d, x, y, w, h)
        # League badge
        d.text((x + 30, y + 24), m["league"].upper(), fill=ACCENT, font=font(24, bold=True))
        # Teams
        d.text((x + 30, y + 64), m["home_team"], fill=TEXT, font=font(40, bold=True))
        d.text((x + 30, y + 110), "vs " + m["away_team"], fill=TEXT_DIM, font=font(34))
        # Probabilities (small bars)
        odds = m["odds"]
        probs = prob_from_odds([odds["home"], odds["draw"], odds["away"]])
        bx = x + w - 360
        for i, (p, c) in enumerate(zip(probs, [ACCENT, TEXT_DIM, DANGER])):
            d.rounded_rectangle((bx + i*120, y + 70, bx + i*120 + 100, y + 130),
                                 radius=8, fill=c)
            d.text((bx + i*120 + 18, y + 80), f"{p}%", fill=BG, font=font(32, bold=True))
        # Labels under bars
        for i, lab in enumerate(["1", "X", "2"]):
            d.text((bx + i*120 + 42, y + 140), lab, fill=TEXT_DIM, font=font(28, bold=True))
        y += 220

    # Bottom hint
    d.text((50, H - 130), "Dotknij meczu, by zobaczy\u0107 analiz\u0119 AI",
           fill=TEXT_FAINT, font=font(28))
    return img


def screenshot_match_probs():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_status_bar(d)
    draw_app_bar(d, "Real Madrid", "vs Barcelona \u2022 La Liga", back=True)

    # Big probability card
    y = 360
    card(d, 50, y, W - 100, 540, hi=True)
    d.text((90, y + 30), "Prawdopodobie\u0144stwa", fill=TEXT_DIM, font=font(32, bold=True))
    # Three big circles
    cy = y + 200
    cols = [("1", 38, ACCENT, "Real Madrid"),
            ("X", 22, TEXT_DIM, "Remis"),
            ("2", 40, DANGER, "Barcelona")]
    for i, (label, pct, color, name) in enumerate(cols):
        cx = 200 + i * 320
        d.ellipse((cx - 110, cy - 110, cx + 110, cy + 110), fill=color)
        # White inner ring
        d.ellipse((cx - 95, cy - 95, cx + 95, cy + 95), fill=BG)
        # Pct text
        txt = f"{pct}%"
        bbox = d.textbbox((0, 0), txt, font=font(56, bold=True))
        tw = bbox[2] - bbox[0]
        d.text((cx - tw // 2, cy - 40), txt, fill=color, font=font(56, bold=True))
        d.text((cx - 30, cy + 130), label, fill=TEXT_DIM, font=font(36, bold=True))
        nb = d.textbbox((0, 0), name, font=font(26))
        nw = nb[2] - nb[0]
        d.text((cx - nw // 2, cy + 180), name, fill=TEXT, font=font(26))

    # Odds row
    y = 960
    card(d, 50, y, W - 100, 200)
    d.text((90, y + 30), "Kursy bukmachera", fill=TEXT_DIM, font=font(32, bold=True))
    odds = [("1", "2.20"), ("X", "3.60"), ("2", "3.10")]
    for i, (lab, val) in enumerate(odds):
        x = 150 + i * 380
        d.text((x, y + 90), lab, fill=TEXT_DIM, font=font(40, bold=True))
        d.text((x + 70, y + 80), val, fill=TEXT, font=font(60, bold=True))
    d.text((90, y + 165), "\u017ar\u00f3d\u0142o: Betclic", fill=TEXT_FAINT, font=font(24))

    # Extra markets
    y = 1220
    for label, ph, pa in [("Obie dru\u017cyny strzel\u0105 (BTTS)", 64, 36),
                          ("Powy\u017cej 2.5 goli", 58, 42),
                          ("Powy\u017cej 1.5 goli", 82, 18)]:
        card(d, 50, y, W - 100, 150)
        d.text((90, y + 30), label, fill=TEXT, font=font(32, bold=True))
        # Mini bar
        bar_x, bar_y, bar_w = 90, y + 90, W - 280
        d.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + 30),
                             radius=15, fill=PANEL_HI)
        d.rounded_rectangle((bar_x, bar_y, bar_x + int(bar_w * ph / 100), bar_y + 30),
                             radius=15, fill=ACCENT2)
        d.text((bar_x + bar_w + 30, bar_y - 5), f"{ph}%", fill=ACCENT2, font=font(36, bold=True))
        y += 170

    return img


def screenshot_ai_commentary():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_status_bar(d)
    draw_app_bar(d, "Bayern \u2014 Dortmund", "Bundesliga \u2022 Der Klassiker", back=True)

    y = 360
    # AI badge
    card(d, 50, y, W - 100, 100, hi=True)
    d.ellipse((80, y + 25, 130, y + 75), fill=ACCENT2)
    d.text((90, y + 28), "AI", fill=BG, font=font(28, bold=True))
    d.text((160, y + 28), "Analiza AI", fill=TEXT, font=font(40, bold=True))

    y = 500
    # Big text card
    card(d, 50, y, W - 100, 1700)
    text = (
        "Bayern wraca po mocnym wyjazdowym zwyci\u0119stwie 3:1 z Lipskiem\n"
        "i strzeli\u0142 w ostatnich 5 meczach \u015brednio 2.6 gola na mecz.\n"
        "Forma w lidze (W-W-W-D-W) sugeruje \u017ce gospodarze startuj\u0105\n"
        "jako wyra\u017any faworyt.\n\n"
        "Dortmund jednak zmieni\u0142 trenera 3 tygodnie temu i od tamtej\n"
        "pory ma bilans 2W-2D, w tym remis 2:2 na Allianz Arena w 2024.\n"
        "Czarno-\u017c\u00f3\u0142ci notuj\u0105 BTTS w 7 z ostatnich 8 spotka\u0144.\n\n"
        "KLUCZOWE LICZBY:\n"
        "\u2022 Bayern xG dom: 2.1 \u2022 Dortmund xGA wyj.: 1.8\n"
        "\u2022 Ostatnie 5 H2H: 3W Bayern, 1D, 1W Dortmund\n"
        "\u2022 Kontuzje: brak kluczowych zawodnik\u00f3w po obu stronach\n\n"
        "Implikowane prawdopodobie\u0144stwo gospodarzy 57% jest\n"
        "zgodne z mark\u0105 modelu xG (55-60%). Rynek BTTS\n"
        "@ 1.65 wygl\u0105da statystycznie atrakcyjnie wzgl\u0119dem 64%\n"
        "trafienia w ostatnich starciach.\n\n"
        "UWAGA: To analiza informacyjna, nie porada bukmacherska."
    )
    yt = y + 50
    for line in text.split("\n"):
        is_header = "KLUCZOWE LICZBY" in line or "UWAGA" in line
        clr = ACCENT2 if "KLUCZOWE" in line else (TEXT_FAINT if "UWAGA" in line else TEXT_DIM)
        f = font(28, bold=is_header)
        d.text((90, yt), line, fill=clr, font=f)
        yt += 50

    return img


def screenshot_welcome():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_status_bar(d)

    # Center icon
    from generate_icon import make_icon
    icon = make_icon(360, transparent_bg=True, with_text=True)
    img.paste(icon, ((W - 360) // 2, 280), icon)

    # Title
    title = "ProbWin AI"
    bbox = d.textbbox((0, 0), title, font=font(96, bold=True))
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2 - bbox[0], 720), title, fill=TEXT, font=font(96, bold=True))

    sub = "Statystyki + AI komentarz"
    sb = d.textbbox((0, 0), sub, font=font(40))
    sw = sb[2] - sb[0]
    d.text(((W - sw) // 2 - sb[0], 850), sub, fill=TEXT_DIM, font=font(40))

    # Disclaimer card
    y = 1050
    card(d, 80, y, W - 160, 900, hi=True)
    d.text((130, y + 50), "Aplikacja informacyjna",
           fill=ACCENT2, font=font(40, bold=True))

    bullets = [
        "Top 10 mecz\u00f3w dnia z lig europejskich",
        "Prawdopodobie\u0144stwa wyliczone z kurs\u00f3w",
        "Komentarz AI dla ka\u017cdego spotkania",
        "Aktualizacja codziennie o 8:00",
        "",
        "CZEGO TU NIE MA:",
        "Brak mo\u017cliwo\u015bci obstawiania",
        "Brak typowania pewniak\u00f3w",
        "Brak rejestracji konta",
    ]
    yt = y + 130
    for line in bullets:
        if not line:
            yt += 30
            continue
        is_header = line.endswith(":")
        if is_header:
            d.text((130, yt), line, fill=DANGER, font=font(32, bold=True))
        else:
            d.text((130, yt), "\u2022 " + line, fill=TEXT, font=font(32))
        yt += 60

    # Accept button
    by = 2050
    d.rounded_rectangle((150, by, W - 150, by + 140), radius=70, fill=ACCENT)
    txt = "Rozumiem, dalej"
    bbox = d.textbbox((0, 0), txt, font=font(44, bold=True))
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2 - bbox[0], by + 38), txt, fill=BG, font=font(44, bold=True))

    d.text((100, 2400), "Maj\u0105c 18+ akceptujesz polityk\u0119 prywatno\u015bci",
           fill=TEXT_FAINT, font=font(26))

    return img


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))

    shots = [
        ("01_home.png", screenshot_home),
        ("02_match_probabilities.png", screenshot_match_probs),
        ("03_ai_commentary.png", screenshot_ai_commentary),
        ("04_welcome.png", screenshot_welcome),
    ]
    for name, fn in shots:
        img = fn()
        out = OUT / name
        img.save(out, "PNG")
        print(f"Wrote {out}")
