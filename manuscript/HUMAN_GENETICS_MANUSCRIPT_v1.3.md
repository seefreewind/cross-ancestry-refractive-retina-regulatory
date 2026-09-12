# Predominantly shared cross-ancestry genetic architecture of refractive error despite ancestry-associated retinal regulatory variation

## Abstract

Ancestry-associated molecular regulatory variation is increasingly measurable in human tissues, but its relationship to ancestry-divergent genetic effects on complex traits remains unclear. We tested whether ancestry-associated retinal regulatory variation marks divergent European (EUR) and East Asian (EAS) genetic architecture for refractive error. Public EUR no-23andMe and EAS refractive-error GWAS summary statistics were harmonized, reference anchored and analyzed with ancestry-matched LD score regression, cross-population S-LDXR, human retinal open chromatin regions (OCRs) and a matched heterogeneity test comparing ancestry-associated differentially accessible retinal regions (DARs) with non-DAR retinal OCRs. The analysis set included 3,112,573 shared SNPs after effect alignment and paired-reference checks. Using the method-standard MAF > 0.05 threshold, genome-wide S-LDXR estimated high EUR-EAS sharing (GCORSQ = 1.028, SE = 0.100), and broad retinal OCRs showed a compatible pattern (GCORSQ = 0.948, SE = 0.097). In the primary DAR analysis, 71 of 1,232 DAR SNPs and 19,653 of 379,279 matched comparator SNPs fell in the top 5% heterogeneity endpoint (OR = 1.119, 95% CI 0.867-1.423, P = 0.367; matched permutation P = 0.334). Ancestry-associated retinal regulatory variation was not accompanied by a detectable large systematic excess of EUR-EAS association-effect heterogeneity, although modest enrichment remains possible.

## Keywords

refractive error; cross-ancestry genetics; genetic architecture; retinal regulatory genomics; population genetics; chromatin accessibility

## Introduction

Refractive error is common, highly polygenic and a major global visual-health burden, making it a strong model for studying cross-ancestry complex-trait architecture. Large refractive-error GWAS have identified many susceptibility loci, and the most recent multi-ancestry study of EUR, EAS and AFR cohorts greatly expanded discovery while reporting broad cross-ancestry sharing (Verhoeven et al. 2013; Hysi et al. 2020; Cheng et al. 2026). That shared background does not remove the need to understand local differences. The same source study also reported ancestry-enriched or ancestry-specific association signals, consistent with the principle that locus discovery and cross-ancestry effect sharing are distinct questions. Allele frequency, LD and tagging can change association signals even when effects are conserved, and fine-scale ancestry work shows that effect-size conservation can coexist with reduced portability and local ancestry-dependent patterns (Hu et al. 2025). The key question is therefore not simply whether ancestry-related association differences exist, but where true effect divergence is concentrated and whether it follows biologically relevant regulatory variation.

The retina is a biologically relevant tissue for refractive development and visually guided eye growth. Experimental and genetic studies support retinal contributions to refractive-error biology, but GWAS alone rarely resolves whether ancestry-linked regulatory differences mark divergent trait effects (Wallman et al. 1987; Kiefer et al. 2013; Hysi et al. 2020). The Human Retina Cell Atlas provides the necessary tissue context by mapping single-cell transcriptomes and chromatin accessibility across retinal cell classes and reporting ancestry-associated regulatory variation (Li et al. 2026). This establishes that ancestry-associated retinal molecular variation exists, but not its translation into ancestry-divergent association effects. It therefore enables a direct test of whether ancestry-associated retinal chromatin differences correspond to ancestry-divergent genetic effects for refractive error.

