"""
ProbWin AI - rdzen modelu probabilistycznego.
Zawiera funkcje konwersji Elo -> prawdopodobienstwo i kursu -> implikowane P.
"""
import math

# Przewaga gospodarzy w punktach Elo (literatura: 65-100)
HOME_ADVANTAGE = 70

# Szerokosc strefy remisu (im wieksza, tym wiecej remisow przewiduje model)
DRAW_WIDTH = 100

# Maksymalny udzial remisu (przy diff=0). 30% to typowa wartosc w pilce
MAX_DRAW_PROB = 0.30


def elo_to_probabilities(elo_home: float, elo_away: float) -> tuple[float, float, float]:
    """Konwertuje ratingi Elo na prawdopodobienstwa 1/X/2."""
    elo_home_adj = elo_home + HOME_ADVANTAGE
    diff = elo_home_adj - elo_away

    p_home_raw = 1.0 / (1.0 + 10 ** (-diff / 400.0))
    p_away_raw = 1.0 - p_home_raw

    p_draw = math.exp(-(diff / DRAW_WIDTH) ** 2) * MAX_DRAW_PROB

    remaining = 1.0 - p_draw
    return p_home_raw * remaining, p_draw, p_away_raw * remaining


def odds_to_implied_probabilities(o1: float, ox: float, o2: float) -> tuple[float, float, float, float]:
    """Kurs decimal -> implikowane prawdopodobienstwo (znormalizowane) + marza vig%."""
    raw = [1.0 / o1, 1.0 / ox, 1.0 / o2]
    s = sum(raw)
    vig_pct = (s - 1.0) * 100
    return raw[0] / s, raw[1] / s, raw[2] / s, vig_pct
