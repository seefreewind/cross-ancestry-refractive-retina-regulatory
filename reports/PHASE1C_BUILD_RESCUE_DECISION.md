# Phase 1C Build-Rescue Decision

**Project:** Cross-ancestry genetic effects of refractive error × retinal regulatory architecture  
**Decision date:** 2026-09-08  
**Historical Phase 1B status:** `NO-GO` because source-level GWAS genome assembly was not explicitly documented  
**Phase 1C decision:** `RESCUED_FOR_REFERENCE-ANCHORED_ANALYSIS`

## Authoritative build state

```text
RAW_RELEASED_BUILD        = SOURCE_UNRESOLVED
EMPIRICAL_BUILD_ADJUDICATION = GRCh37_STRONG
ANALYSIS_BUILD            = GRCh37.p13
ANALYSIS_COORDINATES      = REFERENCE_ANCHORED_GRCh37_PASS
```

The source release still does not provide an explicit assembly declaration. The raw `CHR/POS` fields are nevertheless empirically consistent with GRCh37 using an independent NCBI dbSNP Build 151 dual-assembly reference. Downstream coordinates are therefore reconstructed from `rsID + allele pair` against the frozen GRCh37.p13 reference. The historical `reports/PHASE1B_DECISION.md` is unchanged.

## Gate 1 — GWAS rsID coverage

All four released GWAS files contain valid rsIDs for every parsed marker:

| Dataset | Total variants | Valid rsIDs | rsID coverage | Gate |
|---|---:|---:|---:|---|
| EUR | 5,590,053 | 5,590,053 | 100.000000% | PASS |
| EAS | 4,739,897 | 4,739,897 | 100.000000% | PASS |
| AFR | 9,519,284 | 9,519,284 | 100.000000% | PASS |
| CROSS | 9,555,806 | 9,555,806 | 100.000000% | PASS |

The biallelic-SNP fraction among valid-rsID markers is reported separately in `results/phase1c/GWAS_RSID_COVERAGE.tsv`; it is not used as the rsID-coverage denominator.

## Gate 2 — Official reference resources

The following NCBI dbSNP Build 151 common-SNP VCFs and tabix indexes were downloaded and checksum verified:

- GRCh37.p13: `common_all_20180423.vcf.gz`, MD5 `29b5ddb6f4da121de8fcfd061dc9000c`
- GRCh38.p7: `common_all_20180418.vcf.gz`, MD5 `a274dcecff9cfe6084eaef848080ad8d`

The complete resource manifest is `metadata/DBSNP_REFERENCE_MANIFEST.tsv`.

## Gate 3 — Empirical build adjudication

The audit used deterministic hash-selected autosomal biallelic SNP samples with independent holdout subsets. Every dataset contributed more than 20,000 informative SNPs.

| Dataset | Informative SNPs | Assembly | chr+pos concordance | Allele-compatible concordance | Holdout chr+pos concordance |
|---|---:|---|---:|---:|---:|
| EUR | 124,171 | GRCh37 | 100.000000% | 100.000000% | 100.000000% |
| EUR | 124,171 | GRCh38 | 0.907619% | 100.000000% | 0.903138% |
| EAS | 123,288 | GRCh37 | 100.000000% | 100.000000% | 100.000000% |
| EAS | 123,288 | GRCh38 | 0.936831% | 100.000000% | 0.938118% |
| AFR | 127,175 | GRCh37 | 100.000000% | 100.000000% | 100.000000% |
| AFR | 127,175 | GRCh38 | 0.974248% | 100.000000% | 1.027042% |

GRCh37 satisfies the required informative-SNP count, chosen-assembly thresholds, holdout threshold, and chromosome-wide consistency. Across all 22 autosomes and all three ancestry-specific files, GRCh37 chromosome-plus-position concordance ranged from 100% to 100%, with no chromosome below 99.5%. GRCh38 is clearly worse for coordinate concordance despite allele compatibility because rsIDs and alleles identify the same variants while the released coordinates match GRCh37.

## Gate 4 — Canonical reference anchoring

The canonical map contains all 3,262,168 rows of `data/processed/EUR_EAS_HARMONIZED.parquet`. Mapping uses rsID and allele compatibility against dbSNP GRCh37.p13; raw coordinates are retained as audit fields and are not the identity key.

| Target set | Total | Unique rsID+allele anchored | Anchoring rate | Gate |
|---|---:|---:|---:|---|
| EUR/EAS harmonized GWAS | 3,262,168 | 3,261,022 | 99.964870% | STRONG |
| Generic LDSC HapMap3 | 1,190,321 | 1,190,048 | 99.977065% | STRONG |

The GWAS map contains 1,146 rows with `MISSING_RSID_PLACEMENT`; these rows remain explicitly represented and are not silently dropped. Among anchored variants, 1,765,932 require allele-order flipping and 1,495,090 retain the original allele order; no strand-resolved matches were required in this map.

## Decision and allowed next step

Phase 1C provenance rescue passes. The project may proceed with retina interval liftover and build-resolved SNP counts using the frozen GRCh37.p13 canonical coordinates. Formal ancestry-matched LDSC and genome-wide S-LDXR may proceed only with the corresponding ancestry-matched LD/weight bundles and their own completeness/QC checks.

This decision does not convert the undocumented source release into a source-level GRCh37 declaration. It authorizes a reproducible reference-anchored analysis state while preserving the distinction between released-source provenance and analysis-coordinate provenance.

## Phase 1C outputs

- `results/phase1c/GWAS_RSID_COVERAGE.tsv`
- `results/phase1c/EMPIRICAL_BUILD_CONCORDANCE.tsv`
- `results/phase1c/EMPIRICAL_BUILD_BY_CHROMOSOME.tsv`
- `results/phase1c/LD_REFERENCE_VARIANT_ANCHORING.tsv`
- `data/processed/reference_anchored/CANONICAL_VARIANT_MAP.parquet`
- `metadata/DBSNP_REFERENCE_MANIFEST.tsv`
- `reports/AUTHOR_BUILD_QUERY_EMAIL.txt`
