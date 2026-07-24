"""
AI-Assisted Breeding Selection Workflow in Python

Author: Mokkala Siva Prasad

Purpose:
    Demonstrate an AI-assisted breeding workflow using synthetic marker and
    phenotype data.

Important:
    This is not a real genomic-selection study. Marker and phenotype data are
    simulated only for portfolio demonstration.

Dependencies:
    Python standard library + NumPy
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
DOCS_DIR = ROOT / "docs"
REPORT_DIR = ROOT / "reports"

for directory in [DATA_DIR, OUTPUT_DIR, DOCS_DIR, REPORT_DIR]:
    directory.mkdir(exist_ok=True)

RNG = np.random.default_rng(20260724)
N_GENOTYPES = 140
N_MARKERS = 72
MARKERS = [f"M{idx:03d}" for idx in range(1, N_MARKERS + 1)]
TRAITS = ["yield_t_ha", "disease_score_1_9", "days_to_maturity", "vigor_score_1_9"]


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_synthetic_marker_data() -> tuple[Path, Path]:
    genotypes = [f"AIBREED_G{idx:03d}" for idx in range(1, N_GENOTYPES + 1)]

    allele_frequencies = RNG.uniform(0.15, 0.75, size=N_MARKERS)
    marker_matrix = np.column_stack(
        [RNG.binomial(2, freq, size=N_GENOTYPES) for freq in allele_frequencies]
    ).astype(float)

    # Sparse synthetic effects: most markers have tiny or zero influence.
    effect_yield = np.zeros(N_MARKERS)
    effect_disease = np.zeros(N_MARKERS)
    effect_maturity = np.zeros(N_MARKERS)
    effect_vigor = np.zeros(N_MARKERS)

    yield_markers = [2, 9, 14, 25, 38, 51, 65]
    disease_markers = [4, 18, 26, 41, 56, 70]
    maturity_markers = [7, 21, 32, 47, 60]
    vigor_markers = [1, 14, 29, 44, 53, 67]

    effect_yield[yield_markers] = [0.55, 0.45, 0.38, 0.42, -0.30, 0.36, 0.28]
    effect_disease[disease_markers] = [-0.34, 0.28, -0.25, 0.22, -0.20, 0.18]
    effect_maturity[maturity_markers] = [-1.20, 0.90, -0.75, 0.65, -0.55]
    effect_vigor[vigor_markers] = [0.28, 0.24, 0.22, -0.18, 0.20, 0.16]

    marker_std = marker_matrix.std(axis=0, ddof=1)
    marker_std[marker_std == 0] = 1.0
    standardized_markers = (marker_matrix - marker_matrix.mean(axis=0)) / marker_std

    breeding_noise = RNG.normal(0, 1.0, size=N_GENOTYPES)

    yield_trait = (
        24.0
        + standardized_markers @ effect_yield
        + 0.15 * (standardized_markers @ effect_vigor)
        - 0.10 * (standardized_markers @ effect_disease)
        + 0.18 * breeding_noise
        + RNG.normal(0, 0.55, size=N_GENOTYPES)
    )

    disease_trait = (
        3.2
        + standardized_markers @ effect_disease
        - 0.08 * (standardized_markers @ effect_vigor)
        + RNG.normal(0, 0.30, size=N_GENOTYPES)
    )

    maturity_trait = (
        84.0
        + standardized_markers @ effect_maturity
        + RNG.normal(0, 1.10, size=N_GENOTYPES)
    )

    vigor_trait = (
        7.2
        + standardized_markers @ effect_vigor
        + 0.05 * (standardized_markers @ effect_yield)
        + RNG.normal(0, 0.25, size=N_GENOTYPES)
    )

    marker_rows = []
    for genotype, marker_values in zip(genotypes, marker_matrix):
        row = {"genotype": genotype}
        row.update({marker: int(value) for marker, value in zip(MARKERS, marker_values)})
        marker_rows.append(row)

    phenotype_rows = []
    for idx, genotype in enumerate(genotypes):
        phenotype_rows.append(
            {
                "genotype": genotype,
                "yield_t_ha": round(float(np.clip(yield_trait[idx], 17, 32)), 3),
                "disease_score_1_9": round(float(np.clip(disease_trait[idx], 1, 9)), 3),
                "days_to_maturity": round(float(np.clip(maturity_trait[idx], 74, 96)), 3),
                "vigor_score_1_9": round(float(np.clip(vigor_trait[idx], 1, 9)), 3),
            }
        )

    marker_path = DATA_DIR / "synthetic_marker_matrix.csv"
    phenotype_path = DATA_DIR / "synthetic_breeding_phenotypes.csv"
    write_csv(marker_path, marker_rows, ["genotype", *MARKERS])
    write_csv(phenotype_path, phenotype_rows, ["genotype", *TRAITS])
    return marker_path, phenotype_path


def read_numeric_matrix(marker_path: Path, phenotype_path: Path) -> tuple[list[str], np.ndarray, dict[str, np.ndarray]]:
    genotypes: list[str] = []
    markers: list[list[float]] = []
    with marker_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            genotypes.append(row["genotype"])
            markers.append([float(row[m]) for m in MARKERS])

    trait_values = {trait: [] for trait in TRAITS}
    with phenotype_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for trait in TRAITS:
                trait_values[trait].append(float(row[trait]))

    return genotypes, np.array(markers, dtype=float), {trait: np.array(values, dtype=float) for trait, values in trait_values.items()}


def standardize_train_test(x_train: np.ndarray, x_test: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mean = x_train.mean(axis=0)
    std = x_train.std(axis=0, ddof=1)
    std[std == 0] = 1.0
    return (x_train - mean) / std, (x_test - mean) / std, mean, std


def fit_ridge(x: np.ndarray, y: np.ndarray, alpha: float = 10.0) -> tuple[float, np.ndarray]:
    x_aug = np.column_stack([np.ones(len(x)), x])
    penalty = np.eye(x_aug.shape[1]) * alpha
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(x_aug.T @ x_aug + penalty, x_aug.T @ y)
    return float(beta[0]), beta[1:]


def predict(x: np.ndarray, intercept: float, coefficients: np.ndarray) -> np.ndarray:
    return intercept + x @ coefficients


def score_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    residuals = y_true - y_pred
    rmse = float(np.sqrt(np.mean(residuals**2)))
    mae = float(np.mean(np.abs(residuals)))
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((y_true - y_true.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot else 0.0
    corr = float(np.corrcoef(y_true, y_pred)[0, 1]) if len(y_true) > 1 else 0.0
    return {"rmse": round(rmse, 4), "mae": round(mae, 4), "r2": round(float(r2), 4), "correlation": round(corr, 4)}


def kfold_indices(n: int, k: int = 5) -> list[np.ndarray]:
    indices = np.arange(n)
    RNG.shuffle(indices)
    return np.array_split(indices, k)


def cross_validate(x: np.ndarray, y_by_trait: dict[str, np.ndarray], k: int = 5) -> tuple[list[dict], dict[str, np.ndarray]]:
    folds = kfold_indices(len(x), k)
    rows: list[dict] = []
    predictions_by_trait = {trait: np.zeros(len(x)) for trait in TRAITS}

    for trait in TRAITS:
        y = y_by_trait[trait]
        for fold_number, test_idx in enumerate(folds, start=1):
            train_idx = np.setdiff1d(np.arange(len(x)), test_idx)
            x_train, x_test, _, _ = standardize_train_test(x[train_idx], x[test_idx])
            intercept, coefficients = fit_ridge(x_train, y[train_idx], alpha=12.0)
            y_pred = predict(x_test, intercept, coefficients)
            predictions_by_trait[trait][test_idx] = y_pred
            fold_metrics = score_metrics(y[test_idx], y_pred)
            rows.append({"trait": trait, "fold": fold_number, **fold_metrics})

    summary_rows = []
    for trait in TRAITS:
        trait_metrics = score_metrics(y_by_trait[trait], predictions_by_trait[trait])
        summary_rows.append({"trait": trait, "fold": "overall", **trait_metrics})

    return rows + summary_rows, predictions_by_trait


def minmax(values: np.ndarray, reverse: bool = False) -> np.ndarray:
    vals = -values if reverse else values
    low, high = vals.min(), vals.max()
    if math.isclose(float(low), float(high)):
        return np.repeat(0.5, len(vals))
    return (vals - low) / (high - low)


def write_bar_svg(path: Path, rows: list[dict], value_key: str, label_key: str, title: str, color: str) -> None:
    width, height = 920, 520
    margin_left, margin_top = 250, 70
    plot_width = width - margin_left - 70
    bar_height, gap = 26, 12
    values = [abs(float(row[value_key])) for row in rows[:12]]
    max_value = max(values) if values else 1.0
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="35" text-anchor="middle" font-family="Arial" font-size="22" font-weight="bold">{title}</text>',
    ]
    for i, row in enumerate(rows[:12]):
        y = margin_top + i * (bar_height + gap)
        val = abs(float(row[value_key]))
        bar_width = val / max_value * plot_width if max_value else 0.0
        lines.append(f'<text x="{margin_left-10}" y="{y+19}" text-anchor="end" font-family="Arial" font-size="13">{row[label_key]}</text>')
        lines.append(f'<rect x="{margin_left}" y="{y}" width="{bar_width:.1f}" height="{bar_height}" fill="{color}" opacity="0.85"/>')
        lines.append(f'<text x="{margin_left+bar_width+8}" y="{y+19}" font-family="Arial" font-size="13">{float(row[value_key]):.3f}</text>')
    lines.append('<text x="460" y="495" text-anchor="middle" font-family="Arial" font-size="12">Synthetic marker data demonstration</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_scatter_svg(path: Path, observed: np.ndarray, predicted: np.ndarray, title: str) -> None:
    width, height = 720, 620
    margin = 80
    low = float(min(observed.min(), predicted.min())) - 0.8
    high = float(max(observed.max(), predicted.max())) + 0.8

    def convert(xv: float, yv: float) -> tuple[float, float]:
        x = margin + (xv - low) / (high - low) * (width - 2 * margin)
        y = height - margin - (yv - low) / (high - low) * (height - 2 * margin)
        return x, y

    x1, y1 = convert(low, low)
    x2, y2 = convert(high, high)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="35" text-anchor="middle" font-family="Arial" font-size="22" font-weight="bold">{title}</text>',
        f'<line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" stroke="#333"/>',
        f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" stroke="#333"/>',
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#999" stroke-dasharray="5,5"/>',
    ]
    for obs, pred in zip(observed, predicted):
        x, y = convert(float(obs), float(pred))
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#6A1B9A" opacity="0.68"/>')
    lines.append(f'<text x="{width/2}" y="{height-25}" text-anchor="middle" font-family="Arial" font-size="14">Observed yield</text>')
    lines.append(f'<text x="24" y="{height/2}" text-anchor="middle" font-family="Arial" font-size="14" transform="rotate(-90 24 {height/2})">Predicted yield</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    marker_path, phenotype_path = generate_synthetic_marker_data()
    genotypes, marker_matrix, y_by_trait = read_numeric_matrix(marker_path, phenotype_path)

    cv_rows, cv_predictions = cross_validate(marker_matrix, y_by_trait, k=5)
    write_csv(OUTPUT_DIR / "cross_validation_metrics.csv", cv_rows, ["trait", "fold", "rmse", "mae", "r2", "correlation"])

    final_predictions = {}
    marker_effect_rows_yield: list[dict] = []

    for trait in TRAITS:
        x_standardized, _, mean, std = standardize_train_test(marker_matrix, marker_matrix)
        intercept, coefficients = fit_ridge(x_standardized, y_by_trait[trait], alpha=12.0)
        final_predictions[trait] = predict(x_standardized, intercept, coefficients)

        if trait == "yield_t_ha":
            marker_effect_rows_yield = [
                {"marker": marker, "standardized_effect": round(float(effect), 5), "absolute_effect": round(abs(float(effect)), 5)}
                for marker, effect in sorted(zip(MARKERS, coefficients), key=lambda item: abs(item[1]), reverse=True)
            ]

    selection_index = (
        0.45 * minmax(final_predictions["yield_t_ha"])
        + 0.20 * minmax(final_predictions["vigor_score_1_9"])
        + 0.20 * minmax(final_predictions["disease_score_1_9"], reverse=True)
        + 0.15 * minmax(final_predictions["days_to_maturity"], reverse=True)
    )

    predicted_rows = []
    for i, genotype in enumerate(genotypes):
        predicted_rows.append(
            {
                "genotype": genotype,
                "observed_yield_t_ha": round(float(y_by_trait["yield_t_ha"][i]), 3),
                "predicted_yield_t_ha": round(float(final_predictions["yield_t_ha"][i]), 3),
                "predicted_disease_score_1_9": round(float(final_predictions["disease_score_1_9"][i]), 3),
                "predicted_days_to_maturity": round(float(final_predictions["days_to_maturity"][i]), 3),
                "predicted_vigor_score_1_9": round(float(final_predictions["vigor_score_1_9"][i]), 3),
                "ai_selection_index": round(float(selection_index[i]), 4),
            }
        )

    predicted_rows = sorted(predicted_rows, key=lambda row: row["ai_selection_index"], reverse=True)
    top_candidates = predicted_rows[:12]

    write_csv(
        OUTPUT_DIR / "predicted_breeding_values.csv",
        predicted_rows,
        [
            "genotype",
            "observed_yield_t_ha",
            "predicted_yield_t_ha",
            "predicted_disease_score_1_9",
            "predicted_days_to_maturity",
            "predicted_vigor_score_1_9",
            "ai_selection_index",
        ],
    )

    write_csv(
        OUTPUT_DIR / "top_selection_candidates.csv",
        top_candidates,
        [
            "genotype",
            "observed_yield_t_ha",
            "predicted_yield_t_ha",
            "predicted_disease_score_1_9",
            "predicted_days_to_maturity",
            "predicted_vigor_score_1_9",
            "ai_selection_index",
        ],
    )

    write_csv(OUTPUT_DIR / "marker_effects_yield.csv", marker_effect_rows_yield, ["marker", "standardized_effect", "absolute_effect"])

    write_scatter_svg(
        OUTPUT_DIR / "observed_vs_predicted_yield.svg",
        y_by_trait["yield_t_ha"],
        final_predictions["yield_t_ha"],
        "Observed vs Predicted Yield",
    )
    write_bar_svg(OUTPUT_DIR / "marker_effects_yield.svg", marker_effect_rows_yield, "absolute_effect", "marker", "Top Synthetic Marker Effects for Yield", "#6A1B9A")
    write_bar_svg(OUTPUT_DIR / "selection_index_bar.svg", top_candidates, "ai_selection_index", "genotype", "Top AI-Assisted Selection Candidates", "#1B5E20")

    overall_metrics = [row for row in cv_rows if row["fold"] == "overall"]

    model_card = [
        "# Model card",
        "",
        "## Intended use",
        "",
        "Demonstration of an AI-assisted breeding selection workflow using synthetic marker and phenotype data.",
        "",
        "## Data",
        "",
        "Synthetic marker matrix and genotype-level phenotype table.",
        "",
        "## Model",
        "",
        "Ridge regression implemented with NumPy.",
        "",
        "## Validation",
        "",
        "Five-fold genotype-level cross-validation.",
        "",
        "## Overall cross-validation metrics",
        "",
        "| Trait | RMSE | MAE | R² | Correlation |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in overall_metrics:
        model_card.append(f"| {row['trait']} | {row['rmse']} | {row['mae']} | {row['r2']} | {row['correlation']} |")
    model_card.extend(
        [
            "",
            "## Limitations",
            "",
            "- Synthetic data only.",
            "- Not a real genomic-selection experiment.",
            "- Marker effects are simulated.",
            "- No claim of cultivar recommendation.",
            "- Intended to show reproducible workflow design and AI-assisted breeding awareness.",
        ]
    )
    (DOCS_DIR / "model_card.md").write_text("\n".join(model_card), encoding="utf-8")

    report = [
        "# AI-assisted breeding selection report",
        "",
        "This report uses synthetic marker and phenotype data to demonstrate a prediction-supported breeding selection workflow.",
        "",
        "## Overall cross-validation summary",
        "",
        "| Trait | RMSE | MAE | R² | Correlation |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in overall_metrics:
        report.append(f"| {row['trait']} | {row['rmse']} | {row['mae']} | {row['r2']} | {row['correlation']} |")
    report.extend(
        [
            "",
            "## Top AI-assisted selection candidates",
            "",
            "| Rank | Genotype | Selection index | Predicted yield | Predicted disease score | Predicted maturity |",
            "|---:|---|---:|---:|---:|---:|",
        ]
    )
    for rank, row in enumerate(top_candidates[:8], start=1):
        report.append(
            f"| {rank} | {row['genotype']} | {row['ai_selection_index']} | {row['predicted_yield_t_ha']} | {row['predicted_disease_score_1_9']} | {row['predicted_days_to_maturity']} |"
        )
    report.extend(
        [
            "",
            "## Interpretation",
            "",
            "The selection index favors higher predicted yield and vigor, lower predicted disease score, and earlier predicted maturity.",
            "",
            "Because the dataset is synthetic, this ranking demonstrates workflow logic rather than real breeding recommendations.",
        ]
    )
    (REPORT_DIR / "ai_breeding_selection_report.md").write_text("\n".join(report), encoding="utf-8")

    print("AI-assisted breeding workflow complete.")
    print(json.dumps({row["trait"]: {"r2": row["r2"], "correlation": row["correlation"]} for row in overall_metrics}, indent=2))
    print("Top selection candidates:")
    for row in top_candidates[:5]:
        print(row["genotype"], row["ai_selection_index"], row["predicted_yield_t_ha"])


if __name__ == "__main__":
    main()
