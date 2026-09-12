# S-LDXR invalid first-generation baseline provenance

**Project:** Cross-ancestry genetic effects of refractive error × retinal regulatory architecture  
**Discovery date:** 2026-09-10  
**Status:** `INVALID_FOR_FORMAL_ANALYSIS_ROWSET_MISMATCH`

## Decision

The first-generation paired S-LDXR baseline scores are permanently excluded from formal regression. They are retained for provenance and must not be deleted, overwritten, or cited as valid analytical inputs.

## Mismatch

| Input | Autosomal rows |
|---|---:|
| Original baseline-LD annotation | 9,997,231 |
| Paired EUR–EAS panel | 6,309,729 |
| Strictly aligned replacement baseline annotation | 6,309,729 |

The first-generation score workflow supplied the unfiltered baseline-LD annotation matrix to a smaller derived EUR–EAS paired PLINK panel. The S-LDXR score implementation indexes annotation rows by the paired-panel genotype row indices and assumes exact row identity. Because the original annotation matrix contained a different SNP universe and order, successful file generation did not establish row alignment. The resulting first-generation baseline scores are therefore not valid for formal analysis.

The replacement annotation was joined by rsID to the paired panel, reordered to the exact paired-panel order, and checked chromosome by chromosome. Across chromosomes 1–22, all 6,309,729 paired-panel SNPs were retained, with zero missing SNPs, zero chromosome mismatches and zero base-pair mismatches. The machine-readable audit is `results/phase1c/SLDXR_BASELINE_ANNOTATION_ALIGNMENT.tsv`.

## Affected retained outputs

The following retained files or file families are invalid for formal analysis:

- `data/interim/sldxr_scores/baseline_chr.<1-22>_pop1.gz`
- `data/interim/sldxr_scores/baseline_chr.<1-22>_pop2.gz`
- `data/interim/sldxr_scores/baseline_chr.<1-22>_te.gz`
- `data/interim/sldxr_scores/baseline_chr.<1-22>.log`
- `results/phase1c/SMOKE_GCOR_CHR22*`
- `results/phase1c/sldxr_formal/GCOR_baseline_blocks200_maf0p01_analytic*`

`results/phase1c/SMOKE_GCOR_CHR22` used the invalid first-generation baseline scores and is invalid. The subsequent genome-wide attempt was stopped after the row-count mismatch became visible in the load log; it did not produce a completed formal estimate. Its logs are retained as evidence of detection and termination.

## Unaffected inputs

The paired EUR/EAS PLINK panels, paired MAF files, base regression weights, and retinal annotations were generated directly in paired-panel order. They remain subject to the Phase 1C.2 hard row-identity, numerical and cross-score-universe gates before any formal regression.

## Replacement paths

- Aligned baseline annotation: `data/interim/sldxr_annotations/baseline_paired/<1-22>.annot.gz`
- Replacement baseline scores: `data/interim/sldxr_scores_aligned/baseline_chr.<1-22>_{pop1,pop2,te}.gz`
- Alignment audit: `results/phase1c/SLDXR_BASELINE_ANNOTATION_ALIGNMENT.tsv`
- Replacement score QC: `results/phase1c/SLDXR_SCORE_QC_ALIGNED_BASELINE.tsv`

No formal EUR–EAS genome-wide S-LDXR result is valid until all replacement scores complete and the Phase 1C.2 hard gates pass for all 22 autosomes.
