# Shared cross-ancestry genetic architecture of refractive error across retinal regulatory regions

## Abstract

Ancestry-associated molecular regulatory variation is increasingly measurable in human tissues, but its relationship to ancestry-divergent genetic effects on complex traits remains unclear. We used refractive error as a model trait to test whether ancestry-associated retinal regulatory variation concentrates variants with divergent European (EUR) and East Asian (EAS) genetic effects. EUR and EAS refractive-error GWAS summary statistics were harmonized, reference anchored, and analyzed with ancestry-matched LD score regression, cross-population S-LDXR, human retinal open chromatin regions (OCRs), and a frozen heterogeneity test comparing ancestry-associated differentially accessible retinal regions (DARs) with matched non-DAR retinal OCRs. The formal analysis universe included 3,112,573 shared SNPs. Genome-wide S-LDXR estimated a high shared EUR-EAS architecture (GCORSQ = 1.010 +/- 0.108). Broad retinal OCRs showed a compatible pattern (GCORSQ = 0.935 +/- 0.101). In the primary DAR analysis, 71 of 1,232 DAR SNPs and 19,653 of 379,279 matched non-DAR retinal OCR SNPs fell in the top 5% of heterogeneity (OR = 1.119, 95% CI 0.867-1.423, P = 0.367; matched permutation P = 0.334). The continuous heterogeneity comparison was also unsupported (P = 0.711). The confidence interval was inconsistent with a large enrichment of OR >= 1.5, although modest enrichment remains possible. These results support predominantly shared EUR-EAS genetic architecture of refractive error and provide no evidence for a large systematic excess of ancestry-divergent effects within ancestry-associated retinal regulatory regions.

## Keywords

refractive error; cross-ancestry genetics; genetic architecture; retinal regulatory genomics; population genetics; chromatin accessibility

## Introduction

Genome-wide association studies have established that many complex traits are influenced by large numbers of common variants, yet the interpretation of genetic effects across ancestries remains a central problem in human genetics. Cross-ancestry analyses can identify additional loci and improve polygenic prediction, but they also expose a distinction that is often blurred: the discovery of ancestry-enriched association signals is not the same as evidence that causal or tagged genetic effects differ systematically between ancestry groups. Differences in allele frequency, linkage disequilibrium, imputation quality, environmental context, ascertainment and sample size can all change association signals across populations even when much of the underlying architecture is shared. Refractive error is a useful trait for examining this distinction because it is common, highly polygenic and supported by large GWAS resources spanning European and Asian cohorts. Earlier multi-ancestry GWAS identified many refractive-error and myopia loci, European-ancestry meta-analysis expanded the associated locus set, and the most recent multi-ancestry refractive-error GWAS further augmented discovery and prediction across populations (Verhoeven et al. 2013; Hysi et al. 2020; Cheng et al. 2026).

The retina provides a biologically relevant regulatory context for refractive-error genetics. Experimental and genetic studies support roles for visual input, retinal signaling, extracellular matrix remodeling, visual-cycle biology and neuronal development in refractive development and myopia susceptibility (Wallman et al. 1987; Kiefer et al. 2013; Hysi et al. 2020). Human retinal single-cell and chromatin resources now make it possible to connect common-variant association statistics with tissue-specific regulatory maps rather than interpreting GWAS loci only through nearest genes or generic genome annotations. The Human Retina Cell Atlas defined transcriptomic and chromatin-accessibility landscapes across retinal cell classes and reported ancestry-associated chromatin-accessibility differences in retinal regulatory elements (Li et al. 2026). These data create an opportunity to test whether molecular regulatory differences observed in retinal tissue correspond to ancestry-divergent genetic effects for an ocular quantitative trait. The connection is plausible, but it is not automatic: an open chromatin region that differs in accessibility between sampled ancestry groups may reflect demographic, technical, cell-composition or context-specific regulatory processes without concentrating variants whose GWAS effects differ between ancestries.

