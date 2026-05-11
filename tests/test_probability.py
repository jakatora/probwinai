"""Testy modelu probabilistycznego."""
import math
import pytest

from backend.models.probability import (
    HOME_ADVANTAGE, elo_to_probability, odds_to_implied,
)


class TestEloToProbability:
    def test_equal_teams_home_favored(self):
        """Gdy obie druzyny maja te sama Elo, gospodarz ma przewage."""
        p = elo_to_probability(1500, 1500)
        assert p.home > p.away
        # Home advantage +70 daje ~10pp przewagi
        assert p.home - p.away > 0.05

    def test_probabilities_sum_to_one(self):
        """Prawdopodobienstwa zawsze sumuja sie do 1.0."""
        for elo_h in [1400, 1500, 1700, 2000]:
            for elo_a in [1400, 1500, 1700, 2000]:
                p = elo_to_probability(elo_h, elo_a)
                assert math.isclose(p.home + p.draw + p.away, 1.0, abs_tol=0.001)

    def test_stronger_home_team_higher_prob(self):
        """Silniejsza druzyna domowa ma wyzsze P niz slabsza."""
        weak_strong = elo_to_probability(1500, 1900)
        strong_weak = elo_to_probability(1900, 1500)
        assert strong_weak.home > weak_strong.home

    def test_extreme_diff_draw_low(self):
        """Przy bardzo duzej roznicy Elo P remisu jest niskie."""
        p = elo_to_probability(2000, 1400)
        assert p.draw < 0.10  # mismatch -> rzadki remis
        assert p.home > 0.85  # gospodarz silnie faworyzowany

    def test_no_negative_probability(self):
        """Zadne P nie moze byc < 0."""
        for elo_h in range(1200, 2200, 100):
            for elo_a in range(1200, 2200, 100):
                p = elo_to_probability(elo_h, elo_a)
                assert p.home >= 0 and p.draw >= 0 and p.away >= 0

    def test_home_advantage_applied(self):
        """Bonus dla gospodarza zwieksza P home w stosunku do symetrycznej sytuacji."""
        p_eq = elo_to_probability(1500, 1500)
        # Bez home advantage: 50/draw/50. Z bonusem: home > away
        assert p_eq.home > 0.40
        assert p_eq.away < 0.40


class TestOddsToImplied:
    def test_fair_odds_no_vig(self):
        """Idealne kursy bez marzy."""
        # 3 rownie prawdopodobne wyniki -> kursy 3.00
        p, vig = odds_to_implied(3.0, 3.0, 3.0)
        assert math.isclose(p.home, 1/3, abs_tol=0.001)
        assert math.isclose(p.draw, 1/3, abs_tol=0.001)
        assert math.isclose(p.away, 1/3, abs_tol=0.001)
        assert math.isclose(vig, 0.0, abs_tol=0.001)

    def test_typical_vig(self):
        """Typowy bukmacher: marza ~5-8%."""
        p, vig = odds_to_implied(2.0, 3.5, 4.0)
        assert 2.0 < vig < 15.0

    def test_implied_sums_to_one(self):
        """Implikowane prawdopodobienstwa po normalizacji sumuja sie do 1."""
        p, _ = odds_to_implied(1.85, 3.50, 4.20)
        assert math.isclose(p.home + p.draw + p.away, 1.0, abs_tol=0.001)

    def test_lower_odds_higher_prob(self):
        """Im nizszy kurs, tym wyzsze implikowane P."""
        p, _ = odds_to_implied(1.5, 4.0, 6.0)
        assert p.home > p.draw > p.away


def test_home_advantage_constant():
    """Stala HOME_ADVANTAGE jest w sensownym zakresie."""
    assert 30 <= HOME_ADVANTAGE <= 120
