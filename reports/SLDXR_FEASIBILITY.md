# S-LDXR feasibility audit

## Target estimand

The requested estimand is the stratified squared trans-ancestry genetic-correlation enrichment, λ²(C), for EUR versus EAS refractive-error summary statistics. S-LDXR requires ancestry-paired summary statistics, ancestry-matched allele-frequency files, trans-ancestry LD scores, regression weights and SNP annotations. Ordinary LDSC baselineLD files alone are not equivalent to the S-LDXR input because S-LDXR uses paired reference-panel LD scores for the two ancestries.

## Software

The public S-LDXR repository was cloned at:

`/Users/zy/.codex/tools/s-ldxr`

Repository commit: `ab39882d692d9b0f528a0ea21103866dcd1dd2f8`

The current code is version 0.3-beta lineage and was developed for an older Python/dependency stack. A direct Python 3 smoke import initially failed because `pysnptools` was absent. The current environment requires a dedicated compatible environment before production execution; no S-LDXR estimate is reported in Phase 0.

## Reference-panel requirement

The official workflow requires matched EUR and EAS PLINK reference panels, chromosome-wise paired LD scores, regression weights, ancestry-specific MAF files, and annotation files. The public S-LDXR reference directory identified by the software documentation is now requester-pays on Google Cloud and cannot be treated as freely available without a billing project. The project has begun downloading public 1000 Genomes EUR/EAS PLINK and LDSC resources from the Zenodo mirror, but standard LDSC resources do not by themselves satisfy the full S-LDXR paired-LD-score requirement.

## Input and annotation audit

The EUR/EAS harmonized table contains 3,262,168 non-palindromic shared SNPs before any reference-panel or S-LDXR MAF filter. In the explicit S-LDXR input schema, the source-level filtered files contain 4,447,171 EUR SNPs and 3,652,675 EAS SNPs before paired-LD intersection and the software's MAF filter. HRCA S12/S19 annotation coordinates are hg38; the GWAS build remains unresolved. Consequently, the final S-LDXR SNP count after build-validated intersection and MAF filtering is not yet reportable.

The recommended annotation sequence is: genome-wide baseline annotation, HRCA stable non-DAR OCR control, global S19 ancestry-DAR union, then cell-class/ancestry-specific S19 DAR annotations. Each annotation must be generated on the same SNP set used to compute the paired LD scores.

## Current verdict

**Conditional feasibility; production S-LDXR is not yet cleared.** The estimand and software are identifiable, and the harmonized input size is adequate for a dry-run. Two conditions remain: resolve the GWAS build and either obtain the requester-pays S-LDXR resources or generate paired EUR/EAS LD scores and weights from auditable 1000 Genomes PLINK panels in a compatible environment. Do not replace S-LDXR with ordinary LDSC and label the result λ²(C).
