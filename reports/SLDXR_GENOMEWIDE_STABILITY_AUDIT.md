# S-LDXR genome-wide stability audit

**Input freeze:** `SLDXR_FORMAL_INPUT_FREEZE_v1:6da435f42faa40f20ecf4b0b1e48d70782224704c86a829fe1e73c5269250b0a`  
**Jackknife blocks:** 200  
**Effective regression SNPs:** 3,112,573  
**Stability gate:** `PASS`

The S-LDXR files named `pseudo_*` contain leave-one-block coefficient estimates. The table below propagates those coefficients through the official S-LDXR definitions for the genome-wide base annotation.

| Metric | Full estimate | SE | Min leave-block | Max leave-block | Largest block | Largest |Δ|/SE | Non-finite | Sign flips | Catastrophic blocks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HSQ1 | 0.494264 | 0.0331367 | 0.486773 | 0.499821 | 100 | 0.2261 | 0 | 0 | 0 |
| HSQ2 | 0.3788 | 0.019862 | 0.371425 | 0.381467 | 53 | 0.3713 | 0 | 0 | 0 |
| GCOV | 0.435406 | 0.0222462 | 0.423985 | 0.438234 | 164 | 0.5134 | 0 | 0 | 0 |
| GCOR | 1.00626 | 0.0539309 | 0.989163 | 1.01797 | 164 | 0.317 | 0 | 0 | 0 |
| GCORSQ | 1.00994 | 0.108276 | 0.975796 | 1.03357 | 164 | 0.3154 | 0 | 0 | 0 |

A block is flagged as catastrophic when its leave-block estimate is non-finite, changes sign relative to a non-zero full estimate, or differs from the full estimate by at least one full-estimate standard error. This is a pre-specified numerical stability rule, not a biological significance test.

For the official GCORSQ metric, the leave-block range is 0.975796 to 1.03357; the largest influence is block 164.

Detailed block-level results are in `results/phase1c/SLDXR_BLOCK_JACKKNIFE.tsv`.
