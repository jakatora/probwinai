"""Pydantic schematy uzywane przez API i serwisy."""
from datetime import datetime, date, timezone
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field


def utcnow() -> datetime:
    """Aware UTC datetime (zastepuje deprecated datetime.utcnow())."""
    return datetime.now(timezone.utc)


# Wszystkie schematy nie maja kolizji 'model_' - wylaczamy ostrzezenie
_CFG = ConfigDict(protected_namespaces=())


# ---- Surowe dane wejsciowe ----

class MatchOdds(BaseModel):
    """Kursy bukmacherskie 1X2 dla jednego meczu."""
    home: float = Field(..., gt=1.0)
    draw: float = Field(..., gt=1.0)
    away: float = Field(..., gt=1.0)
    bookmaker: str = "Betclic"


class MatchInput(BaseModel):
    """Wejscie do generatora raportu - dane o nadchodzacym meczu."""
    home_team: str
    away_team: str
    league: str = "Premier League"
    kick_off: datetime
    odds: MatchOdds


# ---- Pochodne struktury obliczone z danych ----

class Probability(BaseModel):
    """Prawdopodobienstwo dla wyniku 1X2 (jedna z trzech wartosci)."""
    home: float = Field(..., ge=0.0, le=1.0)
    draw: float = Field(..., ge=0.0, le=1.0)
    away: float = Field(..., ge=0.0, le=1.0)


class FormSummary(BaseModel):
    """Forma druzyny w ostatnich N meczach."""
    last_n: int
    results: list[Literal["W", "D", "L"]]  # od najstarszego do najnowszego
    points: int
    goals_for: int
    goals_against: int

    @property
    def avg_gf(self) -> float:
        return self.goals_for / self.last_n if self.last_n else 0.0

    @property
    def avg_ga(self) -> float:
        return self.goals_against / self.last_n if self.last_n else 0.0


class H2HMatch(BaseModel):
    """Pojedynczy mecz w historii bezposrednich spotkan."""
    date: date
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int

    def result_string(self) -> str:
        return f"{self.home_goals}-{self.away_goals}"


class TeamContext(BaseModel):
    """Kontekst druzyny: Elo, forma, ostatnie mecze."""
    name: str
    elo: Optional[float] = None
    form: Optional[FormSummary] = None


class MatchInsights(BaseModel):
    """Pelny raport o meczu generowany przez aplikacje."""
    model_config = _CFG
    home_team: str
    away_team: str
    league: str
    kick_off: datetime
    home_context: TeamContext
    away_context: TeamContext
    h2h: list[H2HMatch] = Field(default_factory=list)
    model_probability: Probability
    implied_probability: Probability
    bookmaker_odds: MatchOdds
    vig_pct: float = 0.0
    ai_commentary: Optional[str] = None
    generated_at: datetime = Field(default_factory=utcnow)

    def edges(self) -> dict[str, float]:
        """Roznica (P modelu - P bukmachera) dla kazdego wyniku."""
        return {
            "home": self.model_probability.home - self.implied_probability.home,
            "draw": self.model_probability.draw - self.implied_probability.draw,
            "away": self.model_probability.away - self.implied_probability.away,
        }


class MatchListItem(BaseModel):
    """Skrocony rekord meczu - na liste 'top 10'."""
    id: str  # unikalny identyfikator (slug)
    home_team: str
    away_team: str
    league: str
    kick_off: datetime
    odds: MatchOdds
    has_insights: bool = False
