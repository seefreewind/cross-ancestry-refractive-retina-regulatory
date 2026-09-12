# Phase 2 Route B Method Design

## 1. Research Question

This phase asks whether SNPs located in HRCA ancestry-differential retinal accessible regions show stronger EUR-EAS refractive-error effect heterogeneity than matched non-DAR retinal OCR SNPs within the formal shared S-LDXR SNP universe.

The study type is a genetic-statistical multi-omics integration analysis. The primary claim is enrichment of cross-ancestry genetic-effect heterogeneity in ancestry-DAR retinal regulatory regions. The analysis does not claim cell-type-specific genetic correlation, causal mechanism, clinical prediction, or experimental validation.

## 2. Data Requirement

| Data Type | Required | Optional | Purpose |
|---|---|---|---|
| EUR/EAS harmonized GWAS effects | Yes | No | Compute SNP-level beta-difference heterogeneity |
| Formal shared S-LDXR SNP universe | Yes | No | Keep Phase 2 inside the audited Phase 1C.2 SNP universe |
| HRCA ancestry-DAR annotation | Yes | No | Define primary regulatory case SNPs |
| Matched non-DAR retinal OCR annotation | Yes | No | Define primary retinal comparator |
| All retinal OCR annotation | Yes | No | Define broad retinal positive-control context |
| Reference MAF and baseline LD score | Yes | No | Build matched permutation strata |
| Cell-class DAR labels | Secondary | Yes | Descriptive follow-up if SNP counts are sufficient |

## 3. Overall Workflow

Step 1: Freeze the Phase 2 estimand and inputs in `config/PHASE2_ANALYSIS_FREEZE_v1.yaml`.

Step 2: Build a formal SNP-level feature matrix with harmonized EUR/EAS effects, heterogeneity statistics, retinal annotations, reference MAF, baseline LD score, and matching strata.

Step 3: Test whether DAR SNPs are enriched among high-heterogeneity SNPs versus genome-wide, all retinal OCR, and matched non-DAR retinal OCR backgrounds.

Step 4: Use matched permutations stratified by chromosome, MAF, MAF difference, baseline LD score, and OCR status for the primary matched comparator.

Step 5: Continue to cell-class, locus, CRE, and motif analyses only after the primary enrichment output exists and passes QC.

## 4. Core Analysis Modules

### Module 1

名称：Formal Phase 2 input contract

输入：Phase 1C.2 formal freeze, genome-wide S-LDXR decision, harmonized EUR/EAS effects, HRCA annotations.

方法：Freeze the analysis universe, allowed claims, primary statistic, comparator hierarchy, and permutation design.

工具：YAML freeze and file-level provenance.

输出：`config/PHASE2_ANALYSIS_FREEZE_v1.yaml`

验证：All referenced input files must exist and belong to the Phase 1C.2 passed universe.

对应 Figure：Supplementary workflow or Methods schematic.

风险：If the formal universe is changed, all Phase 2 outputs must be regenerated.

### Module 2

名称：EUR-EAS SNP-level heterogeneity matrix

输入：`data/processed/EUR_EAS_HARMONIZED.parquet`, formal S-LDXR sumstats, DAR/OCR annotations, reference MAF, baseline score.

方法：Compute `z_het = (b_EUR - b_EAS) / sqrt(se_EUR^2 + se_EAS^2)` and `chi2_het = z_het^2` under the frozen no-overlap assumption.

工具：`scripts/analysis/build_phase2_heterogeneity_features.py`

输出：`data/processed/phase2/EUR_EAS_HETEROGENEITY_FEATURES.parquet`; `results/phase2/PHASE2_HETEROGENEITY_FEATURE_QC.tsv`

验证：Formal SNP count must match 3,112,573; DAR SNP count must remain above the frozen minimum of 1,000.

对应 Figure：Genome-wide heterogeneity distribution and annotation overlay.

