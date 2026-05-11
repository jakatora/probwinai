"""Pytest fixtures."""
import sys
from pathlib import Path

# Dodaj katalog projektu do sys.path zeby `from backend.* import ...` dzialalo
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
