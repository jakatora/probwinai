"""Globalne ustawienia z .env (lub zmiennych srodowiskowych)."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str = ""
    odds_api_key: str = ""
    odds_api_region: str = "eu"
    odds_api_sport: str = "soccer_epl"
    top_n_matches: int = 10
    database_path: str = "backend/db/probwin.sqlite"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    elo_cache_path: str = "backend/data/elo_cache.json"
    allowed_origins: str = "*"

    @property
    def cors_origins(self) -> list[str]:
        """Parsuje ALLOWED_ORIGINS (comma-separated) na liste."""
        if self.allowed_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def db_path_abs(self) -> Path:
        """Sciezka absolutna do DB - obsluguje zarowno relatywne jak i absolutne path."""
        p = Path(self.database_path)
        return p if p.is_absolute() else ROOT / p

    @property
    def elo_cache_path_abs(self) -> Path:
        p = Path(self.elo_cache_path)
        return p if p.is_absolute() else ROOT / p


settings = Settings()
