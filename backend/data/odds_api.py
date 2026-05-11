"""Klient the-odds-api.com - aktualne kursy bukmacherskie z 70+ bukmacherow.

Wymaga klucza API (darmowy plan: 500 req/mies). Jesli klucza nie ma,
funkcje zwracaja przykladowe dane testowe zeby aplikacja dzialala 'na sucho'.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests

from ..config import settings
from ..models.schemas import MatchListItem, MatchOdds

log = logging.getLogger(__name__)

ODDS_API_BASE = "https://api.the-odds-api.com/v4"


def _has_key() -> bool:
    return bool(settings.odds_api_key)


def _bookmaker_odds(bookmaker_data: dict) -> Optional[MatchOdds]:
    """Wyciaga 1X2 z odpowiedzi the-odds-api dla jednego bukmachera."""
    markets = bookmaker_data.get("markets", [])
    for market in markets:
        if market.get("key") == "h2h":
            outcomes = {o["name"]: o["price"] for o in market.get("outcomes", [])}
            # the-odds-api zwraca nazwy: home_team, away_team, "Draw"
            # Trzeba zmapowac w wywolaniu (mamy tylko nazwy druzyn)
            return outcomes  # type: ignore[return-value]
    return None


def fetch_upcoming(sport: Optional[str] = None) -> list[MatchListItem]:
    """Pobiera nadchodzace mecze + kursy. Bez klucza zwraca dane mock."""
    if not _has_key():
        log.info("Brak ODDS_API_KEY - uzywam danych mockowych")
        return _mock_matches()

    sport_key = sport or settings.odds_api_sport
    url = f"{ODDS_API_BASE}/sports/{sport_key}/odds"
    params = {
        "apiKey": settings.odds_api_key,
        "regions": settings.odds_api_region,
        "markets": "h2h",
        "oddsFormat": "decimal",
    }

    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        log.error("the-odds-api error: %s. Uzywam mocku.", e)
        return _mock_matches()

    events = r.json()
    items: list[MatchListItem] = []

    for ev in events:
        home = ev["home_team"]
        away = ev["away_team"]
        kick_off = datetime.fromisoformat(ev["commence_time"].replace("Z", "+00:00"))

        # Preferuj Betclic, fallback do pierwszego dostepnego bukmachera
        bookmakers = ev.get("bookmakers", [])
        chosen = next(
            (b for b in bookmakers if b.get("key", "").lower() == "betclic"),
            bookmakers[0] if bookmakers else None,
        )
        if not chosen:
            continue

        outcomes = _bookmaker_odds(chosen) or {}
        try:
            odds = MatchOdds(
                home=float(outcomes[home]),
                away=float(outcomes[away]),
                draw=float(outcomes.get("Draw", 0)) or float(outcomes.get("Tie", 0)),
                bookmaker=chosen.get("title", "Unknown"),
            )
        except (KeyError, ValueError):
            log.debug("Brak pelnych kursow 1X2 dla %s vs %s, pomijam", home, away)
            continue

        items.append(MatchListItem(
            id=f"{kick_off.date().isoformat()}_{_slugify(home)}_{_slugify(away)}",
            home_team=home,
            away_team=away,
            league=_league_from_sport(sport_key),
            kick_off=kick_off,
            odds=odds,
        ))

    return items


def _slugify(s: str) -> str:
    return s.lower().replace(" ", "-").replace("'", "")


def _league_from_sport(sport_key: str) -> str:
    mapping = {
        "soccer_epl": "Premier League",
        "soccer_spain_la_liga": "La Liga",
        "soccer_italy_serie_a": "Serie A",
        "soccer_germany_bundesliga": "Bundesliga",
        "soccer_france_ligue_one": "Ligue 1",
    }
    return mapping.get(sport_key, sport_key)


# ---- DANE MOCK do testowania bez klucza API ----

def _mock_matches() -> list[MatchListItem]:
    """Statyczna lista 10 hipotetycznych meczow do dema."""
    base_date = datetime.now(timezone.utc).replace(hour=18, minute=0, second=0, microsecond=0)
    matches = [
        ("Aston Villa", "Liverpool", 3.10, 3.90, 2.05),
        ("Arsenal", "Tottenham", 1.90, 3.80, 4.20),
        ("Manchester City", "Chelsea", 1.65, 4.20, 5.00),
        ("Newcastle", "Brighton", 2.10, 3.50, 3.40),
        ("Real Madrid", "Barcelona", 2.20, 3.60, 3.10),
        ("Bayern Munich", "Borussia Dortmund", 1.75, 4.00, 4.50),
        ("PSG", "Marseille", 1.55, 4.40, 6.00),
        ("Juventus", "Inter Milan", 2.80, 3.20, 2.60),
        ("Liverpool", "Manchester United", 1.85, 3.80, 4.30),
        ("Atletico Madrid", "Sevilla", 1.95, 3.40, 4.00),
    ]
    return [
        MatchListItem(
            id=f"{base_date.date().isoformat()}_{_slugify(h)}_{_slugify(a)}",
            home_team=h,
            away_team=a,
            league=_league_for_team(h),
            kick_off=base_date + timedelta(hours=i),
            odds=MatchOdds(home=h_o, draw=d_o, away=a_o, bookmaker="Betclic (mock)"),
        )
        for i, (h, a, h_o, d_o, a_o) in enumerate(matches)
    ]


def _league_for_team(team: str) -> str:
    polish = {"Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla"}
    bundes = {"Bayern Munich", "Borussia Dortmund"}
    ligue1 = {"PSG", "Marseille"}
    serieA = {"Juventus", "Inter Milan"}
    if team in polish:
        return "La Liga"
    if team in bundes:
        return "Bundesliga"
    if team in ligue1:
        return "Ligue 1"
    if team in serieA:
        return "Serie A"
    return "Premier League"
