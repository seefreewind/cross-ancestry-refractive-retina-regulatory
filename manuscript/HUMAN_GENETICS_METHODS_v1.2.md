# Materials and methods

### GWAS datasets and study design

The study used publicly available ancestry-specific refractive-error GWAS summary statistics from Cheng et al. The source study reported ancestry-stratified and cross-ancestry meta-analyses for refractive error in people of European (EUR; n = 1,495,159), East Asian (EAS; n = 121,172) and African (AFR; n = 144,737) ancestries. The EUR source study included a 23andMe component of 106,086 cases and 85,757 controls. The publicly released EUR summary statistics used here excluded 23andMe participants; the released file provided variant-level effective sample-size values, which were retained as the analysis sample-size information rather than replacing them with the full source EUR total. The EAS public file also included a variant-level `N` field, and the source EAS total was treated as source-study metadata rather than a constant analysis N. The present analysis focused on the EUR-EAS comparison because this was the specified inference unit for paired LD-based S-LDXR and SNP-level heterogeneity testing.

The EUR source meta-analysis included directly measured mean spherical equivalent, imputed mean spherical equivalent from age of spectacle wear, binary myopia status and EHR-derived resources. The EAS source meta-analysis included examination-based myopia, self-reported categorical myopia, high-myopia GWAS and biobank resources. The analysis tested cross-ancestry genetic-effect sharing at three nested levels: genome-wide common-variant architecture, broad retinal OCRs and ancestry-associated retinal DARs.

### Variant QC and EUR-EAS harmonization

EUR and EAS summary statistics were filtered to biallelic SNPs. Palindromic SNPs, unresolved allele mismatches and duplicated variants were excluded before effect alignment. EUR and EAS variants were matched by chromosome and position, alleles were aligned to the EUR effect allele, and EAS effect estimates were oriented to the same allele. This produced 3,262,168 harmonized EUR-EAS shared SNPs.

S-LDXR and DAR heterogeneity analyses used the stricter analysis SNP set retained after intersection with paired reference resources, ancestry-specific frequency files and exact score-universe alignment. This set contained 3,112,573 SNPs. The distinction between the broader harmonized set and the analysis SNP set was preserved in result tables and figure-ready files.

### Genome-build adjudication and reference anchoring

The released GWAS summary-statistics files did not explicitly report the genome assembly. Coordinates were independently adjudicated against dbSNP Build 151 using assembly-informative variants and an independent holdout procedure. Downstream variant coordinates were anchored to a GRCh37.p13 reference framework. Concordance with GRCh37 was complete across autosomes and in holdout validation.

Human retinal annotations derived from hg38 resources were lifted into the same GRCh37.p13 framework. Annotation and LD-score files were required to match the paired reference SNP universe before analysis. Preliminary baseline files that failed row-set compatibility checks were excluded from inference and retained only as provenance records.

### Human retinal regulatory annotations

Retinal regulatory annotations were derived from the Human Retina Cell Atlas. Broad retinal OCRs were defined from the union retinal open-chromatin annotation. Ancestry-associated DARs were defined from the atlas ancestry-DAR table using the source definition. The final analysis counts were 380,615 SNPs in all retinal OCRs, 1,232 SNPs in ancestry-associated DARs and 379,279 SNPs in matched non-DAR retinal OCRs.

The ancestry-associated DAR annotation was treated as a regulatory context for statistical testing, not as a causal mechanism label. The matched non-DAR retinal OCR set was used as an operational comparator and was not interpreted as proof of regulatory invariance across ancestries. Cell-type-specific S-LDXR, locus prioritization, CRE-to-gene mapping and motif analyses were not performed.

### Ancestry-specific LD score regression

Ancestry-matched LD score regression was used to estimate SNP heritability for EUR and EAS refractive-error GWAS summary statistics. Analyses used matched reference resources for the corresponding ancestry, with summary-statistic filtering and harmonization recorded in input records. The reported EUR and EAS heritability estimates were used as context for cross-population S-LDXR.

### Cross-population S-LDXR analysis