The central gap is whether ancestry-associated retinal regulatory regions preferentially harbor variants with ancestry-divergent genetic effects on refractive error. Prior refractive-error GWAS characterized association architecture, expanded the catalog of associated loci and evaluated cross-ancestry prediction (Verhoeven et al. 2013; Hysi et al. 2020; Cheng et al. 2026). Retinal single-cell atlases characterized regulatory landscapes and ancestry-associated chromatin features (Li et al. 2026). Statistical methods now allow cross-population genetic sharing to be estimated with ancestry-specific LD information and functional annotations, providing a framework for separating broad shared architecture from annotation-specific heterogeneity (Bulik-Sullivan et al. 2015a; Bulik-Sullivan et al. 2015b; Finucane et al. 2015; Shi et al. 2021). Whether ancestry-associated retinal regulatory regions preferentially harbor variants with ancestry-divergent genetic effects on refractive error has not been directly tested. This missing link matters because a positive result would suggest that ancestry-associated retinal regulatory variation marks regions of cross-ancestry effect divergence, whereas a negative but well-powered and bounded result would support a more shared architecture despite measurable regulatory differences. It also provides a concrete test of how ancestry terminology and molecular annotations should be used in genetic interpretation (Khan et al. 2022).

Here, we addressed that gap using a reference-anchored EUR-EAS human genetics design. We first estimated ancestry-specific SNP heritability and genome-wide cross-population sharing for refractive error. We then tested whether broadly accessible retinal open chromatin regions showed cross-ancestry sharing compatible with the genome-wide pattern. Finally, we asked whether ancestry-associated retinal differentially accessible regions were enriched for SNPs with high EUR-EAS effect heterogeneity compared with matched non-DAR retinal OCRs. The study was designed as a targeted manuscript analysis rather than an open-ended discovery screen. Primary endpoints, comparators and robustness checks were frozen before post-primary robustness work, and the analysis was stopped after the predefined robustness boundary. This design allowed the manuscript to focus on a specific question: whether ancestry-associated retinal regulatory variation necessarily translates into ancestry-divergent genetic effects on refractive error.

## Materials and methods

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

## Results

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

## Discussion

This study tested whether ancestry-associated retinal regulatory variation is accompanied by ancestry-divergent genetic effects on refractive error. Three findings define the paper. First, genome-wide EUR-EAS analyses supported a predominantly shared common-variant architecture for refractive error, with strong ancestry-specific LDSC heritability estimates and a boundary-adjacent genome-wide S-LDXR estimate compatible with very high sharing. Second, broadly accessible retinal regulatory regions showed an S-LDXR estimate broadly compatible with the genome-wide pattern, indicating that retinal open chromatin does not appear to mark a globally divergent EUR-EAS architecture for this trait. Third, ancestry-associated retinal DARs did not show detectable excess EUR-EAS effect heterogeneity relative to matched non-DAR retinal OCRs under the frozen top 5% endpoint, continuous heterogeneity comparison or matched permutation test. Together, these results support a human genetics interpretation in which refractive error is largely shared across EUR and EAS common-variant architectures, while the available ancestry-associated retinal regulatory annotation does not identify a large systematic concentration of ancestry-divergent effects.

The findings sharpen a general question in human genetics: ancestry-associated molecular variation does not automatically imply ancestry-divergent complex-trait effect sizes. Chromatin accessibility can differ across sampled ancestry groups for many reasons, including demographic history, local environmental exposures, cell-state composition, statistical power and context-specific regulatory activity. Complex-trait GWAS effects then pass through an additional layer of architecture, where polygenicity, LD, allele frequency, tagging, developmental timing and regulatory redundancy influence what can be detected in association statistics. For refractive error, the observed pattern is consistent with a model in which many common-variant effects are shared across EUR and EAS analyses even though a subset of retinal regulatory elements shows ancestry-associated accessibility differences. This interpretation should be kept statistical. The present results do not show that ancestry-associated chromatin differences are biologically irrelevant, and they do not rule out regulatory mechanisms at specific loci. They show that, within the frozen matched analysis, those retinal DARs did not concentrate large EUR-EAS GWAS effect heterogeneity.

The study extends two bodies of prior work. Multi-ancestry refractive-error GWAS have expanded variant discovery, mapped many loci and strengthened the empirical basis for evaluating shared and ancestry-enriched association signals (Verhoeven et al. 2013; Hysi et al. 2020; Cheng et al. 2026). These studies established refractive error as a strongly polygenic trait with broad cross-population relevance, but their primary goal was not to test whether ancestry-associated retinal regulatory elements preferentially carry ancestry-divergent effect sizes. The Human Retina Cell Atlas established a single-cell transcriptomic and chromatin-accessibility reference for human retina and reported ancestry-associated regulatory variation (Li et al. 2026). That atlas motivates genetic follow-up, but a chromatin-accessibility difference and a GWAS effect-size difference are distinct measurements. The present analysis connects these resources through a prespecified estimand: enrichment of high EUR-EAS effect heterogeneity in ancestry-associated retinal DARs compared with matched non-DAR retinal OCRs. This design makes the negative result informative rather than merely an absence of locus discovery.

