# EUR/EAS effect-scale audit

Final verdict: CONDITIONAL

## Question

Are the released EUR and EAS beta/SE values directly comparable across ancestries for a beta-difference heterogeneity statistic?

## Evidence inspected

1. Source GWAS article: Cheng et al. 2026, *Nature Genetics*, DOI 10.1038/s41588-026-02576-0.
2. Released EUR file: `data/raw/gwas/EUR_meta_no23andMe.fastGWAz`.
3. Released EAS file: `data/raw/gwas/EAS_meta.fastGWAz`.
4. Local metadata: `metadata/GWAS_METADATA.tsv`.
5. Harmonized file: `data/processed/EUR_EAS_HARMONIZED.parquet`.
6. Phase 2 feature matrix: `data/processed/phase2/EUR_EAS_HETEROGENEITY_FEATURES.parquet`.

## Source columns

| Dataset | Header | Source effect fields | Local interpretation |
|---|---|---|---|
| EUR_meta_no23andMe | `SNP A1 A2 freq b se p N CHR POS z` | `b`, `se`, `z`, `p`, `N` | beta-like source effect and SE |
| EAS_meta | `SNP A1 A2 freq b se p N CHR POS z` | `b`, `se`, `z`, `p`, `N` | beta-like source effect and SE |

## Phenotype and meta-analysis heterogeneity

The source GWAS combined multiple phenotype sources. EUR included directly measured mean spherical equivalent, imputed MSE from age of spectacle wear, binary myopia cohorts and EHR-derived resources. EAS included examination-based myopia, self-reported categorical myopia and high-myopia GWAS sources. The source paper reports ancestry-stratified and cross-ancestry meta-analyses and describes sample-size-weighted meta-analysis for association discovery.

This supports using the released files as ancestry-specific association summary statistics. It does not fully establish that every released `b` value represents the same raw phenotype-scale beta across EUR and EAS after mixed continuous and case-control meta-analysis.

## Technical cross-check

Using the released `b` and `se` values as source-effect inputs, the current statistic

```text
chi2_het = (b_EUR - b_EAS_aligned)^2 / (se_EUR^2 + se_EAS^2)
```

is numerically equivalent to the standard two-study Cochran Q formula with inverse-variance weights. The cross-check is saved at:

`results/presubmission/HETEROGENEITY_STATISTIC_CROSSCHECK.tsv`

Summary:

| Metric | Value |
|---|---:|
| SNP N | 3,112,573 |
| Pearson correlation with Cochran Q | 1.000 |
| Spearman correlation with Cochran Q | 1.000 |
| Top 5% overlap | 1.000 |
| Maximum absolute numerical difference | 2.84e-14 |

## Conclusion

The heterogeneity formula is mathematically defensible if the released ancestry-specific `b/se` values are treated as comparable source-effect estimates. The source documentation available at presubmission does not fully prove raw phenotype-scale identity across mixed EUR and EAS input cohorts.

Final answer to the critical question: CONDITIONAL.

## Manuscript wording required

Use:

> We calculated a two-study source-effect-scale heterogeneity statistic from aligned EUR and EAS beta and standard-error fields. This statistic is equivalent to Cochran Q under the released source-effect scale.

Avoid:

> EUR and EAS raw phenotype-scale beta values were directly comparable without qualification.

