"""
Create polished SVG visuals for the AI-assisted breeding portfolio repository.

The visuals are generated only from synthetic demonstration outputs already
present in the repository.
"""

from __future__ import annotations

import csv
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"

FONT = "Inter, Segoe UI, Arial, sans-serif"
INK = "#221B38"
MUTED = "#6A6177"
GRID = "#E5DFEC"
PURPLE = "#6A1B9A"
PLUM = "#8E24AA"
GREEN = "#1B5E20"
BLUE = "#1E88E5"
PAPER = "#FDFCFF"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(value: str) -> float:
    return float(value)


def write(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines), encoding="utf-8")


def defs() -> list[str]:
    return [
        "<defs>",
        '<linearGradient id="heroGradient" x1="0" y1="0" x2="1" y2="1">',
        '<stop offset="0%" stop-color="#2A0B45"/>',
        '<stop offset="60%" stop-color="#6A1B9A"/>',
        '<stop offset="100%" stop-color="#1B5E20"/>',
        "</linearGradient>",
        '<linearGradient id="softPurple" x1="0" y1="0" x2="1" y2="0">',
        '<stop offset="0%" stop-color="#6A1B9A"/>',
        '<stop offset="100%" stop-color="#1E88E5"/>',
        "</linearGradient>",
        '<filter id="softShadow" x="-10%" y="-10%" width="120%" height="130%">',
        '<feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#2A0B45" flood-opacity="0.14"/>',
        "</filter>",
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#6A1B9A"/></marker>',
        "</defs>",
    ]


def text(x: float, y: float, value: str, size: int = 16, weight: int = 400, fill: str = INK, anchor: str = "start") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(value)}</text>'
    )


def rounded_rect(x: float, y: float, w: float, h: float, fill: str, stroke: str = "none", radius: int = 22) -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def overall_metrics() -> list[dict[str, str]]:
    return [row for row in read_csv(OUTPUT_DIR / "cross_validation_metrics.csv") if row["fold"] == "overall"]


def portfolio_overview() -> None:
    metrics = overall_metrics()
    top_candidates = read_csv(OUTPUT_DIR / "top_selection_candidates.csv")[:4]
    marker_effects = read_csv(OUTPUT_DIR / "marker_effects_yield.csv")[:5]
    width, height = 1180, 560
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title id=\"title\">AI-assisted breeding portfolio overview</title>",
        "<desc id=\"desc\">Synthetic breeding workflow summary with cross-validation metrics, marker effects, candidate ranking, and workflow stages.</desc>",
        *defs(),
        f'<rect width="{width}" height="{height}" rx="28" fill="{PAPER}"/>',
        '<rect x="28" y="28" width="1124" height="160" rx="28" fill="url(#heroGradient)" filter="url(#softShadow)"/>',
        text(62, 84, "AI-assisted breeding selection", 30, 500, "#FFFFFF"),
        text(62, 126, "Synthetic marker data → prediction models → multi-trait selection index", 17, 400, "#F1E8F8"),
        text(62, 162, "Portfolio demonstration for genomic-prediction and crop-improvement roles", 14, 400, "#E6D8F0"),
    ]
    display_metrics = [
        ("Yield R²", metrics[0]["r2"], metrics[0]["correlation"]),
        ("Disease R²", metrics[1]["r2"], metrics[1]["correlation"]),
        ("Vigor R²", metrics[3]["r2"], metrics[3]["correlation"]),
    ]
    for i, (label, r2, corr) in enumerate(display_metrics):
        x = 694 + i * 142
        lines.append(rounded_rect(x, 70, 122, 88, "#FFFFFF", "none", 18))
        lines.append(text(x + 16, 100, label, 13, 500, MUTED))
        lines.append(text(x + 16, 130, r2, 24, 500, PURPLE))
        lines.append(text(x + 16, 150, f"corr {corr}", 11, 400, MUTED))

    lines.extend([
        rounded_rect(36, 220, 525, 284, "#FFFFFF", "#E2D8EA", 24),
        text(66, 264, "Top synthetic marker effects", 20, 500),
        text(66, 291, "Largest absolute standardized effects for yield", 13, 400, MUTED),
    ])
    max_effect = max(num(row["absolute_effect"]) for row in marker_effects)
    for i, row in enumerate(marker_effects):
        y = 330 + i * 34
        value = num(row["absolute_effect"])
        signed = num(row["standardized_effect"])
        bar_w = 245 * value / max_effect
        fill = PURPLE if signed >= 0 else "#C56B5E"
        lines.append(text(70, y + 18, row["marker"], 13, 500, INK))
        lines.append(f'<rect x="238" y="{y}" width="245" height="18" rx="9" fill="#F0EBF5"/>')
        lines.append(f'<rect x="238" y="{y}" width="{bar_w:.1f}" height="18" rx="9" fill="{fill}" opacity="0.88"/>')
        lines.append(text(500, y + 15, f"{signed:.3f}", 12, 500, MUTED))

    lines.extend([
        rounded_rect(610, 220, 532, 284, "#FFFFFF", "#E2D8EA", 24),
        text(640, 264, "Selection index preview", 20, 500),
        text(640, 291, "Top genotypes ranked by prediction-supported index", 13, 400, MUTED),
    ])
    for i, row in enumerate(top_candidates):
        y = 326 + i * 42
        score = num(row["ai_selection_index"])
        lines.append(f'<circle cx="662" cy="{y+10}" r="16" fill="#F2E7F8" stroke="#D6B8E5"/>')
        lines.append(text(662, y + 16, str(i + 1), 13, 500, PURPLE, "middle"))
        lines.append(text(696, y + 15, row["genotype"], 15, 500, INK))
        lines.append(f'<rect x="850" y="{y}" width="220" height="20" rx="10" fill="#F0EBF5"/>')
        lines.append(f'<rect x="850" y="{y}" width="{220*score:.1f}" height="20" rx="10" fill="url(#softPurple)"/>')
        lines.append(text(1084, y + 16, f"{score:.3f}", 12, 500, MUTED))
    lines.append("</svg>")
    write(OUTPUT_DIR / "portfolio_overview.svg", lines)


