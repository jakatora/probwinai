"""Testy warstwy DB (SQLite)."""
import os
import tempfile
from datetime import datetime, timezone

import pytest

from backend.config import settings
from backend.db.database import (
    init_db, save_match_list, save_insights, get_insights,
    list_matches, get_match_meta,
)
from backend.models.schemas import (
    MatchInsights, MatchListItem, MatchOdds,
    Probability, TeamContext,
)


@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    """Kazdy test dostaje swiezy SQLite w tymczasowym pliku."""
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    monkeypatch.setattr(settings, "database_path", path)
    init_db()
    yield path
    if os.path.exists(path):
        os.unlink(path)


def _make_match_item(home: str = "A", away: str = "B") -> MatchListItem:
    return MatchListItem(
        id=f"2026-05-17_{home.lower()}_{away.lower()}",
        home_team=home, away_team=away, league="Test League",
        kick_off=datetime(2026, 5, 17, 16, 0, tzinfo=timezone.utc),
        odds=MatchOdds(home=2.0, draw=3.5, away=4.0),
    )


def _make_insights(item: MatchListItem) -> MatchInsights:
    return MatchInsights(
        home_team=item.home_team, away_team=item.away_team,
        league=item.league, kick_off=item.kick_off,
        home_context=TeamContext(name=item.home_team, elo=1800),
        away_context=TeamContext(name=item.away_team, elo=1700),
        model_probability=Probability(home=0.5, draw=0.3, away=0.2),
        implied_probability=Probability(home=0.5, draw=0.28, away=0.22),
        bookmaker_odds=item.odds,
        vig_pct=5.5,
        ai_commentary="Test commentary",
    )


def test_save_and_get_meta():
    item = _make_match_item()
    save_match_list([item])
    fetched = get_match_meta(item.id)
    assert fetched is not None
    assert fetched.home_team == item.home_team
    assert fetched.has_insights is False


def test_save_and_get_insights_roundtrip():
    item = _make_match_item()
    save_match_list([item])
    insights = _make_insights(item)
    save_insights(item.id, insights)

    fetched = get_insights(item.id)
    assert fetched is not None
    assert fetched.home_team == "A"
    assert fetched.model_probability.home == 0.5
    assert fetched.ai_commentary == "Test commentary"


def test_get_missing_insights_returns_none():
    assert get_insights("nonexistent") is None


def test_list_matches_filters_by_insights():
    item1 = _make_match_item("A", "B")
    item2 = _make_match_item("C", "D")
    save_match_list([item1, item2])
    save_insights(item1.id, _make_insights(item1))

    all_matches = list_matches(only_with_insights=False)
    only_ready = list_matches(only_with_insights=True)
    assert len(all_matches) == 2
    assert len(only_ready) == 1
    assert only_ready[0].id == item1.id
