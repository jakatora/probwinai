"""Testy rankingu popularnosci meczu."""
from datetime import datetime, timezone

from backend.models.schemas import MatchListItem, MatchOdds
from backend.services.popularity import score, rank_matches


def _mk(home: str, away: str, league: str = "Premier League",
        odds: tuple[float, float, float] = (2.0, 3.5, 4.0)) -> MatchListItem:
    return MatchListItem(
        id=f"{home.lower()}_{away.lower()}",
        home_team=home, away_team=away, league=league,
        kick_off=datetime(2026, 5, 17, 16, 0, tzinfo=timezone.utc),
        odds=MatchOdds(home=odds[0], draw=odds[1], away=odds[2]),
    )


def test_premier_league_higher_than_lower_division():
    pl = _mk("Arsenal", "Chelsea", "Premier League")
    champ = _mk("Norwich", "Watford", "Championship")
    assert score(pl) > score(champ)


def test_derby_boost():
    derby = _mk("Real Madrid", "Barcelona", "La Liga")
    non_derby = _mk("Getafe", "Mallorca", "La Liga")
    assert score(derby) > score(non_derby)


def test_popular_team_boost():
    with_big = _mk("Liverpool", "Burnley")
    no_big = _mk("Brentford", "Bournemouth")
    assert score(with_big) > score(no_big)


def test_low_vig_bonus():
    """Niska marza = bardziej profesjonalnie wyceniony rynek."""
    pro_market = _mk("Liverpool", "Chelsea", odds=(2.10, 3.40, 3.30))  # ~3% vig
    high_vig = _mk("Liverpool", "Chelsea", odds=(1.90, 3.20, 3.60))    # ~10% vig
    assert score(pro_market) > score(high_vig)


def test_rank_returns_top_n():
    matches = [_mk(f"Team{i}", f"Other{i}") for i in range(15)]
    top5 = rank_matches(matches, top_n=5)
    assert len(top5) == 5


def test_rank_orders_by_score():
    matches = [
        _mk("Brentford", "Bournemouth"),  # low score
        _mk("Real Madrid", "Barcelona", "La Liga"),  # derby + popular
        _mk("Getafe", "Mallorca", "La Liga"),  # neutral
    ]
    top = rank_matches(matches, top_n=3)
    assert top[0].home_team == "Real Madrid"