def observed_vs_predicted_yield() -> None:
    rows = read_csv(OUTPUT_DIR / "predicted_breeding_values.csv")
    obs = [num(r["observed_yield_t_ha"]) for r in rows]
    pred = [num(r["predicted_yield_t_ha"]) for r in rows]
    low = min(min(obs), min(pred)) - 0.8
    high = max(max(obs), max(pred)) + 0.8
    width, height = 920, 640
    left, top, plot_w, plot_h = 96, 96, 700, 420
    yield_metric = [m for m in overall_metrics() if m["trait"] == "yield_t_ha"][0]

    def xy(xv: float, yv: float) -> tuple[float, float]:
        x = left + (xv - low) / (high - low) * plot_w
        y = top + plot_h - (yv - low) / (high - low) * plot_h
        return x, y

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title id=\"title\">Observed versus predicted yield</title>",
        "<desc id=\"desc\">Scatter plot comparing observed and predicted yield for synthetic breeding genotypes.</desc>",
        *defs(),
        f'<rect width="{width}" height="{height}" rx="28" fill="{PAPER}"/>',
        text(58, 50, "Observed vs predicted yield", 24, 500),
        text(58, 78, "Synthetic marker-based ridge prediction for breeding selection", 14, 400, MUTED),
    ]
    for i in range(6):
        val = low + i * (high - low) / 5
        x, y = xy(val, val)
        lines.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left+plot_w}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        lines.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top+plot_h}" stroke="{GRID}" stroke-width="1"/>')
        lines.append(text(left - 12, y + 5, f"{val:.0f}", 12, 400, MUTED, "end"))
        lines.append(text(x, top + plot_h + 26, f"{val:.0f}", 12, 400, MUTED, "middle"))
    x1, y1 = xy(low, low)
    x2, y2 = xy(high, high)
    lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#A98CC4" stroke-width="2" stroke-dasharray="8 8"/>')
    for o, p in zip(obs, pred):
        x, y = xy(o, p)
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{PURPLE}" opacity="0.66" stroke="#FFFFFF" stroke-width="1"/>')
    lines.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="{INK}" stroke-width="1.4"/>')
    lines.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="{INK}" stroke-width="1.4"/>')
    lines.append(text(left + plot_w / 2, 585, "Observed yield (t/ha)", 14, 500, INK, "middle"))
    lines.append(f'<text x="26" y="{top+plot_h/2:.1f}" font-family="{FONT}" font-size="14" font-weight="500" fill="{INK}" text-anchor="middle" transform="rotate(-90 26 {top+plot_h/2:.1f})">Predicted yield (t/ha)</text>')
    lines.append(rounded_rect(694, 118, 166, 104, "#FFFFFF", "#E2D8EA", 18))
    lines.append(text(719, 149, "Yield model", 13, 500, MUTED))
    lines.append(text(719, 184, f"R² {num(yield_metric['r2']):.4f}", 27, 500, PURPLE))
    lines.append(text(719, 210, f"corr {num(yield_metric['correlation']):.4f}", 13, 400, MUTED))
    lines.append(text(735, 538, "Dashed line = perfect prediction", 12, 400, MUTED, "middle"))
    lines.append("</svg>")
    write(OUTPUT_DIR / "observed_vs_predicted_yield.svg", lines)


