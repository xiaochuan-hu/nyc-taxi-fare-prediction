# NYC Taxi Fare Prediction

## Project Overview

This project analyzes the Kaggle NYC Taxi Fare Prediction dataset and develops
a reproducible workflow for data cleaning, feature engineering, exploratory
analysis, and later predictive modelling. The current repository contains the
completed Phase 1 and Phase 2 work.

## Dataset

The source dataset is not stored in Git because the raw and processed files are
several gigabytes in size. Download the NYC Taxi Fare Prediction data from
Kaggle and place the files under `data/raw/` before running the pipeline.

After cleaning, the local training dataset contains 54,004,358 valid trips.

## Project Progress

- Phase 1 — Data Understanding & Cleaning ✅
- Phase 2 — Feature Engineering & EDA ✅
- Phase 3 — Predictive Modelling ⏳
- Phase 4 — Business Recommendations ⏳

## Repository Structure

```text
notebooks/
  01_data_understanding.ipynb
  02_data_cleaning.ipynb
  03_exploratory_data_analysis.ipynb
src/
  cleaning.py
  features.py
  geographic_analysis.py
  visualization.py
reports/
  figures/week2/
  *_stats.csv
  geographic_density.npz
  geographic_hotspots.csv
  week2_key_findings.md
  week2_weekly_report.md
  week2_executive_summary_outline.md
data/
  raw/          # local only; ignored by Git
  processed/    # local only; ignored by Git
```

## Key Week 2 Findings

- Trip distance has a strong positive association with fare: Pearson = 0.8535
  and Spearman = 0.8466.
- Demand peaks around 19:00, while the highest average fare and distance occur
  around 05:00 when demand is lowest.
- Friday has the highest trip volume; weekly average-fare differences are
  relatively modest.
- Pickup and drop-off density patterns are highly similar, with a grid-level
  spatial correlation of 0.9625 and strong concentration in a small share of
  the fixed spatial grid.

See [`reports/week2_key_findings.md`](reports/week2_key_findings.md) for the
consolidated findings and supporting evidence.

## How to Run

Create a Python environment with `numpy`, `pandas`, `matplotlib`, `seaborn`, and
Jupyter installed. The commands below assume the Kaggle data has already been
downloaded locally.

```bash
python src/cleaning.py \
  --input data/raw/train.csv \
  --output data/processed/train_clean.csv

python src/features.py \
  --input data/processed/train_clean.csv \
  --output data/processed/train_features.csv \
  --chunksize 500000

python src/geographic_analysis.py

cd notebooks
jupyter notebook 03_exploratory_data_analysis.ipynb
```

Large datasets are intentionally excluded from the repository, so a fresh
clone cannot run the full pipeline until the Kaggle files are supplied.
