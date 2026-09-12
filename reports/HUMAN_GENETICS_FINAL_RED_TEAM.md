# Final red-team review

## Reviewer 1: statistical genetics

Major concern: S-LDXR GCORSQ estimates near or above one need bounded interpretation. Response: v1.2 states that boundary-adjacent estimates are unbounded estimator behavior and reports MAF > 0.05 as the method-standard threshold, with MAF > 0.01 as supporting analysis.

Major concern: The EUR-EAS heterogeneity statistic assumes zero covariance and source-effect comparability. Response: Methods define it as association-effect heterogeneity on the released source-effect scale and state the zero-covariance assumption. Residual overlap is listed as a limitation.

## Reviewer 2: human genetics/population genetics

Major concern: Ancestry-linked chromatin differences should not be interpreted as innate biological categories. Response: v1.2 uses ancestry labels as sampled-population descriptors and cites ancestry-reporting guidance. The interpretation stays at the statistical annotation level.

Major concern: AFR and other populations are absent from the formal test. Response: v1.2 restricts conclusions to EUR-EAS and states that other populations require larger and compatible resources.

## Reviewer 3: retinal genetics

Major concern: DARs are not mechanistically linked to refractive-error loci. Response: v1.2 avoids CRE-to-gene, motif, pathway and locus mechanism claims. Functional experiments are OUT_OF_SCOPE_FOR_CURRENT_STUDY because the existing analyses do not identify a large global DAR enrichment or a prioritized causal locus.

Major concern: Retina is only one component of refractive development. Response: v1.2 lists tissue and developmental-stage specificity as limitations.
