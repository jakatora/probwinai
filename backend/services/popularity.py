"""Ranking 'popularnosci' meczu - heurystyka do wyboru top N.

Im wyzszy score, tym wyzej w rankingu top N codziennej listy.

Komponenty score (waga):
  - waga ligi (top 5 europejskich: PL/LaLiga/Bundesliga/SerieA/Ligue1)
  - obecnosc 'big six'/popularnych klubow
  - obecnosc derbow / klasykow
  - 'pewnosc kursu' (im nizsza marza vig%, tym ladniej wyceniony, czyli wazniejszy)
"""
from ..models.schemas import MatchListItem
from ..models.probability import odds_to_implied


# Wagi lig (top europejskie najwyzej, ligi nizsze nizej)
LEAGUE_WEIGHTS: dict[str, float] = {
    "Premier League": 1.0,
    "La Liga": 0.95,
    "Bundesliga": 0.90,
    "Serie A": 0.90,
    "Ligue 1": 0.80,
    "Eredivisie": 0.55,
    "Primeira Liga": 0.50,
    "Championship": 0.45,
    "MLS": 0.40,
    "Ekstraklasa": 0.45,
}

# Kluby o wysokiej rozpoznawalnosci globalnej
POPULAR_TEAMS: set[str] = {
    "Liverpool", "Manchester United", "Manchester City", "Chelsea", "Arsenal",
    "Tottenham", "Real Madrid", "Barcelona", "Atletico Madrid", "Bayern",
    "Bayern Munich", "Borussia Dortmund", "Dortmund", "PSG",
    "Paris Saint Germain", "Paris Saint-Germain", "Marseille",
    "Juventus", "Inter", "Inter Milan", "AC Milan", "Milan", "Napoli",
    "AS Roma", "Roma", "Ajax", "Porto", "Benfica",
}

# Slynne derby - wystepuja jako pary
DERBIES: list[frozenset[str]] = [
    frozenset({"Real Madrid", "Barcelona"}),
    frozenset({"Real Madrid", "Atletico Madrid"}),
    frozenset({"Manchester United", "Manchester City"}),
    frozenset({"Liverpool", "Manchester United"}),
    frozenset({"Arsenal", "Tottenham"}),
    frozenset({"Chelsea", "Tottenham"}),
    frozenset({"Inter Milan", "AC Milan"}),
    frozenset({"Inter", "Milan"}),
    frozenset({"AS Roma", "Lazio"}),
    frozenset({"Roma", "Lazio"}),
    frozenset({"Bayern Munich", "Borussia Dortmund"}),
    frozenset({"Bayern", "Dortmund"}),
    frozenset({"PSG", "Marseille"}),
    frozenset({"Boca Juniors", "River Plate"}),
    frozenset({"Celtic", "Rangers"}),
]


def score(match: MatchListItem) -> float:
    """Score wieksze = mecz wazniejszy/popularniejszy."""
    s = 0.0

    # Waga ligi
    s += LEAGUE_WEIGHTS.get(match.league, 0.3)

    # Popularne kluby (1 punkt za kazdego)
    if match.home_team in POPULAR_TEAMS:
        s += 0.5
    if match.away_team in POPULAR_TEAMS:
        s += 0.5

    # Derby - duzy bonus
    pair = frozenset({match.home_team, match.away_team})
    if pair in DERBIES:
        s += 1.0

    # Niska marza vig% = profesjonalnie wyceniony rynek = wazny mecz dla bukmachera
    try:
        _, vig = odds_to_implied(match.odds.home, match.odds.draw, match.odds.away)
        # vig 5% -> bonus +0.5, vig 10% -> +0.0, vig 15% -> -0.5
        s += (10.0 - vig) / 10.0 * 0.5
    except Exception:
        pass

    return s


def rank_matches(matches: list[MatchListItem], top_n: int = 10) -> list[MatchListItem]:
    """Sortuje mecze wg popularnosci i zwraca top N."""
    scored = [(score(m), m) for m in matches]
    scored.sort(key=lambda t: t[0], reverse=True)
    return [m for _, m in scored[:top_n]]