The unresolved question is not whether ancestry-associated retinal regulatory variation exists, but whether it maps onto ancestry-divergent genetic effects for refractive error. Current cross-ancestry genetics provides two relevant precedents. Complex-trait effects can be broadly conserved while association signals still differ through LD, allele frequency and tagging (Hu et al. 2025). Multi-ancestry molecular-QTL fine-mapping also shows that regulatory architectures can be highly consistent across ancestries while retaining gene- or locus-level heterogeneity (Lu et al. 2025). Together, these studies define a precise gap: what remains unknown is whether ancestry-associated retinal regulatory elements preferentially harbor variants with divergent EUR-EAS refractive-error effects. Enrichment would suggest that ancestry-sensitive retinal regulation helps localize cross-ancestry trait-effect divergence. Absence of enrichment would suggest that molecular ancestry differences and complex-trait effect divergence can represent distinct architectural layers. This distinction requires careful ancestry terminology because ancestry labels summarize correlated genetic, demographic and social histories rather than a single biological exposure (Khan et al. 2022).

We tested whether ancestry-associated retinal regulatory variation predicts where cross-ancestry refractive-error association effects diverge. The analysis used a three-level nested design. First, we estimated whether EUR-EAS refractive-error common-variant architecture is broadly shared genome-wide. Second, we asked whether this shared pattern extends to broad retinal open chromatin regions. Third, we tested whether ancestry-associated retinal differentially accessible regions preferentially concentrate association-effect heterogeneity relative to a tissue-matched non-DAR retinal regulatory background. The key innovation is testing whether ancestry-associated regulatory variation predicts where cross-ancestry trait-effect divergence occurs. This nested design distinguishes broad cross-ancestry genetic sharing from the narrower question of whether ancestry-associated retinal accessibility marks identify regions of effect divergence.

## Materials and methods

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

## Results

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

## Discussion

Our results indicate that ancestry-associated retinal molecular variation and cross-ancestry divergence in refractive-error association effects are not interchangeable features of genetic architecture. Refractive error showed predominantly shared EUR-EAS common-variant architecture at the genome-wide level and within broad retinal regulatory regions, whereas ancestry-associated retinal DARs did not identify a large systematic concentration of ancestry-divergent association effects. This pattern directly addresses the central question of the study: measurable ancestry-associated retinal regulatory variation does not necessarily map onto systematic divergence in common-variant trait effects. The result should not be read as evidence that ancestry-specific biology is absent, or that locus-specific divergence cannot occur. It instead separates two related layers of variation. One layer captures molecular regulatory differences observed in retinal tissue across sampled ancestry groups. The other captures marginal GWAS association effects for refractive error after allele alignment, reference anchoring and ancestry-matched LD modeling. The main interpretation is that these layers can coexist without being interchangeable.

This separation is biologically plausible. Chromatin accessibility is a molecular phenotype that reflects regulatory state, regulatory potential and cell-context-dependent activity. A difference in accessibility between sampled groups can identify regulatory elements whose molecular state differs, but it does not by itself show that nearby variants have different marginal effects on a complex trait. Refractive error is highly polygenic, and its common-variant architecture is distributed across many loci and biological processes. Ancestry-related regulatory differences may therefore be spread across regulatory networks without producing large, annotation-wide differences in marginal GWAS effects. Regulatory redundancy, distributed polygenicity, developmental compensation and context dependence could all reduce the translation from local chromatin differences to detectable trait-effect heterogeneity. This interpretation remains cautious: the present data do not prove buffering or compensation. They are consistent with a model in which molecular regulatory variation and complex-trait association-effect heterogeneity are connected through intermediate biological, developmental and statistical layers. Global sharing and local ancestry specificity are therefore not competing models. A trait can have highly shared common-variant architecture while still containing isolated ancestry-specific loci, local regulatory differences, allele-frequency differences and LD/tagging differences.

