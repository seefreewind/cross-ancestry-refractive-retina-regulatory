# Results

### Reference-anchored analysis framework

The EUR and EAS refractive-error GWAS summary statistics were harmonized into a shared effect-aligned dataset. After biallelic SNP filtering, removal of palindromic SNPs, duplicate handling and allele alignment, 3,262,168 shared SNPs were retained for harmonized EUR-EAS effect comparison. S-LDXR and DAR heterogeneity analyses used a stricter analysis SNP set of 3,112,573 SNPs with exact paired-reference, score and annotation alignment. Genome-build uncertainty was handled by empirical adjudication because the released GWAS files lacked an explicit source-level assembly declaration. dbSNP Build 151 adjudication and holdout checks supported GRCh37.p13 anchoring across autosomes. Retinal annotations were lifted into this framework and checked before analysis.

### Genome-wide cross-ancestry sharing

Ancestry-matched LDSC supported substantial common-variant signal in both ancestry-specific GWAS analyses. The EUR estimate was h2 = 0.1219 (SE = 0.0072, Z = 16.93), and the EAS estimate was h2 = 0.1494 (SE = 0.0119, Z = 12.55). Using the method-standard MAF > 0.05 threshold, genome-wide cross-population S-LDXR estimated high EUR-EAS sharing, with GCORSQ = 1.027596 (SE = 0.099604; 95% CI 0.832373-1.222820) across 3,112,573 SNPs and 200 jackknife blocks. A broader MAF > 0.01 supporting analysis gave a consistent estimate of GCORSQ = 1.009945 (SE = 0.108276). These boundary-adjacent estimates were treated as compatible with very high sharing under an unbounded estimator.

### Broad retinal OCR architecture

Broad retinal OCRs showed a cross-ancestry S-LDXR estimate compatible with the genome-wide pattern. Using MAF > 0.05, the all-retinal-OCR estimate was GCORSQ = 0.947606 (SE = 0.096926; 95% CI 0.757631-1.137582) for the OCR annotation. The broader MAF > 0.01 analysis also supported high sharing (GCORSQ = 0.935405, SE = 0.101099). The global ancestry-DAR S-LDXR estimate was retained only as a descriptive underpowered result (GCORSQ = 0.571191, SE = 0.577063; 1,232 analysis SNPs) and was not used as the primary biological test.

### Primary DAR heterogeneity test

The primary DAR heterogeneity test did not support enrichment of high EUR-EAS association-effect heterogeneity within ancestry-associated retinal DARs. In the top 5% chi2_het endpoint, 71 of 1,232 DAR SNPs (5.76%) and 19,653 of 379,279 matched non-DAR retinal OCR SNPs (5.18%) were classified as high heterogeneity. The primary odds ratio was 1.119 (95% CI 0.867-1.423), with Fisher P = 0.367. Continuous heterogeneity gave the same interpretation: the mean chi2_het difference between DAR and matched non-DAR retinal OCR SNPs was 0.0351, with Mann-Whitney P = 0.711. The matched permutation test also did not support enrichment: the observed mean chi2_het difference was 0.0647, with empirical P = 0.334 after 1,000 permutations within chromosome, MAF, MAF-difference, LD-score and OCR-status strata. Top 1% and top 10% sensitivity endpoints did not alter the conclusion (OR = 1.014, P = 0.888; OR = 1.050, P = 0.605).

### Robustness against SNP dependence

LD-reduced sensitivity analyses were label blind and based only on SNP position and LD structure in paired EUR and EAS reference panels. Stringent pruning sharply reduced the DAR sample size: r2 < 0.1 retained only 9 DAR SNPs, and r2 < 0.01 retained only 1 DAR SNP. These pruned analyses were therefore severely underpowered and were not used to infer a trend. Block-level robustness provided the more interpretable check against SNP-level dependence. Using 200 jackknife block boundaries, the adjusted block-level comparison of mean chi2_het between blocks with at least one DAR SNP and blocks without DAR SNPs gave P = 0.3836 after adjustment for block SNP count, mean MAF, baseline LD score and retinal OCR density. This analysis did not indicate that SNP-level dependence changed the primary conclusion.

### Effect-size precision

The negative primary result was interpreted through effect-size precision rather than P values alone. The primary top 5% odds ratio was 1.119, with a 95% CI of 0.867-1.423. With 1,232 DAR SNPs and a matched comparator event rate of 5.18%, the minimum detectable odds ratio was 1.397 for 80% power and 1.467 for 90% power at alpha = 0.05. Using OR = 1.5 as a prespecified robustness boundary, the confidence interval excluded an enrichment as large as OR = 1.5 under the selected endpoint. The same analysis did not exclude modest enrichment. The most accurate conclusion is that the data do not support a large systematic excess of ancestry-divergent effects in ancestry-associated retinal DARs, while smaller effects remain unresolved.
