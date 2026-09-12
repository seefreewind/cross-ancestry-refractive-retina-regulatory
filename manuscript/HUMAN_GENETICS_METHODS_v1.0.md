# Human Genetics targeted manuscript revision: Methods

### GWAS datasets and study design

The study used publicly available ancestry-specific refractive-error GWAS summary statistics for EUR and EAS analyses. The inference unit was the EUR-EAS comparison. AFR data were catalogued during project setup but were not introduced into the Phase 2B manuscript analysis because the formal heterogeneity endpoint and S-LDXR framework were frozen for EUR-EAS.

The analysis was designed to test cross-ancestry genetic-effect sharing at three levels: genome-wide common-variant architecture, broad retinal OCRs, and ancestry-associated retinal DARs. The primary regulatory question compared ancestry-associated DAR SNPs with matched non-DAR retinal OCR SNPs. The matched non-DAR retinal OCR set was used as an operational comparator and was not interpreted as proof of regulatory stability.

### Variant QC and EUR-EAS harmonization

EUR and EAS summary statistics were filtered to biallelic SNPs. Palindromic SNPs, unresolved allele mismatches and duplicated variants were excluded before effect alignment. EUR and EAS variants were matched by chromosome and position, alleles were aligned to the EUR effect allele, and EAS effect estimates were oriented to the same allele. This produced 3,262,168 harmonized EUR-EAS shared SNPs.

Formal downstream analyses used the stricter S-LDXR-aligned shared SNP universe. This universe retained 3,112,573 SNPs after intersection with the paired reference, MAF filter and exact score-universe alignment. The distinction between the harmonized SNP set and the formal analysis universe was preserved throughout all result tables.

### Genome-build adjudication and reference anchoring

The released GWAS summary-statistics files did not explicitly report the genome assembly. Coordinates were therefore independently adjudicated against dbSNP Build 151 using assembly-informative variants and an independent holdout procedure, after which downstream variant coordinates were anchored to a frozen GRCh37.p13 reference framework. Concordance with GRCh37 was complete across autosomes and in holdout validation.

Human retinal annotations derived from hg38 resources were lifted and anchored to the same GRCh37.p13 framework. All formal annotations and LD-score files were required to match the paired reference SNP universe exactly before analysis. First-generation baseline files that failed row-set compatibility checks were excluded from formal inference and retained only as provenance records.

### Human retinal regulatory annotations

Retinal regulatory annotations were derived from the Human Retina Cell Atlas. Broad retinal OCRs were defined from the union retinal open-chromatin annotation. Ancestry-associated DARs were defined from the atlas ancestry-DAR table using the frozen source definition. The final formal SNP counts were 380,615 SNPs in all retinal OCRs, 1,232 SNPs in ancestry-associated DARs and 379,279 SNPs in matched non-DAR retinal OCRs.

The ancestry-associated DAR annotation was treated as a regulatory context for statistical testing, not as a causal mechanism label. Cell-class summaries were retained only as descriptive post-primary outputs when at least 100 formal DAR SNPs were available for a class. Cell-type-specific S-LDXR, locus prioritization, CRE-to-gene mapping and motif analyses were not performed.

### Ancestry-specific LD score regression

Ancestry-matched LD score regression was used to estimate SNP heritability for EUR and EAS refractive-error GWAS summary statistics. Analyses used matched reference resources for the corresponding ancestry, with summary-statistic filtering and harmonization recorded in frozen manifests. The reported EUR and EAS heritability estimates were used as context for cross-population S-LDXR.

### Cross-population S-LDXR analysis

Cross-population S-LDXR was used to estimate squared trans-ancestry genetic correlation across the formal SNP universe and within retinal annotations. The formal analysis used paired EUR and EAS 1000 Genomes reference panels, aligned annotations, ancestry-specific allele frequencies, matched weights, 200 jackknife blocks and a minimum MAF threshold of 0.01 in both ancestries.

The official S-LDXR GCORSQ metric was reported with standard error and 95% confidence interval. Boundary-adjacent estimates above 1 were interpreted as unbounded estimator behavior around high sharing, not as evidence that the underlying correlation exceeds its natural parameter boundary.

### Cross-ancestry heterogeneity statistic

SNP-level EUR-EAS effect heterogeneity was defined before Phase 2B robustness analyses. For SNP \(i\), the signed statistic was

```text
z_het_i = (beta_EUR_i - beta_EAS_aligned_i) / sqrt(SE_EUR_i^2 + SE_EAS_i^2)
```

and the primary heterogeneity score was

```text
chi2_het_i = z_het_i^2.
```

The EUR and EAS GWAS were treated as independent for this statistic. Potential residual overlap between ancestry-specific analyses was handled as a limitation of interpretation rather than adjusted post hoc.

### Ancestry-DAR enrichment analysis

The primary binary endpoint was membership in the top 5% of the genome-wide formal `chi2_het` distribution. The primary comparison tested ancestry-associated DAR SNPs against matched non-DAR retinal OCR SNPs. Top 1% and top 10% thresholds were analyzed as sensitivity endpoints only. Continuous `chi2_het` was compared as a supporting analysis.

Odds ratios were estimated for the binary endpoint and Fisher exact tests were used for the primary contingency comparison. Continuous heterogeneity was compared using the Mann-Whitney test. Confidence intervals for the primary odds ratio were reported using a conditional exact odds-ratio interval.

### Matched permutation

The matched permutation analysis used 1,000 permutations with random seed 20260912. Case labels were permuted within strata defined by chromosome, average EUR/EAS reference MAF decile, absolute EUR-EAS MAF-difference quintile, baseline LD-score decile and retinal OCR status. The empirical P value was calculated as

```text
(1 + number of null statistics with abs(null) >= abs(observed)) / (1 + number of permutations).
```

The observed statistic was the mean `chi2_het` difference between ancestry-associated DAR SNPs and matched non-DAR retinal OCR SNPs. A matching balance audit recorded total strata, informative strata, retained DAR SNPs, excluded DAR SNPs and control availability.

### Post-primary robustness analyses

Phase 2B analyses were conducted after the negative primary DAR enrichment result and could not redefine the primary endpoint. Primary results were first reproduced from frozen inputs. LD-reduced sensitivity used label-blind PLINK2 pruning with EUR and EAS paired reference panels, a 500 kb window and conservative retention only of SNPs retained in both ancestries. Two thresholds were evaluated: r2 < 0.1 and r2 < 0.01. These analyses were labeled sensitivity because stringent pruning retained very few DAR SNPs.

Block-level robustness used the project-standard 200 S-LDXR jackknife block boundaries. For each block, SNP count, DAR SNP count, matched non-DAR retinal OCR SNP count, retinal OCR SNP count and summary `chi2_het` statistics were calculated. The frozen block-level statistic was mean `chi2_het`, comparing blocks with at least one DAR SNP against blocks without DAR SNPs, adjusted for log SNP count, mean reference MAF, mean baseline LD score and retinal OCR density.

Effect-size precision was evaluated for the frozen top 5% endpoint. Minimum detectable odds ratios were calculated prospectively for 80% and 90% power at alpha = 0.05, using the frozen DAR sample size and matched comparator event rate. OR = 1.5 was prespecified as a large-enrichment boundary.

### Statistical analysis

All analyses used frozen configuration files, frozen input manifests and scripted outputs. Sensitivity analyses were reported regardless of direction. No new DAR definition, SNP universe, heterogeneity metric, ancestry comparison, pathway analysis, fine-mapping, TWAS, SMR, MR, PRS, motif analysis or locus fishing was introduced after the primary result.
