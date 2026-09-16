# Final retinal set identity audit

| Set                                     |       N | Definition                                                                                       | Source file/script                                                                                          |
|:----------------------------------------|--------:|:-------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------|
| Broad retinal OCR                       | 380,615 | Union retinal open-chromatin annotation in formal analysis overlap                               | data/processed/phase2/EUR_EAS_HETEROGENEITY_FEATURES.parquet; scripts/annotation/build_sldxr_annotations.py |
| Ancestry-associated DAR total           |   1,232 | Source-defined ancestry-associated DAR annotation intersecting formal analysis SNP universe      | data/processed/phase2/EUR_EAS_HETEROGENEITY_FEATURES.parquet                                                |
| DAR in broad OCR                        |   1,069 | DAR SNPs with broad retinal OCR membership                                                       | data/processed/phase2/EUR_EAS_HETEROGENEITY_FEATURES.parquet                                                |
| DAR outside broad OCR                   |     163 | Source-defined DAR SNPs outside the union-OCR annotation                                         | data/processed/phase2/EUR_EAS_HETEROGENEITY_FEATURES.parquet                                                |
| OCR non-DAR interval exclusions         |     267 | OCR non-DAR SNPs removed by interval-level comparator filtering after DAR exclusion              | results/final_qc/NONDAR_COUNT_RECONCILIATION.tsv; scripts/annotation/build_sldxr_annotations.py             |
| Eligible non-DAR retinal OCR comparator | 379,279 | Retinal OCR comparator SNPs retained after DAR exclusion and interval-level comparator filtering | data/processed/phase2/EUR_EAS_HETEROGENEITY_FEATURES.parquet                                                |

Count identity: `380,615 - 1,069 - 267 = 379,279`.

Final verdict: `PASS`.
