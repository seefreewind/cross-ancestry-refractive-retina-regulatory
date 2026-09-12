# PHASE 1C.2 VERDICT

Overall: **PASS**

The aligned genome-wide EUR–EAS S-LDXR baseline passed the formal technical gate. All row-identity, numerical, score-universe, frozen-input, convergence, jackknife, chromosome-influence and qualitative LDSC-triangulation checks completed. The three permitted global retinal annotations were then tested only for numerical estimability. No cell-type S-LDXR or Phase 2 analysis was run.

## Alignment

paired panel N: **6,309,729**  
aligned baseline N: **6,309,729**  
22 chromosome exact match: **YES, 22/22 PASS**  
missing SNP: **0**  
CHR mismatch: **0**  
BP mismatch: **0**  
SNP ID mismatch: **0**  
order mismatch: **0**

The aligned score universe after the pre-specified EAS/EUR MAF > 0.01 filter contained 5,877,249 SNPs. Baseline numerical QC passed for 66/66 files, and the five annotation/weight score families passed 330/330 ordered-universe checks. Formal EUR/EAS summary statistics were independently rebuilt in score order and passed 1/1 alignment gate with 3,112,573 shared rows.

The first-generation baseline score remains preserved and excluded under `INVALID_FOR_FORMAL_ANALYSIS_ROWSET_MISMATCH`. It was not referenced by the formal regression.

## Formal S-LDXR

metric: **GCORSQ — stratified squared trans-ancestry genetic correlation**  
estimate: **1.009945**  
SE: **0.108276**  
95% CI: **0.797725 to 1.222165**  
effective SNP N: **3,112,573**  
jackknife blocks: **200**  
warnings: **NONE**

Companion estimates retained under their official definitions were EAS `HSQ1 = 0.494264 ± 0.033137`, EUR `HSQ2 = 0.378800 ± 0.019862`, `GCOV = 0.435406 ± 0.022246`, and `GCOR = 1.006258 ± 0.053931` (95% CI 0.900553–1.111962).

GCOR and GCORSQ are unbounded software estimates and lie slightly above one. Their confidence intervals include one, and all block diagnostics remain close to the boundary. They are interpreted as boundary-adjacent estimates consistent with very high shared genetic effects, not as literal correlations greater than one.

## Stability

jackknife: **PASS**  
LOCO: **PASS as block-influence approximation; not an exact refit-based LOCO**  
largest influence: **chromosome 15 / block 164**

Across the 200 official leave-one-block estimates, GCORSQ ranged from 0.975796 to 1.033567. The largest shift was block 164 on chr15:26,211,385–44,081,143, with `|delta|/SE = 0.315`. No block was non-finite, sign-flipping or catastrophic.

S-LDXR has no direct leave-one-chromosome-out command. A clearly labelled first-order reconstruction from the official block influence statistics gave GCORSQ values from 0.966369 to 1.039377; chr15 had the largest shift (`|delta|/SE = 0.402`). No chromosome was catastrophic. This diagnostic is robustness QC and is not an exact LOCO refit.

## LDSC triangulation

EUR LDSC h2: **0.1219 ± 0.0072**  
EAS LDSC h2: **0.1494 ± 0.0119**  
compatible: **CONDITIONAL**

Both analyses yielded positive, finite and well-resolved signal. Direct numerical equality is not expected: the frozen S-LDXR analysis used allelic LD scores to estimate per-allele effect correlation, whereas standalone LDSC reported observed-scale heritability under standardized-genotype LD-score regression. This allele-frequency weighting distinction explains why S-LDXR HSQ is larger. The roughly three- to four-fold HSQ difference and the slight correlation-boundary overshoot remain the strongest reporting limitations.

The previously reported high EUR–EAS Popcorn genetic correlation was used only as a qualitative scale check. Popcorn and S-LDXR are not treated as the same estimator, and no parameter was tuned to match the published result.

## Annotation pilot

all retinal OCR: **estimable YES**  
GCORSQ = 0.935405 ± 0.101099; 95% CI 0.737250–1.133559; 713,105 MAF > 0.01 annotation SNPs.

ancestry-DAR: **estimable YES, numerically weak**  
usable SNP N: **1,232 shared formal SNPs**  
GCORSQ = 0.571191 ± 0.577063; 95% CI −0.559852–1.702234; 2,511 paired-panel annotation SNPs with MAF > 0.01.

matched non-DAR: **estimable YES**  
GCORSQ = 0.935585 ± 0.101018; 95% CI 0.737591–1.133580; 709,523 MAF > 0.01 annotation SNPs.

These are numerical-estimability pilots, not formal biological hypothesis tests. Their estimates must not be used to claim enrichment, depletion, mechanistic difference or equivalence.

## DAR power tier

**CONDITIONAL**

| DAR count | N |
|---|---:|
| Original unique intervals | 2,227 |
| Mapped unique intervals | 2,219 |
| Paired-panel SNPs | 2,697 |
| Shared usable formal SNPs | 1,232 |
| Paired-panel SNPs with MAF > 0.01 in both populations | 2,511 |
| Paired-panel SNPs with MAF > 0.05 in both populations | 1,916 |

The usable DAR scale falls within the pre-specified 1,000–5,000 conditional tier. The very large S-LDXR standard error confirms that global DAR S-LDXR is suitable only as confirmatory evidence. The DAR FDR threshold was not relaxed.

## Recommended Phase 2 route

**ROUTE B — heterogeneity-enrichment-led**

The recommended primary architecture is cross-ancestry heterogeneity followed by matched ancestry-DAR enrichment and a matched non-DAR retinal OCR comparator. Broad retinal OCR remains a positive control; genome-wide S-LDXR is architecture validation; global DAR S-LDXR is confirmatory. Cell-class enrichment is secondary, and locus/CRE/motif analysis remains gated behind the primary statistics.

The requested draft was created at `config/PHASE2_ANALYSIS_FREEZE_DRAFT_v2.yaml`. It is explicitly marked `DRAFT_NOT_EXECUTED` and does not authorize Phase 2 execution.

## Audit trail

- Formal freeze: `config/SLDXR_FORMAL_INPUT_FREEZE_v1.yaml`
- Invalid-input provenance: `reports/SLDXR_INVALID_BASELINE_PROVENANCE.md`
- Row identity: `results/phase1c/SLDXR_BASELINE_ROW_IDENTITY.tsv`
- Numerical QC: `results/phase1c/SLDXR_ALIGNED_BASELINE_NUMERICAL_QC.tsv`
- Score-universe QC: `results/phase1c/SLDXR_ALL_SCORE_UNIVERSE_ALIGNMENT.tsv`
- Formal result: `results/phase1c/SLDXR_GENOMEWIDE_EUR_EAS_FORMAL.tsv`
- Block jackknife: `results/phase1c/SLDXR_BLOCK_JACKKNIFE.tsv`
- Chromosome influence: `results/phase1c/SLDXR_LOCO_DIAGNOSTIC.tsv`
- LDSC triangulation: `reports/SLDXR_LDSC_TRIANGULATION.md`
- Global pilot: `results/phase1c/SLDXR_GLOBAL_ANNOTATION_PILOT.tsv`
- DAR power: `results/phase1c/SLDXR_DAR_POWER_COUNTS.tsv`
- S-LDXR version: commit `ab39882d692d9b0f528a0ea21103866dcd1dd2f8`
- Formal input freeze ID: `SLDXR_FORMAL_INPUT_FREEZE_v1:6da435f42faa40f20ecf4b0b1e48d70782224704c86a829fe1e73c5269250b0a`
