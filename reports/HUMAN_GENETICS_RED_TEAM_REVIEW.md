# Human Genetics red-team review

## Reviewer 1 — statistical genetics

Likely recommendation: major revision, technically promising.

### Major comments

1. The S-LDXR MAF threshold differs from the original method default. The 0.05 sensitivity should be reported clearly.
2. The beta-difference heterogeneity statistic depends on effect-scale comparability across mixed phenotype meta-analyses. The manuscript should describe it as a source-effect-scale screen and include the Cochran-Q equivalence check.
3. Sample overlap covariance is set to zero. The manuscript should state that no material overlap was identified from public documentation and residual overlap cannot be excluded.

### Minor comments

1. Define GCORSQ and distinguish it from GCOR at first use.
2. Avoid implying equivalence from overlapping confidence intervals.
3. Keep LD-pruned sensitivity out of the main claim because DAR SNP counts are too small after pruning.

## Reviewer 2 — retinal genomics

Likely recommendation: major revision, acceptable if regulatory claims remain bounded.

### Major comments

1. DARs should not be interpreted as causal regulatory mechanisms without functional validation.
2. The matched non-DAR retinal OCR comparator should not be called ancestry-stable.
3. The broad retinal OCR analysis should be presented as an intermediate regulatory-context layer, not as a cell-type discovery result.

### Minor comments

1. Clarify HRCA-derived annotation provenance.
2. State that retina is not the only tissue or developmental stage relevant to refractive error.
3. Avoid post hoc locus, CRE, motif or pathway narratives.

## Reviewer 3 — population genetics

Likely recommendation: major revision, favorable to bounded ancestry-language framing.

### Major comments

1. Ancestry labels from GWAS and HRCA are not interchangeable biological categories. The manuscript should keep labels source-specific.
2. Popcorn and S-LDXR should not be compared numerically because they estimate different quantities.
3. The conclusion should not generalize from EUR-EAS to all populations.

### Minor comments

1. Cite peer-reviewed ancestry terminology sources.
2. Distinguish allele-frequency/LD effects from ancestry-specific biology.
3. Avoid “no ancestry effect” language.

## Manuscript changes made in response

v1.1 adds standard MAF-threshold sensitivity, source-effect-scale wording, sample-overlap qualification, Popcorn/S-LDXR estimand distinction, bounded retinal OCR language and a cleaner nested-architecture framing.