Recent human-genetics studies support this mixed picture, while also providing useful contrasts. The source refractive-error GWAS reported broad cross-ancestry sharing and improved discovery across EUR, EAS and AFR analyses, yet it also described ancestry-enriched and ancestry-specific association signals and differences in prediction portability (Cheng et al. 2026). Hu et al. showed that fine-scale human groups can have widespread conservation of genetic effect sizes across traits even when portability and association patterns differ, which is consistent with the genome-wide sharing observed here (Hu et al. 2025). Multi-ancestry molecular-QTL work using SuShiE similarly supports a model in which cis-molecular architectures are often shared across ancestries while gene- or locus-level heterogeneity remains detectable (Lu et al. 2025). Evidence from other biological contexts shows why the present result should not be generalized too broadly. Wang et al. reported that genes with differential expression across ancestries were enriched in ancestry-specific disease effects, likely reflecting gene-by-environment interactions in their setting (Wang et al. 2024). That finding does not contradict the retinal result. Differences in tissue context, immune or environmental sensitivity, molecular phenotype, annotation scale, phenotype architecture and statistical power could all affect whether ancestry-associated molecular variation aligns with trait-effect heterogeneity. The emerging picture across recent multi-ancestry studies is therefore not one of either complete conservation or pervasive divergence, but of broadly shared genetic and molecular architectures containing subsets of locally heterogeneous effects. The refractive-error retina analysis fits this framework.

The study’s main contribution is the direct test linking these two previously separate observations. Cheng et al. established where refractive-error genetic associations are broadly shared or ancestry enriched. The Human Retina Cell Atlas established where retinal molecular and chromatin features vary with ancestry. The present study asked whether ancestry-associated retinal regulatory regions preferentially mark genomic locations in which refractive-error association effects diverge across ancestries. The tissue-matched comparator is central to that test. Ancestry-associated DAR SNPs were compared with matched non-DAR retinal OCR SNPs, rather than with the rest of the genome. This design controls for broad retinal regulatory context and targets the ancestry-DAR label itself. It avoids treating all retinal open chromatin as equivalent to ancestry-associated accessibility, and it avoids attributing a generic retinal regulatory signal to ancestry-associated molecular variation. The nested design separates whether retinal regulatory regions broadly preserve cross-ancestry sharing from the narrower question of whether ancestry-associated accessibility identifies regions of effect divergence.

The scientific implication is that ancestry-associated molecular annotations should be treated as hypotheses about cross-ancestry trait heterogeneity, not as evidence of heterogeneity by themselves. This distinction matters as multi-ancestry GWAS are increasingly interpreted alongside single-cell ATAC, eQTL, pQTL, spatial-omics and cell-state annotations. An annotation associated with ancestry can be biologically informative, but it should not be converted into an ancestry-specific disease mechanism without testing trait-level effect divergence. The same caution applies to genetic prediction. Reduced cross-ancestry prediction portability in refractive error should not be automatically attributed to ancestry-associated retinal chromatin differences. LD, allele frequency, training imbalance, phenotype heterogeneity, local effect differences and environmental structure may all contribute, and this study was not designed to apportion those sources. The precision analysis gives the bounded interpretation of the DAR result. The primary estimate was OR = 1.119, with a 95% CI of 0.867-1.423, so a large OR = 1.5 enrichment was not compatible with the observed interval under the tested endpoint. The absence of statistical enrichment should therefore not be interpreted as evidence of exact equivalence. The confidence interval and power analysis indicate that a large systematic enrichment is unlikely under the tested endpoint, while modest distributed effects remain compatible with the data.

Several limitations define where this interpretation stops. First, the DAR annotation was sparse, with 1,232 analysis DAR SNPs, and it depends on HRCA donor composition, cell representation, assay depth and power to detect accessibility differences. Annotation misclassification or incomplete detection of ancestry-associated accessibility would generally be expected to reduce sensitivity to modest enrichment, although the direction and magnitude of that effect cannot be known from the present data. Larger ancestry-balanced retinal atlases, independent retinal ATAC datasets, donor-level chromatin QTL maps and deeper cell-state annotations would sharpen this test. Second, the heterogeneity statistic reflects association-effect heterogeneity on the released source-effect scale. The source GWAS combined heterogeneous phenotype definitions, and the present result should not be read as evidence that causal effects are equivalent across ancestries. Phenotype-harmonized cohorts, shared quantitative refractive measures, individual-level models and direct covariance estimation would better separate effect-scale, overlap and ascertainment issues. Third, the scope is EUR-EAS, common-variant, adult-retinal and retina-focused. The result does not address AFR, South Asian or admixed populations, rare variants, developmental retinal states, choroid or sclera, gene-environment interactions, or locus-specific functional mechanisms. In conclusion, refractive error shows predominantly shared EUR-EAS architecture genome-wide and within broad retinal regulatory regions, with no evidence for a large systematic DAR concentration of association-effect heterogeneity. Modest or local effects remain possible. Ancestry-associated molecular differences should be tested empirically as candidate markers of disease-effect divergence rather than presumed to imply it.