The negative primary result is best interpreted through effect-size precision, not through P values alone. In the primary endpoint, 5.76% of DAR SNPs and 5.18% of matched non-DAR retinal OCR SNPs fell in the top 5% of genome-wide heterogeneity, yielding OR = 1.119 with a 95% confidence interval of 0.867-1.423. The matched permutation test accounted for chromosome, average MAF, absolute MAF difference, LD-score bin and retinal OCR status and remained unsupported. The block-level analysis, adjusted for block SNP count, mean MAF, baseline LD score and retinal OCR density, did not suggest that SNP-level dependence changed the inference. These analyses argue against a large systematic DAR enrichment. They do not establish exact equivalence between DAR and non-DAR regions. The power calculations are central: with 1,232 DAR SNPs and the observed comparator event rate, the analysis had 80% power to detect an odds ratio of about 1.40 and 90% power to detect an odds ratio of about 1.47. Thus, OR >= 1.5 is inconsistent with the observed confidence interval, while modest enrichment remains possible.

Several design features strengthen the inference for a targeted Human Genetics manuscript. The study used a reference-anchored EUR-EAS framework after identifying that released GWAS files did not explicitly report genome assembly. It preserved the distinction between the broader harmonized shared SNP set and the stricter formal S-LDXR-aligned universe. It treated retinal DARs as an annotation for a statistical question rather than as a causal label. It used a retinal comparator, matched non-DAR retinal OCRs, rather than relying only on a genome-wide background that could confound retinal regulatory context with ancestry-DAR status. It also froze the primary endpoint before Phase 2B robustness analyses and retained unsupported sensitivity results rather than selecting favorable thresholds. The LD-pruned analyses illustrate why this matters: stringent pruning retained too few DAR SNPs to support directional interpretation, so the manuscript relies on matched permutation and block-level robustness as the interpretable post-primary checks. The stop rule prevented expansion into CRE-to-gene mapping, motifs, pathway fishing or locus narratives after the primary regulatory-enrichment result was negative.

The study has clear limitations. First, only 1,232 formal DAR SNPs were available, limiting sensitivity to modest enrichment. Second, DAR-specific S-LDXR was underpowered and should remain descriptive. Third, the ancestry-DAR annotation depends on the HRCA sample composition, cell representation, ancestry labels, assay depth and power to detect accessibility differences. Fourth, the analysis was restricted to EUR and EAS GWAS and should not be generalized to African, admixed, South Asian or other populations. Fifth, retina is central to visually guided eye growth but is not the only tissue, developmental stage or biological process relevant to refractive error. Sixth, chromatin accessibility marks regulatory potential and does not establish causal regulation of nearby genes or trait effects. Seventh, the released GWAS files did not explicitly declare genome assembly, so the analysis used empirical GRCh37.p13 reference anchoring rather than source-confirmed build metadata. Eighth, the heterogeneity statistic treated EUR and EAS GWAS as independent, and residual sample overlap could affect variance estimates. Ninth, matched non-DAR retinal OCRs are an operational comparator and should not be interpreted as invariant regulatory regions across ancestries. Tenth, absence of global DAR enrichment does not rule out locus-specific ancestry-divergent effects, developmental-stage-specific effects, rare-variant effects or gene-environment interactions. These limitations define the boundary of the claim. The manuscript supports a shared-architecture conclusion at genome-wide and broad retinal-OCR levels and a bounded negative result for ancestry-DAR enrichment; it does not claim that retinal regulatory variation is unimportant, that all refractive-error loci are shared across ancestries, or that ancestry-related regulatory effects are absent.

In conclusion, refractive error shows predominantly shared EUR-EAS common-variant architecture at the genome-wide level and within broadly accessible retinal regulatory regions. Within the frozen matched analysis, ancestry-associated retinal DARs did not show detectable excess EUR-EAS effect heterogeneity, and the observed confidence interval was inconsistent with a large enrichment of high-heterogeneity SNPs. Modest regulatory enrichment remains possible, and locus-specific effects require larger and more diverse resources. The main contribution is a constrained statistical result: ancestry-associated retinal molecular variation need not translate into a large systematic concentration of ancestry-divergent GWAS effects for a complex ocular trait. Larger multi-ancestry retinal regulatory resources, independent ancestry-specific refractive-error GWAS and locus-resolved functional studies will be needed to resolve modest and local regulatory heterogeneity.
This framing should help future studies separate regulatory annotation differences from genetic-effect divergence before moving to mechanistic experiments.

