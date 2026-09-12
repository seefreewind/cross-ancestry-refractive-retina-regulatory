# EUR/EAS sample-overlap audit

Final verdict: POSSIBLE_MINOR_OVERLAP

## Question

Can the EUR and EAS GWAS be treated as independent for the SNP-level heterogeneity statistic?

## Evidence inspected

1. Cheng et al. 2026 article page and cohort overview.
2. Local metadata: `metadata/GWAS_METADATA.tsv`.
3. Current manuscript v1.0 Methods.

## Cohort evidence

The source paper reports ancestry-stratified GWAS meta-analyses with EUR n = 1,495,159, EAS n = 121,172 and AFR n = 144,737. EUR inputs included UK Biobank, GERA, FinnGen, 23andMe, MVP and All of Us. EAS inputs included ToMMo, MVP, high-myopia GWAS, WeGene and 23Mofang. The public EUR file used in this project is the no-23andMe release.

No material cross-ancestry individual overlap was identified from the available cohort documentation. However, some large biobank resources appear across ancestry strata, and the public source files do not provide individual-level identifiers. A strict zero-overlap proof is therefore not available from the public files.

## Statistical implication

The current heterogeneity statistic sets cross-ancestry covariance to zero. This is a reasonable reviewer-facing approximation when no material cross-ancestry overlap is identified, but it should be stated as an assumption rather than as proven independence.

## Required manuscript wording

Use:

> Covariance between EUR and EAS estimates was set to zero because no material cross-ancestry sample overlap was identified from the available cohort documentation; residual overlap cannot be excluded.

Avoid:

> The EUR and EAS GWAS were independent.