## Tables

Table 1. GWAS and analysis characteristics.

Table 2. Main cross-ancestry architecture results.

Table 3. DAR heterogeneity and robustness tests.

## Figure legends

Fig. 1. Study design. Public EUR no-23andMe and EAS refractive-error GWAS summary statistics were harmonized, empirically anchored to the reference coordinate framework and analyzed with ancestry-matched LDSC, S-LDXR and retinal regulatory annotations. The primary DAR analysis compared ancestry-associated retinal DAR SNPs with matched non-DAR retinal OCR SNPs for association-effect heterogeneity, with permutation, block-level robustness and effect-size precision analyses.

Fig. 2. Cross-ancestry genetic architecture of refractive error. Forest plot shows S-LDXR GCORSQ estimates and 95% confidence intervals for the genome-wide analysis, all retinal OCRs and the descriptive ancestry-DAR annotation. Method-standard MAF > 0.05 estimates are shown for genome-wide and all-retinal-OCR analyses; the DAR estimate is descriptive because of sparse SNP support.

Fig. 3. Primary DAR heterogeneity analysis. (A) Proportion of SNPs in the top 5% association-effect heterogeneity endpoint for ancestry-associated DARs and matched non-DAR retinal OCRs. (B) Primary odds ratio and 95% confidence interval. (C) Matched permutation null distribution for the mean chi2_het difference, with the observed statistic marked.

Fig. 4. Effect-size precision and robustness. The primary DAR odds ratio and 95% confidence interval are shown with the OR = 1.5 prespecified robustness boundary and the 80% and 90% minimum detectable odds ratios. Block-level robustness did not support a DAR-linked increase in mean heterogeneity (P = 0.3836).

## Data availability

All analyses used publicly available datasets and reference resources. Refractive-error GWAS summary statistics were obtained from the public multi-ancestry refractive-error GWAS resource described by Cheng et al. The human retinal regulatory annotations were derived from the Human Retina Cell Atlas and associated public atlas resources. Reference resources included 1000 Genomes Project EUR and EAS panels, baselineLD annotations, dbSNP Build 151 and UCSC liftover chain files. Third-party GWAS and reference files should be obtained from their original repositories under the terms set by the data providers.

## Code availability

The analysis scripts, fixed configuration files, QC records and figure-ready tables will be made available in a public repository before submission: https://github.com/seefreewind/cross-ancestry-refractive-retina-regulatory. The current analysis package contains reproducible harmonization/QC scripts, S-LDXR scripts, heterogeneity scripts and robustness scripts.

## Acknowledgements

[Acknowledgements to be added by the authors.]

## Author contributions

[Author contributions to be added by the authors using CRediT taxonomy.]

## Funding

[Funding information to be added by the authors.]

## Competing interests

The authors declare no competing interests. [Please confirm before submission.]

## References

Brown BC, Asian Genetic Epidemiology Network Type 2 Diabetes Consortium, Ye CJ, Price AL, Zaitlen N. 2016. Transethnic genetic-correlation estimates from summary statistics. American Journal of Human Genetics 99:76-88. doi:10.1016/j.ajhg.2016.05.001.

Bulik-Sullivan BK, Loh PR, Finucane HK, Ripke S, Yang J, et al. 2015. LD Score regression distinguishes confounding from polygenicity in genome-wide association studies. Nature Genetics 47:291-295. doi:10.1038/ng.3211.

