"""Generowanie Match Insights Report - pelny pipeline dla jednego meczu.

Skleja:
1. Probability modelu z Elo
2. Implikowane P z kursu bukmachera
3. Forma druzyn z football-data.co.uk
4. H2H z football-data.co.uk
5. Komentarz AI (Claude API z web_search lub mock)

Zwraca uzupelniony obiekt MatchInsights gotowy do renderowania w HTML/JSON.
"""
import logging
from datetime import date

import pandas as pd

from ..ai.commentary import generate_commentary
from ..data import clubelo, football_data
from ..models.probability import elo_to_probability, odds_to_implied
from ..models.schemas import (
    H2HMatch, MatchInput, MatchInsights, TeamContext,
)

log = logging.getLogger(__name__)


class InsightsService:
    """Orkiestrator pelnego raportu o meczu.

    Wczytuje historie meczow lazy - jedna liga na zadanie. Cache na ligi
    przechowywany w football_data._season_cache, wiec ponowne wywolania
    dla tej samej ligi nie generuja kolejnych HTTP.
    """

    def __init__(self, history_seasons: int = 3, default_league: str = "Premier League"):
        self.history_seasons = history_seasons
        self.default_league = default_league
        self._history_by_league: dict[str, pd.DataFrame] = {}

        # Wczytaj cache Clubelo
        clubelo.load_cache()

    def _history_for(self, league: str) -> pd.DataFrame:
        """Zwraca DataFrame z meczami danej ligi (lazy load + cache)."""
        if league in self._history_by_league:
            return self._history_by_league[league]
        code = football_data.league_code(league)
        season_codes = football_data.recent_seasons(self.history_seasons)
        try:
            df = football_data.load_seasons(season_codes, league=code)
            log.info("Wczytano %d meczow dla ligi %s (sezony %s)",
                     len(df), league, season_codes)
        except Exception as e:
            log.warning("Nie udalo sie wczytac historii dla %s: %s", league, e)
            df = pd.DataFrame()
        self._history_by_league[league] = df
        return df

    def generate(self, match: MatchInput, with_ai: bool = True) -> MatchInsights:
        """Tworzy pelny raport dla jednego meczu."""
        match_date = match.kick_off.date()
        history_df = self._history_for(match.league)

        # Elo i forma dla obu druzyn
        home_ctx = self._team_context(match.home_team, match_date, history_df)
        away_ctx = self._team_context(match.away_team, match_date, history_df)

        # H2H
        h2h = self._h2h(match.home_team, match.away_team, match_date, history_df)

        # Probability
        if home_ctx.elo is not None and away_ctx.elo is not None:
            model_p = elo_to_probability(home_ctx.elo, away_ctx.elo)
        else:
            # Bez Elo - rzucamy 'neutralne' P (40/30/30) zeby aplikacja sie nie wywalala
            from ..models.schemas import Probability
            model_p = Probability(home=0.40, draw=0.30, away=0.30)

        implied_p, vig = odds_to_implied(
            match.odds.home, match.odds.draw, match.odds.away
        )

        insights = MatchInsights(
            home_team=match.home_team,
            away_team=match.away_team,
            league=match.league,
            kick_off=match.kick_off,
            home_context=home_ctx,
            away_context=away_ctx,
            h2h=h2h,
            model_probability=model_p,
            implied_probability=implied_p,
            bookmaker_odds=match.odds,
            vig_pct=vig,
        )

        # Komentarz AI na koncu (potrzebuje pelnego kontekstu)
        if with_ai:
            insights.ai_commentary = generate_commentary(insights)

        # Zapisz cache Clubelo (jesli dolane nowe druzyny)
        clubelo.save_cache()

        return insights

    def _team_context(self, team: str, match_date: date, history_df: pd.DataFrame) -> TeamContext:
        elo = clubelo.get_elo(team, match_date)
        form = None
        if not history_df.empty:
            form = football_data.get_form(team, history_df, match_date)
        return TeamContext(name=team, elo=elo, form=form)

    def _h2h(self, home: str, away: str, match_date: date, history_df: pd.DataFrame) -> list[H2HMatch]:
        if history_df.empty:
            return []
        return football_data.get_h2h(home, away, history_df, match_date)
