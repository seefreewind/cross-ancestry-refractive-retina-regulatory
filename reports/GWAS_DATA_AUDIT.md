# GWAS data audit

## Scope

The primary Phase 0 inputs are the EUR and EAS ancestry-stratified refractive-error summary statistics from Cheng et al. (Nature Genetics, 2026; DOI: [10.1038/s41588-026-02576-0](https://doi.org/10.1038/s41588-026-02576-0)). AFR is retained as a secondary sensitivity dataset. A released cross-ancestry METAL file is registered for provenance but is not used as a substitute for ancestry-specific summary statistics.

Source data page: <https://yanglab.westlake.edu.cn/pubData/>.

## File integrity and schema

The three ancestry-stratified files are complete by the recorded remote byte counts and have reproducible SHA-256 checksums in `metadata/GWAS_METADATA.tsv`. The fastGWAz schema is:

`SNP A1 A2 freq b se p N CHR POS z`

All three files contain complete P values, alleles, allele frequencies, effective sample-size values, beta-like effects, standard errors and Z scores in the streamed audit. The source analysis code and the paper identify the released EUR/cross-ancestry resources as excluding 23andMe. The released cross-ancestry file is a METAL sample-size-weighted Z meta-analysis with columns `MarkerName Allele1 Allele2 Freq1 ... Zscore P-value ...`; it has no beta or standard-error columns and includes indels, so it is not used in the EUR/EAS beta harmonization.

## Streamed QC summary

| dataset | source rows | biallelic SNP rows | non-SNP/indel rows | ambiguous SNP rows | P < 5e-8 rows | duplicate rsID rows | duplicate CHR:POS rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| EUR | 5,590,053 | 5,260,419 | 329,634 | 813,247 | 28,219 | 218 | 491 |
| EAS | 4,739,897 | 4,324,533 | 415,364 | 671,853 | 1,756 | 1,026 | 2,162 |
| AFR | 9,519,284 | 8,765,891 | 753,393 | 1,353,959 | 63 | 1,498 | 2,117 |

The detailed machine-readable output is `results/phase0/GWAS_QC_SUMMARY.tsv`; P-value and MAF histograms are retained as QC sidecars under `results/phase0/`.

## Build and phenotype boundary

The raw GWAS headers do not state a genome build. The publication and source-file audit completed here do not provide sufficient explicit evidence to assign GRCh37 or GRCh38. This remains a blocking annotation issue because the retinal S12/S19 resources are explicitly hg38, whereas HRCA S20/S21 resources are explicitly hg19. No coordinate-based biological conclusion should be treated as validated until the GWAS build is resolved against an auditable source or reference check.

The released ancestry-stratified phenotype definition is a meta-analysis of refractive error/mean spherical equivalent across cohorts with study-specific definitions; AFR is described as a myopia case-control meta-analysis. These definitions are preserved in the metadata rather than collapsed into a single unqualified phenotype label.

## Decision relevance

The files are technically usable for EUR/EAS harmonization and LDSC input preparation, subject to build compatibility and reference-panel checks. They are not sufficient to justify cross-ancestry causal, clinical, or mechanistic claims on their own.
