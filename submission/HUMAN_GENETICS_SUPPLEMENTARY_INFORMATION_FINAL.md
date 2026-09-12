# Supplementary Information

## Supplementary Methods

### Reference anchoring and build adjudication

Released GWAS summary-statistics files did not explicitly report genome assembly. Coordinates were adjudicated against dbSNP Build 151 using assembly-informative variants and holdout checks. Formal downstream inference used the GRCh37.p13 coordinate framework after the anchoring checks summarized in Supplementary Table S5.

### S-LDXR MAF sensitivity

Primary S-LDXR analyses used MAF > 0.05 in both ancestries, matching the method-standard regression setting. A broader MAF > 0.01 analysis was retained as a supporting sensitivity analysis because it used the same aligned inputs, intercept settings, shrinkage and jackknife scheme. Complete estimates are reported in Supplementary Table S2.

### Popcorn and S-LDXR estimands

The source GWAS reported substantial cross-ancestry sharing using Popcorn. The present study used S-LDXR GCORSQ, a squared cross-population genetic-correlation quantity estimated with ancestry-specific LD and functional annotations. The estimates support a similar broad interpretation of sharing but should not be compared numerically because the estimands and scaling differ.

### Effect-scale and sample-overlap considerations

The heterogeneity statistic compares released source beta values after allele alignment and uses standard errors from the public summary statistics. It is interpreted as association-effect heterogeneity on the released source-effect scale. Public documentation did not identify material EUR–EAS participant overlap; covariance was therefore set to zero, although residual overlap cannot be fully excluded.

### Pipeline provenance

Analyses used frozen configuration files and scripted outputs. Unsupported sensitivity analyses were retained in the supplement, and no post-primary discovery analysis was added during final manuscript freezing.

## Supplementary Fig. S1

Supplementary Fig. S1. Descriptive ancestry-DAR S-LDXR estimate. Descriptive S-LDXR estimate for the ancestry-DAR annotation. Sparse SNP support yielded wide uncertainty, so this panel is separated from the main cross-ancestry architecture figure and should not be interpreted as evidence for true ancestry divergence.

## Supplementary Tables

Supplementary Table S1. GWAS files and QC characteristics.

Supplementary Table S2. Complete S-LDXR results.

Supplementary Table S3. DAR robustness analyses.

Supplementary Table S4. Effect-size precision.

Supplementary Table S5. Reference anchoring and build adjudication.

Supplementary Table S6. Retinal annotation processing and liftover QC.
