# PHASE 1C — Protocol Amendment

**Project:** Cross-ancestry genetic effects of refractive error × retinal regulatory architecture  
**Date:** 2026-09-06  
**Pre-amendment status:** Phase 1B `NO-GO`  
**Purpose:** build provenance rescue before any biological-coordinate analysis

## Amendment rationale

Phase 1B required explicit source-level assembly evidence for every released GWAS file. That criterion remains valid for the historical source-provenance record, but it prevented the project from using independent, reproducible variant-identity evidence before any retinal annotation-dependent or downstream biological analysis had been run.

Phase 1C therefore extends the accepted evidence hierarchy. It permits two separate adjudications:

1. **Raw released build:** whether the undocumented `CHR/POS` coordinates are empirically consistent with GRCh37 or GRCh38.
2. **Analysis coordinates:** whether downstream SNPs can be reconstructed from `rsID + allele identity` against a frozen, official, versioned reference and then used consistently with the LD reference.

This amendment does not state that Phase 1B was wrong. It adds an auditable rescue route while preserving `reports/PHASE1B_DECISION.md` as the historical record that source-level assembly evidence was unavailable at that time.

## Scope and constraints

- Phase 0 harmonization output and raw GWAS files remain unchanged.
- Raw `CHR/POS` will not be used for retinal overlap after this amendment unless the raw build is independently validated.
- Primary mapping will use an official NCBI dbSNP dual-assembly resource, not random web lookup, Ensembl web pages, or manual UCSC queries.
- Empirical raw-build validation will use assembly-informative autosomal biallelic SNPs whose GRCh37 and GRCh38 positions differ.
- A strong empirical build call requires at least 20,000 informative SNPs, chosen-assembly `CHR+POS` concordance ≥99.5%, allele-compatible concordance ≥99%, a clear alternative-assembly separation, chromosome-wide consistency, and independent holdout replication ≥99.5%.
- Reference anchoring will be evaluated separately for EUR and EAS using `rsID + allele pair`; raw coordinate concordance is not a substitute for allele anchoring.
- Downstream analysis may use `RAW_RELEASED_BUILD = SOURCE_UNRESOLVED` only if canonical reference anchoring passes and all later build/reference gates pass.
- No pathway enrichment, MAGMA, MR, PRS, TWAS/SMR, fine-mapped biological interpretation, motif analysis, CRE-to-gene analysis, or manuscript-result drafting is allowed in Phase 1C.

## Canonical coordinate rule

The canonical analysis build will follow the frozen formal LD reference. If the formal EUR/EAS LDSC and paired S-LDXR resources use the GRCh37/HapMap3 convention, the project will freeze `ANALYSIS_BUILD = GRCh37` and reconstruct GWAS coordinates from rsID and alleles. HRCA hg38 intervals will then be lifted to GRCh37 with an auditable chain file and retention QC.

## Gate order

1. GWAS rsID coverage and marker audit.
2. Official dual-assembly dbSNP resource acquisition and checksum validation.
3. Empirical raw-build concordance with discovery/holdout separation.
4. Canonical reference-anchored GWAS variant map.
5. LD-reference variant anchoring.
6. Only if the preceding gates pass: retina liftover, build-resolved SNP counts, formal ancestry-matched LDSC and genome-wide S-LDXR.

If any gate fails, the relevant result remains `BLOCKING` and no downstream biological interpretation is produced.

## Authoritative outputs

- `results/phase1c/GWAS_RSID_COVERAGE.tsv`
- `metadata/DBSNP_REFERENCE_MANIFEST.tsv`
- `results/phase1c/EMPIRICAL_BUILD_CONCORDANCE.tsv`
- `results/phase1c/EMPIRICAL_BUILD_BY_CHROMOSOME.tsv`
- `data/processed/reference_anchored/CANONICAL_VARIANT_MAP.parquet`
- `results/phase1c/LD_REFERENCE_VARIANT_ANCHORING.tsv`
- `results/phase1c/TRIANGULATED_VARIANT_VALIDATION.tsv`
- `reports/PHASE1C_BUILD_RESCUE_DECISION.md`
- `reports/AUTHOR_BUILD_QUERY_EMAIL.txt`
- `reports/PHASE1C_FINAL_DECISION.md`
