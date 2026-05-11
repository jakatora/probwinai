"""Renderowanie MatchInsights do HTML uzywajac Jinja2."""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..config import ROOT
from ..models.schemas import MatchInsights


TEMPLATE_DIR = ROOT / "backend" / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_report(insights: MatchInsights) -> str:
    """Zwraca HTML raportu jako string."""
    template = _env.get_template("report.html.j2")
    return template.render(insights=insights)


def write_report(insights: MatchInsights, output_path: Path) -> Path:
    """Zapisuje HTML raportu do pliku. Zwraca sciezke."""
    html = render_report(insights)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path
