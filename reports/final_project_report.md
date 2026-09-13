# NYC Taxi Fare Prediction

## 1. Executive Summary

This project examines which trip characteristics help estimate NYC taxi fares and how an initial predictive model could support a mobility platform. Analysis used 54,004,358 processed records and a reproducible sample of one million eligible trips, with a frozen 800,000-row training and 200,000-row test split.

Random Forest achieved test RMSE of $3.81, MAE of $1.95, and R² of 0.836. Its RMSE was 61.14% below a median-fare baseline. Trip distance dominated model importance, while pickup and drop-off coordinates also contributed useful predictive context. These findings describe associations and model dependence, not causal pricing effects.

Typical errors were substantially smaller than tail errors: median absolute error was $1.18, but zero-distance trips had about 2.93 times the RMSE of positive-distance trips. Fares above $100 were strongly underpredicted, although that test segment contained only 36 records. Near-zero aggregate bias therefore obscures important subgroup weaknesses.

The practical priorities are to combine distance and location in fare estimates, validate ambiguous zero-distance routes separately, and develop evidence-based uncertainty safeguards for expensive trips. Additional route-context data and prospective validation are needed before operational use. The current model is an initial predictive model, not a production-ready pricing system.

## 2. Business Problem

Customers and operations teams need fare estimates that reflect trip characteristics and make important exceptions visible. The analytical question is how well recorded distance, time, passenger count and location predict fare, and where estimates need qualification. Fare prediction alone cannot determine whether surge pricing or another pricing intervention improves revenue or customer outcomes.

## 3. Data and Methodology

The processed source contains **54,004,358 rows**; **54,003,614** satisfy the modelling policy. Eligible records have 1–6 passengers, fare at least $2.50 and finite required values. Zero/near-zero distances, long trips and high fares remain eligible. A uniform random **1,000,000-row** eligible sample supports a frozen **800,000/200,000 train/test split**. [Population audit](modeling_eligibility_metadata.json), [split record](modeling_split_metadata.json)

Feature engineering provides Haversine trip distance and pickup hour/day/weekend fields, alongside passenger count and four coordinates. The identifier and raw datetime string are excluded; fare is the sole target. EDA combines reproducible samples with full-data temporal and geographic summaries. A training-only median baseline, Random Forest and HistGradientBoosting were compared with fixed first-pass parameters, without tuning. Interpretation uses RF impurity importance and five-repeat permutation importance on a fixed 50,000-row test subset; error analysis uses the full 200,000-row test set. [EDA](week2_key_findings.md), [interpretation methods](model_interpretation_metadata.json)

## 4. Key Findings

- **Distance is central:** Pearson/Spearman associations with fare are **0.8535/0.8466**, and distance leads both model-importance methods.
- **Location complements distance:** all four coordinates appear in both top-five lists. Spatial EDA also shows concentrated trip activity; geography should not be judged by Pearson correlation alone.
- **The learned model improves substantially on a naive estimate:** Random Forest reduces test RMSE by **61.1422%** versus the median baseline.
- **Typical trips and exceptions differ:** median absolute error is **$1.1840**, while zero-distance and high-fare segments have much larger errors.

Sources: [reviewed EDA](week2_key_findings.md), [benchmark](model_benchmark_results.csv), [importance comparison](model_feature_importance_summary.csv).

## 5. Predictive Modeling

| Model | Test RMSE ($) | Test MAE ($) | Test R² |
|---|---:|---:|---:|
| Median Baseline | 9.803183 | 5.303599 | -0.086398 |
| Random Forest | 3.809299 | 1.951969 | 0.835962 |
| HistGradientBoosting | 3.847865 | 1.980753 | 0.832624 |

RMSE gives extra weight to large mistakes; MAE reports the average absolute dollar error; R² describes squared-error improvement over a constant test-mean reference, not classification accuracy. Random Forest is the **best-performing model in the initial benchmark**: RMSE **$3.8093**, MAE **$1.9520**, R² **0.8360**, with **61.14%** lower RMSE than the median baseline. HistGradientBoosting performs similarly, and one frozen split cannot establish a universally superior model. [Benchmark results](model_benchmark_results.csv)

