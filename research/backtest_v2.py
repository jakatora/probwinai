"""
ProbWin AI v2 - backtest z wieloma cechami i wytrenowanym klasyfikatorem.

Cechy uzywane przez model (na podstawie danych dostepnych PRZED meczem):
  * Elo druzyn (Clubelo)
  * Forma: punkty zdobyte w 5 ostatnich meczach
  * Forma dom/wyjazd osobno (gospodarz @ home, gosc @ away)
  * Gole strzelone/stracone w 5 ostatnich meczach
  * Glowa-w-glowe (H2H): wynik 5 ostatnich pojedynkow

Klasyfikator: LogisticRegression z multinomial (uczy wagi cech sam,
zamiast recznego dostrajania jak w wersji 1).

Walidacja: trenujemy na 3 sezonach (2021-24), testujemy na 1 sezonie
(2024-25) - out-of-sample, model nigdy nie widzi danych z testu.
"""
import sys
import io
import os
import json
import csv
import time
from collections import defaultdict
from datetime import datetime, date as Date

import requests
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV

from model import odds_to_implied_probabilities

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# =========================================================================
# Konfiguracja
# =========================================================================
TRAIN_SEASONS = ["2122", "2223", "2324"]
TEST_SEASONS = ["2425"]
LEAGUE = "E0"
EDGE_THRESHOLD = 0.03
ODDS_PREFIX = "B365"
ELO_CACHE_FILE = "elo_cache.json"

TEAM_MAP = {
    "Aston Villa": "AstonVilla", "Man United": "ManUnited", "Man City": "ManCity",
    "Nott'm Forest": "Forest", "West Ham": "WestHam", "Crystal Palace": "CrystalPalace",
    "Sheffield United": "SheffieldUnited", "Newcastle": "Newcastle", "Wolves": "Wolves",
    "Tottenham": "Tottenham", "Brighton": "Brighton", "Brentford": "Brentford",
    "Bournemouth": "Bournemouth", "Fulham": "Fulham", "Chelsea": "Chelsea",
    "Liverpool": "Liverpool", "Arsenal": "Arsenal", "Everton": "Everton",
    "Leicester": "Leicester", "Ipswich": "Ipswich", "Southampton": "Southampton",
    "Burnley": "Burnley", "Luton": "Luton", "Leeds": "Leeds",
    "West Brom": "WestBrom", "Watford": "Watford", "Norwich": "Norwich",
}

# =========================================================================
# Clubelo - z cache na dysku
# =========================================================================
ELO_CACHE: dict[str, list[tuple[Date, Date, float]]] = {}
MISSING_TEAMS: set[str] = set()


def slug_for(team: str) -> str:
    return TEAM_MAP.get(team, team.replace(" ", "").replace("'", "").replace("-", ""))