## Data availability

All analyses used publicly available datasets and reference resources. Refractive-error GWAS summary statistics were obtained from the public multi-ancestry refractive-error GWAS resource described by Cheng et al. The human retinal regulatory annotations were derived from the Human Retina Cell Atlas and associated public atlas resources. Reference resources included 1000 Genomes Phase 3 EUR and EAS panels, baselineLD annotations, dbSNP Build 151 and UCSC liftover chain files. Third-party GWAS and reference files should be obtained from their original repositories under the terms set by the data providers.

## Code availability

The analysis scripts, frozen configuration files, QC manifests and figure-ready tables will be made available in a public repository before submission: [repository URL to be added before submission]. The current analysis package contains scripted freeze files, harmonization/QC scripts, S-LDXR execution scripts, Phase 2 heterogeneity scripts and Phase 2B robustness scripts.

## Acknowledgements

[Acknowledgements to be added by the authors.]

## Author contributions

[Author contributions to be added by the authors using CRediT taxonomy.]

## Funding

[Funding information to be added by the authors.]

## Competing interests

The authors declare no competing interests. [Please confirm before submission.]

## References

Birney E, Inouye M, Raff J, Rutherford A, Scally A. 2021. The language of race, ethnicity, and ancestry in human genetic research. arXiv:2106.10041.

Bulik-Sullivan BK, Loh PR, Finucane HK, Ripke S, Yang J, et al. 2015. LD Score regression distinguishes confounding from polygenicity in genome-wide association studies. Nature Genetics 47:291-295. doi:10.1038/ng.3211.

Bulik-Sullivan B, Finucane HK, Anttila V, Gusev A, Day FR, et al. 2015. An atlas of genetic correlations across human diseases and traits. Nature Genetics 47:1236-1241. doi:10.1038/ng.3406.

Cheng FF, Liu X, Mi H, Wang L, Ma R, et al. 2026. Multi-ancestry genome-wide association analyses of refractive error augment genetic discovery and polygenic prediction. Nature Genetics. doi:10.1038/s41588-026-02576-0.

Finucane HK, Bulik-Sullivan B, Gusev A, Trynka G, Reshef Y, et al. 2015. Partitioning heritability by functional annotation using genome-wide association summary statistics. Nature Genetics 47:1228-1235. doi:10.1038/ng.3404.

Hysi PG, Choquet H, Khawaja AP, Wojciechowski R, Tedja MS, et al. 2020. Meta-analysis of 542,934 subjects of European ancestry identifies new genes and mechanisms predisposing to refractive error and myopia. Nature Genetics 52:401-407. doi:10.1038/s41588-020-0599-0.

Khan AT, Gogarten SM, McHugh CP, Stilp AM, Sofer T, et al. 2022. Recommendations on the use and reporting of race, ethnicity, and ancestry in genetic research: experiences from the NHLBI TOPMed program. Cell Genomics 2:100155. doi:10.1016/j.xgen.2022.100155.

Kiefer AK, Tung JY, Do CB, Hinds DA, Mountain JL, et al. 2013. Genome-wide analysis points to roles for extracellular matrix remodeling, the visual cycle, and neuronal development in myopia. PLOS Genetics 9:e1003299. doi:10.1371/journal.pgen.1003299.

Li J, Wang J, Ibarra IL, Cheng X, Luecken MD, et al. 2026. Single-cell atlas of the transcriptome and chromatin accessibility in the human retina. Nature Genetics 58:418-433. doi:10.1038/s41588-025-02454-1.

Shi H, Gazal S, Kanai M, Koch EM, Schoech AP, et al. 2021. Population-specific causal disease effect sizes in functionally important regions impacted by selection. Nature Communications 12:1098. doi:10.1038/s41467-021-21286-1.

The 1000 Genomes Project Consortium. 2015. A global reference for human genetic variation. Nature 526:68-74. doi:10.1038/nature15393.

Verhoeven VJM, Hysi PG, Wojciechowski R, Fan Q, Guggenheim JA, et al. 2013. Genome-wide meta-analyses of multiancestry cohorts identify multiple new susceptibility loci for refractive error and myopia. Nature Genetics 45:314-318. doi:10.1038/ng.2554.

Wallman J, Gottlieb MD, Rajaram V, Fugate-Wentzek LA. 1987. Local retinal regions control local eye growth and myopia. Science 237:73-77. doi:10.1126/science.3603011.
