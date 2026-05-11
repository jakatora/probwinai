"""Warstwa SQLite - cache MatchInsights na dysku.

Tabela 'matches' przechowuje pelny rekord MatchInsights jako JSON.
Pole id = '{date}_{home-slug}_{away-slug}' (np. '2026-05-17_aston-villa_liverpool').

Daje mobile/API szybki dostep bez koniecznosci przeliczania na zywo.
"""
import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from ..config import settings
from ..models.schemas import MatchInsights, MatchListItem, utcnow

log = logging.getLogger(__name__)


SCHEMA = """
CREATE TABLE IF NOT EXISTS matches (
    id TEXT PRIMARY KEY,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    league TEXT NOT NULL,
    kick_off TEXT NOT NULL,
    bookmaker TEXT,
    odds_home REAL,
    odds_draw REAL,
    odds_away REAL,
    insights_json TEXT,
    has_insights INTEGER DEFAULT 0,
    generated_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_kick_off ON matches(kick_off);
CREATE INDEX IF NOT EXISTS idx_has_insights ON matches(has_insights);
"""


def db_path() -> Path:
    p = settings.db_path_abs
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path(), timeout=10.0)
    conn.row_factory = sqlite3.Row
    # WAL mode pozwala czytelnikom (API) i pisarzom (cron) dzialac rownolegle
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Tworzy schemat (idempotentne)."""
    with get_conn() as conn:
        conn.executescript(SCHEMA)
    log.info("DB zainicjalizowane: %s", db_path())


def save_match_list(items: list[MatchListItem]) -> int:
    """Zapisuje liste meczow (bez insights jeszcze)."""
    with get_conn() as conn:
        n = 0
        for it in items:
            conn.execute(
                """
                INSERT OR REPLACE INTO matches
                (id, home_team, away_team, league, kick_off,
                 bookmaker, odds_home, odds_draw, odds_away,
                 insights_json, has_insights)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, 0)
                """,
                (
                    it.id, it.home_team, it.away_team, it.league,
                    it.kick_off.isoformat(),
                    it.odds.bookmaker, it.odds.home, it.odds.draw, it.odds.away,
                ),
            )
            n += 1
        return n


def save_insights(match_id: str, insights: MatchInsights) -> None:
    """Zapisuje pelne insights dla meczu."""
    payload = insights.model_dump_json()
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE matches
            SET insights_json = ?, has_insights = 1, generated_at = ?
            WHERE id = ?
            """,
            (payload, utcnow().isoformat(), match_id),
        )


def get_insights(match_id: str) -> Optional[MatchInsights]:
    """Wczytuje insights dla meczu, jesli juz wygenerowane."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT insights_json FROM matches WHERE id = ? AND has_insights = 1",
            (match_id,),
        ).fetchone()
    if not row or not row["insights_json"]:
        return None
    data = json.loads(row["insights_json"])
    return MatchInsights.model_validate(data)


def list_matches(only_with_insights: bool = False, limit: int = 50) -> list[MatchListItem]:
    """Lista wszystkich meczow w bazie (najnowsze najpierw)."""
    where = "WHERE has_insights = 1" if only_with_insights else ""
    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT id, home_team, away_team, league, kick_off,
                   bookmaker, odds_home, odds_draw, odds_away, has_insights
            FROM matches
            {where}
            ORDER BY kick_off DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    from ..models.schemas import MatchOdds
    items: list[MatchListItem] = []
    for r in rows:
        items.append(MatchListItem(
            id=r["id"],
            home_team=r["home_team"],
            away_team=r["away_team"],
            league=r["league"],
            kick_off=datetime.fromisoformat(r["kick_off"]),
            odds=MatchOdds(
                home=r["odds_home"], draw=r["odds_draw"], away=r["odds_away"],
                bookmaker=r["bookmaker"] or "Unknown",
            ),
            has_insights=bool(r["has_insights"]),
        ))
    return items


def db_stats() -> dict:
    """Zwraca podsumowanie zawartosci bazy (liczba meczow, ostatni refresh)."""
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
        ready = conn.execute(
            "SELECT COUNT(*) FROM matches WHERE has_insights = 1"
        ).fetchone()[0]
        last_gen = conn.execute(
            "SELECT MAX(generated_at) FROM matches WHERE generated_at IS NOT NULL"
        ).fetchone()[0]
    return {
        "matches_total": total,
        "matches_with_insights": ready,
        "last_insights_generated_at": last_gen,
    }


def get_match_meta(match_id: str) -> Optional[MatchListItem]:
    """Skrocony rekord meczu (bez insights)."""
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, home_team, away_team, league, kick_off,
                   bookmaker, odds_home, odds_draw, odds_away, has_insights
            FROM matches WHERE id = ?
            """, (match_id,),
        ).fetchone()
    if not row:
        return None
    from ..models.schemas import MatchOdds
    return MatchListItem(
        id=row["id"],
        home_team=row["home_team"],
        away_team=row["away_team"],
        league=row["league"],
        kick_off=datetime.fromisoformat(row["kick_off"]),
        odds=MatchOdds(
            home=row["odds_home"], draw=row["odds_draw"], away=row["odds_away"],
            bookmaker=row["bookmaker"] or "Unknown",
        ),
        has_insights=bool(row["has_insights"]),
    )
