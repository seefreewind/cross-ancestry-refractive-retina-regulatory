# Human Genetics v1.0 to v1.1 changelog

## STATISTICAL_METHOD

- Added reviewer-style S-LDXR MAF > 0.05 sensitivity for genome-wide and all-retinal-OCR analyses.
- Added Cochran-Q equivalence cross-check for the SNP-level heterogeneity statistic.
- Reframed beta-difference heterogeneity as source-effect-scale heterogeneity because raw phenotype-scale identity is not fully source-proven across mixed GWAS components.
- Qualified sample-overlap covariance as zero with residual-overlap uncertainty.

## CLAIM_BOUNDARY

- Retained the frozen primary DAR result unchanged.
- Kept large-enrichment exclusion limited to OR >= 1.5 under the top 5% endpoint.
- Preserved the statement that modest enrichment remains possible.
- Removed equivalence-style wording for broad retinal OCRs.

## INTRODUCTION

- Compressed repeated gap language.
- Replaced defensive negative-study framing with the neutral unresolved-question framing.
- Added the nested architecture logic: genome-wide, broad retinal OCR, ancestry-DAR subset.

## METHODS

- Expanded GWAS source description using Cheng et al. cohort and phenotype information.
- Corrected S-LDXR MAF-threshold wording and added the 0.05 sensitivity.
- Added Popcorn/S-LDXR distinction indirectly through Methods and Discussion.
- Removed internal project-management terms where possible.

## RESULTS

- Reduced build-rescue detail.
- Added MAF > 0.05 genome-wide and all-retinal-OCR sensitivity results.
- Kept the primary DAR heterogeneity results unchanged.

## DISCUSSION

- Added Popcorn/S-LDXR estimand clarification.
- Strengthened broad retinal OCR as the intermediate layer in the nested design.
- Consolidated limitations into a controlled 10-point boundary paragraph.

## REFERENCES

- Added `manuscript/REFERENCES_HUMAN_GENETICS_v2.tsv` with 26 reference candidates.
- Added Popcorn, polygenic portability, ancestry terminology, functional annotation and regulatory-variation references.
- Removed arXiv-only ancestry wording from the core v1.1 reference list.

## EDITORIAL_STYLE

- Removed “preregistered.”
- Replaced Phase/freeze/stop-rule language in the manuscript with academic wording such as prespecified, fixed configuration, post-primary sensitivity and analysis SNP set.
- Tightened the abstract to 203 words.

## Frozen primary result

No frozen primary result was changed. The primary DAR top 5% result remains OR = 1.119, 95% CI = 0.867–1.423, Fisher P = 0.367, matched permutation P = 0.334.