Bulik-Sullivan B, Finucane HK, Anttila V, Gusev A, Day FR, et al. 2015. An atlas of genetic correlations across human diseases and traits. Nature Genetics 47:1236-1241. doi:10.1038/ng.3406.

Cheng FF, Liu X, Mi H, Wang L, Ma R, et al. 2026. Multi-ancestry genome-wide association analyses of refractive error augment genetic discovery and polygenic prediction. Nature Genetics 58:1030-1039. doi:10.1038/s41588-026-02576-0.

Finucane HK, Bulik-Sullivan B, Gusev A, Trynka G, Reshef Y, et al. 2015. Partitioning heritability by functional annotation using genome-wide association summary statistics. Nature Genetics 47:1228-1235. doi:10.1038/ng.3404.

Hu S, Ferreira LAF, Shi S, Hellenthal G, Marchini J, Lawson DJ, Myers SR. 2025. Fine-scale population structure and widespread conservation of genetic effect sizes between human groups across traits. Nature Genetics 57:379-389. doi:10.1038/s41588-024-02035-8.

Lu Z, Wang X, Carr M, Kim A, Gazal S, Mohammadi P, Wu L, Pirruccello J, Kachuri L, Gusev A, Mancuso N. 2025. Improved multiancestry fine-mapping identifies cis-regulatory variants underlying molecular traits and disease risk. Nature Genetics 57:1881-1889. doi:10.1038/s41588-025-02262-7.

Hysi PG, Choquet H, Khawaja AP, Wojciechowski R, Tedja MS, et al. 2020. Meta-analysis of 542,934 subjects of European ancestry identifies new genes and mechanisms predisposing to refractive error and myopia. Nature Genetics 52:401-407. doi:10.1038/s41588-020-0599-0.

Khan AT, Gogarten SM, McHugh CP, Stilp AM, Sofer T, et al. 2022. Recommendations on the use and reporting of race, ethnicity, and ancestry in genetic research: experiences from the NHLBI TOPMed program. Cell Genomics 2:100155. doi:10.1016/j.xgen.2022.100155.

Kiefer AK, Tung JY, Do CB, Hinds DA, Mountain JL, et al. 2013. Genome-wide analysis points to roles for extracellular matrix remodeling, the visual cycle, and neuronal development in myopia. PLOS Genetics 9:e1003299. doi:10.1371/journal.pgen.1003299.

Li J, Wang J, Ibarra IL, Cheng X, Luecken MD, et al. 2026. Single-cell atlas of the transcriptome and chromatin accessibility in the human retina. Nature Genetics 58:418-433. doi:10.1038/s41588-025-02454-1.

Martin AR, Gignoux CR, Walters RK, Wojcik GL, Neale BM, et al. 2017. Human demographic history impacts genetic risk prediction across diverse populations. American Journal of Human Genetics 100:635-649. doi:10.1016/j.ajhg.2017.03.004.

Shi H, Gazal S, Kanai M, Koch EM, Schoech AP, et al. 2021. Population-specific causal disease effect sizes in functionally important regions impacted by selection. Nature Communications 12:1098. doi:10.1038/s41467-021-21286-1.

The 1000 Genomes Project Consortium. 2015. A global reference for human genetic variation. Nature 526:68-74. doi:10.1038/nature15393.

Wang J, Zhang Z, Lu Z, Mancuso N, Gazal S. 2024. Genes with differential expression across ancestries are enriched in ancestry-specific disease effects likely due to gene-by-environment interactions. American Journal of Human Genetics 111:2117-2128. doi:10.1016/j.ajhg.2024.07.021.

Verhoeven VJM, Hysi PG, Wojciechowski R, Fan Q, Guggenheim JA, et al. 2013. Genome-wide meta-analyses of multiancestry cohorts identify multiple new susceptibility loci for refractive error and myopia. Nature Genetics 45:314-318. doi:10.1038/ng.2554.

Wallman J, Gottlieb MD, Rajaram V, Fugate-Wentzek LA. 1987. Local retinal regions control local eye growth and myopia. Science 237:73-77. doi:10.1126/science.3603011.
