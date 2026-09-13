# NYC Taxi Fare Prediction — Executive Deck Content

Five slides for non-technical stakeholders. Content and layout specification only; no PPTX is generated. Use a consistent light background, dark text and one blue accent; retain chart labels and population notes. Keep charts readable and use the exact existing evidence below.

## Slide 1 — Project Overview and Business Problem

- Objective: understand fare predictors and support better-informed estimates and exception handling.
- Scale: 54,004,358 processed source rows; 1,000,000-row modelling sample.
- Business question: how do distance, time and location relate to fare?
- Business question: can a learned model outperform a naive estimate, and where does it fail?

**Layout:** title and concise objective above a two-column text/context visual. Keep modelling metrics for Slide 3.

**Existing figure:** [NYC pickup density](figures/week2/pickup_trip_density.png), labelled as full-source spatial context.

**Key takeaway:** The project links fare prediction to operational questions rather than testing pricing interventions.

## Slide 2 — Data and EDA Findings

- Distance has strong fare association: Pearson 0.8535 and Spearman 0.8466.
- Demand peaks at 19:00; average fare and distance peak at 05:00 when demand is lowest.
- Pickup and drop-off activity is concentrated, with grid-level density correlation 0.9625.

**Layout:** large distance–fare density chart on the left; hourly chart and two short annotations on the right.

**Existing figures:** [Fare vs distance](figures/week2/fare_vs_distance_hexbin.png) and [average fare by hour](figures/week2/average_fare_by_hour.png). The distance chart uses the EDA sample; the hourly chart uses full-source aggregation. Retain these population labels.

**Key takeaway:** Distance is central, with temporal and geographic context worth preserving. [EDA evidence](week2_key_findings.md)

## Slide 3 — Predictive Modeling

- Frozen split: 800,000 training / 200,000 test rows, shared by every model.
- Random Forest is the best-performing model in the initial benchmark.
- **61.14% RMSE reduction vs median baseline.**

| Model | RMSE ($) | MAE ($) | R² |
|---|---:|---:|---:|
| Median Baseline | 9.803183 | 5.303599 | -0.086398 |
| Random Forest | 3.809299 | 1.951969 | 0.835962 |
| HistGradientBoosting | 3.847865 | 1.980753 | 0.832624 |

**Layout:** one large native table with the Random Forest row highlighted; one improvement callout. Do not add an unrelated figure merely to fill space.

**Existing chart/data:** use the saved [benchmark CSV](model_benchmark_results.csv) directly as the comparison table; no separate benchmark PNG currently exists.

**Key takeaway:** The learned model improves substantially on a naive estimate, but this is not production validation.

## Slide 4 — What Drives Fare and Where the Model Fails

- Distance dominates impurity importance (0.853407); all four coordinates also rank in both top-five lists.
- Zero-distance RMSE **$10.75**, versus **$3.67** for positive distance.
- Actual fares >$100: RMSE **$88.96**, but only **36 test rows**.
- Overall mean error is near zero, masking low-fare overprediction and high-fare underprediction.

**Layout:** left half: feature-importance chart; right half: the two error comparisons and a visible 36-row caveat. Include “importance is not causality.”

**Existing figure/data:** [RF importance](figures/week3/random_forest_feature_importance.png), [distance-slice CSV](model_error_zero_distance.csv), [fare-band CSV](model_error_by_fare_band.csv). Use table values for the right-side comparisons; do not invent a missing chart.

**Key takeaway:** Aggregate accuracy is useful, but exception segments require separate attention.

## Slide 5 — Strategic Recommendations and Next Steps

- Combine distance and location for initial fare estimation.
- Validate zero-distance/ambiguous routes separately; do not automatically discard them.
- Develop and validate uncertainty safeguards for potentially expensive trips; actual completed fare is unavailable at quote time.
- Next data priorities: road distance, traffic/weather, and route/airport features.
- Next validation priority: time-based evaluation before considering operational use.

**Layout:** three concise recommendation columns, with one next-steps line underneath. Keep caveats visible, not hidden in notes.

**Existing evidence:** [Phase 4 recommendations](phase4_synthesis.md); optionally reuse the [actual-versus-predicted chart](figures/week3/actual_vs_predicted.png) as a supporting thumbnail if it remains legible. No new chart is required.

**Key takeaway:** Improve estimation and exception handling through validated extensions, without claiming causal pricing or revenue benefits.
