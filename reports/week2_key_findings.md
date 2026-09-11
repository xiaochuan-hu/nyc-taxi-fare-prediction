# Week 2 Key Findings

## 1. Trip distance is strongly associated with fare

Trip distance has the clearest relationship with fare among the variables
examined in Week 2. Longer trips generally have higher fares, although visible
fare bands and outliers indicate that distance is not the only relevant factor.

**Supporting metrics:** Pearson correlation = **0.8535**; Spearman correlation =
**0.8466**. These values describe a strong positive association, not causation.

## 2. Taxi demand and average fare peak at different times

Demand reaches its daily maximum at approximately **19:00**, with **3,376,393**
trips, while the lowest demand occurs around **05:00**, with **527,879** trips.
The hour with the highest average fare is 05:00 rather than the evening demand
peak, showing that demand volume and average fare follow different daily patterns.

**Supporting metrics:** busiest hour = **19:00**; quietest hour = **05:00**;
highest average fare = **$15.11 at 05:00**.

## 3. Higher early-morning fares coincide with longer trips

The early-morning fare peak occurs alongside a clear increase in average trip
distance. At 05:00, the average trip distance is **5.18 km**, the longest of any
hour, while trip demand is at its minimum. Higher early-morning fares therefore
coincide with longer trips rather than higher demand.

**Supporting metrics:** 05:00 average fare = **$15.11**; 05:00 average distance =
**5.18 km**; 05:00 trip count = **527,879**.

## 4. Weekly fare differences are modest relative to demand variation

Trip demand varies meaningfully across the week: Friday is the busiest day and
Monday the quietest. Average fare varies within a much narrower range. Sunday
has both the highest average fare and the longest average distance, but the
broader weekday/weekend comparison is more nuanced: weekend trips are about
4.8% longer on average while their average fare is about 0.6% lower.

**Supporting metrics:** Friday = **8,308,658 trips**; Monday = **6,922,341
trips**; Sunday average fare = **$11.6071** and average distance = **3.5956 km**.
Weekday/weekend average fares are **$11.3217/$11.2585**, and average distances
are **3.2643/3.4207 km**. Distance is a strong trip-level predictor, but
aggregated temporal fare differences cannot be explained by distance alone.

## 5. Taxi activity is extremely spatially concentrated

Pickup and drop-off density patterns are highly similar, with their strongest
grid cells concentrated in the same central Manhattan area. Drop-offs are
slightly more spatially dispersed, and several outer-area hotspots remain
visible without being assigned unverified landmark names.

**Supporting metrics:** pickup–drop-off spatial density correlation = **0.9625**.
Within the fixed **250 × 250 bounding-box grid**, the densest 1% of cells contain
**92.40% of pickups** and **84.58% of drop-offs**; the corresponding top-5%
shares are **99.51%** and **97.99%**. These localized patterns suggest that
geographic information may add predictive value beyond distance and time.


## 6. Feature Engineering Summary

The Notebook table documents source/generation, business meaning and selection rationale for nine candidates: `trip_distance`, `pickup_hour`, `day_of_week`, `is_weekend`, `passenger_count`, `pickup_longitude`, `pickup_latitude`, `dropoff_longitude`, and `dropoff_latitude`. Distance is Haversine straight-line distance; temporal fields retain the original datetime clock convention. `key` is excluded, `pickup_datetime` is only a source for derived temporal features, and `fare_amount` is the target.

## 7. Feature Relevance Analysis

Pearson/Spearman use the existing 300,000-row EDA sample. Mutual Information uses a reproducible 50,000-row subsample, seed 42, `n_neighbors=5`, and explicitly discrete temporal/passenger fields (`mutual_info_regression`). Settings, versions and sample indices are saved alongside the numeric results.

| Feature | Pearson r (300k) | MI in nats (50k) |
|---|---:|---:|
| `trip_distance` | 0.8535 | 0.9101 |
| `pickup_hour` | -0.0200 | 0.0130 |
| `day_of_week` | 0.0023 | 0.0004 |
| `is_weekend` | -0.0042 | 0.0000 |
| `passenger_count` | 0.0132 | 0.0073 |
| `pickup_longitude` | 0.4187 | 0.0990 |
| `pickup_latitude` | -0.2142 | 0.0808 |
| `dropoff_longitude` | 0.2984 | 0.1181 |
| `dropoff_latitude` | -0.1735 | 0.1048 |

Distance remains strongest in linear, monotonic and MI association. Geography ranks next in MI; its concentrated/localized spatial patterns cannot be valued using Pearson alone. Temporal features retain clear grouped/nonlinear patterns, even though hourly Pearson is near zero and weekly MI is small/zero. Day-of-week and weekend have overlapping information (Pearson ≈0.78).

MI is model-independent univariate dependence, **not Model Feature Importance**, causation, or demonstrated incremental predictive value. Small/zero estimates do not prove absence of useful relationships. Prioritize distance, four coordinates and pickup hour for Week 3 validation; retain weekly fields and passenger count as secondary candidates. No predictive modeling is performed in this addition.

## 8. Passenger Count: Full-Dataset Evidence

Aggregation covers all **54,004,358** trips. One-passenger trips account for **69.39%**. Common counts 1–6 have average fares **$11.16–$12.11** and average distances **3.258–3.491 km**, with no monotonic passenger–fare trend. Two-passenger trips have higher fare and distance than single-passenger trips ($11.79 / 3.491 km vs $11.16 / 3.258 km); six passengers have the highest common-group fare ($12.11), but not the longest distance (3.387 km). These means do not isolate a passenger effect. Pearson **0.0132** and MI **0.0073** indicate weak observed univariate relevance.

Only **64** trips fall outside counts 1–6: 7 (13), 8 (7), 9 (21), 129 (1), 208 (22). Counts 129/208 are data-quality flags; all records remain unchanged. Rare-group means cannot support general passenger conclusions.

New artifacts: [correlation heatmap](figures/week2/feature_correlation_heatmap.png), [target correlations](figures/week2/feature_target_correlation.png), [MI relevance](figures/week2/feature_relevance.png), [passenger fare/distance comparison](figures/week2/average_fare_by_passenger_count.png), and [full passenger aggregation](passenger_count_stats.csv).