def load_elo_cache_from_disk():
    if not os.path.exists(ELO_CACHE_FILE):
        return
    with open(ELO_CACHE_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    for team, rows in raw.items():
        ELO_CACHE[team] = [
            (Date.fromisoformat(r["from"]), Date.fromisoformat(r["to"]), r["elo"])
            for r in rows
        ]


def save_elo_cache_to_disk():
    raw = {
        team: [{"from": f.isoformat(), "to": t.isoformat(), "elo": e}
               for (f, t, e) in rows]
        for team, rows in ELO_CACHE.items()
    }
    with open(ELO_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(raw, f)


def fetch_elo_history(team_slug: str) -> list[tuple[Date, Date, float]]:
    if team_slug in ELO_CACHE:
        return ELO_CACHE[team_slug]
    if team_slug in MISSING_TEAMS:
        return []
    url = f"http://api.clubelo.com/{team_slug}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"  ! Clubelo blad dla {team_slug}: {e}", file=sys.stderr)
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
    history = fetch_elo_history(team_slug)
    if not history:
        return None
    for from_d, to_d, elo in history:
        if from_d <= on_date <= to_d:
            return elo
    last_before = None
    for from_d, to_d, elo in history:
        if to_d < on_date:
            last_before = elo
    return last_before


# =========================================================================
# Pobieranie meczow
# =========================================================================
def load_matches(season: str) -> pd.DataFrame:
    url = f"https://www.football-data.co.uk/mmz4281/{season}/{LEAGUE}.csv"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    text = r.content.decode("utf-8-sig", errors="replace")
    df = pd.read_csv(io.StringIO(text))
    df["Season"] = season
    return df


def load_all(seasons: list[str]) -> pd.DataFrame:
    dfs = [load_matches(s) for s in seasons]
    df = pd.concat(dfs, ignore_index=True)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    return df


# =========================================================================
# Feature engineering - inkrementalnie, tylko z danych z przeszlosci
# =========================================================================
def points(was_home: bool, ftr: str) -> int:
    if was_home:
        return 3 if ftr == "H" else 1 if ftr == "D" else 0
    return 3 if ftr == "A" else 1 if ftr == "D" else 0


def build_features(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, list[int]]:
    """
    Dla kazdego meczu buduje wektor cech wylacznie z meczow ROZEGRANYCH PRZED nim.
    Zwraca (X, y, indeksy_meczow_w_df).
    """
    # Inkrementalna historia per druzyna i per para H2H
    # team_hist[team] = list of (date, was_home, gf, ga, ftr)
    team_hist: dict[str, list[tuple[Date, bool, int, int, str]]] = defaultdict(list)
    h2h_hist: dict[frozenset, list[tuple[Date, str, str]]] = defaultdict(list)

    features = []
    labels = []
    valid_idx = []

    feature_names = [
        "elo_home", "elo_away", "elo_diff",
        "home_pts5", "away_pts5", "form_diff",
        "home_gs5", "home_gc5", "away_gs5", "away_gc5",
        "home_pts_at_home5", "away_pts_at_away5",
        "h2h_home_pts",
        "days_since_home_match", "days_since_away_match",
    ]

    for i, row in df.iterrows():
        home, away = row["HomeTeam"], row["AwayTeam"]
        match_date = row["Date"].date()
        ftr = row["FTR"]

        if ftr not in ("H", "D", "A"):
            continue

        hh = team_hist[home]
        ah = team_hist[away]
        if len(hh) < 3 or len(ah) < 3:
            # za malo historii zeby liczyc forme - aktualizuj historie i pomin
            pass  # skip without continuing yet, need to update history below

        # Cechy z przeszlosci (tylko jesli mamy dosc danych)
        if len(hh) >= 3 and len(ah) >= 3:
            home_recent = hh[-5:]
            away_recent = ah[-5:]
            home_pts5 = sum(points(wh, fr) for (_, wh, _, _, fr) in home_recent)
            away_pts5 = sum(points(wh, fr) for (_, wh, _, _, fr) in away_recent)
            home_gs5 = np.mean([gf for (_, _, gf, _, _) in home_recent])
            home_gc5 = np.mean([ga for (_, _, _, ga, _) in home_recent])
            away_gs5 = np.mean([gf for (_, _, gf, _, _) in away_recent])
            away_gc5 = np.mean([ga for (_, _, _, ga, _) in away_recent])

            home_at_home = [h for h in hh if h[1]][-5:]
            away_at_away = [a for a in ah if not a[1]][-5:]
            home_pts_h5 = sum(points(True, fr) for (_, _, _, _, fr) in home_at_home)
            away_pts_a5 = sum(points(False, fr) for (_, _, _, _, fr) in away_at_away)

            h2h_key = frozenset({home, away})
            h2h = h2h_hist[h2h_key][-5:]
            h2h_home_pts = 0
            for (_, h_team, h_ftr) in h2h:
                if h_team == home:
                    h2h_home_pts += points(True, h_ftr)
                else:
                    # mecz, w ktorym home byl wtedy na wyjezdzie
                    h2h_home_pts += points(False, h_ftr)

            elo_h = get_elo_on(slug_for(home), match_date)
            elo_a = get_elo_on(slug_for(away), match_date)

            days_h = (match_date - hh[-1][0]).days
            days_a = (match_date - ah[-1][0]).days

            if elo_h is not None and elo_a is not None:
                features.append([
                    elo_h, elo_a, elo_h - elo_a,
                    home_pts5, away_pts5, home_pts5 - away_pts5,
                    home_gs5, home_gc5, away_gs5, away_gc5,
                    home_pts_h5, away_pts_a5,
                    h2h_home_pts,
                    days_h, days_a,
                ])
                labels.append({"H": 0, "D": 1, "A": 2}[ftr])
                valid_idx.append(i)

        # Aktualizuj historie tym meczem (zeby kolejne mecze widzialy go w przeszlosci)
        gh = int(row["FTHG"])
        ga = int(row["FTAG"])
        team_hist[home].append((match_date, True, gh, ga, ftr))
        team_hist[away].append((match_date, False, ga, gh, ftr))
        h2h_hist[frozenset({home, away})].append((match_date, home, ftr))

    return np.array(features), np.array(labels), valid_idx, feature_names


# =========================================================================
# Main
# =========================================================================
def main():
    load_elo_cache_from_disk()
    print(f"Elo cache: {len(ELO_CACHE)} druzyn w pamieci podrecznej")

    print("Pobieram dane sezonow...")
    all_df = load_all(TRAIN_SEASONS + TEST_SEASONS)
    print(f"  laczenie: {len(all_df)} meczow ({all_df['Date'].min().date()} - {all_df['Date'].max().date()})")

    print("\nBuduje cechy (i pobieram Elo z Clubelo dla nowych druzyn)...")
    t0 = time.time()
    X_all, y_all, idx_all, feature_names = build_features(all_df)
    print(f"  zbudowano {len(X_all)} wektorow cech w {time.time() - t0:.1f}s")
    save_elo_cache_to_disk()
    print(f"  Elo cache zapisany ({len(ELO_CACHE)} druzyn)")

    # Split train/test po dacie
    cutoff = pd.Timestamp("2024-08-01")
    dates_at_valid = all_df.iloc[idx_all]["Date"].values
    train_mask = dates_at_valid < cutoff
    test_mask = dates_at_valid >= cutoff

    X_train, y_train = X_all[train_mask], y_all[train_mask]
    X_test, y_test = X_all[test_mask], y_all[test_mask]
    test_idx_in_df = [idx_all[k] for k in range(len(idx_all)) if test_mask[k]]

    print(f"\nTrening: {len(X_train)} meczow / Test: {len(X_test)} meczow")

    # Trening
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # Bazowy klasyfikator z mocniejsza regularyzacja (mniejszy C -> mniej overfittu)
    base = LogisticRegression(max_iter=2000, C=0.3)

    # CalibratedClassifierCV stosuje izotoniczne przeskalowanie prawdopodobienstw,
    # zeby model nie byl przesadnie pewny siebie
    clf = CalibratedClassifierCV(base, method="isotonic", cv=5)
    clf.fit(X_train_s, y_train)
    print(f"  dokladnosc na treningu: {clf.score(X_train_s, y_train):.3f}")
    print(f"  dokladnosc na tescie:    {clf.score(X_test_s, y_test):.3f}")
    print(f"  (dla porownania: zgadywanie najczestszej klasy: ~0.43)")

    # Wagi cech: u CalibratedClassifierCV nie sa wprost dostepne (estymatorow jest 5),
    # wiec pobieramy srednia z pierwszego z nich (orientacyjnie)
    try:
        coefs = np.abs(clf.calibrated_classifiers_[0].estimator.coef_).mean(axis=0)
        sorted_idx = np.argsort(-coefs)
        print(f"\nWplyw cech (orientacyjnie z bazowego LR):")
        for k in sorted_idx:
            print(f"  {feature_names[k]:24} {coefs[k]:+.3f}")
    except Exception:
        pass

    # Backtest na tescie
    print(f"\n{'=' * 72}")
    print(f"BACKTEST out-of-sample (sezon {TEST_SEASONS[0]})")
    print(f"{'=' * 72}")
    probs_test = clf.predict_proba(X_test_s)

    bets_placed = 0
    bets_won = 0
    total_stake = 0.0
    total_return = 0.0
    by_outcome = defaultdict(lambda: {"bets": 0, "wins": 0, "stake": 0.0, "return": 0.0})
    by_edge_bucket = defaultdict(lambda: {"bets": 0, "wins": 0, "return": 0.0})

    for j, idx in enumerate(test_idx_in_df):
        row = all_df.iloc[idx]
        try:
            o1 = float(row[f"{ODDS_PREFIX}H"])
            ox = float(row[f"{ODDS_PREFIX}D"])
            o2 = float(row[f"{ODDS_PREFIX}A"])
        except (KeyError, ValueError):
            continue
        ftr = row["FTR"]

        p1, pd_, p2 = probs_test[j]
        i1, ix, i2, _ = odds_to_implied_probabilities(o1, ox, o2)

        for outcome, prob, odd, implied in (
            ("H", p1, o1, i1), ("D", pd_, ox, ix), ("A", p2, o2, i2),
        ):
            edge = prob - implied
            if edge < EDGE_THRESHOLD:
                continue
            bets_placed += 1
            total_stake += 1.0
            by_outcome[outcome]["bets"] += 1
            by_outcome[outcome]["stake"] += 1.0
            bucket = f"{int(edge * 100 / 5) * 5}-{int(edge * 100 / 5) * 5 + 5}%"
            by_edge_bucket[bucket]["bets"] += 1
            if outcome == ftr:
                bets_won += 1
                total_return += odd
                by_outcome[outcome]["wins"] += 1
                by_outcome[outcome]["return"] += odd
                by_edge_bucket[bucket]["wins"] += 1
                by_edge_bucket[bucket]["return"] += odd

    if bets_placed == 0:
        print("Brak zakladow z edge > 3%.")
        return

    pnl = total_return - total_stake
    roi = pnl / total_stake * 100
    win_rate = bets_won / bets_placed * 100

    print(f"Postawione zaklady:        {bets_placed}")
    print(f"Wygrane:                   {bets_won}")
    print(f"Hit rate:                  {win_rate:.1f}%")
    print(f"P&L:                       {pnl:+.2f} jednostek (stake {total_stake:.0f})")
    print(f"ROI:                       {roi:+.1f}%")
    print()
    print(f"--- Wg wyniku ---")
    for outcome, label in (("H", "1 gospodarz"), ("D", "X remis"), ("A", "2 gosc")):
        d = by_outcome[outcome]
        if d["bets"] == 0:
            continue
        wr = d["wins"] / d["bets"] * 100
        oroi = (d["return"] - d["stake"]) / d["stake"] * 100
        print(f"  {label:14}: {d['bets']:4d} bets | hit {wr:5.1f}% | ROI {oroi:+6.1f}%")
    print(f"\n--- Wg edge ---")
    for bucket in sorted(by_edge_bucket.keys(), key=lambda b: int(b.split("-")[0])):
        d = by_edge_bucket[bucket]
        if d["bets"] == 0:
            continue
        wr = d["wins"] / d["bets"] * 100
        oroi = (d["return"] - d["bets"]) / d["bets"] * 100
        print(f"  edge {bucket:>10}: {d['bets']:4d} bets | hit {wr:5.1f}% | ROI {oroi:+6.1f}%")
    print(f"{'=' * 72}")


if __name__ == "__main__":
    main()
