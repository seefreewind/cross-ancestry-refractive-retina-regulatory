# Human Genetics targeted manuscript revision: Results

### A reference-anchored framework for cross-ancestry analysis of refractive error

The EUR and EAS refractive-error GWAS summary statistics could be harmonized into a shared effect-aligned dataset. After biallelic SNP filtering, removal of palindromic SNPs, duplicate handling and allele alignment, 3,262,168 shared SNPs were retained for harmonized EUR-EAS effect comparison. Formal S-LDXR and Phase 2 analyses used a stricter shared SNP universe of 3,112,573 SNPs with exact paired-reference, score and annotation alignment.

Genome-build uncertainty was handled by empirical adjudication. The released GWAS files lacked an explicit source-level assembly declaration, so all downstream analyses were conducted as reference-anchored analyses. dbSNP Build 151 adjudication and holdout checks supported GRCh37.p13 anchoring across autosomes. Retinal annotations were lifted into this framework and subjected to exact row-identity checks before formal use.

### Refractive error shows strong genome-wide EUR-EAS genetic sharing

Ancestry-matched LDSC supported substantial common-variant signal in both ancestry-specific GWAS analyses. The EUR estimate was h2 = 0.1219 (SE = 0.0072, Z = 16.93), and the EAS estimate was h2 = 0.1494 (SE = 0.0119, Z = 12.55).

Genome-wide cross-population S-LDXR estimated a high degree of shared EUR-EAS architecture. The formal genome-wide GCORSQ estimate was 1.009945 (SE = 0.108276) across 3,112,573 SNPs and 200 jackknife blocks. The boundary-adjacent estimate was treated as compatible with very high sharing under an unbounded estimator, not as a literal correlation above one.

### Broad retinal regulatory regions retain a largely shared cross-ancestry architecture

Broad retinal OCRs showed a cross-ancestry S-LDXR estimate broadly compatible with the genome-wide pattern. The all-retinal-OCR GCORSQ estimate was 0.935405 (SE = 0.101099), based on 380,615 formal OCR SNPs. Its 95% confidence interval overlapped the genome-wide estimate, supporting a shared regulatory-context architecture without implying that retinal regulatory effects are identical across ancestries.

The global ancestry-DAR S-LDXR estimate was retained only as a descriptive underpowered result. The DAR estimate was 0.571191 (SE = 0.577063), with 1,232 formal SNPs and a wide confidence interval. This result was not used as a primary biological test.

### Ancestry-associated retinal DARs do not show detectable excess effect heterogeneity

The primary DAR heterogeneity test did not support enrichment of high EUR-EAS effect heterogeneity within ancestry-associated retinal DARs. In the frozen top 5% `chi2_het` endpoint, 71 of 1,232 DAR SNPs (5.76%) and 19,653 of 379,279 matched non-DAR retinal OCR SNPs (5.18%) were classified as high heterogeneity. The primary odds ratio was 1.119 (95% CI 0.867-1.423), with Fisher P = 0.367.

Continuous heterogeneity gave the same interpretation. The mean `chi2_het` difference between DAR and matched non-DAR retinal OCR SNPs was 0.0351, with Mann-Whitney P = 0.711. The matched permutation test also did not support enrichment: the observed mean `chi2_het` difference was 0.0647, with empirical P = 0.334 after 1,000 permutations within chromosome, MAF, MAF-difference, LD-score and OCR-status strata.

Sensitivity thresholds did not alter the conclusion. At the top 1% threshold, the odds ratio was 1.014 (P = 0.888). At the top 10% threshold, the odds ratio was 1.050 (P = 0.605). These results support the preregistered conclusion that ancestry-associated retinal DARs did not show detectable excess EUR-EAS effect heterogeneity under the frozen matched analysis.

### Robustness analyses constrain the role of SNP dependence

Post-primary robustness analyses reproduced the primary result exactly from frozen inputs. LD-reduced sensitivity analyses were label blind and based only on SNP position and LD structure in paired EUR and EAS reference panels. Stringent pruning sharply reduced the DAR sample size: r2 < 0.1 retained only 9 DAR SNPs, and r2 < 0.01 retained only 1 DAR SNP. These pruned analyses were therefore severely underpowered and were not used to infer a trend.

Block-level robustness provided the more interpretable check against SNP-level dependence. Using the project-standard 200 S-LDXR jackknife block boundaries, the adjusted block-level comparison of mean `chi2_het` between blocks with at least one DAR SNP and blocks without DAR SNPs gave P = 0.3836 after adjustment for block SNP count, mean MAF, baseline LD score and retinal OCR density. This analysis did not indicate that SNP-level dependence changed the primary conclusion.

### Current data exclude large but not modest DAR enrichment

The negative primary result was interpreted through effect-size precision rather than P values alone. The primary top 5% odds ratio was 1.119, with a 95% CI of 0.867-1.423. With 1,232 DAR SNPs and a matched comparator event rate of 5.18%, the minimum detectable odds ratio was 1.397 for 80% power and 1.467 for 90% power at alpha = 0.05.

Using OR = 1.5 as a prespecified large-enrichment boundary, the observed 95% CI was inconsistent with large systematic enrichment under the frozen endpoint. The same analysis did not exclude modest enrichment. The most accurate conclusion is that the data do not support a large systematic excess of ancestry-divergent effects in ancestry-associated retinal DARs, while smaller effects remain unresolved.
