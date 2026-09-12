#!/usr/bin/env python3
"""Coordinate-level QC for HRCA OCR/DAR intervals against harmonized SNPs."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]


def interval_mask(snps: pd.DataFrame, intervals: pd.DataFrame) -> np.ndarray:
    out = np.zeros(len(snps), dtype=bool)
    if intervals.empty:
        return out
    for chrom, idx in snps.groupby("CHR", sort=False).groups.items():
        sub = intervals[intervals["seqnames"] == f"chr{chrom}"]
        if sub.empty:
            continue
        starts = np.sort(sub["start"].to_numpy(dtype=np.int64))
        ends = sub.sort_values("start")["end"].to_numpy(dtype=np.int64)
        # Prefix maximum handles overlapping intervals when querying SNP positions.
        prefix_end = np.maximum.accumulate(ends)
        positions = snps.loc[idx, "POS"].to_numpy(dtype=np.int64)
        right = np.searchsorted(starts, positions, side="right") - 1
        valid = right >= 0
        hit = np.zeros(len(positions), dtype=bool)
        hit[valid] = prefix_end[right[valid]] >= positions[valid]
        out[np.asarray(list(idx), dtype=int)] = hit
    return out


def unique_intervals(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(["seqnames", "start", "end"])[["seqnames", "start", "end"]].copy()


def main() -> None:
    dar = pd.read_csv(ROOT / "data/processed/HRCA_ANCESTRY_DAR.tsv", sep="\t")
    dar["start"] = dar["start"].astype(int)
    dar["end"] = dar["end"].astype(int)
    union = pd.read_csv(ROOT / "data/processed/HRCA_UNION_OCR.tsv", sep="\t")
    union["start"] = union["start"].astype(int)
    union["end"] = union["end"].astype(int)
    union = unique_intervals(union)
    dar_intervals = unique_intervals(dar)
    stable = union.loc[~interval_mask(union.rename(columns={"seqnames": "CHR"}), dar_intervals)].copy() if False else None

    # The helper expects harmonized SNP columns, so annotate interval tables directly
    # with a small interval-overlap implementation for OCR-vs-DAR classification.
    def interval_overlaps(a: pd.DataFrame, b: pd.DataFrame) -> np.ndarray:
        flags = np.zeros(len(a), dtype=bool)
        for chrom, idx in a.groupby("seqnames", sort=False).groups.items():
            sub = b[b["seqnames"] == chrom]
            if sub.empty:
                continue
            starts = np.sort(sub["start"].to_numpy(dtype=np.int64))
            ends = sub.sort_values("start")["end"].to_numpy(dtype=np.int64)
            prefix_end = np.maximum.accumulate(ends)
            values = a.loc[idx]
            right = np.searchsorted(starts, values["end"].to_numpy(), side="right") - 1
            valid = right >= 0
            hit = np.zeros(len(values), dtype=bool)
            hit[valid] = prefix_end[right[valid]] >= values["start"].to_numpy()[valid]
            flags[np.asarray(list(idx), dtype=int)] = hit
        return flags

    stable = union.loc[~interval_overlaps(union, dar_intervals)].copy()
    snps = pd.read_parquet(ROOT / "data/processed/EUR_EAS_HARMONIZED.parquet", columns=["CHR", "POS", "p_EUR", "p_EAS"])
    snps["CHR"] = snps["CHR"].astype(str)
    snps["POS"] = snps["POS"].astype(int)

    rows = []
    def add(source, cell, ancestry, intervals, notes, build="hg38"):
        intervals = unique_intervals(intervals) if not intervals.empty else intervals
        mask = interval_mask(snps, intervals)
        rows.append({
            "annotation_source": source,
            "cell_class": cell,
            "ancestry_label": ancestry,
            "build": build,
            "interval_n": len(intervals),
            "total_bp": int((intervals["end"] - intervals["start"] + 1).sum()) if len(intervals) else 0,
            "harmonized_snp_n_coordinate_diagnostic": int(mask.sum()),
            "eur_gws_snp_n_coordinate_diagnostic": int((mask & (snps["p_EUR"].to_numpy() < 5e-8)).sum()),
            "eas_gws_snp_n_coordinate_diagnostic": int((mask & (snps["p_EAS"].to_numpy() < 5e-8)).sum()),
            "status": "CONDITIONAL_BUILD_UNRESOLVED",
            "notes": notes,
        })

    for cell, group in sorted(dar.groupby("cell_class")):
        add("HRCA_S19_DAR", cell, "all_table_labels", group, "Author-defined ancestry-DAR intervals; label-specific rows in ANCESTRY_DAR_AUDIT.tsv.")
    add("HRCA_S19_DAR_UNION", "global", "all_table_labels", dar, "Union across S19 cell classes; coordinate diagnostic only.")
    add("HRCA_S12K_UNION_OCR", "global", "all", union, "Union OCR table S12K; hg38 title.")
    add("HRCA_S12K_STABLE_NON_DAR", "global", "all", stable, "Operational non-DAR control: S12K intervals with no overlap with S19 DAR intervals.")

    counts = pd.read_csv(ROOT / "data/processed/HRCA_OCR_COUNTS.tsv", sep="\t")
    for _, r in counts.iterrows():
        rows.append({
            "annotation_source": "HRCA_S12A_OCR_COUNTS", "cell_class": r["cell_class"], "ancestry_label": "all",
            "build": "hg38", "interval_n": int(float(r["number_of_peaks"])), "total_bp": "",
            "harmonized_snp_n_coordinate_diagnostic": "", "eur_gws_snp_n_coordinate_diagnostic": "",
            "eas_gws_snp_n_coordinate_diagnostic": "", "status": "REPORTED_COUNT_NO_COORDINATES",
            "notes": "Table S12A count; coordinate table is represented by class-specific S12B-J sheets or union S12K.",
        })

    out = ROOT / "results/phase0/RETINAL_ANNOTATION_QC.tsv"
    pd.DataFrame(rows).to_csv(out, sep="\t", index=False)
    print(pd.DataFrame(rows).query("annotation_source == 'HRCA_S19_DAR_UNION'").to_string(index=False))


if __name__ == "__main__":
    main()
