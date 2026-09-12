# OR 1.5 timing audit

## Verdict

PASS as a prespecified robustness boundary. Use the phrase “prespecified robustness boundary” or “large-enrichment boundary” in manuscript-facing text. Do not call it a preregistered boundary or a primary endpoint.

## Evidence

| Evidence item | Finding |
|---|---|
| Configuration source | `config/PHASE2B_ROBUSTNESS_FREEZE_v1.yaml` |
| Recorded status | `POST_PRIMARY_ROBUSTNESS_EXECUTION_AUTHORIZED_2026-09-12` |
| Boundary field | `large_enrichment_boundary_OR: 1.5` |
| Precision output | `results/phase2b/EQUIVALENCE_BOUNDARY.tsv` |
| Observed primary OR | 1.119047 |
| 95% CI | 0.867496 to 1.423387 |
| Boundary result | The 95% CI upper bound is below OR = 1.5 |

## Interpretation

The OR = 1.5 boundary was fixed before the effect-precision/equivalence-boundary output was generated, but after the primary DAR enrichment result existed. It is therefore valid as a robustness-boundary interpretation of precision, not as the original primary hypothesis.
