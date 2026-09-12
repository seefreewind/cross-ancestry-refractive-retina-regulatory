#!/usr/bin/env python3
"""Summarize the official S-LDXR block-jackknife stability diagnostics."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[2]
S_LDXR_REPO = Path("/Users/zy/.codex/tools/s-ldxr")
sys.path.insert(0, str(S_LDXR_REPO))

from src.estimation import create_block, get_gcorsq  # noqa: E402


FREEZE = ROOT / "config/SLDXR_FORMAL_INPUT_FREEZE_v1.yaml"
RAW = ROOT / "results/phase1c/sldxr_formal/SLDXR_GENOMEWIDE_EUR_EAS_RAW.tsv"
FORMAL = ROOT / "results/phase1c/SLDXR_GENOMEWIDE_EUR_EAS_FORMAL.tsv"
OUT = ROOT / "results/phase1c/SLDXR_BLOCK_JACKKNIFE.tsv"
REPORT = ROOT / "reports/SLDXR_GENOMEWIDE_STABILITY_AUDIT.md"
ANNOT_ROOT = ROOT / "data/interim/sldxr_annotations/baseline_paired"
FREQ_ROOT = ROOT / "data/interim/sldxr_reference/frequency"
SUMSTATS = ROOT / "data/interim/sldxr_formal/EAS_sumstats_aligned.gz"


def annotation_sums(min_maf: float) -> tuple[np.ndarray, list[str]]:
    total: np.ndarray | None = None
    names: list[str] = []
    for chrom in range(1, 23):
        annot = pd.read_csv(ANNOT_ROOT / f"{chrom}.annot.gz", sep="\t", compression="gzip")
        eas = pd.read_csv(FREQ_ROOT / f"EAS.{chrom}.frq", sep="\t", usecols=["SNP", "MAF"])
        eur = pd.read_csv(FREQ_ROOT / f"EUR.{chrom}.frq", sep="\t", usecols=["SNP", "MAF"])
        if not annot["SNP"].equals(eas["SNP"]) or not annot["SNP"].equals(eur["SNP"]):
            raise RuntimeError(f"Annotation/frequency order mismatch on chr{chrom}")
        mask = (eas["MAF"].to_numpy() > min_maf) & (eur["MAF"].to_numpy() > min_maf)
        names = list(annot.columns[4:])
        values = annot.loc[mask, names].to_numpy(dtype=np.float64, copy=False)
        sums = values.sum(axis=0)
        total = sums if total is None else total + sums
    if total is None:
        raise RuntimeError("No annotation rows loaded")
    return total, names


def direct_gcor(h1: np.ndarray, h2: np.ndarray, cov: np.ndarray) -> np.ndarray:
    result = np.full(len(h1), np.nan, dtype=float)
    valid = (h1 > 0) & (h2 > 0) & np.isfinite(h1) & np.isfinite(h2) & np.isfinite(cov)
    result[valid] = cov[valid] / np.sqrt(h1[valid] * h2[valid])
    return result


def main() -> None:
    freeze = yaml.safe_load(FREEZE.read_text())
    nblocks = int(freeze["jackknife_blocks"])
    min_maf = float(freeze["formal_estimation_min_maf"])
    raw = pd.read_csv(RAW, sep="\t")
    base = raw.loc[raw["ANNOT"] == "base"]
    if len(base) != 1:
        raise RuntimeError("The formal output does not contain exactly one base row")
    base = base.iloc[0]
    formal = pd.read_csv(FORMAL, sep="\t").set_index("metric_name")

    sums, names = annotation_sums(min_maf)
    pseudo = {}
    for metric in ("tau1", "tau2", "theta"):
        array = np.loadtxt(Path(f"{RAW}.pseudo_{metric}.gz"))
        if array.ndim == 1:
            array = array.reshape(1, -1)
        if array.shape != (nblocks, len(names) + 1):
            raise RuntimeError(f"Unexpected pseudo coefficient shape for {metric}: {array.shape}")
        pseudo[metric] = array

    ps_hsq1 = pseudo["tau1"][:, :-1] @ sums
    ps_hsq2 = pseudo["tau2"][:, :-1] @ sums
    ps_gcov = pseudo["theta"][:, :-1] @ sums
    ps_gcor = direct_gcor(ps_hsq1, ps_hsq2, ps_gcov)
    _, _, ps_gcorsq_matrix = get_gcorsq(
        np.array([float(base["HSQ1"])]),
        ps_hsq1[:, None],
        np.array([float(base["HSQ2"])]),
        ps_hsq2[:, None],
        np.array([float(base["GCOV"])]),
        ps_gcov[:, None],
        np.array([float(base["NSNP"])]),
        False,
        float(freeze["shrinkage_alpha"]),
        False,
    )
    ps_gcorsq = ps_gcorsq_matrix[:, 0]

    keys = pd.read_csv(SUMSTATS, sep=r"\s+", compression="gzip", usecols=["CHR", "BP"])
    if len(keys) != int(formal.iloc[0]["effective_SNP_N"]):
        raise RuntimeError("Aligned sumstats row count differs from formal effective SNP N")
    blocks = create_block(0, len(keys) - 1, nblocks)
    if len(blocks) != nblocks:
        raise RuntimeError(f"Expected {nblocks} blocks; S-LDXR created {len(blocks)}")

    metric_values = {
        "HSQ1": ps_hsq1,
        "HSQ2": ps_hsq2,
        "GCOV": ps_gcov,
        "GCOR": ps_gcor,
        "GCORSQ": ps_gcorsq,
    }
    rows = []
    summary_rows = []
    for metric, values in metric_values.items():
        full = float(formal.loc[metric, "estimate"])
        se = float(formal.loc[metric, "SE"])
        finite_values = values[np.isfinite(values)]
        minimum = float(np.min(finite_values)) if len(finite_values) else math.nan
        maximum = float(np.max(finite_values)) if len(finite_values) else math.nan
        deltas = values - full
        ratios = np.abs(deltas) / se if math.isfinite(se) and se > 0 else np.full(len(values), np.nan)
        largest_idx = int(np.nanargmax(np.abs(deltas))) if np.isfinite(deltas).any() else -1
        for index, block in enumerate(blocks):
            first = keys.iloc[int(block[0])]
            last = keys.iloc[int(block[-1])]
            sign_flip = bool(math.isfinite(values[index]) and full != 0 and np.sign(values[index]) != np.sign(full))
            catastrophic = bool(
                not math.isfinite(values[index])
                or (math.isfinite(ratios[index]) and ratios[index] >= 1.0)
                or sign_flip
            )
            rows.append(
                {
                    "metric_name": metric,
                    "block_index": index + 1,
                    "block_start_row": int(block[0]) + 1,
                    "block_end_row": int(block[-1]) + 1,
                    "block_snp_n": len(block),
                    "start_chr": int(first["CHR"]),
                    "start_bp": int(first["BP"]),
                    "end_chr": int(last["CHR"]),
                    "end_bp": int(last["BP"]),
                    "full_estimate": full,
                    "full_SE": se,
                    "full_CI95_low": full - 1.96 * se,
                    "full_CI95_high": full + 1.96 * se,
                    "leave_block_estimate": values[index],
                    "delta_from_full": deltas[index],
                    "absolute_delta": abs(deltas[index]),
                    "influence_SE_ratio": ratios[index],
                    "sign_flip": sign_flip,
                    "influential": bool(math.isfinite(ratios[index]) and ratios[index] >= 0.5),
                    "catastrophic": catastrophic,
                    "min_leave_block_estimate": minimum,
                    "max_leave_block_estimate": maximum,
                    "largest_influence_block": largest_idx + 1,
                    "number_blocks": nblocks,
                }
            )
        summary_rows.append(
            {
                "metric": metric,
                "estimate": full,
                "SE": se,
                "minimum": minimum,
                "maximum": maximum,
                "largest_block": largest_idx + 1,
                "largest_abs_delta": float(np.nanmax(np.abs(deltas))),
                "largest_SE_ratio": float(np.nanmax(ratios)) if np.isfinite(ratios).any() else math.nan,
                "nonfinite": int((~np.isfinite(values)).sum()),
                "sign_flips": int(sum(r["sign_flip"] for r in rows if r["metric_name"] == metric)),
                "catastrophic_blocks": int(sum(r["catastrophic"] for r in rows if r["metric_name"] == metric)),
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, sep="\t", index=False)
    summary = pd.DataFrame(summary_rows)
    gcorsq = summary.loc[summary["metric"] == "GCORSQ"].iloc[0]
    overall = "PASS" if int(summary["nonfinite"].sum()) == 0 and int(summary["catastrophic_blocks"].sum()) == 0 else "FAIL"
    lines = [
        "# S-LDXR genome-wide stability audit",
        "",
        f"**Input freeze:** `{freeze['freeze_id']}`  ",
        f"**Jackknife blocks:** {nblocks}  ",
        f"**Effective regression SNPs:** {int(formal.iloc[0]['effective_SNP_N']):,}  ",
        f"**Stability gate:** `{overall}`",
        "",
        "The S-LDXR files named `pseudo_*` contain leave-one-block coefficient estimates. The table below propagates those coefficients through the official S-LDXR definitions for the genome-wide base annotation.",
        "",
        "| Metric | Full estimate | SE | Min leave-block | Max leave-block | Largest block | Largest |Δ|/SE | Non-finite | Sign flips | Catastrophic blocks |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in summary.itertuples(index=False):
        lines.append(
            f"| {item.metric} | {item.estimate:.6g} | {item.SE:.6g} | {item.minimum:.6g} | {item.maximum:.6g} | {item.largest_block} | {item.largest_SE_ratio:.4g} | {item.nonfinite} | {item.sign_flips} | {item.catastrophic_blocks} |"
        )
    lines.extend(
        [
            "",
            "A block is flagged as catastrophic when its leave-block estimate is non-finite, changes sign relative to a non-zero full estimate, or differs from the full estimate by at least one full-estimate standard error. This is a pre-specified numerical stability rule, not a biological significance test.",
            "",
            f"For the official GCORSQ metric, the leave-block range is {gcorsq['minimum']:.6g} to {gcorsq['maximum']:.6g}; the largest influence is block {int(gcorsq['largest_block'])}.",
            "",
            "Detailed block-level results are in `results/phase1c/SLDXR_BLOCK_JACKKNIFE.tsv`.",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n")
    print(f"wrote={OUT}")
    print(f"wrote={REPORT} stability={overall}")
    if overall != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
