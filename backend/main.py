"""FastAPI - REST API dla aplikacji mobilnej i web preview.

Endpointy:
    GET  /api/health              - health check
    GET  /api/matches             - lista meczow (top N)
    GET  /api/matches/{id}        - pelne insights dla jednego meczu
    GET  /matches/{id}            - render HTML raportu (do podgladu w przegladarce)
    POST /api/refresh             - manualny refresh top N (zwykle robi cron)

Uruchom:
    uvicorn backend.main:app --reload --port 8000
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings, ROOT
from .db.database import (
    init_db, get_insights, list_matches, save_match_list, save_insights,
    get_match_meta, db_stats,
)
from .data import odds_api
from .models.schemas import MatchInsights, MatchInput, MatchListItem, utcnow
from .services.insights_service import InsightsService
from .services.popularity import rank_matches
from .services.reporting import render_report

log = logging.getLogger(__name__)


# Globalny serwis - tworzony raz przy starcie
_service: Optional[InsightsService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _service
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    init_db()
    try:
        _service = InsightsService(history_seasons=3)
    except Exception as e:
        log.warning("Nie udalo sie zainicjalizowac serwisu: %s", e)
        _service = None
    yield


app = FastAPI(
    title="ProbWin AI API",
    description="Sport analytics z prawdopodobienstwami i komentarzem AI",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Health & info ----

class HealthResponse(BaseModel):
    status: str
    version: str
    has_anthropic_key: bool
    has_odds_key: bool
    db_path: str
    matches_total: int
    matches_with_insights: int
    last_insights_generated_at: Optional[str] = None


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    stats = db_stats()
    return HealthResponse(
        status="ok",
        version=app.version,
        has_anthropic_key=bool(settings.anthropic_api_key),
        has_odds_key=bool(settings.odds_api_key),
        db_path=str(settings.db_path_abs),
        matches_total=stats["matches_total"],
        matches_with_insights=stats["matches_with_insights"],
        last_insights_generated_at=stats["last_insights_generated_at"],
    )


# ---- Lista meczow ----

@app.get("/api/matches", response_model=list[MatchListItem])
def get_matches(limit: int = 50, only_with_insights: bool = False) -> list[MatchListItem]:
    """Lista meczow z bazy. Wywolaj /api/refresh zeby pobrac swieze dane."""
    return list_matches(only_with_insights=only_with_insights, limit=limit)


@app.get("/api/matches/{match_id}", response_model=MatchInsights)
def get_match_insights(match_id: str) -> MatchInsights:
    """Pelny raport (z komentarzem AI) dla jednego meczu."""
    insights = get_insights(match_id)
    if insights is None:
        raise HTTPException(status_code=404, detail=f"Match insights not found: {match_id}")
    return insights


# ---- HTML preview (do przegladarki/dev) ----

@app.get("/matches/{match_id}", response_class=HTMLResponse)
def get_match_html(match_id: str) -> HTMLResponse:
    """Render HTML raportu - do podgladu w przegladarce."""
    insights = get_insights(match_id)
    if insights is None:
        raise HTTPException(status_code=404, detail=f"Match insights not found: {match_id}")
    return HTMLResponse(render_report(insights))


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    """Strona startowa - lista meczow w prostym HTML."""
    matches = list_matches(limit=50)
    rows = ""
    for m in matches:
        edge_class = "value" if m.has_insights else "pending"
        rows += f"""
        <tr>
            <td>{m.kick_off.strftime('%Y-%m-%d %H:%M')}</td>
            <td>{m.home_team}</td>
            <td>vs</td>
            <td>{m.away_team}</td>
            <td>{m.league}</td>
            <td>{m.odds.home:.2f} / {m.odds.draw:.2f} / {m.odds.away:.2f}</td>
            <td>{'<a href="/matches/' + m.id + '">Raport</a>' if m.has_insights else 'pending'}</td>
        </tr>
        """
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>ProbWin AI</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #0f1419; color: #e6edf3; padding: 24px; max-width: 1100px; margin: 0 auto; }}
        h1 {{ font-size: 24px; }} .sub {{ color: #8b9bab; font-size: 14px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 24px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #2d3748; }}
        th {{ color: #8b9bab; font-size: 12px; text-transform: uppercase; }}
        a {{ color: #60a5fa; text-decoration: none; }} a:hover {{ text-decoration: underline; }}
        .empty {{ padding: 40px; text-align: center; color: #8b9bab; }}
    </style></head><body>
    <h1>ProbWin AI</h1>
    <div class="sub">Sport analytics z prawdopodobienstwami i komentarzem AI &middot; {len(matches)} meczow</div>
    {'<table><thead><tr><th>Kick-off</th><th>Gospodarz</th><th></th><th>Gosc</th><th>Liga</th><th>1X2</th><th>Raport</th></tr></thead><tbody>' + rows + '</tbody></table>' if matches else '<div class="empty">Brak meczow w bazie. Uruchom: <code>py scripts/refresh_daily.py</code></div>'}
    </body></html>
    """)


# ---- Manualny refresh ----

class RefreshResponse(BaseModel):
    matches_fetched: int
    insights_generated: int
    started_at: datetime
    finished_at: datetime


@app.post("/api/refresh", response_model=RefreshResponse)
def refresh(top: int = settings.top_n_matches, with_ai: bool = True) -> RefreshResponse:
    """Manualny refresh top N meczow. Normalnie robi to cron (refresh_daily.py)."""
    if _service is None:
        raise HTTPException(status_code=503, detail="InsightsService not initialized")

    started = utcnow()
    all_matches = odds_api.fetch_upcoming()
    matches = rank_matches(all_matches, top_n=top)
    save_match_list(matches)

    generated = 0
    for m in matches:
        try:
            mi = MatchInput(
                home_team=m.home_team, away_team=m.away_team,
                league=m.league, kick_off=m.kick_off, odds=m.odds,
            )
            insights = _service.generate(mi, with_ai=with_ai)
            save_insights(m.id, insights)
            generated += 1
        except Exception as e:
            log.exception("Refresh error for %s: %s", m.id, e)

    return RefreshResponse(
        matches_fetched=len(matches),
        insights_generated=generated,
        started_at=started,
        finished_at=utcnow(),
    )
