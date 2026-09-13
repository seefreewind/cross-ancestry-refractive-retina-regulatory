# Matched permutation logic audit

Final verdict: `PASS`.

The code permutes DAR/non-DAR annotation labels within matched strata. The manuscript wording has been corrected from case-label language to annotation-label language. The initial universe contains SNPs annotated as DAR or eligible matched non-DAR retinal OCRs, not the whole genome. Informative strata are strata containing both annotation labels; this retained 1,069 DAR SNPs and 59,215 matched non-DAR SNPs. Retinal OCR status is useful before filtering because 163 DAR SNPs are outside the broad OCR annotation and have no matched non-DAR OCR controls. After informative-strata filtering, the retained comparison is OCR-only, so the OCR-status variable is constant among retained informative strata but valid as part of the pre-filter matching definition.

| item                                        | definition                                                                    |      n |
|:--------------------------------------------|:------------------------------------------------------------------------------|-------:|
| initial permutation universe                | dar_global == 1 OR matched_non_dar_ocr == 1                                   | 380511 |
| initial DAR labels                          | case = dar_global                                                             |   1232 |
| initial matched non-DAR labels              | matched_non_dar_ocr == 1                                                      | 379279 |
| informative retained DAR labels             | strata containing both labels                                                 |   1069 |
| informative retained matched non-DAR labels | strata containing both labels                                                 |  59215 |
| informative strata                          | CHR, MAF decile, MAF-difference quintile, LD-score decile, retinal OCR status |    834 |
