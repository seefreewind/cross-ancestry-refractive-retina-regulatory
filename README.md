# Cross-ancestry genetic architecture of refractive error and retinal regulatory variation

This repository contains reproducible code, configuration files, manuscript-ready tables/figures, QC reports and submission materials for a Human Genetics manuscript testing whether ancestry-associated retinal regulatory variation marks genomic regions where refractive-error association effects diverge between European and East Asian ancestry GWAS.

## Scope

The repository reports a bounded statistical genetics analysis:

1. genome-wide EUR-EAS shared refractive-error architecture;
2. broad retinal open-chromatin-region architecture;
3. enrichment testing of ancestry-associated retinal DAR SNPs for EUR-EAS association-effect heterogeneity relative to matched non-DAR retinal OCR SNPs.

The primary manuscript-facing S-LDXR estimates use MAF > 0.05. Broader MAF > 0.01 estimates are retained as supporting analyses.

## What is included

- `scripts/`: QC, harmonization, annotation, S-LDXR, heterogeneity, robustness and submission-generation scripts.
- `config/`: fixed analysis configuration files used to define inputs and robustness checks.
- `metadata/`: resource inventories and source metadata tables.
- `results/`: small machine-readable summary outputs used in the manuscript, excluding large raw/intermediate arrays.
- `figures/human_genetics/`: manuscript figures exported as PDF, SVG and 600-dpi PNG.
- `manuscript/`, `supplement/`, `submission/`: current manuscript, supplement, tables, declarations and cover-letter materials.
- `reports/`: provenance, QC, reference and final submission audits.

## What is not included

Raw and large third-party data are not redistributed here. This includes public GWAS summary-statistics files, 1000 Genomes/baselineLD resources, dbSNP downloads, raw HRCA files, intermediate parquet feature matrices and compressed S-LDXR sidecar outputs. Obtain these files from their original providers and rebuild local intermediates with the scripts and configuration files in this repository.

## Key manuscript files

- `manuscript/HUMAN_GENETICS_MANUSCRIPT_v1.3.md`
- `manuscript/HUMAN_GENETICS_INTRODUCTION_v1.3.md`
- `supplement/HUMAN_GENETICS_SUPPLEMENT_v1.0.md`
- `submission/tables/Table1_GWAS_analysis_characteristics.tsv`
- `submission/tables/Table2_main_cross_ancestry_architecture.tsv`
- `submission/tables/Table3_DAR_heterogeneity_tests.tsv`

## Data availability boundary

This study uses publicly available summary-level and aggregate datasets and involved no new participant recruitment. Provider-restricted or license-governed files should be downloaded by users from the original repositories under the applicable terms. The repository is intended to make the analysis logic, QC decisions and manuscript summary outputs auditable without redistributing restricted source data.

## Repository URL

https://github.com/seefreewind/cross-ancestry-refractive-retina-regulatory

## Citation status

The manuscript currently requires author final review before journal submission, especially final institutional ethics wording and journal metadata checks.
