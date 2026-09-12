# S-LDXR–LDSC triangulation

## Decision

**Triangulation status: `CONDITIONAL_COMPATIBLE`**

The frozen genome-wide S-LDXR baseline completed on 3,112,573 shared regression SNPs. It estimated EAS `HSQ1 = 0.4943 ± 0.0331`, EUR `HSQ2 = 0.3788 ± 0.0199`, `GCOR = 1.0063 ± 0.0539`, and analytically bias-corrected `GCORSQ = 1.0099 ± 0.1083`. The 200-block jackknife passed, and no block or chromosome-level block-influence approximation was catastrophic.

The standalone ancestry-matched LDSC estimates were EUR observed-scale SNP heritability `0.1219 ± 0.0072` and EAS observed-scale SNP heritability `0.1494 ± 0.0119`. Both methods therefore return positive, finite, well-resolved genetic signal, but the S-LDXR HSQ values are substantially larger.

## Quantity compatibility

The numerical HSQ values are not treated as direct replications of the LDSC values. The frozen S-LDXR analysis uses **allelic LD scores**, which the installed S-LDXR documentation recommends for per-allele effect correlation. The standalone LDSC analysis reports observed-scale heritability under standardized-genotype LD-score regression. Allelic-scale S-LDXR HSQ and standardized-genotype LDSC heritability differ in weighting by allele-frequency-dependent genotype variance; exact equality is not expected.

This scale distinction explains why the S-LDXR HSQ values cannot be compared to the LDSC values by subtraction or ratio. The comparison is limited to sign, finiteness, order of magnitude, and evidence of pathological instability. There is no negative estimate, non-finite standard error, extreme intercept, or jackknife collapse. The S-LDXR heritability values remain below one, although they are roughly three to four times the standalone LDSC values.

## Boundary behavior of the cross-ancestry estimate

The unbounded S-LDXR point estimates are slightly above the natural correlation boundary: `GCOR = 1.0063` and `GCORSQ = 1.0099`. The excess is small relative to uncertainty; the 95% intervals are `0.9006–1.1120` and `0.7977–1.2222`, respectively. Leave-one-block GCOR ranged from `0.9892` to `1.0180`, and GCORSQ ranged from `0.9758` to `1.0336`. The chromosome block-influence approximation also showed no catastrophic dominance. These outputs are interpreted as boundary-adjacent estimates consistent with very high shared genetic effects, not as literal correlations greater than one.

The published Popcorn result is used only as a qualitative sanity check that EUR–EAS genetic correlation was reported to be high. Popcorn and the current S-LDXR analysis estimate different quantities and use different modeling assumptions; no parameter was selected to reproduce the published result.

## Gate conclusion

The triangulation is conditionally compatible: direction and broad scale are coherent, while direct numerical agreement is not expected because the heritability quantities use different effect-size scales. The small boundary overshoot is fully covered by the jackknife uncertainty and is stable across blocks. It is retained as the main limitation and must be reported wherever the baseline result is summarized.

This audit supports treating the genome-wide baseline as technically passing for the narrowly defined purpose of testing whether the three pre-specified global retinal annotations are numerically estimable. It does not authorize biological interpretation, cell-type S-LDXR, or Phase 2 analyses.
