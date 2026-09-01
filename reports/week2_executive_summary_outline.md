# Week 2 Executive Summary Outline

## Slide 1 — Project & Dataset

**Main message:** Week 2 transformed the cleaned NYC taxi data into a
feature-ready dataset and completed full Phase 2 exploratory analysis.

**Recommended chart:** No chart; use a compact workflow or dataset summary.

- 54,004,358 cleaned trips processed with memory-safe chunking.
- Added distance and corrected temporal features.
- Completed Distance, Temporal, and Geographic Analysis.

## Slide 2 — Distance and Fare

**Main message:** Trip distance has a strong positive association with fare and
is the clearest fare-related variable examined so far.

**Recommended chart:** `fare_vs_distance_hexbin.png`

- Pearson correlation = 0.8535.
- Spearman correlation = 0.8466.
- Distance is important, but visible fare bands indicate additional influences.

## Slide 3 — Temporal Patterns

**Main message:** Peak demand and peak average fare occur at different times;
higher early-morning fares coincide with longer trips and low demand.

**Recommended chart:** `trip_volume_by_hour.png`, paired with
`average_fare_by_hour.png` if space permits.

- Demand peaks at 19:00 and is lowest at 05:00.
- Average fare and average distance both peak at 05:00.
- Weekly fare differences are modest relative to demand variation.

## Slide 4 — Geographic Patterns

**Main message:** Taxi activity is highly concentrated, and pickup/drop-off
density patterns are strongly aligned but not identical.

**Recommended chart:** `pickup_dropoff_density_comparison.png`

- Grid-level pickup–drop-off spatial correlation = 0.9625.
- Within the fixed grid, the densest 1% of cells contain 92.4% of pickups and
  84.6% of drop-offs.
- Drop-offs are more spatially dispersed than pickups.

## Slide 5 — Key Insights / Implications

**Main message:** Distance, time, and location provide complementary signals for
fare prediction and should be evaluated together in Phase 3.

**Recommended chart:** `weekday_vs_weekend.png` or a compact three-insight
summary assembled from existing figures.

- Distance is strongly associated with fare at the trip level.
- Aggregated temporal fare differences are not explained by distance alone.
- Geographic concentration suggests location features may add predictive value.
