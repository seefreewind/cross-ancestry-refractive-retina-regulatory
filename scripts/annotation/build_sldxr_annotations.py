#!/usr/bin/env python3
"""Build GRCh37 S-LDXR annotation files in the exact PLINK SNP order."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
INTERIM = ROOT / "data/interim/sldxr_reference"
OUT = ROOT / "data/interim/sldxr_annotations"


def companion(prefix: Path, extension: str) -> Path:
    """Append PLINK companion extensions without replacing numeric chr suffixes."""
    return prefix.parent / f"{prefix.name}{extension}"


def bfile_prefix(population: str, chrom: int) -> Path:
    qc = pd.read_csv(ROOT / "results/phase1c/SLDXR_REFERENCE_QC.tsv", sep="\t")
    row = qc.loc[(qc["population"] == population) & (qc["chromosome"] == chrom)]
    if len(row) != 1:
        raise RuntimeError(f"Missing unique S-LDXR bfile for {population} chr{chrom}")
    return Path(row.iloc[0]["bfile_prefix"])


def read_bim(prefix: Path) -> pd.DataFrame:
    return pd.read_csv(
        companion(prefix, ".bim"), sep=r"\s+", header=None,
        names=["CHR", "SNP", "CM", "BP", "A1", "A2"],
        dtype={"CHR": str, "SNP": str, "CM": float, "BP": "Int64"},
        engine="python",
    )


def read_intervals(path: Path) -> pd.DataFrame:
    table = pd.read_csv(path, sep="\t", dtype={"canonical_seqnames": str})
    table = table.loc[table["liftover_status"].astype(str).str.startswith("MAPPED")].copy()
    table["chrom"] = table["canonical_seqnames"].astype(str).str.replace("chr", "", regex=False)
    table["start"] = pd.to_numeric(table["canonical_start"], errors="coerce")
    table["end"] = pd.to_numeric(table["canonical_end"], errors="coerce")
    return table.loc[
        table["chrom"].isin([str(x) for x in range(1, 23)])
        & table["start"].notna()
        & table["end"].notna(),
        ["chrom", "start", "end"],
    ].drop_duplicates().reset_index(drop=True)


def interval_overlap_mask(positions: np.ndarray, intervals: pd.DataFrame) -> np.ndarray:
    if intervals.empty:
        return np.zeros(len(positions), dtype=np.int8)
    ordered = intervals.sort_values(["start", "end"])
    starts = ordered["start"].to_numpy(dtype=np.int64)
    ends = ordered["end"].to_numpy(dtype=np.int64)
    prefix_end = np.maximum.accumulate(ends)
    right = np.searchsorted(starts, positions, side="right") - 1
    valid = right >= 0
    hit = np.zeros(len(positions), dtype=np.int8)
    hit[valid] = (prefix_end[right[valid]] >= positions[valid]).astype(np.int8)
    return hit


def remove_overlapping_intervals(intervals: pd.DataFrame, mask_with: pd.DataFrame) -> pd.DataFrame:
    keep = np.ones(len(intervals), dtype=bool)
    for chrom, idx in intervals.groupby("chrom", sort=False).groups.items():
        target = mask_with.loc[mask_with["chrom"] == chrom]
        if target.empty:
            continue
        starts = np.sort(target["start"].to_numpy(dtype=np.int64))
        ordered = target.sort_values("start")
        prefix_end = np.maximum.accumulate(ordered["end"].to_numpy(dtype=np.int64))
        values = intervals.loc[idx]
        right = np.searchsorted(starts, values["end"].to_numpy(dtype=np.int64), side="right") - 1
        valid = right >= 0
        hit = np.zeros(len(values), dtype=bool)
        hit[valid] = prefix_end[right[valid]] >= values["start"].to_numpy(dtype=np.int64)[valid]
        keep[np.asarray(list(idx), dtype=int)] = ~hit
    return intervals.loc[keep].copy()


def write_target(name: str, intervals: pd.DataFrame) -> None:
    target_dir = OUT / name
    target_dir.mkdir(parents=True, exist_ok=True)
    for chrom in range(1, 23):
        bim = read_bim(bfile_prefix("EUR", chrom))
        eas = read_bim(bfile_prefix("EAS", chrom))
        if not bim[["SNP", "BP"]].reset_index(drop=True).equals(eas[["SNP", "BP"]].reset_index(drop=True)):
            raise RuntimeError(f"EUR/EAS SNP order mismatch on chr{chrom}")
        sub = intervals.loc[intervals["chrom"] == str(chrom)]
        annot = pd.DataFrame({
            "CHR": bim["CHR"].astype(str).str.replace("chr", "", regex=False),
            "BP": bim["BP"].astype(int),
            "SNP": bim["SNP"],
            "CM": bim["CM"].fillna(0).astype(float),
            name: interval_overlap_mask(bim["BP"].to_numpy(dtype=np.int64), sub),
        })
        annot.to_csv(target_dir / f"{chrom}.annot.gz", sep="\t", index=False, compression="gzip", float_format="%.10g")


def write_base_annotation() -> None:
    target_dir = OUT / "base"
    target_dir.mkdir(parents=True, exist_ok=True)
    for chrom in range(1, 23):
        bim = read_bim(bfile_prefix("EUR", chrom))
        annot = pd.DataFrame({
            "CHR": bim["CHR"].astype(str).str.replace("chr", "", regex=False),
            "BP": bim["BP"].astype(int),
            "SNP": bim["SNP"],
            "CM": bim["CM"].fillna(0).astype(float),
            "base": 1,
        })
        annot.to_csv(target_dir / f"{chrom}.annot.gz", sep="\t", index=False, compression="gzip")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--targets",
        nargs="+",
        choices=["base", "dar_global", "ocr_union", "matched_non_dar_ocr"],
        default=["base", "dar_global", "ocr_union", "matched_non_dar_ocr"],
    )
    args = parser.parse_args()
    dar = read_intervals(ROOT / "data/processed/reference_anchored/HRCA_ANCESTRY_DAR_GRCh37.tsv")
    ocr = read_intervals(ROOT / "data/processed/reference_anchored/HRCA_UNION_OCR_GRCh37.tsv")
    stable = remove_overlapping_intervals(ocr, dar)
    if "base" in args.targets:
        write_base_annotation()
    if "dar_global" in args.targets:
        write_target("dar_global", dar)
    if "ocr_union" in args.targets:
        write_target("ocr_union", ocr)
    if "matched_non_dar_ocr" in args.targets:
        write_target("matched_non_dar_ocr", stable)
    print(f"DAR intervals={len(dar)} OCR intervals={len(ocr)} stable_non_DAR={len(stable)}")


if __name__ == "__main__":
    main()
