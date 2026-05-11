"""Klient Clubelo.com - historyczne ratingi Elo klubow pilkarskich.

API: http://api.clubelo.com/{slug}  -> CSV z historia Elo
     http://api.clubelo.com/{YYYY-MM-DD}  -> snapshot wszystkich klubow

Cache na dysku (JSON) zeby kolejne uruchomienia nie pobieraly tych samych danych.
"""
import csv
import io
import json
import logging
import sys
from datetime import datetime, date as Date
from pathlib import Path
from typing import Optional

import requests

from ..config import settings
from .team_names import clubelo_slug

log = logging.getLogger(__name__)

CLUBELO_BASE = "http://api.clubelo.com"

# In-memory cache: {slug: [(from_date, to_date, elo), ...]}
_cache: dict[str, list[tuple[Date, Date, float]]] = {}
_missing: set[str] = set()


def _cache_path() -> Path:
    return settings.elo_cache_path_abs


def load_cache() -> int:
    """Wczytuje cache z pliku JSON. Zwraca liczbe wczytanych druzyn."""
    path = _cache_path()
    if not path.exists():
        return 0
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        log.warning("Cache Clubelo nieczytelny: %s", e)
        return 0
    for slug, rows in raw.items():
        _cache[slug] = [
            (Date.fromisoformat(r["from"]), Date.fromisoformat(r["to"]), float(r["elo"]))
            for r in rows
        ]
    log.info("Wczytano cache Clubelo: %d druzyn", len(_cache))
    return len(_cache)


def save_cache() -> None:
    """Zapisuje cache na dysk."""
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = {
        slug: [{"from": f.isoformat(), "to": t.isoformat(), "elo": e}
               for (f, t, e) in rows]
        for slug, rows in _cache.items()
    }
    path.write_text(json.dumps(raw), encoding="utf-8")


def fetch_history(team_name: str) -> list[tuple[Date, Date, float]]:
    """Pobiera pelna historie Elo danej druzyny (z cache lub HTTP)."""
    slug = clubelo_slug(team_name)
    if slug in _cache:
        return _cache[slug]
    if slug in _missing:
        return []

    url = f"{CLUBELO_BASE}/{slug}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        log.warning("Clubelo niedostepne dla %s: %s", slug, e)
        _missing.add(slug)
        return []

    rows = []
    for row in csv.DictReader(io.StringIO(r.text)):
        try:
            rows.append((
                datetime.strptime(row["From"], "%Y-%m-%d").date(),
                datetime.strptime(row["To"], "%Y-%m-%d").date(),
                float(row["Elo"]),
            ))
        except (KeyError, ValueError):
            continue

    if not rows:
        _missing.add(slug)
    _cache[slug] = rows
    return rows


def get_elo(team_name: str, on_date: Optional[Date] = None) -> Optional[float]:
    """Zwraca Elo druzyny obowiazujace w danym dniu (lub aktualne)."""
    history = fetch_history(team_name)
    if not history:
        return None
    target = on_date or Date.today()

    for from_d, to_d, elo in history:
        if from_d <= target <= to_d:
            return elo

    # Fallback: ostatni okres przed targetem
    last_before = None
    for from_d, to_d, elo in history:
        if to_d < target:
            last_before = elo
    if last_before is not None:
        return last_before

    # Druga proba: jesli target jest przed historia, wez najstarszy znany
    return history[0][2] if history else None
