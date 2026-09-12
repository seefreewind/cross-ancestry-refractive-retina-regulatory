# Final figure/table restructuring QA

## Figure contract

| Panel     | Archetype                | Unique claim                                       | Check                                                                                        | Pass   |
|:----------|:-------------------------|:---------------------------------------------------|:---------------------------------------------------------------------------------------------|:-------|
| Figure 1  | schematic-led composite  | Data → analytical framework → scientific questions | No panel labels; balanced horizontal boxes; validation footer only                           | yes    |
| Figure 2  | quantitative forest      | Genome-wide and broad retinal-OCR sharing          | DAR S-LDXR removed from main figure; primary vs sensitivity hierarchy encoded by size/weight | yes    |
| Figure 3A | dot comparison           | Top-5% heterogeneity proportions                   | Dot comparison avoids bar-height exaggeration                                                | yes    |
| Figure 3B | forest effect            | Primary top-5% OR                                  | OR=1 reference shown; estimate and P directly labeled                                        | yes    |
| Figure 3C | permutation distribution | Matched permutation support                        | Observed statistic and two-sided tail shading displayed                                      | yes    |
| Figure 3D | precision axis           | Effect-size precision                              | CI, MDE markers and OR=1.5 boundary shown without equivalence language                       | yes    |
| Figure S1 | quantitative forest      | Descriptive DAR S-LDXR                             | Separated as underpowered descriptive estimate                                               | yes    |

## Export contract

- PDF, SVG and 600-dpi PNG were exported for every final figure.
- Ambiguous main-table `SNP_N` labels were removed or relabeled.
- Original Figure 4 files were copied to `figures/archive/` with `_original` suffix.
