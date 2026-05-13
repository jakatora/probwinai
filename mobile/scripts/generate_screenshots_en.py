"""Generate 8 App Store screenshots (1284x2778 - 6.5" iPhone) for ProbWin AI.
English text with captions/marketing headlines on top of mockup screens.

Run: py -3.12 mobile/scripts/generate_screenshots_en.py
Output: mobile/store_assets/screenshots/ios_65/01..08.png
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs" / "data" / "top10.json"
OUT = ROOT / "mobile" / "store_assets" / "screenshots" / "ios_65"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1284, 2778

BG = (15, 20, 25)
PANEL = (24, 32, 41)
PANEL_HI = (32, 42, 53)
BORDER = (45, 58, 71)
ACCENT = (96, 165, 250)
ACCENT2 = (74, 222, 128)
DANGER = (248, 113, 113)
WARN = (251, 191, 36)
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


def caption(d, line1, line2=None, line1_color=TEXT, line2_color=ACCENT2):
    """Marketing caption banda at top - 380px high."""
    d.rectangle((0, 0, W, 380), fill=BG)
    f1 = font(78, bold=True)
    bbox = d.textbbox((0, 0), line1, font=f1)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2 - bbox[0], 90), line1, fill=line1_color, font=f1)
    if line2:
        f2 = font(46, bold=True)
        bbox = d.textbbox((0, 0), line2, font=f2)
        tw = bbox[2] - bbox[0]
        d.text(((W - tw) // 2 - bbox[0], 200), line2, fill=line2_color, font=f2)
    # Divider
    d.rectangle((W // 2 - 60, 290, W // 2 + 60, 296), fill=line2_color)


def draw_status_bar(d, top=410):
    d.text((60, top - 30), "9:41", fill=TEXT, font=font(36, bold=True))
    bx = W - 220
    d.text((bx, top - 30), "100%", fill=TEXT, font=font(32))
    d.rounded_rectangle((bx + 130, top - 22, bx + 200, top + 10), radius=6, outline=TEXT, width=2)
    d.rounded_rectangle((bx + 134, top - 18, bx + 196, top + 6), radius=4, fill=TEXT)


def card(d, x, y, w, h, hi=False):
    d.rounded_rectangle((x, y, x + w, y + h), radius=20,
                        fill=PANEL_HI if hi else PANEL, outline=BORDER, width=2)


def prob_from_odds(o):
    if not o:
        return None
    inv = [1 / x for x in o]
    s = sum(inv)
    return [round(100 * v / s) for v in inv]


def base_canvas(caption_l1, caption_l2):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    caption(d, caption_l1, caption_l2)
    # Phone frame area starts at y=420
    return img, d


def shot_home():
    img, d = base_canvas("Top 10 Matches Daily", "Smart picks from European leagues")
    draw_status_bar(d, top=410)

    # App bar
    d.text((60, 460), "ProbWin AI", fill=TEXT, font=font(56, bold=True))
    d.text((60, 540), "Top matches • May 14", fill=TEXT_DIM, font=font(32))

    matches = json.loads(DATA.read_text(encoding="utf-8"))["matches"][:6]
    y = 660
    for m in matches:
        x, w, h = 50, W - 100, 190
        card(d, x, y, w, h)
        d.text((x + 30, y + 24), m["league"].upper(), fill=ACCENT, font=font(22, bold=True))
        d.text((x + 30, y + 60), m["home_team"], fill=TEXT, font=font(38, bold=True))
        d.text((x + 30, y + 105), "vs " + m["away_team"], fill=TEXT_DIM, font=font(32))
        odds = m["odds"]
        probs = prob_from_odds([odds["home"], odds["draw"], odds["away"]])
        bx = x + w - 360
        for i, (p, c) in enumerate(zip(probs, [ACCENT, TEXT_DIM, DANGER])):
            d.rounded_rectangle((bx + i * 120, y + 68, bx + i * 120 + 100, y + 124),
                                radius=8, fill=c)
            d.text((bx + i * 120 + 16, y + 78), f"{p}%", fill=BG, font=font(30, bold=True))
        for i, lab in enumerate(["1", "X", "2"]):
            d.text((bx + i * 120 + 42, y + 132), lab, fill=TEXT_DIM, font=font(26, bold=True))
        y += 210
    return img


def shot_probs():
    img, d = base_canvas("AI-powered Probabilities", "Beyond raw bookmaker odds")
    draw_status_bar(d, top=410)
    d.text((60, 460), "< Real Madrid", fill=ACCENT, font=font(50, bold=True))
    d.text((60, 530), "vs Barcelona • La Liga", fill=TEXT_DIM, font=font(32))

    y = 640
    card(d, 50, y, W - 100, 540, hi=True)
    d.text((90, y + 30), "Win Probability", fill=TEXT_DIM, font=font(32, bold=True))
    cy = y + 220
    cols = [("1", 38, ACCENT, "Real Madrid"), ("X", 22, TEXT_DIM, "Draw"), ("2", 40, DANGER, "Barcelona")]
    for i, (label, pct, color, name) in enumerate(cols):
        cx = 195 + i * 320
        d.ellipse((cx - 110, cy - 110, cx + 110, cy + 110), fill=color)
        d.ellipse((cx - 95, cy - 95, cx + 95, cy + 95), fill=BG)
        txt = f"{pct}%"
        bbox = d.textbbox((0, 0), txt, font=font(52, bold=True))
        tw = bbox[2] - bbox[0]
        d.text((cx - tw // 2, cy - 38), txt, fill=color, font=font(52, bold=True))
        d.text((cx - 20, cy + 130), label, fill=TEXT_DIM, font=font(36, bold=True))
        nb = d.textbbox((0, 0), name, font=font(24))
        nw = nb[2] - nb[0]
        d.text((cx - nw // 2, cy + 178), name, fill=TEXT, font=font(24))

    y = 1240
    card(d, 50, y, W - 100, 180)
    d.text((90, y + 28), "Bookmaker odds", fill=TEXT_DIM, font=font(28, bold=True))
    for i, (lab, val) in enumerate([("1", "2.20"), ("X", "3.60"), ("2", "3.10")]):
        x = 130 + i * 380
        d.text((x, y + 84), lab, fill=TEXT_DIM, font=font(38, bold=True))
        d.text((x + 70, y + 74), val, fill=TEXT, font=font(58, bold=True))

    y = 1470
    for label, ph in [("Both teams to score (BTTS)", 64),
                      ("Over 2.5 goals", 58),
                      ("Over 1.5 goals", 82)]:
        card(d, 50, y, W - 100, 140)
        d.text((90, y + 26), label, fill=TEXT, font=font(28, bold=True))
        bar_x, bar_y, bar_w = 90, y + 82, W - 280
        d.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + 26), radius=13, fill=PANEL_HI)
        d.rounded_rectangle((bar_x, bar_y, bar_x + int(bar_w * ph / 100), bar_y + 26), radius=13, fill=ACCENT2)
        d.text((bar_x + bar_w + 30, bar_y - 5), f"{ph}%", fill=ACCENT2, font=font(32, bold=True))
        y += 160
    return img


def shot_ai():
    img, d = base_canvas("AI Match Analysis", "Trained on form, H2H, lineups")
    draw_status_bar(d, top=410)
    d.text((60, 460), "< Bayern — Dortmund", fill=ACCENT, font=font(46, bold=True))
    d.text((60, 530), "Bundesliga • Der Klassiker", fill=TEXT_DIM, font=font(30))

    y = 640
    card(d, 50, y, W - 100, 100, hi=True)
    d.ellipse((80, y + 25, 130, y + 75), fill=ACCENT2)
    d.text((90, y + 28), "AI", fill=BG, font=font(26, bold=True))
    d.text((160, y + 28), "AI Commentary", fill=TEXT, font=font(38, bold=True))

    y = 780
    card(d, 50, y, W - 100, 1750)
    text = (
        "Bayern returns after a strong 3:1 away win over Leipzig\n"
        "and is averaging 2.6 goals per match across the last 5\n"
        "fixtures. With W-W-W-D-W form in the league, Munich\n"
        "starts as the clear favorite at home.\n\n"
        "Dortmund, however, switched coaches 3 weeks ago and\n"
        "has since posted 2W-2D, including a 2:2 draw at\n"
        "Allianz Arena in 2024. Schwarzgelben have hit BTTS in\n"
        "7 of their last 8 matches.\n\n"
        "KEY NUMBERS\n"
        "• Bayern home xG: 2.1 • Dortmund away xGA: 1.8\n"
        "• Last 5 H2H: 3W Bayern, 1D, 1W Dortmund\n"
        "• Injuries: no key absences either side\n\n"
        "The 57% implied probability for the home side aligns\n"
        "with our xG-based model (55-60%). The BTTS market\n"
        "at 1.65 looks statistically appealing relative to the 64%\n"
        "hit-rate in recent encounters.\n\n"
        "Note: This is an informational analysis, not betting\n"
        "advice."
    )
    yt = y + 50
    for line in text.split("\n"):
        is_header = "KEY NUMBERS" in line or line.startswith("Note:")
        clr = ACCENT2 if "KEY" in line else (TEXT_FAINT if line.startswith("Note") else TEXT_DIM)
        f = font(26, bold=is_header)
        d.text((90, yt), line, fill=clr, font=f)
        yt += 46
    return img


def shot_form():
    img, d = base_canvas("Track Recent Form", "Quick visual indicators")
    draw_status_bar(d, top=410)
    d.text((60, 460), "< Liverpool", fill=ACCENT, font=font(50, bold=True))
    d.text((60, 530), "vs Manchester United • PL", fill=TEXT_DIM, font=font(30))

    # Two team cards
    y = 660
    for team_name, results, goals, color in [
        ("Liverpool", ["W", "W", "D", "W", "L", "W", "W", "D"], "Goals: 18-7", ACCENT2),
        ("Manchester United", ["L", "W", "D", "L", "D", "W", "L", "L"], "Goals: 8-12", DANGER),
    ]:
        card(d, 50, y, W - 100, 360)
        d.text((90, y + 30), team_name, fill=TEXT, font=font(40, bold=True))
        d.text((90, y + 84), "Last 8 league matches", fill=TEXT_DIM, font=font(26))

        # Form indicators (squares with W/D/L)
        sx = 90
        for r in results:
            c = ACCENT2 if r == "W" else (WARN if r == "D" else DANGER)
            d.rounded_rectangle((sx, y + 140, sx + 110, y + 250), radius=14, fill=c)
            bbox = d.textbbox((0, 0), r, font=font(60, bold=True))
            tw = bbox[2] - bbox[0]
            d.text((sx + 55 - tw // 2 - bbox[0], y + 158), r, fill=BG, font=font(60, bold=True))
            sx += 130
        d.text((90, y + 280), goals, fill=color, font=font(28, bold=True))
        y += 380

    # H2H card
    card(d, 50, y, W - 100, 220, hi=True)
    d.text((90, y + 30), "Head-to-head (last 10)", fill=TEXT_DIM, font=font(26, bold=True))
    # Bar
    bar_x, bar_y, bar_w = 90, y + 90, W - 280
    d.rounded_rectangle((bar_x, bar_y, bar_x + int(bar_w * 0.6), bar_y + 50), radius=10, fill=ACCENT)
    d.rounded_rectangle((bar_x + int(bar_w * 0.6), bar_y, bar_x + int(bar_w * 0.8), bar_y + 50), radius=10, fill=TEXT_DIM)
    d.rounded_rectangle((bar_x + int(bar_w * 0.8), bar_y, bar_x + bar_w, bar_y + 50), radius=10, fill=DANGER)
    d.text((90, y + 150), "Liverpool 6  •  Draws 2  •  Man Utd 2", fill=TEXT, font=font(28))
    return img


def shot_favorites():
    img, d = base_canvas("Follow Your Teams", "Saved locally on your device")
    draw_status_bar(d, top=410)
    d.text((60, 460), "My Favorites", fill=TEXT, font=font(56, bold=True))
    d.text((60, 540), "3 teams • next matches", fill=TEXT_DIM, font=font(30))

    y = 660
    teams = [
        ("Liverpool", "Premier League", "vs Manchester United • today 20:00", "1.85"),
        ("Real Madrid", "La Liga", "vs Barcelona • today 22:00", "2.20"),
        ("Bayern Munich", "Bundesliga", "vs Borussia Dortmund • tomorrow", "1.75"),
    ]
    for name, league, next_match, odd in teams:
        card(d, 50, y, W - 100, 260)
        # Star
        d.text((W - 130, y + 30), "★", fill=WARN, font=font(60))
        d.text((90, y + 30), name, fill=TEXT, font=font(42, bold=True))
        d.text((90, y + 86), league, fill=ACCENT, font=font(26, bold=True))
        d.text((90, y + 130), "Next match:", fill=TEXT_DIM, font=font(24))
        d.text((90, y + 168), next_match, fill=TEXT, font=font(28))
        d.text((90, y + 210), f"Home odds: {odd}", fill=ACCENT2, font=font(26, bold=True))
        y += 280

    # Tip box
    card(d, 50, y, W - 100, 150, hi=True)
    d.text((90, y + 30), "Tip", fill=ACCENT, font=font(28, bold=True))
    d.text((90, y + 72), "Tap any team to add or remove from", fill=TEXT_DIM, font=font(26))
    d.text((90, y + 108), "favorites. We keep this list private.", fill=TEXT_DIM, font=font(26))
    return img


def shot_market_compare():
    img, d = base_canvas("Compare Bookmaker Odds", "Spot the best line in seconds")
    draw_status_bar(d, top=410)
    d.text((60, 460), "< PSG vs Marseille", fill=ACCENT, font=font(46, bold=True))
    d.text((60, 530), "Ligue 1 • Le Classique", fill=TEXT_DIM, font=font(30))

    y = 640
    card(d, 50, y, W - 100, 110, hi=True)
    d.text((90, y + 36), "Odds across 5 bookmakers", fill=TEXT, font=font(32, bold=True))

    y = 770
    bookies = [
        ("Pinnacle", "1.55", "4.40", "6.00", True),
        ("Bet365", "1.53", "4.20", "5.80", False),
        ("Betclic", "1.50", "4.30", "5.90", False),
        ("Unibet", "1.48", "4.10", "5.70", False),
        ("Bwin", "1.52", "4.25", "5.85", False),
    ]
    # Header row
    card(d, 50, y, W - 100, 80)
    headers = ["Bookmaker", "1", "X", "2"]
    cols_x = [90, 540, 760, 980]
    for h, x in zip(headers, cols_x):
        d.text((x, y + 22), h, fill=TEXT_DIM, font=font(28, bold=True))
    y += 90
    # Bookmaker rows
    for name, h, draw, a, best in bookies:
        card(d, 50, y, W - 100, 120, hi=best)
        if best:
            d.rounded_rectangle((50 + W - 100 - 200, y + 30, 50 + W - 100 - 30, y + 90),
                                 radius=10, fill=ACCENT2)
            bbox = d.textbbox((0, 0), "BEST", font=font(28, bold=True))
            tw = bbox[2] - bbox[0]
            d.text((50 + W - 100 - 115 - tw // 2, y + 42), "BEST", fill=BG, font=font(28, bold=True))
        d.text((90, y + 38), name, fill=TEXT, font=font(34, bold=True))
        for val, x in zip([h, draw, a], [540, 760, 980]):
            d.text((x, y + 38), val, fill=TEXT, font=font(36, bold=True))
        y += 140
    return img


def shot_history():
    img, d = base_canvas("Model Accuracy", "We show our track record")
    draw_status_bar(d, top=410)
    d.text((60, 460), "Past Predictions", fill=TEXT, font=font(56, bold=True))
    d.text((60, 540), "Last 30 days", fill=TEXT_DIM, font=font(30))

    # Big metric cards
    y = 660
    metrics = [
        ("Hit rate", "63%", ACCENT2),
        ("ROI", "+2.4%", ACCENT),
        ("Total", "287", TEXT_DIM),
    ]
    cw = (W - 200) // 3
    for i, (label, val, color) in enumerate(metrics):
        x = 50 + i * (cw + 25)
        card(d, x, y, cw, 240, hi=True)
        bbox = d.textbbox((0, 0), val, font=font(72, bold=True))
        tw = bbox[2] - bbox[0]
        d.text((x + cw // 2 - tw // 2, y + 60), val, fill=color, font=font(72, bold=True))
        bbox = d.textbbox((0, 0), label, font=font(28))
        tw = bbox[2] - bbox[0]
        d.text((x + cw // 2 - tw // 2, y + 160), label, fill=TEXT_DIM, font=font(28))

    # Recent predictions list
    y = 950
    d.text((60, y), "Recent results", fill=TEXT, font=font(36, bold=True))
    y += 70
    items = [
        ("Liverpool 3-1 Arsenal", "Model: 1 (68%)", True),
        ("Real Madrid 2-2 Sevilla", "Model: 1 (54%)", False),
        ("Bayern 4-0 Hertha", "Model: 1 (78%)", True),
        ("PSG 2-1 Lyon", "Model: 1 (62%)", True),
        ("Inter 1-0 Roma", "Model: 1 (51%)", True),
        ("Chelsea 0-2 Tottenham", "Model: 1 (58%)", False),
        ("Juventus 3-0 Genoa", "Model: 1 (71%)", True),
    ]
    for match, pred, hit in items:
        card(d, 50, y, W - 100, 120)
        # Hit / miss indicator
        cc = ACCENT2 if hit else DANGER
        d.ellipse((80, y + 38, 130, y + 88), fill=cc)
        sym = "✓" if hit else "✕"
        bbox = d.textbbox((0, 0), sym, font=font(36, bold=True))
        tw = bbox[2] - bbox[0]
        d.text((105 - tw // 2 - bbox[0], y + 46), sym, fill=BG, font=font(36, bold=True))
        d.text((170, y + 28), match, fill=TEXT, font=font(28, bold=True))
        d.text((170, y + 70), pred, fill=TEXT_DIM, font=font(24))
        y += 140
    return img


def shot_welcome():
    img, d = base_canvas("Built for Football Fans", "No bets. No accounts. No ads.")
    draw_status_bar(d, top=410)

    # Icon
    from generate_icon import make_icon
    icon = make_icon(360, transparent_bg=True, with_text=True)
    img.paste(icon, ((W - 360) // 2, 470), icon)

    title = "ProbWin AI"
    bbox = d.textbbox((0, 0), title, font=font(92, bold=True))
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2 - bbox[0], 880), title, fill=TEXT, font=font(92, bold=True))

    sub = "Stats + AI commentary"
    sb = d.textbbox((0, 0), sub, font=font(40))
    sw = sb[2] - sb[0]
    d.text(((W - sw) // 2 - sb[0], 1000), sub, fill=TEXT_DIM, font=font(40))

    y = 1180
    card(d, 80, y, W - 160, 900, hi=True)
    d.text((130, y + 40), "An informational tool", fill=ACCENT2, font=font(38, bold=True))

    bullets = [
        "Top 10 matches from European leagues",
        "Probabilities from real bookmaker odds",
        "AI commentary for every match",
        "Daily refresh at 8 AM local time",
        "",
        "WHAT YOU WON'T FIND HERE:",
        "No way to place bets",
        "No 'sure-win' tips",
        "No account or sign-up required",
    ]
    yt = y + 120
    for line in bullets:
        if not line:
            yt += 24
            continue
        is_header = line.endswith(":")
        if is_header:
            d.text((130, yt), line, fill=DANGER, font=font(28, bold=True))
        else:
            d.text((130, yt), "• " + line, fill=TEXT, font=font(30))
        yt += 56

    by = 2180
    d.rounded_rectangle((150, by, W - 150, by + 130), radius=65, fill=ACCENT)
    txt = "I'm 18+ — Continue"
    bbox = d.textbbox((0, 0), txt, font=font(42, bold=True))
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2 - bbox[0], by + 36), txt, fill=BG, font=font(42, bold=True))

    d.text((100, 2520), "By continuing you accept the privacy policy",
           fill=TEXT_FAINT, font=font(26))
    return img


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))

    shots = [
        ("01_home.png", shot_home),
        ("02_probabilities.png", shot_probs),
        ("03_ai_analysis.png", shot_ai),
        ("04_form_h2h.png", shot_form),
        ("05_favorites.png", shot_favorites),
        ("06_compare_odds.png", shot_market_compare),
        ("07_track_record.png", shot_history),
        ("08_welcome.png", shot_welcome),
    ]
    for name, fn in shots:
        img = fn()
        out = OUT / name
        img.save(out, "PNG")
        print(f"Wrote {out} ({img.size[0]}x{img.size[1]})")