## 6. Model Interpretation and Error Analysis

Distance impurity importance is **0.853407**. Its permutation RMSE degradation is **$7.408122**, followed by destination longitude (**$1.192368**). Distance and the four coordinates comprise both top-five sets. Correlated/derived features may share information; these scores do not isolate causal effects or the gain from retraining with a field removed. [Impurity](random_forest_feature_importance.csv), [permutation](random_forest_permutation_importance.csv)

Full-test absolute-error median/P90/P95/P99 are **$1.1840/$4.0674/$5.9492/$13.3022**. Common lower-fare trips are comparatively well estimated, but this does not imply every ordinary trip has a small error. [Residual statistics](model_interpretation_metadata.json)

| Test segment | Rows | RMSE ($) | MAE ($) |
|---|---:|---:|---:|
| Zero distance | 2,096 | 10.7459 | 6.1401 |
| Positive distance | 197,904 | 3.6663 | 1.9076 |
| Actual fare >$100 | 36 | 88.9635 | 72.6768 |

Zero-distance RMSE is **2.93×** positive-distance RMSE, without proving the records are incorrect. The >$100 tail has only **36 test rows**, so it identifies a weakness but cannot support a stable operational threshold. These segments overlap and their row counts should not be added. [Distance slices](model_error_zero_distance.csv), [fare bands](model_error_by_fare_band.csv)

Using **mean error = predicted − actual**, the lowest fare band is overpredicted by **$0.7292**, while >$100 fares are underpredicted by **$72.3029**. The overall mean error is only **−$0.0081**. Small aggregate bias therefore hides fare-band-specific bias. Residuals use **actual − predicted**, with median **-0.3977**. [Error evidence](model_interpretation_metadata.json)

## 7. Strategic Recommendations

1. **Distance + location-aware estimation.** Finding/evidence: distance dominates, and four coordinates remain important under both methods. Recommendation: retain these inputs in an initial prototype and validate route/location inputs. Expected value: better-informed quotes and operational context. Limitation: road distance and route details are missing, and incremental geographic gain has not been isolated through retrained ablation.
2. **Separate validation for ambiguous routes.** Finding/evidence: zero-distance RMSE is **2.93×** higher. Recommendation: confirm coincident pickup/drop-off locations and provide qualified estimates or assisted review when route uncertainty remains. Expected value: fewer misleading estimates and focused input checks. Limitation: some zero-distance trips are genuine; do not automatically delete them or assume every near-zero trip has the same risk.
3. **High-fare uncertainty safeguards.** Finding/evidence: the >$100 slice shows severe underprediction, but only **36 test rows**. Recommendation: collect unusual-route/toll context and validate prospective flags and calibrated ranges. Expected value: clearer customer expectations and less severe underestimation exposure. Limitation: actual fare is unknown at quote time; neither a prospective trigger nor a confidence interval has been validated. No revenue uplift is claimed.

The detailed finding → evidence → recommendation → expected value → limitation chains are in the [Phase 4 synthesis](phase4_synthesis.md).

## 8. Limitations and Next Steps

Haversine distance differs from road distance. Weather, traffic, toll, airport and detailed route variables are absent from current inputs. Zero-distance trips remain ambiguous, and extreme fares have sparse test coverage. Importance is not causality; the random split tests historical generalization, not future forecasting. The reused test set is no longer untouched evidence for subsequent model changes.

Before operational adoption, obtain richer trip-context data, assess a forward-looking evaluation population, validate uncertainty and exception handling, and evaluate service requirements and drift. These are proposals, not completed experiments. The project provides an initial predictive model and evidence for prioritizing work; it does not provide deployment validation or a causal pricing strategy.

*Prepared for a final report of approximately five pages or fewer; final pagination remains subject to layout review.*
