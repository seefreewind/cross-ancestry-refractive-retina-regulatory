#!/usr/bin/env python3
"""Prepare the explicit S-LDXR summary-statistic input schema."""

from __future__ import annotations

import gzip
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/gwas"
OUT = ROOT / "data/interim/sldxr"
AUDIT = ROOT / "results/phase1/SLDXR_INPUT_FILTER.tsv"


def one(ancestry: str, source: str) -> dict:
    out = OUT / f"{ancestry}_sumstats.gz"
    cols = ["SNP", "CHR", "POS", "A1", "A2", "z", "N"]
    usecols = ["SNP", "CHR", "POS", "A1", "A2", "z", "N"]
    seen: set[str] = set()
    counts = {"source_rows": 0, "biallelic_rows": 0, "palindromic_removed": 0, "duplicate_snp_removed": 0, "output_rows": 0}
    with gzip.open(out, "wt") as fh:
        fh.write("SNP CHR BP A1 A2 Z N\n")
        for chunk in pd.read_csv(RAW / source, sep=r"\s+", usecols=usecols, dtype={"SNP": "string", "CHR": "string", "A1": "string", "A2": "string"}, chunksize=250_000, low_memory=False):
            counts["source_rows"] += len(chunk)
            chunk["A1"] = chunk["A1"].fillna("").str.upper()
            chunk["A2"] = chunk["A2"].fillna("").str.upper()
            valid = chunk["A1"].str.fullmatch(r"[ACGT]") & chunk["A2"].str.fullmatch(r"[ACGT]") & chunk["SNP"].notna() & chunk["CHR"].notna() & chunk["POS"].notna() & chunk["z"].notna() & chunk["N"].notna()
            counts["biallelic_rows"] += int(valid.sum())
            chunk = chunk[valid].copy()
            pal = ((chunk["A1"] == "A") & (chunk["A2"] == "T")) | ((chunk["A1"] == "T") & (chunk["A2"] == "A")) | ((chunk["A1"] == "C") & (chunk["A2"] == "G")) | ((chunk["A1"] == "G") & (chunk["A2"] == "C"))
            counts["palindromic_removed"] += int(pal.sum())
            chunk = chunk[~pal]
            keep = []
            for snp in chunk["SNP"].astype(str):
                if snp in seen:
                    keep.append(False)
                    counts["duplicate_snp_removed"] += 1
                else:
                    seen.add(snp)
                    keep.append(True)
            chunk = chunk[keep]
            counts["output_rows"] += len(chunk)
            chunk["POS"] = pd.to_numeric(chunk["POS"], errors="coerce").astype("Int64")
            chunk[["SNP", "CHR", "POS", "A1", "A2", "z", "N"]].rename(columns={"POS": "BP", "z": "Z"}).to_csv(fh, sep=" ", index=False, header=False, float_format="%.8g")
    return {
        "ancestry": ancestry,
        **counts,
        "output": str(out),
        "build_status": "GRCh37_EMPIRICALLY_ADJUDICATED",
        "build_note": "Raw source declaration remains absent; Phase 1C rsID/allele concordance adjudicated GRCh37.p13.",
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [one("EUR", "EUR_meta_no23andMe.fastGWAz"), one("EAS", "EAS_meta.fastGWAz")]
    pd.DataFrame(rows).to_csv(AUDIT, sep="\t", index=False)


if __name__ == "__main__":
    main()
