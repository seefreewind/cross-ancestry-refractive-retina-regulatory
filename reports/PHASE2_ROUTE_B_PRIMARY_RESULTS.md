# Phase 2 Route B Primary Results

**Status date:** 2026-09-12  
**Analysis build:** GRCh37.p13 reference-anchored  
**Freeze:** `config/PHASE2_ANALYSIS_FREEZE_v1.yaml`  
**Primary conclusion:** `PRIMARY_ENRICHMENT_NOT_SUPPORTED`

## Summary

Phase 2 Route B was executed within the formal Phase 1C.2 shared SNP universe. The feature matrix retained all 3,112,573 formal SNPs, including 1,232 ancestry-DAR SNPs, 380,615 all-retinal OCR SNPs, and 379,279 matched non-DAR retinal OCR SNPs.

The primary enrichment test does not support excess EUR-EAS effect heterogeneity in ancestry-DAR SNPs relative to matched non-DAR retinal OCR SNPs. The top 5% heterogeneity fraction was 5.76% in DAR SNPs and 5.18% in matched non-DAR retinal OCR SNPs, with OR = 1.119 and Fisher P = 0.367. The matched permutation test gave an observed mean chi-square difference of 0.0647 and empirical P = 0.334.

This result blocks progression to locus/CRE/motif interpretation under the Phase 2 freeze. The project can still report a robust genome-wide cross-ancestry architecture result from Phase 1C.2, but the DAR-led local heterogeneity enrichment claim is not supported by the current data.

## Feature QC

| Metric | Value | Status |
|---|---:|---|
| formal_snp_n | 3,112,573 | PASS |
| feature_snp_n | 3,112,573 | PASS |
| dar_snp_n | 1,232 | PASS |
| ocr_union_snp_n | 380,615 | PASS |
| matched_non_dar_snp_n | 379,279 | PASS |
| chi2_het_finite_n | 3,112,573 | PASS |
| top_5pct_threshold | 4.5169 | PASS |

## Primary Matched Comparator

| Endpoint | DAR SNPs | Comparator SNPs | DAR fraction | Comparator fraction | OR / Difference | P value |
|---|---:|---:|---:|---:|---:|---:|
| top_5pct_chi2_het | 1,232 | 379,279 | 0.0576 | 0.0518 | OR 1.119 | 0.367 |
| top_1pct_chi2_het | 1,232 | 379,279 | 0.0106 | 0.0104 | OR 1.014 | 0.888 |
| top_10pct_chi2_het | 1,232 | 379,279 | 0.1071 | 0.1026 | OR 1.050 | 0.605 |
| chi2_het_continuous | 1,232 | 379,279 | NA | NA | mean diff 0.0351 | 0.711 |
| matched permutation | 1,069 | 59,215 | NA | NA | mean diff 0.0647 | empirical 0.334 |

The matched permutation used 60,284 SNPs after retaining strata that contained both DAR and non-DAR labels. Strata were defined by chromosome, average EUR/EAS reference MAF decile, absolute EUR/EAS MAF-difference quintile, baseline LD-score decile, and retinal OCR status.

## Contextual Comparisons

DAR showed small positive point estimates versus the genome-wide formal universe and all retinal OCR background, but none reached statistical support:

| Comparator | Endpoint | OR / Difference | P value |
|---|---|---:|---:|
| genome-wide formal universe | top_5pct_chi2_het | OR 1.162 | 0.214 |
| all retinal OCR | top_5pct_chi2_het | OR 1.184 | 0.189 |
| genome-wide formal universe | chi2_het_continuous | mean diff 0.0531 | 0.484 |
| all retinal OCR | chi2_het_continuous | mean diff 0.0436 | 0.858 |

## Interpretation Boundary

This analysis supports three statements:

1. The Phase 2 formal heterogeneity feature matrix is technically valid and complete for the audited SNP universe.
2. Ancestry-DAR SNPs show only a small positive enrichment point estimate for high EUR-EAS heterogeneity.
3. The point estimate is not statistically supported under the matched comparator or permutation design.

This analysis does not support DAR-led local regulatory heterogeneity as a main biological claim. Under the freeze, cell-class, locus, CRE, and motif interpretation should not proceed as primary discovery analysis without a revised user-approved plan.

## Output Files

- `data/processed/phase2/EUR_EAS_HETEROGENEITY_FEATURES.parquet`
- `results/phase2/PHASE2_HETEROGENEITY_FEATURE_QC.tsv`
- `results/phase2/PHASE2_DAR_HETEROGENEITY_ENRICHMENT.tsv`
- `results/phase2/PHASE2_DAR_MATCHED_PERMUTATION_NULL.tsv`
- `reports/PHASE2_ROUTE_B_METHOD_DESIGN.md`
