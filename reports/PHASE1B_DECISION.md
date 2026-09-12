# PHASE 1B VERDICT

## Overall verdict

**NO-GO**

Phase 1B stopped at the first blocking gate because the genome build of the released EUR, EAS, AFR and cross-ancestry GWAS files remains unresolved after source-level audit. No later coordinate-dependent or reference-dependent result was promoted to formal status.

## 1. GWAS build

EUR: `UNRESOLVED`  
EAS: `UNRESOLVED`  
AFR: `UNRESOLVED`  
Cross-ancestry: `UNRESOLVED`  

Evidence confidence: `UNRESOLVED` for all four datasets. Official data-page, paper, Supplementary Information, reconstruction-script and available public-metadata checks did not provide an explicit GRCh37/GRCh38 declaration.  

Final analysis build: **not frozen**  

Verdict: **FAIL — BLOCKING**

Full evidence is recorded in `reports/GWAS_BUILD_EVIDENCE.md`.

## 2. Retina build harmonization

S12 OCR:  
original N: 700,146 intervals  
lifted N: **NOT RUN — stopped after GWAS build gate**  
retention: **NOT available**

S19 ancestry-DAR:  
original N: 2,227 unique intervals  
lifted N: **NOT RUN — stopped after GWAS build gate**  
retention: **NOT available**

Verdict: **NOT ASSESSED**

The existing hg38 S12/S19 overlap numbers remain Phase 0 coordinate diagnostics and are not biological results.

## 3. Formal ancestry-matched LDSC

### EUR

h2: **NOT RUN**  
SE: **NOT RUN**  
Z: **NOT RUN**  
intercept: **NOT RUN**  
mean chi-square: **NOT RUN**  
SNP N: **NOT RUN**  
reference: **not adjudicated; ancestry-matched formal run blocked by unresolved build**

Verdict: **NOT CLEARED**

Existing generic-reference diagnostic: h2 = 0.0904, SE = 0.0046, Z = 19.65. This is not a formal ancestry-matched result.

### EAS

h2: **NOT RUN**  
SE: **NOT RUN**  
Z: **NOT RUN**  
intercept: **NOT RUN**  
mean chi-square: **NOT RUN**  
SNP N: **NOT RUN**  
reference: **not adjudicated; ancestry-matched formal run blocked by unresolved build**

Verdict: **NOT CLEARED**

Existing generic-reference diagnostic: h2 = 0.1069, SE = 0.0081, Z = 13.20. This is not a formal ancestry-matched result.

## 4. Genome-wide S-LDXR EUR–EAS

GCOR² / official metric: **NOT RUN**  
SE: **NOT RUN**  
SNP N: **NOT RUN**  
jackknife: **NOT RUN**  
warnings: **BLOCKED — GWAS build unresolved; paired reference not adjudicated**

Verdict: **FAIL / NOT CLEARED**

The existing S-LDXR summary-statistics inputs are retained. No formal EUR–EAS GCOR² exists.

## 5. Build-resolved retinal annotations

All retinal OCR:  
N intervals: 700,146 original hg38 intervals  
N usable EUR–EAS SNPs: **NOT available after build resolution**

Ancestry-DAR:  
N intervals: 2,227 original hg38 intervals  
N usable EUR–EAS SNPs: **NOT available after build resolution**

Matched non-DAR pool:  
N intervals: 697,837 original operational comparator intervals  
N usable SNPs: **NOT available after build resolution**

The Phase 0 diagnostic values of 410,516 broad OCR coordinate-diagnostic SNPs and approximately 1,466 ancestry-DAR coordinate-diagnostic SNPs are not used for Phase 1B adjudication.

## 6. DAR power tier

**CONDITIONAL — provisional only**

The unresolved-build diagnostic of approximately 1,466 ancestry-DAR coordinate-diagnostic SNPs falls in the 1,000–5,000 conditional range, but this is not a build-resolved power tier. The final tier cannot be assigned until a unified build is documented and the annotations are lifted or otherwise harmonized.

## 7. Recommended Phase 2 architecture

**ROUTE C — NO-GO / redesign pending build evidence**

The project should not enter Phase 2. If an auditable GWAS build is later obtained and the downstream gates pass, the Phase 2 route will be reassessed; no ROUTE A or ROUTE B selection is valid at the current state.

## Required conditions to reopen Phase 1B

1. Obtain explicit source-level build evidence for EUR, EAS, AFR and cross-ancestry files.
2. Freeze one analysis build and record the chain file and SHA256 if liftover is needed.
3. Re-run the downstream gates in the prescribed order without changing the established GWAS files or harmonization output.

## Files generated or updated in this decision

- `reports/GWAS_BUILD_EVIDENCE.md`
- `reports/PHASE1B_DECISION.md`
- `metadata/GWAS_METADATA.tsv`

No `config/PHASE2_ANALYSIS_FREEZE_DRAFT_v1.yaml` was generated because the verdict is `NO-GO`.