def marker_effects_chart() -> None:
    rows = read_csv(OUTPUT_DIR / "marker_effects_yield.csv")[:12]
    max_effect = max(num(row["absolute_effect"]) for row in rows)
    width, height = 920, 560
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title id=\"title\">Top synthetic marker effects for yield</title>",
        "<desc id=\"desc\">Horizontal bar chart showing marker-effect magnitudes for synthetic yield prediction.</desc>",
        *defs(),
        f'<rect width="{width}" height="{height}" rx="28" fill="{PAPER}"/>',
        text(58, 55, "Top synthetic marker effects for yield", 25, 500),
        text(58, 84, "Standardized marker effects from the final ridge-prediction model", 14, 400, MUTED),
    ]
    for i, row in enumerate(rows):
        y = 120 + i * 34
        effect = num(row["standardized_effect"])
        value = abs(effect)
        bar_w = 500 * value / max_effect
        fill = PURPLE if effect >= 0 else "#C56B5E"
        lines.append(text(66, y + 18, row["marker"], 13, 500, INK))
        lines.append(f'<rect x="220" y="{y}" width="500" height="20" rx="10" fill="#F0EBF5"/>')
        lines.append(f'<rect x="220" y="{y}" width="{bar_w:.1f}" height="20" rx="10" fill="{fill}" opacity="0.88"/>')
        lines.append(text(742, y + 16, f"{effect:.4f}", 12, 500, MUTED))
    lines.append(text(58, 525, "Positive and negative effects are color separated; values are synthetic demonstration outputs.", 13, 400, MUTED))
    lines.append("</svg>")
    write(OUTPUT_DIR / "marker_effects_yield.svg", lines)


def selection_index_chart() -> None:
    rows = read_csv(OUTPUT_DIR / "top_selection_candidates.csv")[:10]
    max_score = max(num(row["ai_selection_index"]) for row in rows)
    width, height = 920, 560
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title id=\"title\">Top AI-assisted selection candidates</title>",
        "<desc id=\"desc\">Horizontal bar chart ranking top synthetic genotypes by AI-assisted selection index.</desc>",
        *defs(),
        f'<rect width="{width}" height="{height}" rx="28" fill="{PAPER}"/>',
        text(58, 55, "Top AI-assisted selection candidates", 25, 500),
        text(58, 84, "Multi-trait index: predicted yield, vigor, disease score, and maturity", 14, 400, MUTED),
    ]
    for i, row in enumerate(rows):
        y = 122 + i * 38
        score = num(row["ai_selection_index"])
        bar_w = 500 * score / max_score
        lines.append(text(66, y + 18, row["genotype"], 13, 500, INK))
        lines.append(f'<rect x="250" y="{y}" width="500" height="22" rx="11" fill="#F0EBF5"/>')
        lines.append(f'<rect x="250" y="{y}" width="{bar_w:.1f}" height="22" rx="11" fill="url(#softPurple)"/>')
        lines.append(text(770, y + 17, f"{score:.4f}", 12, 500, MUTED))
    lines.append(text(58, 525, "Ranking is for synthetic workflow demonstration, not cultivar recommendation.", 13, 400, MUTED))
    lines.append("</svg>")
    write(OUTPUT_DIR / "selection_index_bar.svg", lines)


def workflow_diagram() -> None:
    width, height = 1100, 330
    stages = [
        ("1", "Marker inputs", "Synthetic marker matrix for breeding lines"),
        ("2", "Trait prediction", "Ridge models for yield, disease, maturity, vigor"),
        ("3", "Validation", "Five-fold genotype-level cross-validation"),
        ("4", "Selection support", "Multi-trait index and candidate ranking"),
    ]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title id=\"title\">AI-assisted breeding workflow diagram</title>",
        "<desc id=\"desc\">Four-stage workflow from synthetic marker input to trait prediction, validation, and selection support.</desc>",
        *defs(),
        f'<rect width="{width}" height="{height}" rx="28" fill="{PAPER}"/>',
        text(50, 55, "AI-assisted breeding workflow", 25, 500),
        text(50, 84, "A reproducible pipeline from marker-style data to transparent selection decisions", 14, 400, MUTED),
    ]
    for i, (number, title, body) in enumerate(stages):
        x = 54 + i * 260
        y = 130
        lines.append(rounded_rect(x, y, 220, 128, "#FFFFFF", "#E2D8EA", 22))
        lines.append(f'<circle cx="{x+34}" cy="{y+35}" r="18" fill="#F2E7F8" stroke="#D7B8E5"/>')
        lines.append(text(x + 34, y + 41, number, 15, 500, PURPLE, "middle"))
        lines.append(text(x + 64, y + 40, title, 16, 500, INK))
        lines.append(text(x + 24, y + 78, body[:31], 12, 400, MUTED))
        lines.append(text(x + 24, y + 99, body[31:], 12, 400, MUTED))
        if i < len(stages) - 1:
            ax = x + 226
            lines.append(f'<path d="M {ax} {y+64} L {ax+36} {y+64}" stroke="{PURPLE}" stroke-width="2.2" marker-end="url(#arrow)"/>')
    lines.append("</svg>")
    write(OUTPUT_DIR / "workflow_diagram.svg", lines)


def main() -> None:
    portfolio_overview()
    observed_vs_predicted_yield()
    marker_effects_chart()
    selection_index_chart()
    workflow_diagram()
    print("Portfolio visuals refreshed for AI-assisted breeding repository.")


if __name__ == "__main__":
    main()
