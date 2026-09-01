# 实习周报（Week 2）

## 一、本周工作内容

本周基于 Week 1 的 cleaned dataset，完成 Feature Engineering 与 Phase 2 EDA。分析对象为 54,004,358 条有效记录，重点研究行程距离、时间和空间位置与车费及需求的关系，并整理了统计文件、图表和完整 Notebook。

## 二、Feature Engineering

新增 `trip_distance`、`pickup_hour`、`day_of_week` 和 `is_weekend`。行程距离使用向量化 Haversine distance，表示上下车坐标间的直线距离。约 5.2GB 的 cleaned dataset 通过 chunk-based processing 处理，避免一次加载全部数据。

检查中发现 temporal timezone interpretation 存在偏差。Kaggle 时间应直接按原始 `pickup_datetime` clock time 提取，不应额外转换为纽约时区。修正后重新生成全量特征，并通过 10 万行样本及 5400 万行统计验证。

## 三、Exploratory Data Analysis

### Distance Analysis

距离与车费呈明显正向关系，Pearson correlation 为 0.8535，Spearman correlation 为 0.8466，是目前最显著的 fare-related variable；但图中仍有 fare bands，说明距离并非唯一影响因素。

### Temporal Analysis

需求在 19:00 达到高峰，在 05:00 最低；05:00 的平均车费和平均距离却同时最高，说明 early-morning 高车费与较长行程同时出现，而非对应更高需求。Friday 需求最高。Weekend 平均距离约高 4.8%，平均车费却约低 0.6%，说明 aggregated temporal fare variation 不能只由距离解释。

### Geographic Analysis

使用全量数据完成 250×250 的 2D spatial density aggregation，没有绘制 5400 万个散点。Pickup 与 drop-off spatial density 的相关性为 0.9625，分布高度相似且集中于少量网格；drop-off 相对更分散，并存在少量外围热点。

## 四、技术实现与数据处理

不同任务采用不同数据策略：Distance visualization 使用可复现的 300k sample；hour、day 和 weekday/weekend statistics 使用 full-dataset chunk aggregation；Geographic Analysis 使用全量 2D histogram。这样兼顾了内存限制、可视化效率和关键统计的完整性。

## 五、本周主要成果

- 完成 feature-ready dataset 与相关脚本；
- 完成 Distance、Temporal、Geographic EDA；
- 更新 EDA Notebook，保存统计 CSV、Week 2 figures、density cache 与 hotspots；
- 整理 Key Findings 和 Executive Summary 内容框架。

## 六、下周工作计划

正式进入 Phase 3 前，先完成 3–5 页 Executive Summary。之后开展 Predictive Modeling & Validation，包括 train/test split、baseline regression、Random Forest、Gradient Boosting、RMSE comparison 与 feature importance。

## 七、本周总结

本周完成了从大规模特征工程到多维 EDA 的流程，也通过 timezone 修正认识到字段语义验证的重要性。Week 2 技术分析和文档已基本收尾，可进入结果汇报准备阶段。
