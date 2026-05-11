"""CLI: usuwa raporty HTML starsze niz N dni.

Uzycie:
    py scripts/cleanup_reports.py            # domyslnie 14 dni
    py scripts/cleanup_reports.py --days 7
"""
import argparse
import io
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from backend.config import ROOT


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14, help="Wiek pliku do usuniecia (dni)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    reports_dir = ROOT / "reports"
    if not reports_dir.exists():
        print("Brak folderu reports/. Nic do zrobienia.")
        return 0

    cutoff = time.time() - args.days * 86400
    removed = 0
    kept = 0
    for p in reports_dir.glob("*.html"):
        if p.stat().st_mtime < cutoff:
            if args.dry_run:
                print(f"  [dry-run] usunalbym: {p.name}")
            else:
                p.unlink()
                print(f"  usunieto: {p.name}")
            removed += 1
        else:
            kept += 1

    print(f"\n{'[dry-run] ' if args.dry_run else ''}Usunieto: {removed}, zachowano: {kept}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
