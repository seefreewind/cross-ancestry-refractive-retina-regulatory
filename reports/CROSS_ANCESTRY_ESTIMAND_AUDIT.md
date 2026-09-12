# Cross-ancestry estimand audit

Final verdict: POPCORN VS S-LDXR EXPLAINED

## Why this audit was needed

Cheng et al. 2026 reported cross-ancestry sharing for refractive error using Popcorn. The current manuscript uses S-LDXR GCOR and GCORSQ. These quantities should not be compared numerically as if they were the same estimator.

## Estimand comparison

| Method | Quantity | Squared? | Allele scaling | LD model | Functional annotations | Interpretation |
|---|---|---:|---|---|---|---|
| Popcorn genetic-impact correlation | Correlation of causal variant genetic impacts across populations | No | Impact-scale; incorporates allele-frequency/genotype-variance scaling | Popcorn model with ancestry-specific LD information | No stratified functional annotation by default | Broad cross-population sharing of genetic impact |
| Popcorn genetic-effect correlation | Correlation of causal variant effect sizes across populations | No | Effect-scale | Popcorn model with ancestry-specific LD information | No stratified functional annotation by default | Broad cross-population sharing of effect sizes |
| S-LDXR GCOR | Stratified trans-ancestry genetic correlation | No | Per-allele effect modeling; accounts for population MAF differences | Cross-population LD-score regression with ancestry-matched LD and weights | Yes | Annotation-aware cross-population sharing |
| S-LDXR GCORSQ | Stratified squared trans-ancestry genetic correlation | Yes | Per-allele effect modeling; reported as squared correlation metric | Cross-population LD-score regression with ancestry-matched LD and weights | Yes | Squared sharing metric used for stratified annotation context |

## Interpretation for this manuscript

Cheng et al. reported Popcorn genetic-impact correlation of 0.80 ± 0.03 between EUR and EAS. The current project estimated S-LDXR genome-wide GCORSQ near 1. These values are not a replication-discrepancy pair because they use different effect scaling, different model assumptions and, for GCORSQ, a squared metric.

The correct manuscript claim is qualitative:

> Published Popcorn and current S-LDXR analyses both support substantial broad EUR-EAS sharing for refractive error, but their numerical estimates should not be directly equated.

