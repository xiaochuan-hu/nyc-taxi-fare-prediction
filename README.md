# NYC Taxi Fare Prediction

End-to-end data analytics and machine learning project using more than 54 million NYC taxi trip records.

## Project Overview

Understand the main predictors of taxi fare, compare initial prediction models, and turn the results into cautious recommendations for fare estimation and operations. Phases 1–4 are complete: data preparation, EDA, modelling, interpretation, error analysis and synthesis.

Start with the [final report](reports/final_project_report.md), [five-slide executive content](reports/final_executive_deck.md) or [final internship report](reports/final_internship_weekly_report.md).

## Business Questions

- How do distance, time and location relate to recorded fare?
- How much does a learned model improve on a naive fare estimate?
- Which trip segments need additional validation or uncertainty safeguards?

## Dataset

The Kaggle NYC Taxi Fare Prediction data is stored locally, not in Git. Raw and processed large datasets are not committed to Git. The **processed source** contains **54,004,358 rows**, of which **54,003,614** are modelling-eligible. A reproducible **1,000,000-row** random sample keeps development practical while sampling across the eligible population; the frozen split contains **800,000 training / 200,000 test rows**.

Eligibility retains 1–6 passengers, fares ≥$2.50 and finite required values. Zero/near-zero distance, long-distance and high-fare trips remain included. [Population evidence](reports/modeling_eligibility_audit.csv)

## Project Workflow

Raw Data → Cleaning → Feature Engineering → EDA → Modeling → Model Interpretation → Error Analysis → Strategic Recommendations

## Key Features

`trip_distance`, `pickup_hour`, `day_of_week`, `is_weekend`, `passenger_count`, `pickup_longitude`, `pickup_latitude`, `dropoff_longitude`, `dropoff_latitude`.

`fare_amount` is the sole target; the identifier and raw datetime string are excluded from model inputs.

## EDA Highlights

- Distance has strong positive fare association: Pearson **0.8535**, Spearman **0.8466**.
- Demand peaks at **19:00**, whereas **05:00** has the highest average fare and distance, alongside the lowest demand.
- Friday has the highest trip volume; weekly average-fare differences are relatively modest.
- Pickup/drop-off grid densities are highly concentrated and similar, with spatial correlation **0.9625**.

[Reviewed Week 2 findings](reports/week2_key_findings.md) · [Distance–fare figure](reports/figures/week2/fare_vs_distance_hexbin.png)

## Model Performance

| Model | RMSE ($) | MAE ($) | R² |
|---|---:|---:|---:|
| Median Baseline | 9.803183 | 5.303599 | -0.086398 |
| Random Forest | 3.809299 | 1.951969 | 0.835962 |
| HistGradientBoosting | 3.847865 | 1.980753 | 0.832624 |

**Random Forest is the best-performing model in the initial benchmark:** RMSE **$3.8093**, a **61.14% reduction** versus the median baseline. All models use the same frozen test set. RMSE weights larger errors more heavily; MAE is average absolute dollar error; R² is not a classification accuracy percentage. [Benchmark results](reports/model_benchmark_results.csv)

## Model Interpretation

`trip_distance` dominates impurity importance (**0.853407**). Distance and all four coordinates are the top five under both impurity and permutation importance, supporting useful geographic information within the fitted model. Redundant/derived fields can share importance; incremental retrained geographic benefit was not isolated. **Feature Importance ≠ causality.** [Importance comparison](reports/model_feature_importance_summary.csv)

## Error Analysis

Median absolute error is **$1.18** and P95 **$5.95**. Zero-distance RMSE is **$10.75**, versus **$3.67** for positive distance. The >$100 fare slice has RMSE **$88.96**, but only **36 test observations**.

Near-zero overall bias hides low-fare overprediction and high-fare underprediction. Zero distance does not necessarily indicate erroneous data. [Distance errors](reports/model_error_zero_distance.csv) · [Fare-band errors](reports/model_error_by_fare_band.csv)

## Strategic Recommendations

1. Combine distance and location in initial fare estimates.
2. Validate ambiguous zero-distance routes separately rather than automatically discard them.
3. Develop and validate uncertainty safeguards for potentially expensive trips; the observed high-fare slice alone cannot define a prospective rule.

[Evidence and limitations](reports/phase4_synthesis.md) · [Dashboard wireframe](reports/dashboard_wireframe.md)

## Repository Structure

Selected contents; all paths below exist. Data directories are local and ignored.

```text
README.md
requirements.txt
notebooks/
  01_data_understanding.ipynb
  02_data_cleaning.ipynb
  03_exploratory_data_analysis.ipynb
  04_predictive_modeling.ipynb
  basic_code.ipynb                  # auxiliary exploration; outside the main workflow
src/
  cleaning.py
  features.py
  geographic_analysis.py
  visualization.py
reports/
  figures/week2/
  figures/week3/
  week2_key_findings.md
  model_benchmark_results.csv
  model_interpretation_metadata.json
  phase4_synthesis.md
  dashboard_wireframe.md
  final_project_report.md
  final_executive_deck.md
  final_internship_weekly_report.md
  final_repository_audit.md
  final_submission_checklist.md
data/
  raw/                             # local only
  processed/                       # local sample and split indices
```

## Reproducibility

The modelling sample fingerprint, persistent `modeling_split_indices.npz` and fixed seed **42** identify the frozen assignment. [Split metadata](reports/modeling_split_metadata.json) records hashes and settings; verify them before reuse. Local data and large indices are intentionally excluded, so a fresh clone alone cannot reproduce training.

### Environment and workflow

The logged model environment used Python 3.14.6. [requirements.txt](requirements.txt) pins the installed versions of direct analytical dependencies and required notebook/statistical runtime support; it is not a complete transitive lockfile.

From the repository root, using Python 3.14.6:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

These are setup instructions for a separate environment; no packages were installed or changed during submission hardening. IPython and ipykernel are included. The current environment does not contain the `jupyter` metapackage or `notebook` server: open `.ipynb` files in a compatible editor/frontend and select this environment's kernel. The historical `jupyter notebook` command below requires a separately available Notebook frontend and is not supplied by this manifest.

Lightweight imports, artifact paths and serialized reports were checked in the existing environment. A clean-environment installation and complete project replay have not been performed.

Preserved pipeline commands for a **separate local rebuild**, after obtaining Kaggle `train.csv` under `data/raw/`:

```bash
python src/cleaning.py --input data/raw/train.csv --output data/processed/train_clean.csv
python src/features.py --input data/processed/train_clean.csv --output data/processed/train_features.csv --chunksize 500000
python src/geographic_analysis.py
cd notebooks
jupyter notebook 03_exploratory_data_analysis.ipynb
```

These commands generate/replace derived outputs. For reviewing this submission, inspect saved notebook outputs first. Open notebooks with `notebooks/` as the working directory; do not blindly Run All on the frozen modelling notebook, whose preparation/training cells can regenerate artifacts. The [repository audit](reports/final_repository_audit.md) records execution-order and portability review items.

## Limitations

Straight-line Haversine distance differs from road distance; traffic, weather, toll and explicit airport/route features are absent. The random split measures historical generalization, not future forecasting. High fares have limited test coverage, and importance is not causality. This is not production deployment validation or a causal pricing study.

## Next Steps

Evaluate road-network distance, airport/borough/route features and traffic/weather context; use time-based validation for any future changes. Dashboard implementation or deployment assessment is optional and would require further validation. Final presentation and repository submission are the immediate handoff tasks; see the [submission checklist](reports/final_submission_checklist.md).