Cross-population S-LDXR was used to estimate squared trans-ancestry genetic correlation across the genome-wide analysis SNP set and within retinal annotations. The analysis used paired EUR and EAS 1000 Genomes reference panels, aligned annotations, ancestry-specific allele frequencies, matched weights, 200 jackknife blocks, fixed cross-population intercept of zero, fitted ancestry-specific intercepts and shrinkage alpha = 0.5.

The primary manuscript-facing S-LDXR estimates used MAF > 0.05 in both ancestries, matching the S-LDXR method paper and software default for regression and heritability SNPs. A broader MAF > 0.01 analysis with the same summary statistics, reference scores, annotations, weights, intercept settings, shrinkage and jackknife scheme was retained as a supporting analysis. The official S-LDXR GCORSQ metric was reported with standard error and 95% confidence interval. Boundary-adjacent estimates above one were interpreted as unbounded estimator behavior around high sharing, not as evidence that the underlying correlation exceeds its natural parameter boundary.

### Cross-ancestry heterogeneity statistic

SNP-level EUR-EAS association-effect heterogeneity was calculated from aligned source beta and standard-error fields. For SNP i, the signed statistic was z_het = (beta_EUR - beta_EAS_aligned) / sqrt(SE_EUR^2 + SE_EAS^2), and the primary heterogeneity score was chi2_het = z_het^2. The statistic is algebraically equivalent to the two-study Cochran Q statistic when evaluated on the released source-effect scale under zero covariance. Because the source meta-analyses combined heterogeneous phenotype definitions, it was interpreted as an association-effect heterogeneity statistic rather than as a comparison of uniform raw quantitative-trait effects.

No material cross-ancestry participant overlap was identified from the available cohort documentation; covariance was therefore set to zero, although residual overlap cannot be fully excluded.

### Ancestry-DAR enrichment analysis

The primary binary endpoint was membership in the top 5% of the genome-wide chi2_het distribution. The primary comparison tested ancestry-associated DAR SNPs against matched non-DAR retinal OCR SNPs. Top 1% and top 10% thresholds were analyzed as sensitivity endpoints only. Continuous chi2_het was compared as a supporting analysis.

Odds ratios were estimated for the binary endpoint and Fisher exact tests were used for the primary contingency comparison. Confidence intervals for the primary odds ratio were reported using a conditional exact odds-ratio interval. Continuous heterogeneity was compared using the Mann-Whitney test.

### Matched permutation and robustness analyses

The matched permutation analysis used 1,000 permutations with random seed 20260912. Case labels were permuted within strata defined by chromosome, average EUR/EAS reference MAF decile, absolute EUR-EAS MAF-difference quintile, baseline LD-score decile and retinal OCR status. The empirical P value was calculated as (1 + number of null statistics with absolute value greater than or equal to the observed absolute statistic) / (1 + number of permutations). The observed statistic was the mean chi2_het difference between ancestry-associated DAR SNPs and matched non-DAR retinal OCR SNPs.

Sensitivity and precision analyses were specified after completion of the primary DAR enrichment analysis and were not permitted to redefine the primary endpoint. LD-reduced sensitivity used label-blind PLINK2 pruning with EUR and EAS paired reference panels, a 500 kb window and conservative retention only of SNPs retained in both ancestries. Block-level robustness used the 200 S-LDXR jackknife block boundaries and compared blocks with at least one DAR SNP against blocks without DAR SNPs, adjusted for log SNP count, mean reference MAF, mean baseline LD score and retinal OCR density. Effect-size precision was evaluated for the top 5% endpoint. Minimum detectable odds ratios were calculated for 80% and 90% power at alpha = 0.05, using the DAR sample size and matched comparator event rate. OR = 1.5 was used as a prespecified robustness boundary for large enrichment.

### Statistical analysis

All analyses used fixed configuration files, input records and scripted outputs. Sensitivity analyses were reported regardless of direction. No new DAR definition, SNP universe, heterogeneity metric, ancestry comparison, pathway analysis, fine-mapping, TWAS, SMR, MR, PRS, motif analysis or locus fishing was introduced after the primary result.
