# GWAS Genome Build Evidence Audit

**项目：** Cross-ancestry genetic effects of refractive error × retinal regulatory architecture  
**阶段：** Phase 1B — Blocking Issues Resolution  
**审计日期：** 2026-09-06  
**审计结论：** `UNRESOLVED` for all four released GWAS files  
**Blocking status：** `BLOCKING`

## Scope

本审计只确认 summary-statistics 文件的 genome build，不根据 SNP 坐标外观、rsID spot-check、染色体长度直觉或坐标匹配结果推断 build。审计优先检查现有项目记录、官方数据页、原始论文和补充方法；未发现能够把当前四份 released GWAS 明确归为 GRCh37 或 GRCh38 的来源级证据。

## Build evidence table

| Dataset | Ancestry | Build | Evidence tier | Source | Exact evidence | Confidence |
|---|---|---|---|---|---|---|
| RE EUR | EUR | `UNRESOLVED` | Tier 1–4 audit completed; no assembly declaration | [Yang Lab data page](https://yanglab.westlake.edu.cn/pubData/); [Nature Genetics article](https://doi.org/10.1038/s41588-026-02576-0); [Supplementary Information](https://media.springernature.com/original/springer-static/esm/art:10.1038%2Fs41588-026-02576-0/MediaObjects/41588_2026_2576_MOESM1_ESM.pdf) | Official data page identifies `EUR_meta_no23andMe` but does not state hg19/GRCh37 or hg38/GRCh38. The article and Supplementary Note describe cohort genotyping/imputation and reference panels, but do not declare the released summary-statistics assembly. The local raw header contains `CHR POS` but no build field. | `UNRESOLVED` |
| RE EAS | EAS | `UNRESOLVED` | Tier 1–4 audit completed; no assembly declaration | [Yang Lab data page](https://yanglab.westlake.edu.cn/pubData/); [Nature Genetics article](https://doi.org/10.1038/s41588-026-02576-0); [Supplementary Information](https://media.springernature.com/original/springer-static/esm/art:10.1038%2Fs41588-026-02576-0/MediaObjects/41588_2026_2576_MOESM1_ESM.pdf) | Official data page identifies `EAS_meta` but does not state a genome assembly. Supplementary Note states that several EAS cohorts were imputed to 1KGP3 or used ancestry-specific references; this identifies the imputation/reference population, not the coordinate assembly of the released meta-analysis file. The local raw header contains `CHR POS` but no build field. | `UNRESOLVED` |
| RE AFR | AFR | `UNRESOLVED` | Tier 1–4 audit completed; no assembly declaration | [Yang Lab data page](https://yanglab.westlake.edu.cn/pubData/); [Nature Genetics article](https://doi.org/10.1038/s41588-026-02576-0); [Supplementary Information](https://media.springernature.com/original/springer-static/esm/art:10.1038%2Fs41588-026-02576-0/MediaObjects/41588_2026_2576_MOESM1_ESM.pdf) | Official data page identifies `AFR_meta` but does not state a genome assembly. The article reports the AFR cohort composition and analysis, but no released-file build declaration was found. The local raw header contains `CHR POS` but no build field. | `UNRESOLVED` |
| Cross ancestry | EUR/EAS/AFR | `UNRESOLVED` | Tier 1–4 audit completed; no assembly declaration | [Yang Lab data page](https://yanglab.westlake.edu.cn/pubData/); [Nature Genetics article](https://doi.org/10.1038/s41588-026-02576-0); [official reconstruction script](https://yanglab.westlake.edu.cn/resources/publication_data/Chengfeifei/fixed_effect/fixed_effect_recreate.script) | Official data page identifies `Cross_ancestry_EUR_EAS_AFR_no23andMe`; the METAL reconstruction script specifies marker, allele, frequency, weight and effect columns but no genome assembly. The released local header contains `MarkerName` and alleles but no build field. | `UNRESOLVED` |

## Evidence audit by tier

### Tier 1 — official summary-statistics page and README

The official Yang Lab publication-data entry lists the four files and their roles:

- `Cross_ancestry_EUR_EAS_AFR_no23andMe`
- `EUR_meta_no23andMe`
- `EAS_meta`
- `AFR_meta`

The page does not state `hg19`, `GRCh37`, `hg38` or `GRCh38` for any of the four files. The official reconstruction script only contains the METAL column declarations and does not define a coordinate assembly.

### Tier 2 — original paper and Supplementary Methods

The main paper and Supplementary Note describe cohort-specific genotyping, imputation and LD references. They mention 1000 Genomes Phase 3, population-specific reference panels, UKB imputed-genotype LD references and ancestry-specific analyses. None of these statements is an explicit declaration of the genome assembly used for the released meta-analysis coordinates.

The Supplementary Information was checked for `hg19`, `hg38`, `GRCh37`, `GRCh38` and `genome build`; no matching assembly declaration was found.

### Tier 3 — GWAS Catalog / public metadata

The project metadata already records the publication DOI and official download URLs. A DOI-based GWAS Catalog search on 2026-09-06 did not return a matching record with build metadata. This does not provide positive build evidence.

### Tier 4 — limited file-level supporting checks

The local raw headers expose chromosome and position columns, but no assembly field. The current project record therefore remains:

`UNRESOLVED: source file and publication audit do not yet provide an explicit build`

No coordinate-based validation was promoted to a build call. The existing hg38 overlap counts are retained as Phase 0 coordinate diagnostics only and are not evidence of GWAS build.

## Decision

| Dataset | Final build call |
|---|---|
| EUR | `UNRESOLVED` |
| EAS | `UNRESOLVED` |
| AFR | `UNRESOLVED` |
| Cross ancestry | `UNRESOLVED` |

**Final analysis build:** not frozen.  
**Blocking issue:** yes.  
**Allowed next evidence:** an author/source README or download manifest that explicitly names the assembly, or auditable upstream coordinate provenance for each released file. The fact that a cohort used 1KGP3 for imputation is insufficient to assign GRCh37 or GRCh38 to the released summary-statistics coordinates.

## Consequences for Phase 1B

The priority order stops at the first blocking gate. The following steps were deliberately not run or generated from unresolved coordinates:

- retinal liftover;
- build-resolved annotation SNP counts;
- formal ancestry-matched LDSC;
- paired EUR–EAS S-LDXR reference audit and genome-wide run;
- annotation-level S-LDXR pilot;
- DAR matching feasibility based on build-resolved coordinates;
- Phase 2 analysis freeze draft.

The generic-reference LDSC values already present in Phase 0 remain diagnostic only and are not used to override this build block.

## Local audit inputs

- `metadata/GWAS_METADATA.tsv`
- `scripts/download/download_primary_resources.sh`
- `data/raw/gwas/EUR_meta_no23andMe.fastGWAz`
- `data/raw/gwas/EAS_meta.fastGWAz`
- `data/raw/gwas/AFR_meta.fastGWAz`
- `data/raw/gwas/Cross_ancestry_EUR_EAS_AFR_no23andMe`
- `reports/GWAS_DATA_AUDIT.md`
- `results/phase0/BUILD_HARMONIZATION.tsv`
