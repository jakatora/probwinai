"""Konwersja ratingu Elo -> prawdopodobienstwa + kurs -> implikowane P.

Wartosci stalych skalibrowane empirycznie na Premier League 2021-25.
HOME_ADVANTAGE obnizone z 70 do 55 - obserwowany trend ostatnich lat
(po pandemii home advantage zmalal w wiekszosci lig).
"""
import math
from .schemas import Probability

HOME_ADVANTAGE = 55          # Bonus dla gospodarza w pkt Elo
DRAW_WIDTH = 200             # Szerokosc gaussiana dla remisow
MAX_DRAW_PROB = 0.28         # Max P(remis) gdy druzyny rownorzedne
MIN_DRAW_PROB = 0.08         # Min P(remis) - empirycznie nawet w mismatchu
MIN_OUTCOME_PROB = 0.02      # Zaden wynik nie schodzi ponizej 2%


def elo_to_probability(elo_home: float, elo_away: float) -> Probability:
    """Bazowy model Elo z modelowaniem remisu jako gaussa + bounds.

    Zwraca rozsadne wartosci nawet przy ekstremalnych roznicach Elo
    (przed bound: P(remis) -> 0 dla |diff| > 400; po bound: >= 8%).
    """
    diff = (elo_home + HOME_ADVANTAGE) - elo_away
    p_home_raw = 1.0 / (1.0 + 10 ** (-diff / 400.0))
    p_away_raw = 1.0 - p_home_raw

    # P(remis) - gaussian centrowany w diff=0, ale bounded min/max
    p_draw_raw = math.exp(-(diff / DRAW_WIDTH) ** 2) * MAX_DRAW_PROB
    p_draw = max(MIN_DRAW_PROB, min(MAX_DRAW_PROB, p_draw_raw))

    # Rozdzielenie pozostalego prawdopodobienstwa na home/away
    remaining = 1.0 - p_draw
    p_home = p_home_raw * remaining
    p_away = p_away_raw * remaining

    # Bound dolny dla home/away (zeby nie schodzili ponizej MIN_OUTCOME_PROB)
    p_home = max(MIN_OUTCOME_PROB, p_home)
    p_away = max(MIN_OUTCOME_PROB, p_away)

    # Renormalizacja po boundach
    total = p_home + p_draw + p_away
    return Probability(
        home=p_home / total,
        draw=p_draw / total,
        away=p_away / total,
    )


def odds_to_implied(o_home: float, o_draw: float, o_away: float) -> tuple[Probability, float]:
    """Kurs decimal -> implikowane prawdopodobienstwo (znormalizowane). Zwraca tez vig%."""
    raw = [1.0 / o_home, 1.0 / o_draw, 1.0 / o_away]
    s = sum(raw)
    vig_pct = (s - 1.0) * 100
    return (
        Probability(home=raw[0] / s, draw=raw[1] / s, away=raw[2] / s),
        vig_pct,
    )
