# Phase 4 — Synthesis and Strategic Recommendations

## 1. Business Objective

Understand the main predictors of taxi fare and assess an initial fare-estimation model that could inform a mobility platform's customer estimates and operational exception handling. This project evaluates prediction, not demand elasticity or the causal effect of changing prices.

## 2. Key Analytical Findings

1. **Trip distance is the strongest fare predictor.** Week 2 Pearson/Spearman associations are **0.8535/0.8466**, and distance leads both model-importance methods. These are associations, not causal estimates. [EDA](week2_key_findings.md)
2. **Geographic information provides useful additional predictive context.** Distance and all four coordinates form both top-five importance sets; disrupting individual coordinates increases interpretation-subset RMSE by **$0.249801–$1.192368**. This demonstrates model reliance, but does not isolate retrained incremental value beyond distance. [Permutation importance](random_forest_permutation_importance.csv)
3. **Random Forest substantially outperforms the naive median baseline.** Test RMSE falls from **$9.8032** to **$3.8093**, a **61.1422%** reduction on the same frozen test set. [Benchmark](model_benchmark_results.csv)
4. **Most ordinary trips have comparatively moderate errors.** Full-test median absolute error is **$1.1840**, with P95 **$5.9492**. The common [2.50, 10] fare band has MAE **$1.2477**. These results are useful for an initial prototype, but are not a customer service guarantee. [Residual summary](model_interpretation_metadata.json), [fare bands](model_error_by_fare_band.csv)
5. **Zero-distance trips form a high-error segment.** Their RMSE is **2.93×** positive-distance RMSE; genuine short trips or limited coordinate precision may contribute. No records are reclassified or deleted here. [Distance slices](model_error_zero_distance.csv)
6. **The high-fare tail is a weakness, with limited evidence.** The >$100 slice has RMSE **$88.9635** but only **36 test rows**. Its underprediction is hidden by the near-zero overall mean error. [Fare bands](model_error_by_fare_band.csv)

## 3. Model Performance

| Model | Test RMSE ($) | Test MAE ($) | Test R² |
|---|---:|---:|---:|
| Median Baseline | 9.803183 | 5.303599 | -0.086398 |
| Random Forest | 3.809299 | 1.951969 | 0.835962 |
| HistGradientBoosting | 3.847865 | 1.980753 | 0.832624 |

**RMSE** penalizes large errors more heavily and reports them in dollars; it is the primary comparison measure, not an average absolute mistake. **MAE** is the average absolute gap between prediction and actual fare. **R²** compares squared error with using the test-target mean; 0.8360 corresponds to approximately 83.6% of test-fare variation accounted for by this metric, not a percentage of correctly priced trips.

Random Forest is the **best-performing model in this project’s initial benchmark**, with RMSE about **$3.81** and MAE about **$1.95**. HistGradientBoosting is close at RMSE **$3.8479**. This small difference has not been established across repeated splits; neither model is production-ready on the evidence available. [Source](model_benchmark_results.csv)

## 4. Model Interpretation

Distance dominates impurity importance (**0.853407**), while geography remains useful to the fitted model. Both methods select the same five fields; coordinate ordering differs. Permutation importance measures increased RMSE after disrupting a field on a fixed 50,000-row test subset; it is not a forecasted benefit from adding that field. Its five-repeat variability is not a causal uncertainty estimate. Distance derives from coordinates, and weekend derives from day of week, so importance can be shared. The analysis supports preserving location context, not setting prices based on importance weights. [Impurity](random_forest_feature_importance.csv), [permutation](random_forest_permutation_importance.csv)

## 5. Strategic Recommendations

### Recommendation 1 — Use distance and location together for fare estimation

- **Finding:** Trip distance is the dominant predictor, while origins and destinations add useful predictive context in the fitted model.
- **Evidence:** Distance has impurity importance **0.853407**; permuting it increases subset RMSE by **$7.408122**. All four coordinates also appear in both top-five lists. [Importance evidence](model_feature_importance_summary.csv)
- **Recommendation:** Use distance plus pickup/drop-off location as the core of an initial fare-estimation prototype. Validate coordinate inputs and collect actual route distance, toll and route context before considering route-specific rules.
- **Expected Business Value:** More informative fare estimates and clearer trip-level explanations for customers and operations teams; business impact remains to be tested.
- **Limitation:** Haversine distance is not road distance. Correlated inputs share information, and no retrained distance-only comparison has isolated the incremental gain from coordinates. This is not evidence for causal pricing changes or revenue uplift.

### Recommendation 2 — Add a separate validation path for zero-distance estimates

- **Finding:** Zero-distance observations are a high-error segment, not automatically incorrect transactions.
- **Evidence:** Their test RMSE is **$10.7459** across **2,096** trips, versus **$3.6663** for positive distance (**2.93×**). [Distance-slice evidence](model_error_zero_distance.csv)
- **Recommendation:** Flag coincident or near-coincident pickup/drop-off coordinates for location/route confirmation. When route details remain unresolved, show a qualified estimate or offer assisted review rather than silently excluding the trip. Retain these records for monitoring and further investigation; the measured ratio applies to exactly zero distance, not every near-zero trip.
- **Expected Business Value:** Fewer misleading estimates for ambiguous routes and a focused queue for input-quality investigation; these outcomes are proposed, not measured.
- **Limitation:** Short journeys and coordinate precision can create genuine zero-distance observations. The analysis does not establish the cause or validate a replacement estimate.

### Recommendation 3 — Develop cautious safeguards for the high-fare tail

- **Finding:** High actual fares have large errors and systematic underprediction despite almost zero aggregate bias.
- **Evidence:** The **>$100** band has RMSE **$88.9635**, MAE **$72.6768**, and mean predicted-minus-actual error **$-72.3029**, but contains only **36 test rows**. [Fare-band evidence](model_error_by_fare_band.csv)
- **Recommendation:** Collect more unusual-route, toll and other trip-context data. Design and separately validate exception-review triggers and calibrated estimate ranges for potentially expensive trips. A future customer warning should reflect uncertainty rather than promise a precise price.
- **Expected Business Value:** Better expectation setting and reduced exposure to severe underestimation; no financial or service-level improvement has yet been quantified.
- **Limitation:** The >$100 group is defined by the actual completed fare, which is unavailable when quoting. A prospective flag must use available trip information and needs validation. The **36-row** slice cannot establish a reliable cutoff or interval; pooled error percentiles are not calibrated trip-specific confidence intervals. Do not cap targets, discard high fares or claim dynamic surge-pricing benefits.

## Limitations

- Engineered distance is Haversine straight-line/geodesic-style distance, not the actual driven route.
- Weather, traffic, tolls, airport indicators and detailed route information are not current model inputs. Coordinates may proxy some context but do not verify it.
- Zero-distance trips are heterogeneous; poor aggregate performance does not prove each record is a data error.
- Extreme fares have very limited held-out representation: the >$100 slice contains **36 rows**.
- The frozen random 80/20 split measures performance within the historical population, not strict future forecasting. The same test set has supported initial comparison and interpretation; subsequent changes require fresh or forward-looking evaluation rather than treating it as untouched evidence.
- Feature importance and correlations are not causal effects. No demand-elasticity, intervention, revenue or customer-impact study was conducted.
- This is not production deployment validation: prospective input availability, calibrated uncertainty, drift, latency and operational safeguards remain untested.

Phase 4 reads the frozen reports only. No model was retrained, no split changed, and no zero-distance or high-fare record was removed.
