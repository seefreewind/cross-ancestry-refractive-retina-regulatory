# EUR–EAS Effect Direction Audit

This is a QC sanity check, not formal genetic correlation. EAS z-scores were aligned to the EUR A1 allele using the CHR:POS harmonization table. Palindromic SNPs were excluded from the primary harmonized set.

The last row uses a 250-kb position-based lead selection because a validated ancestry-specific LD reference was not yet available in Phase 0; it must not be described as LD-independent.

| set                                           |       n |   pearson_r |   spearman_r |   same_direction_n |   same_direction_fraction |   same_direction_binom_p_two_sided |
|:----------------------------------------------|--------:|------------:|-------------:|-------------------:|--------------------------:|-----------------------------------:|
| all_shared_nonpalindromic                     | 3262168 |    0.204581 |     0.146358 |            1770295 |                  0.542674 |                        0           |
| EUR_genomewide_significant_in_EAS             |   20104 |    0.754441 |     0.741274 |              17192 |                  0.855153 |                        0           |
| EAS_genomewide_significant_in_EUR             |    1435 |    0.859956 |     0.764717 |               1393 |                  0.970732 |                        0           |
| position_based_250kb_leads_not_LD_independent |     546 |    0.599834 |     0.597474 |                435 |                  0.796703 |                        2.66965e-46 |
