# NYC Taxi Fare Prediction — Final Internship Report

## 1. 本阶段工作概述

本项目已完成从 Business Understanding、Data Cleaning、Feature Engineering、EDA 到 Predictive Modeling、Model Interpretation、Error Analysis 和 Strategic Recommendations 的 end-to-end workflow。本阶段将冻结的分析结果整理为 README、final report、五页 executive deck 内容和提交检查清单，没有重新训练模型或调整数据。

## 2. 数据处理与分析完成情况

Processed source 共 **54,004,358 行**，其中 **54,003,614 行**满足 modelling eligibility。通过 chunk-based processing 控制内存使用；针对 missing/non-finite values、乘客人数、车费以及坐标和时间字段进行验证。建模样本采用跨全量 eligible population 的可复现随机抽样，得到 **1,000,000 行**，并冻结 **800,000/200,000 train/test split**。

Feature Engineering 包含 Haversine trip distance、pickup hour、day of week、weekend flag，并保留 passenger count 和上下车坐标。EDA 确认距离与车费关系最明显，同时观察到 grouped temporal patterns 和空间集中性。原始 `key` 和 datetime string 不进入模型；zero-distance 与 high-fare records 按已批准规则保留。[数据准备](modeling_eligibility_audit.csv)、[EDA](week2_key_findings.md)

## 3. Predictive Modeling

| Model | RMSE ($) | MAE ($) | R² |
|---|---:|---:|---:|
| Median Baseline | 9.803183 | 5.303599 | -0.086398 |
| Random Forest | 3.809299 | 1.951969 | 0.835962 |
| HistGradientBoosting | 3.847865 | 1.980753 | 0.832624 |

Random Forest 是当前 initial benchmark 的 best-performing model，RMSE 相比 median baseline 降低 **61.14%**。三个模型使用同一 frozen test set；没有 hyperparameter tuning。RMSE 对较大误差更敏感，MAE 表示平均绝对美元误差，R² 不能理解为分类准确率。[Benchmark](model_benchmark_results.csv)

## 4. Model Interpretation

`trip_distance` 的 impurity importance 为 **0.853407**，Permutation Importance 中打乱该变量使解释子集 RMSE 增加 **$7.408122**。距离与四个 geographic features 构成两种方法共同的 Top 5，说明位置对当前模型具有预测信息。

Feature Importance 不代表 causality。距离与坐标、day_of_week 与 is_weekend 存在信息重叠，不能直接把 importance 数值当作单个变量的独立业务贡献。[Importance 对照](model_feature_importance_summary.csv)

## 5. Error Analysis

Absolute error median 为 **$1.1840**，P95 为 **$5.9492**。Zero-distance RMSE 为 **$10.7459**，positive-distance 为 **$3.6663**，前者约为后者 **2.93 倍**。这提示需要单独核查该类行程，但不等于它们全部是数据错误。

>$100 fare test slice 只有 **36 条**，RMSE 为 **$88.9635**、MAE 为 **$72.6768**，不能过度泛化。按 prediction−actual 定义，低车费组平均高估约 **$0.7292**，高车费组平均低估约 **$72.3029**；整体平均误差约 **−$0.0081**，说明 aggregate bias 很小也可能掩盖 subgroup bias。[误差分组](model_error_by_fare_band.csv)、[零距离对照](model_error_zero_distance.csv)

## 6. 主要业务理解

- 距离是估价核心，但位置和行程背景仍值得保留。
- 需求最高的时段不等于平均车费最高的时段，不能仅凭时间分组关联推导涨价策略。
- 总体指标不能替代 subgroup 检查，尤其是 zero-distance 和 high-fare tail。
- 预测分析可以支持估价和异常处理，尚不能证明定价干预会增加收入。

## 7. Strategic Recommendations

1. **Distance + location-aware fare estimation**：以距离和位置支撑初步估价，并验证路线信息。
2. **Separate validation for zero-distance / anomalous trips**：确认上下车位置，对路线不明确的行程提供带说明的估价或人工核查，不自动删除记录。
3. **Safeguards / uncertainty handling for high-fare tail**：补充特殊路线、toll 等信息，验证可在报价前使用的提示条件和不确定性范围。36 条高车费测试记录不足以直接制定稳定规则。

预期价值是更清晰的估价和例外处理；业务收益尚未被实验证实。[完整建议](phase4_synthesis.md)

## 8. 本项目中的学习与提升

本项目要求将数据质量、特征定义、抽样和模型评估连成完整流程，而不是把拟合模型当作终点。特别是相近的总体指标并没有揭示 zero-distance 和 high-fare slice 的大误差，error slicing 改变了对模型能力边界的判断。

Reproducibility 不仅是固定 seed，还需要确认输入内容、行序与 split assignment。文件 fingerprint、持久化索引和 metadata 使这些条件可核对。将技术结果写成业务建议时，也需要区分观测事实、建议行动、预期价值和未验证的限制。

Notebook、CSV、metadata 与报告互相引用有助于保持证据一致。最终审计也暴露了跨会话 execution counts 和依赖清单缺失等交付问题；这些应诚实标记，不能仅通过重编号或隐藏输出来制造整洁印象。

## 9. Limitations

Haversine distance 不等于 road distance；当前没有显式 traffic、weather、toll、airport 或详细 route features。Random split 不等于 future forecasting validation，且同一 test set 已被用于初步比较和解释。Feature Importance 不是因果证据，极端车费样本较少，项目尚未完成 production deployment validation。

## 10. 后续工作

核心分析开发已经完成。当前重点是 final presentation、repository packaging 和人工提交审核。可选扩展包括 road-network distance、route/airport/borough features、traffic/weather、time-based validation，以及经验证后的 dashboard 或 deployment。上述扩展尚未执行；本阶段未改变冻结结果。[提交清单](final_submission_checklist.md)
