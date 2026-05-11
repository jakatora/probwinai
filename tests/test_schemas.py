"""Testy pydantic schematow."""
from datetime import datetime, timezone, date
import pytest
from pydantic import ValidationError

from backend.models.schemas import (
    FormSummary, H2HMatch, MatchInput, MatchInsights,
    MatchOdds, Probability, TeamContext,
)


def test_match_odds_rejects_low_values():
    """Kurs <= 1.0 oznacza brak ryzyka, niemozliwy w bukmacherce."""
    with pytest.raises(ValidationError):
        MatchOdds(home=0.5, draw=3.0, away=3.0)
    with pytest.raises(ValidationError):
        MatchOdds(home=1.0, draw=3.0, away=3.0)


def test_match_odds_accepts_valid():
    o = MatchOdds(home=2.10, draw=3.40, away=3.20)
    assert o.bookmaker == "Betclic"


def test_probability_clamped():
    """P powinno byc w [0, 1]."""
    with pytest.raises(ValidationError):
        Probability(home=-0.1, draw=0.5, away=0.6)
    with pytest.raises(ValidationError):
        Probability(home=1.5, draw=0.0, away=-0.5)


def test_form_summary_avg():
    f = FormSummary(last_n=5, results=["W", "W", "D", "L", "W"],
                    points=10, goals_for=8, goals_against=5)
    assert f.avg_gf == 1.6
    assert f.avg_ga == 1.0


def test_form_summary_zero_safety():
    f = FormSummary(last_n=0, results=[], points=0, goals_for=0, goals_against=0)
    assert f.avg_gf == 0.0
    assert f.avg_ga == 0.0


def test_h2h_match_result_string():
    m = H2HMatch(date=date(2024, 12, 1), home_team="A", away_team="B",
                 home_goals=2, away_goals=1)
    assert m.result_string() == "2-1"


def test_insights_edges():
    home_ctx = TeamContext(name="Liverpool", elo=1900)
    away_ctx = TeamContext(name="Aston Villa", elo=1850)
    odds = MatchOdds(home=2.0, draw=3.5, away=4.0)
    ins = MatchInsights(
        home_team="Liverpool", away_team="Aston Villa",
        league="Premier League",
        kick_off=datetime(2026, 5, 17, 16, 0, tzinfo=timezone.utc),
        home_context=home_ctx, away_context=away_ctx,
        model_probability=Probability(home=0.55, draw=0.25, away=0.20),
        implied_probability=Probability(home=0.50, draw=0.28, away=0.22),
        bookmaker_odds=odds,
    )
    e = ins.edges()
    assert abs(e["home"] - 0.05) < 0.001
    assert abs(e["draw"] - (-0.03)) < 0.001
    assert abs(e["away"] - (-0.02)) < 0.001
