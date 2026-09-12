# Supplementary Information

## Supplementary Methods

### Genome build adjudication

The released GWAS files did not contain an explicit genome-build declaration. Coordinates were adjudicated against dbSNP Build 151 using assembly-informative variants, followed by an independent holdout check. The analysis was anchored to GRCh37.p13 after complete autosomal concordance in the adjudication workflow.

### dbSNP holdout and liftover QC

Assembly-informative variants were split into adjudication and holdout sets. Human retinal annotations originating in hg38 were lifted to GRCh37.p13. Lifted annotations were checked for row-set, coordinate and allele compatibility before use.

### Exact row alignment and excluded preliminary files

Formal analyses were restricted to files passing exact SNP-universe and row-order checks across summary statistics, reference panels, weights, LD scores and annotations. Preliminary baseline files failing this requirement were excluded before inference and retained only as provenance records.

### MAF threshold audit

The S-LDXR method paper and software default use MAF > 0.05 in both populations for regression and heritability SNPs. The manuscript therefore reports MAF > 0.05 estimates as the primary S-LDXR results. The broader MAF > 0.01 run is retained as a supporting analysis because it used the same aligned inputs and produced consistent genome-wide and all-retinal-OCR conclusions.

### Popcorn and S-LDXR estimand comparison

The source GWAS reported substantial cross-ancestry sharing using Popcorn genetic-impact correlation. The present study used S-LDXR GCORSQ, a squared cross-population genetic-correlation quantity estimated with ancestry-specific LD and annotations. The two values should not be compared numerically because they differ in scaling and estimand.

### Effect-scale audit

The EUR-EAS heterogeneity statistic used released source beta and standard-error fields after allele alignment. Because the source meta-analyses combined heterogeneous phenotype definitions, the statistic is interpreted as association-effect heterogeneity on the released source-effect scale.

### Sample-overlap audit

No material cross-ancestry participant overlap was identified from available cohort documentation, and covariance was set to zero. Residual overlap cannot be fully excluded and is treated as a limitation.

## Supplementary Tables

| Table | Content | Source |
|---|---|---|
| S1 | GWAS source cohort and public-file distinction | `reports/EUR_NO23ANDME_SAMPLE_SIZE_AUDIT.md` |
| S2 | Genome-build adjudication and holdout summary | `reports/GWAS_BUILD_EVIDENCE.md`; build-resolution outputs |
| S3 | Harmonized EUR-EAS SNP counts | `data/processed/EUR_EAS_HARMONIZED.parquet`; QC summaries |
| S4 | S-LDXR input filtering and alignment | `results/phase1/SLDXR_INPUT_FILTER.tsv`; `results/phase1c/*ALIGNMENT*.tsv` |
| S5 | Ancestry-matched LDSC heritability | `results/phase1/LDSC_H2_SUMMARY.tsv` |
| S6 | S-LDXR MAF-threshold comparison | `results/presubmission/SLDXR_MAF_SENSITIVITY.tsv` |
| S7 | Broad retinal OCR and DAR S-LDXR context | `results/phase2b/RETINAL_OCR_SLDXR_CONTEXT.tsv` |
| S8 | Primary and sensitivity DAR heterogeneity endpoints | `results/phase2/PHASE2_DAR_HETEROGENEITY_ENRICHMENT.tsv` |
| S9 | Matched permutation null and balance audit | `results/phase2/PHASE2_DAR_MATCHED_PERMUTATION_NULL.tsv`; `results/phase2b/MATCHED_PERMUTATION_BALANCE_AUDIT.tsv` |
| S10 | LD-pruned sensitivity analyses | `results/phase2b/LD_PRUNED_HETEROGENEITY_SENSITIVITY.tsv` |
| S11 | Block-level robustness | `results/phase2b/LD_BLOCK_ROBUSTNESS.tsv`; `results/phase2b/LD_BLOCK_HETEROGENEITY_SUMMARY.tsv` |
| S12 | Effect-size precision and large-enrichment boundary | `results/phase2b/PRIMARY_EFFECT_SIZE_PRECISION.tsv`; `results/phase2b/DAR_POWER_BOUNDS.tsv`; `results/phase2b/EQUIVALENCE_BOUNDARY.tsv` |
