"""Testy InsightsService - z mockami warstw zewnetrznych (Clubelo, football-data)."""
from datetime import datetime, timezone
from unittest.mock import patch

import pandas as pd

from backend.models.schemas import MatchInput, MatchOdds, FormSummary, H2HMatch
from backend.services.insights_service import InsightsService


def _make_match() -> MatchInput:
    return MatchInput(
        home_team="Liverpool",
        away_team="Chelsea",
        league="Premier League",
        kick_off=datetime(2026, 5, 17, 16, 0, tzinfo=timezone.utc),
        odds=MatchOdds(home=1.85, draw=3.80, away=4.20),
    )


def test_generates_insights_with_full_data():
    """Pelny pipeline gdy wszystkie zrodla zwracaja dane."""
    with patch("backend.services.insights_service.clubelo.get_elo") as mock_elo, \
         patch("backend.services.insights_service.football_data.get_form") as mock_form, \
         patch("backend.services.insights_service.football_data.get_h2h") as mock_h2h, \
         patch("backend.services.insights_service.football_data.load_seasons") as mock_load, \
         patch("backend.services.insights_service.clubelo.load_cache"), \
         patch("backend.services.insights_service.clubelo.save_cache"):

        # Mock data
        mock_elo.side_effect = lambda team, *_: {"Liverpool": 1920, "Chelsea": 1820}.get(team)
        mock_form.return_value = FormSummary(
            last_n=5, results=["W", "W", "D", "L", "W"], points=10,
            goals_for=8, goals_against=4,
        )
        mock_h2h.return_value = []
        mock_load.return_value = pd.DataFrame({"Date": pd.to_datetime(["2024-01-01"])})

        service = InsightsService(history_seasons=1)
        result = service.generate(_make_match(), with_ai=False)

        assert result.home_team == "Liverpool"
        assert result.home_context.elo == 1920
        assert result.away_context.elo == 1820
        assert result.home_context.form is not None
        # Liverpool ma wyzsze Elo + home advantage -> wieksze P(home win)
        assert result.model_probability.home > result.model_probability.away


def test_handles_missing_elo_gracefully():
    """Gdy Clubelo nie ma druzyny - fallback neutralne P."""
    with patch("backend.services.insights_service.clubelo.get_elo", return_value=None), \
         patch("backend.services.insights_service.football_data.load_seasons", return_value=pd.DataFrame()), \
         patch("backend.services.insights_service.clubelo.load_cache"), \
         patch("backend.services.insights_service.clubelo.save_cache"):

        service = InsightsService()
        result = service.generate(_make_match(), with_ai=False)

        assert result.home_team == "Liverpool"
        assert result.home_context.elo is None
        # Fallback P powinno sumowac sie do 1
        p = result.model_probability
        assert abs(p.home + p.draw + p.away - 1.0) < 0.01


def test_ai_commentary_skipped_when_flag_false():
    with patch("backend.services.insights_service.clubelo.get_elo", return_value=1800), \
         patch("backend.services.insights_service.football_data.get_form", return_value=None), \
         patch("backend.services.insights_service.football_data.get_h2h", return_value=[]), \
         patch("backend.services.insights_service.football_data.load_seasons", return_value=pd.DataFrame()), \
         patch("backend.services.insights_service.clubelo.load_cache"), \
         patch("backend.services.insights_service.clubelo.save_cache"):

        service = InsightsService()
        result = service.generate(_make_match(), with_ai=False)
        assert result.ai_commentary is None


def test_caches_history_per_league():
    """Drugi mecz w tej samej lidze nie powinien znowu pobierac CSV."""
    with patch("backend.services.insights_service.clubelo.get_elo", return_value=1800), \
         patch("backend.services.insights_service.football_data.get_form", return_value=None), \
         patch("backend.services.insights_service.football_data.get_h2h", return_value=[]), \
         patch("backend.services.insights_service.football_data.load_seasons") as mock_load, \
         patch("backend.services.insights_service.clubelo.load_cache"), \
         patch("backend.services.insights_service.clubelo.save_cache"):

        mock_load.return_value = pd.DataFrame()
        service = InsightsService()
        service.generate(_make_match(), with_ai=False)
        service.generate(_make_match(), with_ai=False)
        # 1 wywolanie load_seasons (cache w obrebie service)
        assert mock_load.call_count == 1
