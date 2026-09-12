# GWAS source methods extraction

Status: COMPLETED FROM PUBLIC ARTICLE AND LOCAL RELEASE FILES

## Source

Cheng et al. 2026, *Nature Genetics*, DOI 10.1038/s41588-026-02576-0.

Local release metadata: `metadata/GWAS_METADATA.tsv`

Raw files:

- `data/raw/gwas/EUR_meta_no23andMe.fastGWAz`
- `data/raw/gwas/EAS_meta.fastGWAz`

## Extracted fields

| Field | EUR | EAS | Source provenance |
|---|---|---|---|
| Source sample size | 1,495,159 | 121,172 | Cheng et al. article abstract and study overview |
| Public file used here | `EUR_meta_no23andMe.fastGWAz` | `EAS_meta.fastGWAz` | Local metadata and raw files |
| 23andMe status | no-23andMe EUR public release used in this project | not applicable to EAS source file name | Local metadata; source paper includes 23andMe in full EUR discovery description |
| Source phenotype composition | Directly measured MSE, imputed MSE from age of spectacle wear, binary myopia and EHR-derived cohorts | Examination-based myopia, self-reported categorical myopia, high-myopia GWAS and biobank resources | Cheng et al. study-design section |
| Raw header | `SNP A1 A2 freq b se p N CHR POS z` | `SNP A1 A2 freq b se p N CHR POS z` | First line of local raw files |
| Allele definition | A1 coded/effect allele; A2 other allele | A1 coded/effect allele; A2 other allele | Local header and harmonization scripts |
| Effect columns | `b`, `se`, `z`, `p`, `N` | `b`, `se`, `z`, `p`, `N` | Local raw files |
| Effect-scale interpretation | beta-like source effect; raw phenotype-scale identity not fully source-proven across all contributing cohorts | beta-like source effect; raw phenotype-scale identity not fully source-proven across all contributing cohorts | Local metadata and phenotype-composition audit |
| Meta-analysis model | Source article reports sample-size-weighted meta-analysis for ancestry-stratified discovery | Source article reports sample-size-weighted meta-analysis for ancestry-stratified discovery | Cheng et al. results text |
| Genome build | Not explicitly declared in released GWAS files | Not explicitly declared in released GWAS files | Local build audit |
| Project build handling | dbSNP Build 151 adjudication; GRCh37.p13 anchoring | dbSNP Build 151 adjudication; GRCh37.p13 anchoring | `reports/GWAS_BUILD_EVIDENCE.md` |

## Manuscript consequence

The Methods should describe source GWAS composition and public release fields, but should not overclaim uniform raw beta scale across all EUR and EAS components. The heterogeneity analysis remains acceptable as a source-effect-scale matched enrichment screen with a Cochran-Q-equivalent statistic.

