# Final Repository Audit

Audit scope: repository working tree, tracked/untracked files, ignored local artifacts, Markdown paths and serialized Notebook outputs. Date: 2026-09-12. Models and notebooks were not rerun. No data, model settings, split assignments or frozen analytical results were changed.

## Repository and Git State

- **[PASS]** Before the earlier packaging task, `git status --short` was empty; **67 files** were tracked before packaging. No ignored large dataset was tracked.
- **[PASS]** `.gitignore` covers `data/raw/`, `data/processed/`, `.venv/`, `__pycache__/`, `.ipynb_checkpoints/`, `.DS_Store`, and the Week 2 relevance sample-index CSV. `git check-ignore` confirmed coverage for the observed data/junk paths, modelling split NPZ and relevance sample indices. No ignore-rule change was needed.
- **[REVIEW]** The earlier packaging changes remain. Submission hardening adds `requirements.txt`, updates README/audit/checklist, and normalizes five artifact-location strings in three metadata JSON files. Nothing was staged, committed or pushed. Human review is still required before the final commit.

## Large Data and Local Artifacts

The following files exceed **10 MiB** outside `.git/` and the ignored dependency environment. This is an audit threshold, not a data-quality rule.

| Local file | Size (GiB) | Git status |
|---|---:|---|
| `data/processed/train_clean.csv` | 5.165 | Untracked and ignored |
| `data/processed/train_features_sample.csv` | 0.012 | Untracked and ignored |
| `data/processed/modeling_sample_1m.csv` | 0.070 | Untracked and ignored |
| `data/processed/eda_sample_300k.csv` | 0.036 | Untracked and ignored |
| `data/processed/train_features.csv` | 6.430 | Untracked and ignored |
| `data/raw/train.csv` | 5.306 | Untracked and ignored |

The local `data/processed/modeling_split_indices.npz` also exists and is ignored. All observed large data files remain local; a fresh Git clone does not include the frozen sample or index artifact.

**[PASS — informational]** Six `.DS_Store` files, four `src/__pycache__` bytecode files and one notebook checkpoint remain locally, all ignored. The checkpoint is `notebooks/.ipynb_checkpoints/01_data_understanding-checkpoint.ipynb`. None was deleted: local housekeeping is optional, and the checkpoint may contain useful work. No additional `.tmp`, `.bak`, `.log` or `~$` candidates were found in the project scan. Dependency-environment internals and Git object storage were excluded from this source-file inventory.

## Notebook Integrity and Execution Order

The table uses **1-based cell positions**. All five top-level notebooks parse as valid notebook documents; the four main analytical notebooks have saved execution counts for all nonempty code cells. No saved error output or traceback was found.

| Notebook | Saved error outputs / traceback | Unexecuted nonempty code cells | Execution-count review |
|---|---|---|---|
| `notebooks/01_data_understanding.ipynb` | 0 / 0 | 0 | No non-increasing count detected |
| `notebooks/02_data_cleaning.ipynb` | 0 / 0 | 0 | No non-increasing count detected |
| `notebooks/03_exploratory_data_analysis.ipynb` | 0 / 0 | 0 | cell 57: 33 → 3; cell 63: 6 → 3 |
| `notebooks/04_predictive_modeling.ipynb` | 0 / 0 | 0 | cell 29: 14 → 3; cell 43: 9 → 1; cell 59: 10 → 1; cell 75: 8 → 1 |
| `notebooks/basic_code.ipynb` | 0 / 0 | 6 | No non-increasing count detected |


**[PASS — informational]** Notebook cells were executed across multiple sessions; saved outputs contain no traceback, but execution counters are not globally monotonic. Static review of code and saved text/table output found no obvious substantive mismatch; this does not certify full execution reproducibility. Main-notebook `execute_result` counters match their owning cells. Modeling cell 67 retains a joblib warning about falling back to logical CPU count, not a traceback. Historical phase labels/stop notes remain untouched; no outputs or counters were cleared, reset or rerun.

**[PASS — auxiliary]** `basic_code.ipynb`: **Auxiliary / exploratory notebook; not required for final reproducibility.** Its six nonempty cells with null execution counts are positions 3–8: `df.head()`, `df.duplicated().sum()`, `df.isna().sum()`, `df.info()`, `df.shape`, and `df.describe()`. They inspect an early 100,000-row raw-data sample. Several retain prior outputs despite null cell counts (including five old `execute_result` counters); those displays are consistent with their inspection operations, but are not certified current. The final empty cell is excluded from the six. README mentions the notebook only in the repository inventory; final reports and the main workflow do not depend on it. The file is unchanged and no cells were executed.

**[REVIEW]** Independent clean-environment replay remains an optional separately authorized validation decision before submission. No clean-kernel Run All is certified. Earlier preparation cells write derived artifacts and later cells fit models; the lightweight checks below do not execute them.

