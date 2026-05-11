"""CLI: napelnia baze przykladowymi meczami z mocku (bez wywolan zewnetrznych API).

Sluzy do pokazania dziala aplikacji na czysto, gdy nie mamy
kluczy API. Po seed-zie mozesz uruchomic 'uvicorn backend.main:app'
i otworzyc http://localhost:8000 zeby zobaczyc dashboard z meczami.

Uzycie:
    py scripts/seed_demo.py
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from backend.data import odds_api
from backend.db.database import init_db, save_match_list, save_insights
from backend.models.schemas import MatchInput
from backend.services.insights_service import InsightsService
from backend.services.popularity import rank_matches


def main() -> int:
    print("Inicjalizuje DB...")
    init_db()

    print("Generuje mock matches...")
    matches = odds_api._mock_matches()
    top = rank_matches(matches, top_n=10)
    save_match_list(top)
    print(f"  zapisano {len(top)} meczow")

    print("Tworze insights (bez AI)...")
    service = InsightsService()
    for i, m in enumerate(top, 1):
        mi = MatchInput(
            home_team=m.home_team, away_team=m.away_team,
            league=m.league, kick_off=m.kick_off, odds=m.odds,
        )
        ins = service.generate(mi, with_ai=False)
        save_insights(m.id, ins)
        print(f"  [{i}/{len(top)}] {m.home_team} vs {m.away_team}")

    print("\nGotowe. Uruchom: uvicorn backend.main:app --reload")
    return 0


if __name__ == "__main__":
    sys.exit(main())
