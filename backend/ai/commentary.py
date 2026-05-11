"""Generowanie komentarza AI dla meczu (Claude API + web search).

Wykorzystuje narzedzie web_search Claude API zeby agent sam znalazl
swieze newsy o meczu (kontuzje, sklady, motywacja) i zwracal zwiezly
komentarz analityczny w jezyku polskim.

Jesli brak klucza ANTHROPIC_API_KEY -> zwraca komentarz mockowy oparty
o liczby (Elo, formy) zeby aplikacja dzialala bez zewnetrznych uslug.
"""
import logging
from typing import Optional

from ..config import settings
from ..models.schemas import MatchInsights

log = logging.getLogger(__name__)

# Claude SDK importujemy leniwie, zeby aplikacja dzialala bez zainstalowanego
# pakietu anthropic dla scenariuszy mockowych
_anthropic_client = None


def _client():
    global _anthropic_client
    if _anthropic_client is None:
        try:
            from anthropic import Anthropic
            _anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
        except ImportError:
            log.warning("Pakiet anthropic nie zainstalowany - komentarze mock")
            return None
    return _anthropic_client


COMMENTARY_PROMPT = """Jestes analitykiem sportowym aplikacji ProbWin AI.
Twoje zadanie: napisac krotki (3-4 zdania, max 400 znakow) komentarz
analityczny do meczu pilkarskiego.

Mecz: {home} vs {away} ({league})
Data: {kick_off}

Dane statystyczne:
- Rating Elo gospodarza: {elo_home}
- Rating Elo goscia: {elo_away}
- Forma gospodarza (ostatnie 5): {form_home}
- Forma goscia (ostatnie 5): {form_away}
- H2H (ostatnie spotkania): {h2h}

Kurs Betclic: 1={odds_home}, X={odds_draw}, 2={odds_away}
Model ProbWin AI: 1={prob_home:.0%}, X={prob_draw:.0%}, 2={prob_away:.0%}

Sprawdz w internecie najnowsze newsy o tym meczu z ostatnich 48h:
kontuzje, zmiany w skladach, motywacja (np. mecz o utrzymanie), formy
zawodnikow kluczowych.

W komentarzu:
1. Wskaz 1-2 kluczowe czynniki ktore wplywaja na wynik
2. Wyjasnij dlaczego model i bukmacher moga sie roznic (jesli sie roznia)
3. Pisz po polsku, zwiezle, faktycznie. Bez wykrzyknikow, bez emoji.
4. NIE rekomenduj zakladu. To komentarz analityczny, nie typ.
"""


def generate_commentary(insights: MatchInsights) -> str:
    """Generuje komentarz AI dla meczu. Fallback do mocka bez klucza."""
    if not settings.anthropic_api_key:
        return _mock_commentary(insights)

    client = _client()
    if client is None:
        return _mock_commentary(insights)

    prompt = _build_prompt(insights)

    try:
        # Uzywamy web_search do swiezych newsow
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 3,
            }],
        )
    except Exception as e:
        log.warning("Claude API error: %s. Uzywam mocku.", e)
        return _mock_commentary(insights)

    # Wyciagnij tekst z odpowiedzi (omijajac bloki tool_use)
    text_parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            text_parts.append(block.text)
    return "\n".join(text_parts).strip() or _mock_commentary(insights)


def _build_prompt(insights: MatchInsights) -> str:
    form_home = (
        "".join(insights.home_context.form.results) if insights.home_context.form else "brak"
    )
    form_away = (
        "".join(insights.away_context.form.results) if insights.away_context.form else "brak"
    )
    h2h_str = (
        ", ".join(f"{m.home_team} {m.result_string()} {m.away_team} ({m.date})" for m in insights.h2h)
        or "brak danych H2H"
    )
    return COMMENTARY_PROMPT.format(
        home=insights.home_team,
        away=insights.away_team,
        league=insights.league,
        kick_off=insights.kick_off.strftime("%Y-%m-%d %H:%M"),
        elo_home=f"{insights.home_context.elo:.0f}" if insights.home_context.elo else "n/a",
        elo_away=f"{insights.away_context.elo:.0f}" if insights.away_context.elo else "n/a",
        form_home=form_home,
        form_away=form_away,
        h2h=h2h_str,
        odds_home=insights.bookmaker_odds.home,
        odds_draw=insights.bookmaker_odds.draw,
        odds_away=insights.bookmaker_odds.away,
        prob_home=insights.model_probability.home,
        prob_draw=insights.model_probability.draw,
        prob_away=insights.model_probability.away,
    )


def _mock_commentary(ins: MatchInsights) -> str:
    """Komentarz oparty wylacznie na liczbach (bez zewnetrznych API)."""
    home_form = ins.home_context.form
    away_form = ins.away_context.form

    parts: list[str] = []

    # Akapit 1: porownanie sil
    if ins.home_context.elo and ins.away_context.elo:
        diff = ins.home_context.elo - ins.away_context.elo
        if abs(diff) > 100:
            stronger = ins.home_team if diff > 0 else ins.away_team
            parts.append(f"Wyrazna roznica klas: {stronger} ma ratingi Elo wyzsze o {abs(diff):.0f} pkt.")
        else:
            parts.append("Rownorzedne ratingi Elo - mecz wyrownany na papierze.")

    # Akapit 2: forma
    form_parts = []
    if home_form:
        wins = home_form.results.count("W")
        form_parts.append(f"{ins.home_team} ma {wins}/{home_form.last_n} zwyciestw w ostatnich meczach")
    if away_form:
        wins = away_form.results.count("W")
        form_parts.append(f"{ins.away_team} {wins}/{away_form.last_n}")
    if form_parts:
        parts.append(", ".join(form_parts) + ".")

    # Akapit 3: porownanie z kursem
    edges = ins.edges()
    biggest_edge = max(edges.items(), key=lambda x: abs(x[1]))
    if abs(biggest_edge[1]) > 0.05:
        direction = "wyzej" if biggest_edge[1] > 0 else "nizej"
        outcome_label = {"home": "wygrana gospodarza", "draw": "remis", "away": "wygrana goscia"}[biggest_edge[0]]
        parts.append(
            f"Model wycenia '{outcome_label}' o {abs(biggest_edge[1]) * 100:.0f}pp {direction} "
            f"niz kurs bukmachera - mozliwe ze rynek inaczej ocenia kontekst meczu."
        )
    else:
        parts.append("Model i bukmacher zgodni - kurs odpowiada modelowemu prawdopodobienstwu.")

    parts.append("(Komentarz wygenerowany na podstawie statystyk - brak klucza Claude API.)")
    return " ".join(parts)
