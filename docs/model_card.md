# Model card

## Intended use

Demonstration of an AI-assisted breeding selection workflow using synthetic marker and phenotype data.

## Data

Synthetic marker matrix and genotype-level phenotype table.

## Model

Ridge regression implemented with NumPy.

## Validation

Five-fold genotype-level cross-validation.

## Overall cross-validation metrics

| Trait | RMSE | MAE | R² | Correlation |
|---|---:|---:|---:|---:|
| yield_t_ha | 0.7175 | 0.5666 | 0.6872 | 0.8297 |
| disease_score_1_9 | 0.4807 | 0.3942 | 0.4973 | 0.7116 |
| days_to_maturity | 1.3997 | 1.1291 | 0.5607 | 0.7583 |
| vigor_score_1_9 | 0.3669 | 0.2988 | 0.6176 | 0.7876 |

## Limitations

- Synthetic data only.
- Not a real genomic-selection experiment.
- Marker effects are simulated.
- No claim of cultivar recommendation.
- Intended to show reproducible workflow design and AI-assisted breeding awareness.
