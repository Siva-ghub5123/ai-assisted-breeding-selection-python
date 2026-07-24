# AI-assisted breeding selection report

This report uses synthetic marker and phenotype data to demonstrate a prediction-supported breeding selection workflow.

## Overall cross-validation summary

| Trait | RMSE | MAE | R² | Correlation |
|---|---:|---:|---:|---:|
| yield_t_ha | 0.7175 | 0.5666 | 0.6872 | 0.8297 |
| disease_score_1_9 | 0.4807 | 0.3942 | 0.4973 | 0.7116 |
| days_to_maturity | 1.3997 | 1.1291 | 0.5607 | 0.7583 |
| vigor_score_1_9 | 0.3669 | 0.2988 | 0.6176 | 0.7876 |

## Top AI-assisted selection candidates

| Rank | Genotype | Selection index | Predicted yield | Predicted disease score | Predicted maturity |
|---:|---|---:|---:|---:|---:|
| 1 | AIBREED_G062 | 0.8367 | 26.266 | 2.512 | 81.103 |
| 2 | AIBREED_G003 | 0.8287 | 27.103 | 1.648 | 86.336 |
| 3 | AIBREED_G017 | 0.7519 | 25.777 | 3.049 | 82.613 |
| 4 | AIBREED_G038 | 0.7483 | 25.533 | 1.972 | 84.295 |
| 5 | AIBREED_G008 | 0.7413 | 26.218 | 2.558 | 81.736 |
| 6 | AIBREED_G073 | 0.7263 | 26.328 | 2.784 | 84.35 |
| 7 | AIBREED_G021 | 0.7214 | 25.988 | 2.331 | 83.126 |
| 8 | AIBREED_G065 | 0.704 | 25.778 | 2.941 | 84.952 |

## Interpretation

The selection index favors higher predicted yield and vigor, lower predicted disease score, and earlier predicted maturity.

Because the dataset is synthetic, this ranking demonstrates workflow logic rather than real breeding recommendations.
