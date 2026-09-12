#!/usr/bin/env python3
"""Append explicitly labelled generic-reference LDSC diagnostic rows."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "results/phase1/LDSC_H2_SUMMARY.tsv"


def parse(log: Path):
    text = log.read_text(errors="replace") if log.exists() else ""
    m = re.search(r"Total Observed scale h2:\s+([-+0-9.eE]+)\s*\(\s*([-+0-9.eE]+)\s*\)", text)
    n = re.search(r"After merging with regression SNP LD,\s+(\d+)\s+SNPs remain", text)
    if not m:
        return None
    h2, se = float(m.group(1)), float(m.group(2))
    return h2, se, h2 / se if se else float("nan"), n.group(1) if n else ""


def main() -> None:
    df = pd.read_csv(SUMMARY, sep="\t", dtype=str) if SUMMARY.exists() else pd.DataFrame()
    if not df.empty:
        df = df[~df["status"].eq("DIAGNOSTIC_GENERIC_REFERENCE")]
    rows = []
    for ancestry in ["EUR", "EAS"]:
        result = parse(ROOT / f"results/phase1/ldsc_generic_{ancestry}_h2.log")
        if result:
            h2, se, z, n = result
            rows.append({"ancestry": ancestry, "sumstats": str(ROOT / f"data/interim/ldsc/{ancestry}.sumstats.gz"), "status": "DIAGNOSTIC_GENERIC_REFERENCE", "h2": h2, "h2_se": se, "h2_z": z, "log": str(ROOT / f"results/phase1/ldsc_generic_{ancestry}_h2.log"), "error": f"Generic 1000G LD-score reference; not ancestry matched; merged_regression_snps={n}"})
    if rows:
        df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
    df.to_csv(SUMMARY, sep="\t", index=False)


if __name__ == "__main__":
    main()
