"""
ProbWin AI - walking-forward cross-validation.

Dla kazdego sezonu testowego:
  1. Trenuje model na WSZYSTKICH wczesniejszych sezonach
  2. Przewiduje na sezonie testowym (out-of-sample)
  3. Liczy ROI dla 3 strategii: overall, no_home (D+A), home_only (H)

To pokazuje czy strategia 'tylko remis + gosc' (zwyciezca w 2024-25)
generuje pozytywny ROI rok po roku, czy to byla wariancja.
"""
import sys
import io
from collections import defaultdict
from datetime import date as Date

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV

from model import odds_to_implied_probabilities

# Importujemy infrastrukture z backtest_v2 (Elo cache, feature engineering)
from backtest_v2 import (
    load_all, build_features, load_elo_cache_from_disk, save_elo_cache_to_disk,
    EDGE_THRESHOLD, ODDS_PREFIX, ELO_CACHE
)

# (sys.stdout juz wrappowany przez import backtest_v2)

# Wszystkie sezony, od najstarszego (wlaczamy 2020-21 i wczesniej dla wiekszej puli treningowej)
ALL_SEASONS = ["2021", "2122", "2223", "2324", "2425"]
TEST_SEASONS = ["2223", "2324", "2425"]  # ostatnie 3 sezony testujemy
MIN_TRAIN_SEASONS = 2  # minimum 2 sezony treningu (~760 meczow)


def train_and_predict(X_train, y_train, X_test):
    """Trenuje skalibrowany LR + zwraca prawdopodobienstwa na zbiorze testowym."""
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    base = LogisticRegression(max_iter=2000, C=0.3)
    clf = CalibratedClassifierCV(base, method="isotonic", cv=5)
    clf.fit(X_train_s, y_train)

    train_acc = clf.score(X_train_s, y_train)
    test_acc = clf.score(scaler.transform(X_test), [0] * len(X_test))  # dummy y; only need accuracy below
    return clf.predict_proba(X_test_s), train_acc


def evaluate_test_set(probs, test_rows):
    """Liczy statystyki dla 3 strategii: overall, no_home, home_only."""
    stats = {
        "overall": {"bets": 0, "wins": 0, "stake": 0.0, "ret": 0.0},
        "no_home": {"bets": 0, "wins": 0, "stake": 0.0, "ret": 0.0},
        "home_only": {"bets": 0, "wins": 0, "stake": 0.0, "ret": 0.0},
        "by_outcome": defaultdict(lambda: {"bets": 0, "wins": 0, "stake": 0.0, "ret": 0.0}),
    }

    for j, row in enumerate(test_rows):
        try:
            o1 = float(row[f"{ODDS_PREFIX}H"])
            ox = float(row[f"{ODDS_PREFIX}D"])
            o2 = float(row[f"{ODDS_PREFIX}A"])
        except (KeyError, ValueError, TypeError):
            continue
        ftr = row["FTR"]

        p1, pd_, p2 = probs[j]
        i1, ix, i2, _ = odds_to_implied_probabilities(o1, ox, o2)

        for outcome, prob, odd, implied in (
            ("H", p1, o1, i1), ("D", pd_, ox, ix), ("A", p2, o2, i2),
        ):
            edge = prob - implied
            if edge < EDGE_THRESHOLD:
                continue

            won = (outcome == ftr)
            ret = odd if won else 0.0

            # overall
            stats["overall"]["bets"] += 1
            stats["overall"]["stake"] += 1.0
            stats["overall"]["ret"] += ret
            stats["overall"]["wins"] += int(won)

            # by outcome
            s = stats["by_outcome"][outcome]
            s["bets"] += 1
            s["stake"] += 1.0
            s["ret"] += ret
            s["wins"] += int(won)

            # filter strategies
            if outcome == "H":
                bucket = stats["home_only"]
            else:
                bucket = stats["no_home"]
            bucket["bets"] += 1
            bucket["stake"] += 1.0
            bucket["ret"] += ret
            bucket["wins"] += int(won)

    return stats


