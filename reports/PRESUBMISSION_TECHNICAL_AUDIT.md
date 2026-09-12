# Presubmission technical audit

Status: ACTIVE

## Technical issue 1 — S-LDXR MAF threshold wording

Severity: METHOD WORDING ISSUE; sensitivity required before final GO decision.

The v1.0 manuscript states that the formal S-LDXR analysis used “a minimum MAF threshold of 0.01 in both ancestries.” The project freeze confirms that the executed analysis used `--min-maf 0.01` and a paired score universe labeled `MAF_EAS>0.01 and MAF_EUR>0.01`.

Official S-LDXR documentation and source code show that the software exposes `--min-maf` as a command-line option and sets the default to 0.05. The S-LDXR paper describes regression and heritability SNPs as HapMap3 SNPs with MAF greater than 5% in both EAS and EUR populations.

Action taken: reviewer-style method sensitivity was initiated for genome-wide and all-retinal-OCR S-LDXR using the same reference, annotations, intercept settings, shrinkage and 200 jackknife blocks with `--min-maf 0.05`.

Manuscript implication: v1.1 must not present 0.01 as the standard S-LDXR method threshold. If the 0.05 sensitivity is consistent, v1.1 can retain the shared-architecture conclusion while explicitly stating that the main project run used an expanded MAF threshold and that a standard-threshold sensitivity supported the same broad conclusion.

## Technical issue 2 — EUR/EAS beta scale for SNP-level heterogeneity

Severity: REVIEWER RISK; current status conditional.

The released EUR and EAS files contain `b`, `se`, `z`, `p`, `N`, allele and frequency fields. The local metadata already records that the released `b` values are beta-like source effects and that raw beta comparison should not be assumed without source support. The v1.0 heterogeneity statistic is numerically equivalent to two-study Cochran Q when those source beta and SE values are accepted as comparable inputs, but source documentation has not yet fully established that all EUR and EAS meta-analysis beta values share one directly comparable phenotype scale across mixed continuous and case-control cohorts.

Action taken: a Cochran Q cross-check was generated at `results/presubmission/HETEROGENEITY_STATISTIC_CROSSCHECK.tsv`.

Manuscript implication: v1.1 should describe the SNP-level heterogeneity statistic as a source-effect-scale heterogeneity screen and matched enrichment test unless source documentation fully supports direct raw phenotype-scale comparability.

## Technical issue 3 — sample-overlap covariance

Severity: WORDING ISSUE; likely conditional.

The v1.0 manuscript states that EUR and EAS GWAS were treated as independent for the heterogeneity statistic. Cheng et al. report ancestry-stratified cohorts, and obvious material cross-ancestry overlap is not identified from the available documentation. Because some contributing resources, such as MVP, appear in more than one ancestry stratum, the safer presubmission wording is that covariance was set to zero because no material cross-ancestry sample overlap was identified from available documentation, while residual overlap cannot be excluded.

Manuscript implication: v1.1 should avoid an absolute independence claim.

