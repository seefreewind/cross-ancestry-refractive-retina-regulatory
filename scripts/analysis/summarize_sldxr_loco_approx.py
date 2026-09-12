#!/usr/bin/env python3
"""Create a clearly labelled chromosome-influence approximation from S-LDXR blocks.

The upstream S-LDXR command-line interface accepts a contiguous chromosome range
but has no leave-one-chromosome-out switch. This diagnostic therefore sums the
first-order influence contributions of the official 200 leave-one-block fits.
It must not be presented as an exact refit-based LOCO analysis.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[2]
S_LDXR_REPO = Path(os.environ.get("S_LDXR_REPO", "s-ldxr"))
sys.path.insert(0, str(S_LDXR_REPO))

from src.estimation import create_block  # noqa: E402


FREEZE = ROOT / "config/SLDXR_FORMAL_INPUT_FREEZE_v1.yaml"
FORMAL = ROOT / "results/phase1c/SLDXR_GENOMEWIDE_EUR_EAS_FORMAL.tsv"
BLOCKS = ROOT / "results/phase1c/SLDXR_BLOCK_JACKKNIFE.tsv"
SUMSTATS = ROOT / "data/interim/sldxr_formal/EAS_sumstats_aligned.gz"
OUT = ROOT / "results/phase1c/SLDXR_LOCO_DIAGNOSTIC.tsv"


def main() -> None:
    freeze = yaml.safe_load(FREEZE.read_text())
    nblocks = int(freeze["jackknife_blocks"])
    formal = pd.read_csv(FORMAL, sep="\t").set_index("metric_name")
    block_results = pd.read_csv(BLOCKS, sep="\t")
    keys = pd.read_csv(SUMSTATS, sep=r"\s+", compression="gzip", usecols=["CHR"])
    blocks = create_block(0, len(keys) - 1, nblocks)
    if len(blocks) != nblocks:
        raise RuntimeError(f"Expected {nblocks} blocks; found {len(blocks)}")

    # Fraction of each contiguous jackknife block contributed by each chromosome.
    fractions: dict[tuple[int, int], float] = {}
    for block_index, indices in enumerate(blocks, start=1):
        counts = keys.iloc[np.asarray(indices, dtype=int)]["CHR"].value_counts()
        for chrom, count in counts.items():
            fractions[(block_index, int(chrom))] = float(count) / len(indices)

    rows: list[dict[str, object]] = []
    for metric in ("HSQ1", "HSQ2", "GCOV", "GCOR", "GCORSQ"):
        metric_blocks = block_results.loc[block_results["metric_name"] == metric].copy()
        if len(metric_blocks) != nblocks:
            raise RuntimeError(f"Expected {nblocks} block rows for {metric}; found {len(metric_blocks)}")
        metric_blocks = metric_blocks.set_index("block_index")
        full = float(formal.loc[metric, "estimate"])
        se = float(formal.loc[metric, "SE"])
        for chrom in range(1, 23):
            delta = 0.0
            contributing = 0
            effective_blocks = 0.0
            chr_snp_n = 0
            for block_index, indices in enumerate(blocks, start=1):
                fraction = fractions.get((block_index, chrom), 0.0)
                if fraction == 0:
                    continue
                contributing += 1
                effective_blocks += fraction
                chr_snp_n += int(round(fraction * len(indices)))
                leave_block = float(metric_blocks.loc[block_index, "leave_block_estimate"])
                delta += fraction * (leave_block - full)
            approximate = full + delta
            shift = approximate - full
            shift_ratio = abs(shift) / se if math.isfinite(se) and se > 0 else math.nan
            sign_flip = bool(math.isfinite(approximate) and full != 0 and np.sign(approximate) != np.sign(full))
            rows.append(
                {
                    "metric_name": metric,
                    "excluded_chromosome": chrom,
                    "full_estimate": full,
                    "full_SE": se,
                    "approximate_leave_chromosome_estimate": approximate,
                    "delta_from_full": shift,
                    "absolute_delta": abs(shift),
                    "influence_SE_ratio": shift_ratio,
                    "sign_flip": sign_flip,
                    "catastrophic": bool(not math.isfinite(approximate) or sign_flip or (math.isfinite(shift_ratio) and shift_ratio >= 1.0)),
                    "chromosome_regression_SNP_N": chr_snp_n,
                    "contributing_jackknife_blocks": contributing,
                    "effective_block_fraction_sum": effective_blocks,
                    "method": "FIRST_ORDER_SUM_OF_LEAVE_BLOCK_INFLUENCE",
                    "diagnostic_class": "BLOCK_INFLUENCE_APPROXIMATION_NOT_EXACT_LOCO",
                    "number_blocks": nblocks,
                    "input_freeze_id": freeze["freeze_id"],
                }
            )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    result = pd.DataFrame(rows)
    result.to_csv(OUT, sep="\t", index=False)
    catastrophic = int(result["catastrophic"].sum())
    print(f"wrote={OUT} rows={len(result)} catastrophic={catastrophic}")
    print("diagnostic=BLOCK_INFLUENCE_APPROXIMATION_NOT_EXACT_LOCO")


if __name__ == "__main__":
    main()
