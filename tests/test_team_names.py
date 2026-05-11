"""Testy slownika nazw druzyn."""
from backend.data.team_names import clubelo_slug


def test_known_alias():
    assert clubelo_slug("Aston Villa") == "AstonVilla"
    assert clubelo_slug("Man United") == "ManUnited"
    assert clubelo_slug("Nott'm Forest") == "Forest"


def test_full_name_alias():
    assert clubelo_slug("Manchester United") == "ManUnited"
    assert clubelo_slug("Tottenham Hotspur") == "Tottenham"


def test_unknown_team_fallback():
    """Nieznana druzyna -> usuniete spacje/apostrofy."""
    assert clubelo_slug("Random FC") == "RandomFC"
    assert clubelo_slug("Real Madrid") == "RealMadrid"


def test_no_spaces_or_special_chars():
    """Slug nigdy nie zawiera spacji/apostrofow/myslnikow."""
    for name in ["Aston Villa", "Nott'm Forest", "West-Ham", "AFC Bournemouth"]:
        slug = clubelo_slug(name)
        assert " " not in slug
        assert "'" not in slug
        assert "-" not in slug
