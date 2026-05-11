"""
ProbWin AI - backtest modelu na historycznych meczach.

Pobiera mecze + kursy zamkniecia z football-data.co.uk (darmowe zrodlo),
pobiera historie Elo z Clubelo.com, symuluje stawianie zakladu
gdy model widzi edge > THRESHOLD, agreguje wyniki.

Stawka plaska: 1 jednostka na kazdy 'value bet'.
"""
import sys
import io
import csv
import time
from collections import defaultdict
from datetime import datetime, date as Date

import requests

from model import elo_to_probabilities, odds_to_implied_probabilities

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# football-data.co.uk: /mmz4281/{SS}/{LEAGUE}.csv, gdzie SS = season code (2425 = 2024-25)
FD_URL = "https://www.football-data.co.uk/mmz4281/{season}/{league}.csv"

# Konfiguracja backtestu
SEASONS = ["2324", "2425"]  # 2 ostatnie zakonczone sezony PL
LEAGUE = "E0"               # Premier League
EDGE_THRESHOLD = 0.03       # minimalny edge zeby uznac za 'value bet'
ODDS_PREFIX = "B365"        # Bet365 (mozna zamienic na BW, PS, WH itd.)

# Mapowanie nazw druzyn football-data -> Clubelo
TEAM_MAP = {
    "Aston Villa": "AstonVilla",
    "Man United": "ManUnited",
    "Man City": "ManCity",
    "Nott'm Forest": "Forest",
    "West Ham": "WestHam",
    "Crystal Palace": "CrystalPalace",
    "Sheffield United": "SheffieldUnited",
    "Newcastle": "Newcastle",
    "Wolves": "Wolves",
    "Tottenham": "Tottenham",
    "Brighton": "Brighton",
    "Brentford": "Brentford",
    "Bournemouth": "Bournemouth",
    "Fulham": "Fulham",
    "Chelsea": "Chelsea",
    "Liverpool": "Liverpool",
    "Arsenal": "Arsenal",
    "Everton": "Everton",
    "Leicester": "Leicester",
    "Ipswich": "Ipswich",
    "Southampton": "Southampton",
    "Burnley": "Burnley",
    "Luton": "Luton",
    "Leeds": "Leeds",
}

ELO_CACHE: dict[str, list[tuple[Date, Date, float]]] = {}
MISSING_TEAMS: set[str] = set()


def parse_date(s: str) -> Date:
    for fmt in ("%d/%m/%y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Nieznany format daty: {s}")


def fetch_elo_history(team_slug: str) -> list[tuple[Date, Date, float]]:
    """Pobiera pelna historie Elo z Clubelo (cachowane). Zwraca [(from, to, elo)]."""
    if team_slug in ELO_CACHE:
        return ELO_CACHE[team_slug]
    if team_slug in MISSING_TEAMS:
        return []
    url = f"http://api.clubelo.com/{team_slug}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"  ! blad Clubelo dla {team_slug}: {e}", file=sys.stderr)
        MISSING_TEAMS.add(team_slug)
        return []
    rows = []
    for row in csv.DictReader(io.StringIO(r.text)):
        try:
            rows.append((
                datetime.strptime(row["From"], "%Y-%m-%d").date(),
                datetime.strptime(row["To"], "%Y-%m-%d").date(),
                float(row["Elo"]),
            ))
        except (KeyError, ValueError):
            continue
    if not rows:
        MISSING_TEAMS.add(team_slug)
    ELO_CACHE[team_slug] = rows
    return rows


def get_elo_on(team_slug: str, on_date: Date) -> float | None:
    """Elo druzyny obowiazujace w dniu meczu (przed meczem)."""
    history = fetch_elo_history(team_slug)
    if not history:
        return None
    for from_d, to_d, elo in history:
        if from_d <= on_date <= to_d:
            return elo
    # Fallback: jesli mecz po ostatnim From-To (np. brak danych po relegacji)
    last_before = None
    for from_d, to_d, elo in history:
        if to_d < on_date:
            last_before = elo
    return last_before


def load_matches(season: str, league: str) -> list[dict]:
    url = FD_URL.format(season=season, league=league)
    print(f"  pobieranie {url}...")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    text = r.content.decode("utf-8-sig", errors="replace")
    return list(csv.DictReader(io.StringIO(text)))


def slug_for(team: str) -> str:
    if team in TEAM_MAP:
        return TEAM_MAP[team]
    return team.replace(" ", "").replace("'", "").replace("-", "")


