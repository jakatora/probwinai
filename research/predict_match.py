"""
ProbWin AI - proof of concept
Liczy prawdopodobienstwo wygranej dla jednego meczu pilkarskiego
na podstawie ratingu Elo z Clubelo.com i porownuje z kursem bukmachera.
"""
import sys
import io
import csv
from dataclasses import dataclass

import requests

from model import elo_to_probabilities, odds_to_implied_probabilities, HOME_ADVANTAGE

# Wymus UTF-8 na stdout (Windows konsola)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CLUBELO_API = "http://api.clubelo.com/{club}"


@dataclass
class TeamElo:
    name: str
    elo: float
    date: str


def fetch_elo(club_slug: str) -> TeamElo:
    """Pobiera najnowszy rating Elo z Clubelo.com. Zwraca dane ostatniej linii CSV."""
    url = CLUBELO_API.format(club=club_slug)
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    rows = list(csv.DictReader(io.StringIO(r.text)))
    if not rows:
        raise ValueError(f"Brak danych Elo dla {club_slug}")
    last = rows[-1]
    return TeamElo(name=last["Club"], elo=float(last["Elo"]), date=last["To"])


def fmt_pct(p: float) -> str:
    return f"{p * 100:5.1f}%"


def print_report(home: TeamElo, away: TeamElo,
                  model_p: tuple[float, float, float],
                  odds: tuple[float, float, float],
                  implied_p: tuple[float, float, float],
                  vig: float):
    p1, px, p2 = model_p
    o1, ox, o2 = odds
    i1, ix, i2 = implied_p

    print("=" * 72)
    print(f"ProbWin AI - analiza meczu")
    print("=" * 72)
    print(f"  {home.name} (Elo {home.elo:.0f}, dane z {home.date})")
    print(f"  vs")
    print(f"  {away.name} (Elo {away.elo:.0f}, dane z {away.date})")
    print()
    print(f"  Przewaga gospodarzy: +{HOME_ADVANTAGE} pkt Elo")
    print(f"  Roznica Elo (z bonusem dom): {home.elo + HOME_ADVANTAGE - away.elo:+.0f}")
    print()
    print(f"{'':24} {'1 (gospodarz)':>14} {'X (remis)':>12} {'2 (gosc)':>12}")
    print("-" * 72)
    print(f"{'Model ProbWin AI':24} {fmt_pct(p1):>14} {fmt_pct(px):>12} {fmt_pct(p2):>12}")
    print(f"{'Kurs Betclic':24} {o1:>14.2f} {ox:>12.2f} {o2:>12.2f}")
    print(f"{'Implikowane P (bukm.)':24} {fmt_pct(i1):>14} {fmt_pct(ix):>12} {fmt_pct(i2):>12}")
    print(f"{'Edge (model - bukm.)':24} "
          f"{(p1 - i1) * 100:+13.1f}% "
          f"{(px - ix) * 100:+11.1f}% "
          f"{(p2 - i2) * 100:+11.1f}%")
    print()
    print(f"  Marza bukmachera (vig): {vig:.2f}%")
    print()

    # Identyfikacja value bets
    edges = [
        ("1 (gospodarz)", p1, o1, p1 - i1),
        ("X (remis)",     px, ox, px - ix),
        ("2 (gosc)",      p2, o2, p2 - i2),
    ]
    value_bets = [(name, p, o, edge) for name, p, o, edge in edges if edge > 0.03]

    if value_bets:
        print("  VALUE BETS znalezione (edge > 3%):")
        for name, p, o, edge in value_bets:
            ev = (p * o) - 1  # expected value przy stawce 1 jednostka
            print(f"    > {name}: edge {edge * 100:+.1f}%, "
                  f"EV {ev * 100:+.1f}% (przy stawce 1: spodziewany zysk {ev:.3f})")
    else:
        print("  Brak value betow (zaden edge > 3%). "
              "Bukmacher wycenil ten mecz blisko modelu.")
    print("=" * 72)


def main():
    # KONFIGURACJA TESTU
    # Mecz: Aston Villa vs Liverpool, 17.05.2026, Premier League
    # Kursy zrodlo: Bet365 (Betclic w PL ma podobne, +/- 3%)
    home_slug = "AstonVilla"
    away_slug = "Liverpool"

    odds_home = 3.10   # 1 - wygrana Aston Villa
    odds_draw = 3.90   # X - remis
    odds_away = 2.05   # 2 - wygrana Liverpool

    print(f"Pobieram ratingi Elo z Clubelo.com...")
    home = fetch_elo(home_slug)
    away = fetch_elo(away_slug)
    print(f"OK\n")

    model_p = elo_to_probabilities(home.elo, away.elo)
    implied = odds_to_implied_probabilities(odds_home, odds_draw, odds_away)
    implied_p = implied[:3]
    vig = implied[3]

    print_report(home, away, model_p, (odds_home, odds_draw, odds_away), implied_p, vig)


if __name__ == "__main__":
    main()
