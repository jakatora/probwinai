"""Klient football-data.co.uk - historia meczow + statystyki + kursy zamkniecia.

Format: https://www.football-data.co.uk/mmz4281/{season}/{league}.csv
  season = 2425 (2024-25), 2324, ...
  league = E0 (Premier League), SP1 (La Liga), I1 (Serie A), etc.

Zwracane dane: HomeTeam, AwayTeam, Date, FTHG, FTAG, FTR, B365H, B365D, B365A...
"""
import io
import logging
from datetime import datetime, date as Date
from typing import Optional

import requests
import pandas as pd

from ..models.schemas import FormSummary, H2HMatch

log = logging.getLogger(__name__)

FD_BASE = "https://www.football-data.co.uk/mmz4281"

# Globalny in-memory cache zaladowanych sezonow
_season_cache: dict[tuple[str, str], pd.DataFrame] = {}


def load_season(season: str, league: str = "E0") -> pd.DataFrame:
    """Wczytuje pojedynczy sezon (np. '2425') dla danej ligi (np. 'E0').

    Zwraca pusty DataFrame jesli plik niedostepny (np. sezon jeszcze
    nie istnieje / liga niewspierana).
    """
    key = (season, league)
    if key in _season_cache:
        return _season_cache[key]

    url = f"{FD_BASE}/{season}/{league}.csv"
    log.info("Pobieranie %s", url)
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        log.warning("Niedostepne: %s (%s) - zwracam pusty DataFrame", url, e)
        empty = pd.DataFrame()
        _season_cache[key] = empty
        return empty

    text = r.content.decode("utf-8-sig", errors="replace")
    df = pd.read_csv(io.StringIO(text))
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"]).reset_index(drop=True)
    _season_cache[key] = df
    return df


def load_seasons(seasons: list[str], league: str = "E0") -> pd.DataFrame:
    """Wczytuje kilka sezonow i scala w jeden DataFrame.
    Puste DataFrames sa pomijane."""
    dfs = [load_season(s, league) for s in seasons]
    dfs = [d for d in dfs if not d.empty]
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True).sort_values("Date").reset_index(drop=True)


def _result_for(team: str, row: pd.Series) -> str:
    """Zwraca 'W', 'D' lub 'L' dla danej druzyny w danym meczu."""
    if row["HomeTeam"] == team:
        return {"H": "W", "D": "D", "A": "L"}[row["FTR"]]
    return {"H": "L", "D": "D", "A": "W"}[row["FTR"]]


def _goals_for_against(team: str, row: pd.Series) -> tuple[int, int]:
    """Gole strzelone i stracone przez druzyne w danym meczu."""
    if row["HomeTeam"] == team:
        return int(row["FTHG"]), int(row["FTAG"])
    return int(row["FTAG"]), int(row["FTHG"])


def get_form(team: str, df: pd.DataFrame, before: Date, last_n: int = 5) -> Optional[FormSummary]:
    """Forma druzyny w ostatnich N meczach przed dana data."""
    matches = df[
        ((df["HomeTeam"] == team) | (df["AwayTeam"] == team))
        & (df["Date"] < pd.Timestamp(before))
    ].tail(last_n)

    if matches.empty:
        return None

    results: list[str] = []
    points = 0
    gf = 0
    ga = 0
    for _, row in matches.iterrows():
        r = _result_for(team, row)
        results.append(r)
        points += {"W": 3, "D": 1, "L": 0}[r]
        g_for, g_against = _goals_for_against(team, row)
        gf += g_for
        ga += g_against

    return FormSummary(
        last_n=len(results),
        results=results,
        points=points,
        goals_for=gf,
        goals_against=ga,
    )


def get_h2h(team_a: str, team_b: str, df: pd.DataFrame, before: Date, last_n: int = 5) -> list[H2HMatch]:
    """Historia ostatnich N spotkan bezposrednich miedzy dwoma druzynami."""
    matches = df[
        (
            ((df["HomeTeam"] == team_a) & (df["AwayTeam"] == team_b))
            | ((df["HomeTeam"] == team_b) & (df["AwayTeam"] == team_a))
        )
        & (df["Date"] < pd.Timestamp(before))
    ].tail(last_n)

    return [
        H2HMatch(
            date=row["Date"].date(),
            home_team=row["HomeTeam"],
            away_team=row["AwayTeam"],
            home_goals=int(row["FTHG"]),
            away_goals=int(row["FTAG"]),
        )
        for _, row in matches.iterrows()
    ]


# Ligi obslugiwane domyslnie (kody football-data)
LEAGUES = {
    "Premier League": "E0",
    "La Liga": "SP1",
    "Serie A": "I1",
    "Bundesliga": "D1",
    "Ligue 1": "F1",
}


def league_code(league_name: str) -> str:
    return LEAGUES.get(league_name, "E0")


def recent_seasons(n: int = 3) -> list[str]:
    """Zwraca kody n ostatnich sezonow (najnowszy najpierw zalad. ostatni)."""
    today = Date.today()
    # Sezon konczy sie w maju. Jesli jestesmy po lipcu, biezacy sezon to YYYY/YYYY+1
    if today.month >= 7:
        current_start = today.year
    else:
        current_start = today.year - 1
    codes = []
    for offset in range(n - 1, -1, -1):
        start = current_start - offset
        end = start + 1
        codes.append(f"{start % 100:02d}{end % 100:02d}")
    return codes