def fmt_strat(label, s):
    if s["bets"] == 0:
        return f"  {label:14}: 0 zakladow"
    roi = (s["ret"] - s["stake"]) / s["stake"] * 100
    wr = s["wins"] / s["bets"] * 100
    return f"  {label:14}: {s['bets']:4d} bets | hit {wr:5.1f}% | ROI {roi:+6.1f}% | P&L {s['ret'] - s['stake']:+7.2f}"


def main():
    load_elo_cache_from_disk()
    print(f"Elo cache: {len(ELO_CACHE)} druzyn\n")

    print(f"Pobieram dane sezonow {ALL_SEASONS}...")
    all_df = load_all(ALL_SEASONS)
    print(f"  laczenie: {len(all_df)} meczow ({all_df['Date'].min().date()} - {all_df['Date'].max().date()})\n")

    print("Buduje cechy (raz dla wszystkich sezonow)...")
    X_all, y_all, idx_all, _ = build_features(all_df)
    print(f"  {len(X_all)} wektorow cech\n")
    save_elo_cache_to_disk()

    season_of_match = all_df.iloc[idx_all]["Season"].values

    # Agregacja po wszystkich sezonach testowych
    aggregate = {
        "overall": {"bets": 0, "wins": 0, "stake": 0.0, "ret": 0.0},
        "no_home": {"bets": 0, "wins": 0, "stake": 0.0, "ret": 0.0},
        "home_only": {"bets": 0, "wins": 0, "stake": 0.0, "ret": 0.0},
    }

    for test_season in TEST_SEASONS:
        test_pos = ALL_SEASONS.index(test_season)
        train_seasons = ALL_SEASONS[:test_pos]
        if len(train_seasons) < MIN_TRAIN_SEASONS:
            print(f"Pomijam {test_season} - tylko {len(train_seasons)} sezonow treningu")
            continue

        train_mask = np.isin(season_of_match, train_seasons)
        test_mask = season_of_match == test_season

        X_train = X_all[train_mask]
        y_train = y_all[train_mask]
        X_test = X_all[test_mask]
        y_test = y_all[test_mask]

        test_match_indices = [idx_all[k] for k in range(len(idx_all)) if test_mask[k]]
        test_rows = [all_df.iloc[i] for i in test_match_indices]

        print(f"{'=' * 72}")
        print(f"TEST: sezon {test_season}  |  TRENING: {train_seasons} ({len(X_train)} meczow)")
        print(f"{'=' * 72}")

        # Trening + predykcja
        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        base = LogisticRegression(max_iter=2000, C=0.3)
        clf = CalibratedClassifierCV(base, method="isotonic", cv=5)
        clf.fit(X_train_s, y_train)

        print(f"  accuracy train: {clf.score(X_train_s, y_train):.3f} | "
              f"test: {clf.score(X_test_s, y_test):.3f}")

        probs = clf.predict_proba(X_test_s)
        stats = evaluate_test_set(probs, test_rows)

        print(fmt_strat("OVERALL", stats["overall"]))
        print(fmt_strat("NO_HOME (D+A)", stats["no_home"]))
        print(fmt_strat("HOME_ONLY (H)", stats["home_only"]))
        for o, label in (("H", "  -> H"), ("D", "  -> D"), ("A", "  -> A")):
            print(fmt_strat(label, stats["by_outcome"][o]))

        # Agregacja
        for key in ("overall", "no_home", "home_only"):
            for k in ("bets", "wins", "stake", "ret"):
                aggregate[key][k] += stats[key][k]

        print()

    # Zbiorcze podsumowanie
    print(f"{'=' * 72}")
    print(f"AGREGACJA NA WSZYSTKICH TESTOWYCH SEZONACH ({len(TEST_SEASONS)} sezony)")
    print(f"{'=' * 72}")
    print(fmt_strat("OVERALL", aggregate["overall"]))
    print(fmt_strat("NO_HOME (D+A)", aggregate["no_home"]))
    print(fmt_strat("HOME_ONLY (H)", aggregate["home_only"]))
    print(f"{'=' * 72}")
    print("INTERPRETACJA:")
    print("  - jesli NO_HOME ma ROI > +3% na wszystkich sezonach -> realny edge")
    print("  - jesli ROI dodatni na 1-2 sezonach, ujemny na innym -> niepewne")
    print("  - jesli ujemny lacznie -> 2024-25 byla anomalia")


if __name__ == "__main__":
    main()
