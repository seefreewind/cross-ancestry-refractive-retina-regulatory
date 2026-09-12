# S-LDXR MAF method audit

Final verdict: REQUIRES_0.05_SENSITIVITY

## Official citation

Shi H, Gazal S, Kanai M, Koch EM, Schoech AP, et al. 2021. Population-specific causal disease effect sizes in functionally important regions impacted by selection. *Nature Communications* 12:1098. DOI: 10.1038/s41467-021-21286-1.

## Official repository and version

Repository inspected locally: `/Users/zy/.codex/tools/s-ldxr`

Git commit: `ab39882d692d9b0f528a0ea21103866dcd1dd2f8`

Local documentation inspected:

- `/Users/zy/.codex/tools/s-ldxr/README.md`
- `/Users/zy/.codex/tools/s-ldxr/docs/gcorsq.md`
- `/Users/zy/.codex/tools/s-ldxr/docs/input_format.md`
- `/Users/zy/.codex/tools/s-ldxr/s-ldxr.py`

## Exact method wording and cutoff evidence

The S-LDXR paper describes the analyzed regression and heritability SNPs as HapMap3 SNPs with MAF greater than 5% in both EAS and EUR populations. The paper also states that the method models per-allele effect sizes while accounting for MAF differences between populations.

The local S-LDXR command-line implementation exposes `--min-maf` as an argument and sets its default to 0.05:

```text
--min-maf ... default=0.05 ... Minimum MAF for performing the estimation
```

## Current project cutoff

The project v1.0 S-LDXR input freeze used:

```text
score_filter: MAF_EAS>0.01 and MAF_EUR>0.01
formal_estimation_min_maf: 0.01
```

This is recorded in `config/SLDXR_FORMAL_INPUT_FREEZE_v1.yaml`.

## Method-compliance decision

MAF = 0.01 is technically accepted by the software through `--min-maf`, but it is not the official default and is not the method threshold described for the original S-LDXR applications. The manuscript should not present 0.01 as the standard S-LDXR method cutoff.

## Reviewer-style 0.05 sensitivity

A reviewer-style sensitivity analysis was run with the same summary statistics, reference scores, annotations, weights, intercept settings, shrinkage and 200 jackknife blocks, changing only `--min-maf` from 0.01 to 0.05.

Output: `results/presubmission/SLDXR_MAF_SENSITIVITY.tsv`

| Analysis | MAF threshold | SNP N | GCORSQ | SE | 95% CI | Interpretation |
|---|---:|---:|---:|---:|---|---|
| Genome-wide | 0.01 | 3,112,573 | 1.009945 | 0.108276 | 0.797725–1.222165 | Boundary-adjacent high sharing |
| All retinal OCR | 0.01 | 380,615 | 0.935405 | 0.101099 | 0.737250–1.133559 | Broadly compatible with genome-wide sharing |
| Genome-wide | 0.05 | 3,112,573 | 1.027596 | 0.099604 | 0.832373–1.222820 | Boundary-adjacent high sharing |
| All retinal OCR | 0.05 | 544,077 | 0.947606 | 0.096926 | 0.757631–1.137582 | Broadly compatible with genome-wide sharing |

## Does MAF = 0.05 materially change the shared-architecture conclusion?

NO.

The 0.05 sensitivity preserves the broad inference that EUR-EAS refractive-error architecture is highly shared genome-wide and broadly compatible with shared architecture in retinal OCRs. v1.1 should report the primary project results and state that the standard-threshold sensitivity supported the same conclusion.

