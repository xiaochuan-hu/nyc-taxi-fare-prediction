# NYC Taxi Fare Analytics Dashboard — Wireframe Specification

## Audience and Purpose

For non-technical pricing, fare-estimation and operations stakeholders: understand typical trips, see the initial model's accuracy, and recognize exceptions. This is a specification only, not a Web App or a new analysis. Dollar values are USD; distance is Haversine kilometres.

## Layout

```text
+-----------------------------------------------------------------------+
| NYC Taxi Fare Analytics | Frozen historical analysis | Population info |
+-----------------------------------------------------------------------+
| Pickup hour [All] | Day of week [All] | Passengers [All] | Fare band [All]|
| Reset filters | Selected trip count | Data scope / refresh label        |
+-----------------+-----------------+-----------------+-------------------+
| Average Fare    | Median Fare     | Median Distance | Model RMSE        |
| $11.27          | $8.50           | 2.15 km         | $3.81             |
| Modeling sample | Modeling sample | Modeling sample | Fixed 200k test   |
+-----------------------------------+-----------------------------------+
| 1. Trip Density / Geographic Map | 2. Average Fare by Hour             |
| Pickup / Drop-off toggle         | Average fare + trip count tooltip   |
+-----------------------------------+-----------------------------------+
| 3. Fare vs Trip Distance         | 4. Top Feature Importance           |
| Density view; full-range context | Impurity / Permutation toggle       |
+-----------------------------------------------------------------------+
| 5. Model Error by Fare Band: count, RMSE, MAE, signed mean error         |
| >$100: only 36 test trips | Zero-distance comparison link              |
+-----------------------------------------------------------------------+
| Initial model only | Definitions | Limitations | Source reports        |
+-----------------------------------------------------------------------+
```

## KPI Definitions and Evidence

| Card | Initial displayed value | Population and source |
|---|---:|---|
| Average Fare | $11.27 | Frozen 1M modelling sample; weighted average of stored train/test target means in [split metadata](modeling_split_metadata.json) |
| Median Fare | $8.50 | Same sample; saved fare median in split metadata |
| Median Trip Distance | 2.15 km | Same sample; saved distance median in split metadata |
| Model RMSE | $3.81 | Random Forest, fixed 200k test set; [benchmark](model_benchmark_results.csv) |

RMSE is not average fare and does not describe every trip's expected error. Keep its **fixed-test** badge visible. Cards must retain source/population labels; none represents live NYC pricing.

## Main Visuals

| Visual | Stakeholder question | Display and source |
|---|---|---|
| Trip Density / Geographic Map | Where are recorded trips concentrated? | Aggregated grid with pickup/drop-off toggle; use [existing full-source map](figures/week2/pickup_dropoff_density_comparison.png) as a clearly labelled, unfiltered 54M-context reference. A sample-filtered map requires aligned aggregates in a later implementation. |
| Average Fare by Hour | How do recorded average fares vary by hour? | Use [hourly statistics](hourly_stats.csv) for an unfiltered full-source reference; tooltip includes count. Label original dataset clock hour without a new timezone interpretation. A fully interactive sample view needs matching sample aggregates. |
| Fare vs Trip Distance | How does fare vary with trip length? | Use the [existing density chart](figures/week2/fare_vs_distance_hexbin.png), labelled as Week 2 EDA sample. Preserve its existing view limits with an explicit note; they are display limits, not data exclusions. |
| Top Feature Importance | Which fields does this model rely on? | Sorted bars from [impurity](random_forest_feature_importance.csv) or [permutation](random_forest_permutation_importance.csv); each mode has its own units. Show permutation SD bars and explain that importance is not causal. |
| Model Error by Fare Band | Where do estimates become less reliable? | Table/bars from [fare-band errors](model_error_by_fare_band.csv), with row counts, RMSE/MAE and predicted−actual mean error. Mark >$100 as only **36 test rows**. |

## Filters and Interaction Contract

- **Pickup hour:** all or 0–23. **Day of week:** all or Monday–Sunday. **Passenger count:** all or 1–6, reflecting the approved modelling population.
- **Fare band:** all, [2.50,10], (10,20], (20,40], (40,100], >100. Boundaries are mutually exclusive; fare is actual historical fare, not a prospective quote-time input.
- Intended interactive scope is the frozen 1M modelling population: descriptive cards and aligned descriptive visuals should respond to these filters and show selected row counts. Do not silently apply a filter to one population and label another population's metric as the result.
- Existing report assets are static and come from different explicitly labelled populations. Their current unfiltered reference views must stay labelled; they cannot be recomputed by jointly filtering already aggregated CSVs. Cross-filtered aggregates would be a later implementation task, not work performed in Phase 4. Until available, show “reference view — filters not applied” for those visuals.
- The overall model RMSE and feature-importance panels remain fixed benchmark references. Fare-band selection can select existing error-table rows; applying hour/day/passenger combinations to errors requires jointly grouped test-error aggregates that are not currently saved. Do not average group RMSEs or invent filtered error values; disable unsupported combinations for that panel.
- Display a clear empty-state message when no observations match. Always show counts with subgroup errors. No retraining, price adjustment or record deletion is triggered by dashboard controls.

## Interpretation Notes

Use tooltips for RMSE (“larger errors count more”), MAE (“average absolute dollar error”) and signed error (“negative means underestimation”). Keep a visible note that zero distance does not necessarily mean a bad record and that the 36-row high-fare result is uncertain. Empirical error percentiles must not be presented as calibrated customer confidence intervals. The dashboard supports analysis and review; it does not establish a surge-pricing or revenue strategy.
