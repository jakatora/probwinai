"""CLI: generuje statyczne pliki JSON z top 10 meczow + insights.

Idea: zastepuje 'live' API. GitHub Actions uruchamia ten skrypt codziennie,
zapisuje wynik do docs/data/, commit do repo, GitHub Pages serwuje.

Aplikacja mobilna pobiera HTTPS GET ze statycznego URL - zero serwera, zero kosztow.

Uzycie (lokalnie):
    py scripts/export_static_json.py --top 10
    py scripts/export_static_json.py --top 10 --no-ai

Uzycie (CI):
    py scripts/export_static_json.py --top 10  # klucze API w env
"""
import argparse
import io
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from backend.config import ROOT
from backend.data import odds_api
from backend.models.schemas import MatchInput
from backend.services.insights_service import InsightsService
from backend.services.popularity import rank_matches


OUTPUT_DIR = ROOT / "docs" / "data"


def main() -> int:
    ap = argparse.ArgumentParser(description="ProbWin AI - export statycznych JSON")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--no-ai", action="store_true", help="Pomin generowanie komentarza AI (oszczedzanie kosztow API)")
    ap.add_argument("--output", default=str(OUTPUT_DIR),
                    help=f"Folder wyjsciowy (domyslnie {OUTPUT_DIR})")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    matches_dir = output_dir / "matches"
    matches_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{time.strftime('%H:%M:%S')}] Pobieram nadchodzace mecze...")
    matches = odds_api.fetch_upcoming()
    print(f"  zrodlo zwrocilo {len(matches)} meczow")

    top_matches = rank_matches(matches, top_n=args.top)
    print(f"  wybieram top {len(top_matches)} wg popularnosci")

    service = InsightsService(history_seasons=3)

    print(f"\n[{time.strftime('%H:%M:%S')}] Generuje insights...")
    full_data = {
        "version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "matches": [],
    }

    # Pojedyncze pliki per match + jeden big file
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

            insights_dict = insights.model_dump(mode="json")
            insights_dict["id"] = m.id  # dodaj id do pelnego JSONa

            # Zapisz pojedynczy plik per mecz
            single_path = matches_dir / f"{m.id}.json"
            single_path.write_text(
                json.dumps(insights_dict, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            # Dodaj do listy zbiorczej (skrocona wersja)
            full_data["matches"].append({
                "id": m.id,
                "home_team": m.home_team,
                "away_team": m.away_team,
                "league": m.league,
                "kick_off": m.kick_off.isoformat(),
                "odds": m.odds.model_dump(),
                "has_insights": True,
            })

            edges = insights.edges()
            print(f"  [{i}/{len(top_matches)}] {m.home_team} vs {m.away_team}: "
                  f"P({insights.model_probability.home:.0%}/{insights.model_probability.draw:.0%}/{insights.model_probability.away:.0%}) "
                  f"edge({edges['home']*100:+.0f}/{edges['draw']*100:+.0f}/{edges['away']*100:+.0f})")
        except Exception as e:
            logging.exception("Blad dla %s vs %s: %s", m.home_team, m.away_team, e)

    # Zapisz zbiorczy plik top10.json
    top10_path = output_dir / "top10.json"
    top10_path.write_text(
        json.dumps(full_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\n[{time.strftime('%H:%M:%S')}] Gotowe!")
    print(f"  Lista: {top10_path}")
    print(f"  Pojedyncze: {matches_dir}/ ({len(top_matches)} plikow)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
