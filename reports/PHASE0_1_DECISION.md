# Phase 0–1 decision

## Overall verdict: CONDITIONAL GO

The primary EUR–EAS analysis is technically feasible at the harmonization level: 3,262,168 non-palindromic shared SNPs were retained, and the match rate among mutually available non-palindromic CHR:POS SNPs is 99.9848%. Directional concordance is strong among ancestry-specific genome-wide significant subsets, while the genome-wide signed-Z correlation remains a QC statistic rather than a genetic-correlation estimate.

The retinal resource is also usable for a conditional annotation analysis. HRCA S12 provides hg38 OCR resources and S19 provides 2,228 ancestry-DAR rows representing 2,227 unique intervals. A coordinate diagnostic yields 1,466 harmonized SNPs in the S19 union and 410,516 in the broad S12K OCR union.

## Conditions before production Phase 2

1. Resolve the EUR/EAS/AFR GWAS genome build from an auditable source or validated reference check. Until then, all GWAS–retina overlaps remain coordinate diagnostics only.
2. Complete ancestry-matched LDSC reference extraction and run EUR/EAS SNP heritability. A generic-reference diagnostic currently gives EUR h2 = 0.0904 (Z = 19.65) and EAS h2 = 0.1069 (Z = 13.20), but these values are explicitly not final because the reference is not ancestry matched. The current `results/phase1/LDSC_H2_SUMMARY.tsv` records both the diagnostic values and the pending ancestry-matched status; no h2 Z threshold is declared passed until compatible references are used.
3. Complete the S-LDXR paired EUR/EAS reference workflow. Ordinary LDSC reference files cannot be substituted for the paired S-LDXR LD-score requirement. The S-LDXR code is available, but the compatible dependency environment and paired LD scores/weights still require completion or auditable generation.
4. Treat cell-class East Asian DAR analyses as underpowered/sparse where the S19 table contains few East Asian intervals. Use global EUR–EAS analyses first and keep cell-class results exploratory until annotation-specific SNP counts and power are documented.
5. Keep RPE out of the primary HRCA S12/S19 analysis until an auditable RPE OCR resource is added.

## What is cleared now

GWAS provenance/QC, EUR–EAS allele harmonization, effect-direction audit, HRCA resource inventory, hg38 S12/S19 extraction, stable-versus-ancestry-sensitive annotation definition, and conditional coordinate-level annotation QC are complete. MR, PRS, pathway, drug, TWAS/SMR and manuscript drafting remain outside this freeze.

## Recommended next action

Resolve the GWAS build first, then rerun coordinate annotation QC and complete ancestry-matched LDSC/S-LDXR reference preparation. Only after those checks pass should the project freeze the Phase 2 annotation files and run production S-LDXR.
