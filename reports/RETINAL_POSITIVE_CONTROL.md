# Retinal annotation positive-control audit

## Coordinate diagnostic

Using the current EUR/EAS harmonized table as a coordinate diagnostic, the hg38 HRCA union OCR table contains 700,146 intervals and overlaps 410,516 of 3,262,168 harmonized SNPs. The S19 ancestry-DAR union contains 2,227 unique intervals and overlaps 1,466 harmonized SNPs. Among the coordinate-overlapping SNPs, 2,980 EUR and 230 EAS SNPs pass P < 5 × 10⁻⁸ in the broad OCR union; 13 EUR and 3 EAS SNPs fall in the S19 ancestry-DAR union.

These are not validated biological enrichment results because the GWAS build remains unresolved. They are retained to verify that the annotation files parse, use chromosome labels consistently and produce non-empty intersections.

## Positive-control interpretation

The broad retinal OCR overlap is a successful technical positive control for the coordinate-intersection pipeline. A formal enrichment positive control is **not declared** in Phase 0: the stable non-DAR set is much larger than the S19 DAR union and requires chromosome-, MAF-, width- and genomic-background-matched nulls after GWAS build resolution. No result is interpreted as evidence that refractive-error loci are enriched in ancestry-sensitive retinal regulatory elements at this stage.

Machine-readable counts are in `results/phase0/RETINAL_ANNOTATION_QC.tsv`. The overlap status is `CONDITIONAL_BUILD_UNRESOLVED` until the GWAS build is resolved and the coordinate intersection is repeated against a validated reference.
