# EUR no-23andMe sample-size audit

## Verdict

Use source-limited wording in the manuscript. The source study reported 1,495,159 EUR participants overall, but the public EUR summary-statistics file used here is the no-23andMe release and contains a variant-level `N` field. The public file should therefore be described as a no-23andMe public release with per-SNP effective sample size, not as a single-source N of 1,495,159.

## Audit table

| Field | Value |
|---|---|
| `full_source_EUR_N` | 1,495,159 |
| `23andMe_component_N` | 191,843, consisting of 106,086 cases and 85,757 controls in the source EUR binary-myopia component |
| `public_no23andMe_nominal_N` | 1,303,316 by arithmetic subtraction only; not promoted as an exact source-supported public-file N |
| `public_file_effective_N_definition` | Variant-level effective N from the released public EUR no-23andMe summary-statistics `N` column |
| `per_SNP_N_available_yes_no` | yes |
| `source_evidence` | Cheng et al. reported EUR n=1,495,159 overall and listed a EUR 23andMe component of 106,086 cases plus 85,757 controls. The local released file is named `EUR_meta_no23andMe.fastGWAz` and has columns `SNP A1 A2 freq b se p N CHR POS z`. Local scan: 5,590,053 rows; EUR per-SNP N min 100,160.0, mean 630,244.5, max 696,704.85. |
| `confidence` | High for source EUR total N, 23andMe component N, and per-SNP N availability; medium for nominal arithmetic no-23andMe N; low for treating any single nominal public N as the actual analysis N. |

## Manuscript wording to use

The source study included 1,495,159 EUR participants overall; the publicly released EUR summary statistics used here excluded 23andMe participants. The released file provided variant-level effective sample-size values, which were retained as the analysis sample-size information rather than replacing them with the full source EUR total.

## EAS check

The source study reported EAS n=121,172. The local public EAS file contains a per-SNP `N` field. Local scan: 4,739,897 rows; EAS per-SNP N min 10,487.49, mean 96,429.22, max 115,388.49. The manuscript should therefore distinguish source-level EAS total N from variant-level effective N in the analyzed file.