风险：Effect-scale differences between GWAS releases can inflate heterogeneity; interpretation remains enrichment-based, not locus-causal.

### Module 3

名称：DAR heterogeneity enrichment

输入：Phase 2 feature matrix.

方法：Fisher tests for top 1%, 5%, and 10% heterogeneity bins; Mann-Whitney tests for continuous heterogeneity; matched permutation for mean chi-square difference between DAR and matched non-DAR retinal OCR SNPs.

工具：`scripts/analysis/run_phase2_dar_heterogeneity_enrichment.py`

输出：`results/phase2/PHASE2_DAR_HETEROGENEITY_ENRICHMENT.tsv`; `results/phase2/PHASE2_DAR_MATCHED_PERMUTATION_NULL.tsv`

验证：Permutation uses 1,000 replicates with fixed seed 20260912 and strata defined in the freeze.

对应 Figure：Primary enrichment forest/table panel and permutation null panel.

风险：DAR SNP count is modest and LD among SNPs means unpruned SNP-level P values are descriptive unless supported by matched permutation and sensitivity analyses.

## 5. Required vs Optional Analysis

| Analysis | Required or Optional | Reason |
|---|---|---|
| SNP-level EUR-EAS heterogeneity matrix | Required | Defines the Phase 2 estimand |
| DAR vs matched non-DAR retinal OCR enrichment | Required | Primary Route B test |
| Matched permutation | Required | Controls MAF, LD proxy, chromosome, and OCR status |
| All retinal OCR context | Required | Positive-control context |
| Global S-LDXR reference | Required context | Confirms high shared architecture but not local DAR enrichment |
| Cell-class DAR descriptive summary | Optional | Only if per-class SNP counts are sufficient |
| Locus/CRE/motif prioritization | Optional after primary pass | Interpretation layer, not primary evidence |

## 6. Validation Strategy

Internal validation: check formal SNP overlap, finite heterogeneity statistics, annotation counts, and threshold stability.

External validation: not available in this phase without an independent ancestry-specific refractive-error GWAS release.

Biological validation: limited to retinal OCR/DAR regulatory context; no wet-lab or independent retina assay validation is claimed.

Sensitivity analysis: top 1%, 5%, and 10% heterogeneity thresholds plus continuous heterogeneity.

Negative/control analysis: matched non-DAR retinal OCR serves as the primary comparator; all retinal OCR gives broader retinal context.

## 7. Expected Figure Mapping

| Figure | Analysis Source | Main Message |
|---|---|---|
| Figure 1 | Phase 1C.2 plus Phase 2 freeze | Audited cross-ancestry and retinal-regulatory workflow |
| Figure 2 | Phase 2 heterogeneity matrix | EUR-EAS effect heterogeneity is measurable in the formal shared universe |
| Figure 3 | DAR enrichment and permutation | Test whether ancestry-DAR SNPs carry excess high heterogeneity |
| Supplementary Figure 1 | Annotation count/QC | DAR is sparse but above the frozen minimum for Route B |
| Supplementary Figure 2 | Sensitivity thresholds | Enrichment stability across top 1%, 5%, and 10% bins |

## 8. Risk and Alternative Plan

The main statistical risk is LD-induced dependence among SNPs. The current route addresses this with matched permutation but does not replace locus-level or LD-pruned sensitivity checks.

The main data risk is sparse DAR SNP coverage. If the matched enrichment is unstable, the result should be reported as underpowered and shifted toward descriptive regulatory-context analysis.

The main interpretation risk is over-reading DARs as mechanisms. Phase 2 can support enrichment of heterogeneity in regulatory annotations; mechanism requires independent fine-mapping, colocalization, or experimental validation.

## 9. Next Step Recommendation

Proceed to CodexPipeline execution for the Phase 2 feature matrix and primary enrichment table. If the primary output passes QC, proceed to a leakage/robustness audit before FigurePlanner.