def main():
    # ============= 1. Wczytaj mecze =============
    print("Pobieram historyczne mecze (football-data.co.uk)...")
    all_matches = []
    for season in SEASONS:
        ms = load_matches(season, LEAGUE)
        print(f"    sezon {season}: {len(ms)} meczow")
        all_matches.extend([(season, m) for m in ms])
    print(f"  Lacznie: {len(all_matches)} meczow\n")

    # ============= 2. Backtest =============
    print(f"Backtest (edge threshold = {EDGE_THRESHOLD * 100:.0f}%, kursy: {ODDS_PREFIX})...")
    bets_placed = 0
    bets_won = 0
    total_stake = 0.0
    total_return = 0.0
    skipped_no_odds = 0
    skipped_no_elo = 0

    by_outcome = defaultdict(lambda: {"bets": 0, "wins": 0, "stake": 0.0, "return": 0.0})
    by_edge_bucket = defaultdict(lambda: {"bets": 0, "wins": 0, "return": 0.0})

    t0 = time.time()
    processed = 0

    for season, m in all_matches:
        date_str = m.get("Date", "")
        home = m.get("HomeTeam", "")
        away = m.get("AwayTeam", "")
        ftr = m.get("FTR", "")  # H/D/A

        if not (date_str and home and away and ftr in ("H", "D", "A")):
            continue

        try:
            o1 = float(m[f"{ODDS_PREFIX}H"])
            ox = float(m[f"{ODDS_PREFIX}D"])
            o2 = float(m[f"{ODDS_PREFIX}A"])
        except (KeyError, ValueError):
            skipped_no_odds += 1
            continue

        try:
            match_date = parse_date(date_str)
        except ValueError:
            continue

        home_slug = slug_for(home)
        away_slug = slug_for(away)
        elo_h = get_elo_on(home_slug, match_date)
        elo_a = get_elo_on(away_slug, match_date)

        if elo_h is None or elo_a is None:
            skipped_no_elo += 1
            continue

        processed += 1
        p1, px, p2 = elo_to_probabilities(elo_h, elo_a)
        i1, ix, i2, _vig = odds_to_implied_probabilities(o1, ox, o2)

        for outcome, prob, odd, implied in (
            ("H", p1, o1, i1),
            ("D", px, ox, ix),
            ("A", p2, o2, i2),
        ):
            edge = prob - implied
            if edge < EDGE_THRESHOLD:
                continue

            bets_placed += 1
            total_stake += 1.0
            by_outcome[outcome]["bets"] += 1
            by_outcome[outcome]["stake"] += 1.0

            # Bucket edge wg wielkosci (do analizy korelacji edge vs ROI)
            bucket = f"{int(edge * 100 / 5) * 5}-{int(edge * 100 / 5) * 5 + 5}%"
            by_edge_bucket[bucket]["bets"] += 1

            if outcome == ftr:
                bets_won += 1
                total_return += odd
                by_outcome[outcome]["wins"] += 1
                by_outcome[outcome]["return"] += odd
                by_edge_bucket[bucket]["wins"] += 1
                by_edge_bucket[bucket]["return"] += odd

    elapsed = time.time() - t0

    # ============= 3. Raport =============
    print(f"\n{'=' * 72}")
    print(f"WYNIKI BACKTESTU")
    print(f"{'=' * 72}")
    print(f"Mecze przetworzone:        {processed}")
    print(f"Mecze pominiete:           {skipped_no_odds + skipped_no_elo} "
          f"(brak kursow: {skipped_no_odds}, brak Elo: {skipped_no_elo})")
    print(f"Niezmapowane druzyny:      {sorted(MISSING_TEAMS)}")
    print(f"Czas trwania:              {elapsed:.1f}s")
    print()

    if bets_placed == 0:
        print("Brak zakladow speniajacych edge threshold - nic nie zostalo postawione.")
        return

    pnl = total_return - total_stake
    roi_pct = pnl / total_stake * 100
    win_rate_pct = bets_won / bets_placed * 100

    print(f"Postawione zaklady:        {bets_placed}")
    print(f"Wygrane:                   {bets_won}")
    print(f"Hit rate:                  {win_rate_pct:.1f}%")
    print(f"Suma stawek:               {total_stake:.1f} jednostek")
    print(f"Suma wyplat:               {total_return:.2f} jednostek")
    print(f"P&L:                       {pnl:+.2f} jednostek")
    print(f"ROI:                       {roi_pct:+.1f}%")
    print()

    print(f"--- Wg wyniku (1/X/2) ---")
    for outcome, label in (("H", "1 (gospodarz)"), ("D", "X (remis)"), ("A", "2 (gosc)")):
        d = by_outcome[outcome]
        if d["bets"] == 0:
            print(f"  {label:18}: brak zakladow")
            continue
        wr = d["wins"] / d["bets"] * 100
        roi = (d["return"] - d["stake"]) / d["stake"] * 100
        print(f"  {label:18}: {d['bets']:4d} bets | hit {wr:5.1f}% | ROI {roi:+6.1f}%")

    print()
    print(f"--- Wg wielkosci edge ---")
    for bucket in sorted(by_edge_bucket.keys(), key=lambda b: int(b.split("-")[0])):
        d = by_edge_bucket[bucket]
        if d["bets"] == 0:
            continue
        wr = d["wins"] / d["bets"] * 100
        roi = (d["return"] - d["bets"]) / d["bets"] * 100
        print(f"  edge {bucket:>9}: {d['bets']:4d} bets | hit {wr:5.1f}% | ROI {roi:+6.1f}%")

    print(f"{'=' * 72}")
    print(f"INTERPRETACJA:")
    print(f"  - ROI > +5% przez 760 zakladow = silny sygnal ze model bije bukmachera")
    print(f"  - ROI -5% do +5% = model w okolicach efektywnosci (brak alpha)")
    print(f"  - ROI < -5% = model jest gorszy niz losowy obstawianie")
    print(f"  - Trend rosnacy ROI wraz z wielkoscia edge = model jest dobrze kalibrowany")
    print(f"{'=' * 72}")


if __name__ == "__main__":
    main()
