# Elevated blood pressure at health screening across districts of South Korea, 2019-2024

Analysis code for a manuscript on the district geography of the elevated blood pressure criterion of the metabolic syndrome at the Korean national general health screening.

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24357348 (v1.0.0).

This code is released under the MIT licence.

## Contents

This repository contains code only. The processed district-year data (analytic panel, expected counts, result tables and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/HBP/` | Covariate pool and model settings (`make_pool_sets_hbp.py`, `sets_HBP_*.json`, `config_HBP_std3.json`), data checks (`gate_sqlite_crosscheck_hbp.py`, `gate_zero_year_audit_hbp.py`), the model chain (`run_std3_chain.sh`, `run_std3_chain_resume.sh`) and the district adjacency graph (`graph_593.graph`). Sensitivity versions: queen contiguity graph `s577`, without the share aged 80 or older `s2`, unstandardised expected counts `sc`, population-based expected counts `sp`, 2013-2017 `aux`, 2013-2024 including 2018 `full` |
| `04_분석/HBP/MS/build/` | Scripts that read the result tables and write every number, table and figure in the manuscript and supplementary material |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- Examinees meeting the elevated blood pressure criterion of the metabolic syndrome (systolic >=130 or diastolic >=85 mmHg, or antihypertensive treatment) and examinees, by district and sex and nationally by sex and age: National Health Insurance Service screening statistics, KOSIS tables DT_35007_N138 and DT_35007_N139, 2013-2024.
- Distribution of measured systolic and diastolic blood pressure by province and age: KOSIS DT_35007_N060 to DT_35007_N063 (judgement check).
- Screening targets and attendees: KOSIS DT_35007_N001 and DT_35007_N001_1.
- Population by sex and 5-year age group: Ministry of the Interior and Safety, resident registration statistics.
- District covariates: Community Health Survey (walking, moderate-or-higher physical activity, obesity, high-risk drinking, current smoking), public sports facility register, health-resource statistics (internal medicine specialists), public assistance statistics and KOSIS local indicators (fixed adjustments and negative controls).

## Pipeline

Set `ST_DATA_ROOT` and `ST_GPT_DATASET` to the local copies of the public source files and the read-only district database, then run from the repository root.

| Step | Script | Output |
|---|---|---|
| 1 | `99G_hbp_judgement_gate.py` | Comparison of the published criterion with the measured blood pressure distribution, by year, sex and province |
| 2 | `99H_build_E_hbp.py` (uses `38_build_Estd_all.py`, `40_region_crosswalk.py`, `50_build_master_panel.py`) | District counts (code-based linkage; Sejong from province-level rows) and expected counts by indirect standardisation in 2 sexes x 15 age groups |
| 3 | `04_분석/HBP/make_pool_sets_hbp.py` | Covariate pool and model settings (fixed and hashed before fitting); comparison outcomes |
| 4 | `80_build_disease_panel_v.py HBP` (`ST_VER=std3`) | Analytic panel |
| 5 | `81_fit_inla.R HBP`, `81R_hbp_refit_binom.R` | Principal model, 200-subset multiverse, period models, sensitivity versions; repeat fit and five likelihoods |
| 6 | `85_window_maps.R`, `86_yearly_maps_ehsa_hbp.py`, `87_window_grid.py` | Maps and yearly smoothed ratios |
| 7 | `88g_sens_prep.py HBP std3 HTNTC,UNDXHC`, `88g_sens_suite_hbp.R` (`GROUP=1..6`), `88h_ppc_varpart.R`, `88k_struct_kh_hbp.R` (nb, struct, kh, review) with `kh_constraints_hbp.R`, `89g_sens_combine.py` | Alternative specifications, comparison outcomes, Knorr-Held models, decomposition |
| 8 | `04_분석/HBP/MS/build/` | Manuscript numbers, tables, figures and supplementary material |

The boundary file is found at `data/boundary/final.shp` by default; set `ST_SHP` to use another path. R jobs are wrapped in `rslot.sh` and run with one INLA thread.

## Software

R 4.6.0 with R-INLA 25.10.19, spdep and sf; Python 3.9 with pandas, geopandas, numpy, scipy, matplotlib and python-docx.

## Licence

MIT (see `LICENSE`).
