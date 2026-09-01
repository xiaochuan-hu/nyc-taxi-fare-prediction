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
