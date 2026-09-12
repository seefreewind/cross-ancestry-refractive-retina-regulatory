# Large-effect boundary audit

Final verdict: PASS AS PRESPECIFIED ROBUSTNESS BOUNDARY

## Question

Can OR = 1.5 be described as prespecified?

## Evidence inspected

1. `config/PHASE2B_ROBUSTNESS_FREEZE_v1.yaml`
2. `results/phase2b/EQUIVALENCE_BOUNDARY.tsv`
3. `results/phase2b/PRIMARY_EFFECT_SIZE_PRECISION.tsv`
4. `reports/PHASE2B_FINAL_DECISION.md`

## Findings

The Phase 2B robustness freeze lists `large_enrichment_boundary_OR: 1.5` under effect precision. The freeze status is `POST_PRIMARY_ROBUSTNESS_EXECUTION_AUTHORIZED_2026-09-12`, after the primary DAR enrichment result but before the Phase 2B effect-precision output was generated.

The primary effect estimate was OR = 1.119 with 95% CI = 0.867–1.423. The upper confidence limit is below OR = 1.5.

## Interpretation

OR = 1.5 can be called a prespecified robustness boundary, not an externally preregistered boundary and not a primary endpoint.

Allowed:

> The confidence interval excludes an enrichment as large as OR = 1.5 under the prespecified robustness boundary.

Avoid:

> Equivalence was established.

Avoid:

> The OR = 1.5 boundary was preregistered.

