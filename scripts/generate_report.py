"""CLI: generuje raport HTML dla jednego meczu.

Uzycie:
    py scripts/generate_report.py "Aston Villa" "Liverpool" 3.10 3.90 2.05
    py scripts/generate_report.py "Aston Villa" "Liverpool" 3.10 3.90 2.05 --date 2026-05-17 --no-ai
"""
import argparse
import io
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Dolacz katalog projektu do sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from backend.config import ROOT
from backend.models.schemas import MatchInput, MatchOdds
from backend.services.insights_service import InsightsService
from backend.services.reporting import write_report


def main() -> int:
    ap = argparse.ArgumentParser(description="ProbWin AI - generator raportu dla 1 meczu")
    ap.add_argument("home", help="Druzyna gospodarzy")
    ap.add_argument("away", help="Druzyna goscia")
    ap.add_argument("odds_home", type=float, help="Kurs Betclic na 1")
    ap.add_argument("odds_draw", type=float, help="Kurs Betclic na X")
    ap.add_argument("odds_away", type=float, help="Kurs Betclic na 2")
    ap.add_argument("--date", help="Data meczu (YYYY-MM-DD), domyslnie dzis", default=None)
    ap.add_argument("--time", help="Godzina meczu (HH:MM), domyslnie 18:00", default="18:00")
    ap.add_argument("--league", default="Premier League")
    ap.add_argument("--league-code", default="E0",
                    help="Kod ligi football-data (E0/SP1/I1/D1/F1)")
    ap.add_argument("--output", "-o", default=None,
                    help="Sciezka pliku HTML (domyslnie reports/{home}_vs_{away}_{date}.html)")
    ap.add_argument("--no-ai", action="store_true", help="Pomin generowanie komentarza AI")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # Parsowanie daty
    if args.date:
        date_part = datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        date_part = datetime.now(timezone.utc).date()
    time_part = datetime.strptime(args.time, "%H:%M").time()
    kick_off = datetime.combine(date_part, time_part).replace(tzinfo=timezone.utc)

    match = MatchInput(
        home_team=args.home,
        away_team=args.away,
        league=args.league,
        kick_off=kick_off,
        odds=MatchOdds(
            home=args.odds_home,
            draw=args.odds_draw,
            away=args.odds_away,
            bookmaker="Betclic",
        ),
    )

    print(f"Generuje raport dla: {match.home_team} vs {match.away_team} ({kick_off.date()})")
    service = InsightsService(history_seasons=3, league_code=args.league_code)
    insights = service.generate(match, with_ai=not args.no_ai)

    # Output
    if args.output:
        output = Path(args.output)
    else:
        output_dir = ROOT / "reports"
        slug = f"{args.home.replace(' ', '-').lower()}_vs_{args.away.replace(' ', '-').lower()}_{date_part.isoformat()}.html"
        output = output_dir / slug
    output_path = write_report(insights, output)

    print(f"\nRaport zapisany: {output_path}")
    print(f"  Model probability: 1={insights.model_probability.home:.0%} "
          f"X={insights.model_probability.draw:.0%} "
          f"2={insights.model_probability.away:.0%}")
    edges = insights.edges()
    print(f"  Edge: 1={edges['home'] * 100:+.1f}% "
          f"X={edges['draw'] * 100:+.1f}% "
          f"2={edges['away'] * 100:+.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