## Documentation and Path Checks

- **[FIXED]** README described only completed Phases 1–2 and showed modelling/recommendations as pending. It now presents the completed workflow, frozen model/error evidence, approved recommendations and actual repository contents. Valuable dataset, Week 2 evidence and rebuild-command guidance were retained.
- **[PASS]** No broken relative Markdown links or machine-specific absolute paths were present in the original eight Markdown files. The expanded documentation is checked again after creation; figures, reports and README links resolve locally. No path replacement was necessary.
- **[PASS]** Five repository artifact-location strings were normalized to repository-relative paths: `modeling_eligibility_metadata.json` (`source_dataset`), `modeling_split_metadata.json` (`source_dataset`, `modelling_sample_path`), and `model_benchmark_metadata.json` (`modeling_sample_path`, `split_indices_artifact`). They identify existing data files, not historical event text. Resolve them against the repository root. Recursive before/after comparison permits only these string substitutions; hashes, counts, timestamps, model parameters and all analytical values are unchanged. All report JSON files parse and no machine-specific absolute path remains in their string values. Historical paths embedded in frozen notebook outputs are preserved.

- **[PASS]** Existing Week 2 and Week 3 figures and source reports referenced by final materials exist. The deck uses the saved benchmark CSV as a table because no benchmark comparison PNG exists; no figure filename is invented.
- **[PASS]** Model metrics, importance and error-slice numbers agree across the new documents and existing report sources. High-fare results explicitly retain the **36-test-row** limitation; zero distance is not declared inherently erroneous.

## Reproducibility and Submission Gaps

- **[PASS]** [requirements.txt](../requirements.txt) contains nine version-pinned dependencies from the current environment: pandas, NumPy, matplotlib, seaborn, scikit-learn, SciPy, joblib, IPython and ipykernel. Imports were scanned in all four source Python files and five top-level notebooks. Joblib/IPython are directly imported; SciPy supports statistical/sklearn operations, and ipykernel provides the Notebook kernel. No plotly, geopandas, folium or xgboost usage was found. The `jupyter` metapackage and `notebook` server are not installed, so no guessed version was added. A compatible editor/frontend must supply the UI; README makes this explicit. No package was installed, upgraded or downgraded. This minimal manifest is not a complete transitive lockfile.
- **[REVIEW]** A clean-environment install/replay has not been attempted. The owner must arrange permitted data/artifact access and decide whether independent replay is required for submission; no training is authorized here.
- **[REVIEW]** License: Project owner should decide repository license before public release. No license file was found or added; no data redistribution rights are asserted.
- **[REVIEW]** Content length appears suitable for a <=5-page report, but final pagination must be verified after export/layout. The roughly 1,143-word final report is unchanged; no PDF was generated. Presentation rendering/readability and final submission format remain human checks.
- **[PASS]** No core deliverable is MISSING within the requested repository submission scope.

## Lightweight Reproducibility Smoke Checks

Checked in the existing `.venv`, without running a notebook pipeline or fitting a model:

| Check | Result / scope |
|---|---|
| Manifest package/version mapping | PASS — all nine pins match installed distribution metadata |
| Python imports | PASS — all nine dependency modules import; notebook kernel/runtime available |
| Report and artifact locations | PASS — 27 repository-relative JSON artifact locations and 102 links across 12 Markdown files exist locally |
| Large data exclusion | PASS — all ten observed raw/processed local files are ignored and absent from Git's tracked-file list |
| Benchmark CSV | PASS — readable, three benchmark model rows; file unchanged |
| JSON parsing | PASS — all seven `reports/*.json` parse; only five allowed path strings differ |
| README links and handoff files | PASS — links resolve; final report, deck and weekly report exist |
| Notebook integrity | PASS — all five validate; no saved traceback; counters reviewed informationally |
| Frozen artifact preservation | PASS — source/notebook/figure/CSV contents unchanged; large data size/mtime unchanged |

The import check emitted a fontconfig cache-directory warning in the sandbox; matplotlib subsequently built its temporary cache and all imports completed successfully. No repository figure was generated or modified.

These checks establish current-environment readiness only, not independent installation, clean-kernel replay, or end-to-end reproducibility certification.

## Packaging Deliverables

| Action | File |
|---|---|
| Add pinned runtime dependencies | [Requirements](../requirements.txt) |
| Reorganize existing entry point | [README](../README.md) |
| Lightly polish existing report | [Final project report](final_project_report.md) |
| Create audit | [Repository audit](final_repository_audit.md) |
| Create five-slide content | [Executive deck](final_executive_deck.md) |
| Create final Chinese summary | [Internship report](final_internship_weekly_report.md) |
| Create evidence-based handoff list | [Submission checklist](final_submission_checklist.md) |

Final link, number and file-preservation checks are read-only. No README path refers to an invented file; no analysis logic or results were altered. Review the outstanding items before staging or committing.
