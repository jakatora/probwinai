"""CLI: codzienne odswiezenie - pobiera top N nadchodzacych meczow,
generuje insights, zapisuje do bazy i tworzy raporty HTML.

Uzycie:
    py scripts/refresh_daily.py
    py scripts/refresh_daily.py --top 10 --no-ai
"""
import argparse
import io
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from backend.config import ROOT, settings
from backend.data import odds_api
from backend.db.database import init_db, save_match_list, save_insights
from backend.models.schemas import MatchInput
from backend.services.insights_service import InsightsService
from backend.services.popularity import rank_matches
from backend.services.reporting import write_report


def main() -> int:
    ap = argparse.ArgumentParser(description="ProbWin AI - codzienne odswiezenie top N")
    ap.add_argument("--top", type=int, default=settings.top_n_matches,
                    help=f"Ile meczow przetworzyc (domyslnie {settings.top_n_matches})")
    ap.add_argument("--no-ai", action="store_true", help="Pomin generowanie komentarza AI")
    ap.add_argument("--no-html", action="store_true", help="Nie zapisuj plikow HTML")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    print(f"[{time.strftime('%H:%M:%S')}] Inicjalizacja bazy danych...")
    init_db()

    print(f"[{time.strftime('%H:%M:%S')}] Pobieram nadchodzace mecze...")
    matches = odds_api.fetch_upcoming()
    print(f"  znaleziono {len(matches)} meczow")

    # Ranking 'popularnosci' (waga ligi + popularne kluby + derby + niska marza)
    top_matches = rank_matches(matches, top_n=args.top)
    print(f"  wybieram top {len(top_matches)} wg score popularnosci")

    saved = save_match_list(top_matches)
    print(f"  zapisano {saved} rekordow do bazy")

    service = InsightsService(history_seasons=3)

    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)

    print(f"\n[{time.strftime('%H:%M:%S')}] Generuje insights dla {len(top_matches)} meczow...")
    for i, m in enumerate(top_matches, 1):
        try:
            match_input = MatchInput(
                home_team=m.home_team,
                away_team=m.away_team,
                league=m.league,
                kick_off=m.kick_off,
                odds=m.odds,
            )
            insights = service.generate(match_input, with_ai=not args.no_ai)
            save_insights(m.id, insights)

            if not args.no_html:
                slug = m.id + ".html"
                write_report(insights, reports_dir / slug)

            edges = insights.edges()
            print(f"  [{i}/{len(top_matches)}] {m.home_team} vs {m.away_team}: "
                  f"P({insights.model_probability.home:.0%}/{insights.model_probability.draw:.0%}/{insights.model_probability.away:.0%}) "
                  f"edge({edges['home']*100:+.0f}/{edges['draw']*100:+.0f}/{edges['away']*100:+.0f})")
        except Exception as e:
            logging.exception("Blad dla %s vs %s: %s", m.home_team, m.away_team, e)

    print(f"\n[{time.strftime('%H:%M:%S')}] Gotowe. Raporty: {reports_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
