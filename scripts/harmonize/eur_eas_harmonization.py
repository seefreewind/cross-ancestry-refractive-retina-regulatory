#!/usr/bin/env python3
"""Pilot harmonization of EUR and EAS fastGWAz files at CHR:POS."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


BASE_COLS = ["SNP", "A1", "A2", "freq", "b", "se", "p", "N", "CHR", "POS", "z"]
READ_DTYPES = {"SNP": "string", "A1": "string", "A2": "string", "CHR": "string"}
COMP = str.maketrans("ACGT", "TGCA")


def complement(s: pd.Series) -> pd.Series:
    return s.fillna("").str.translate(COMP)


def prepare(df: pd.DataFrame, suffix: str) -> pd.DataFrame:
    df = df.copy()
    for c in ["A1", "A2"]:
        df[c] = df[c].fillna("").str.upper()
    df["CHR"] = df["CHR"].astype("string")
    df["POS"] = pd.to_numeric(df["POS"], errors="coerce").astype("Int64")
    for c in ["freq", "b", "se", "p", "N", "z"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["is_biallelic_snp"] = df["A1"].str.fullmatch(r"[ACGT]") & df["A2"].str.fullmatch(r"[ACGT]")
    df["is_palindromic"] = ((df["A1"] == "A") & (df["A2"] == "T")) | ((df["A1"] == "T") & (df["A2"] == "A")) | ((df["A1"] == "C") & (df["A2"] == "G")) | ((df["A1"] == "G") & (df["A2"] == "C"))
    df["key"] = df["CHR"].fillna("") + ":" + df["POS"].astype("string").fillna("")
    df = df[df["is_biallelic_snp"] & df["CHR"].notna() & df["POS"].notna()].copy()
    return df.add_suffix(suffix)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument("--chunksize", type=int, default=250_000)
    args = ap.parse_args()
    ws = args.workspace
    gwas = ws / "data" / "raw" / "gwas"
    out_dir = ws / "data" / "processed"
    result_dir = ws / "results" / "phase0"
    out_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)
    eur_path = gwas / "EUR_meta_no23andMe.fastGWAz"
    eas_path = gwas / "EAS_meta.fastGWAz"
    if not eur_path.exists() or not eas_path.exists():
        raise FileNotFoundError("EUR and EAS source files are required")

    # Load only the EAS fields needed for a position/allele join.
    eas = pd.read_csv(eas_path, sep=r"\s+", usecols=BASE_COLS, dtype=READ_DTYPES, low_memory=False)
    eas = prepare(eas, "_EAS")
    eas_dup = eas["key_EAS"].duplicated(keep=False)
    eas_unique = eas.loc[~eas_dup].copy()
    eas_unique = eas_unique.set_index("key_EAS", drop=False)

    writer = None
    flow = {
        "eur_source_rows": 0,
        "eur_eligible_unique_snp_rows": 0,
        "eas_source_rows": len(eas),
        "eas_eligible_unique_snp_rows": len(eas_unique),
        "position_matched_eligible": 0,
        "allele_matched_nonpalindromic": 0,
        "palindromic_excluded": 0,
        "unresolved_allele_mismatch": 0,
        "duplicate_eur_positions_excluded": 0,
        "duplicate_eas_positions_excluded": int(eas_dup.sum()),
        "final_usable_shared_snps": 0,
        "allele_flip_count": 0,
        "strand_resolved_count": 0,
    }
    outputs = []
    usecols = BASE_COLS
    for eur in pd.read_csv(eur_path, sep=r"\s+", usecols=usecols, dtype=READ_DTYPES, chunksize=args.chunksize, low_memory=False):
        flow["eur_source_rows"] += len(eur)
        eur = prepare(eur, "_EUR")
        eur_dup = eur["key_EUR"].duplicated(keep=False)
        flow["duplicate_eur_positions_excluded"] += int(eur_dup.sum())
        eur = eur.loc[~eur_dup].copy()
        flow["eur_eligible_unique_snp_rows"] += len(eur)
        joined = eur.join(eas_unique, on="key_EUR", how="inner")
        flow["position_matched_eligible"] += len(joined)
        if joined.empty:
            continue
        a1e, a2e = joined["A1_EUR"], joined["A2_EUR"]
        a1a, a2a = joined["A1_EAS"], joined["A2_EAS"]
        direct = (a1e == a1a) & (a2e == a2a)
        swap = (a1e == a2a) & (a2e == a1a)
        ce1, ce2 = complement(a1e), complement(a2e)
        comp_direct = (ce1 == a1a) & (ce2 == a2a)
        comp_swap = (ce1 == a2a) & (ce2 == a1a)
        pal = joined["is_palindromic_EUR"]
        allele_matched = direct | swap | comp_direct | comp_swap
        joined["alignment"] = np.select([direct, swap, comp_direct, comp_swap], ["direct", "allele_flip", "strand_resolved", "strand_resolved_allele_flip"], default="unresolved_mismatch")
        joined["effect_sign_EAS_to_EUR"] = np.select([direct | comp_direct, swap | comp_swap], [1.0, -1.0], default=np.nan)
        joined["palindromic_excluded_primary"] = pal
        usable = joined[allele_matched & ~pal].copy()
        flow["allele_matched_nonpalindromic"] += int((allele_matched & ~pal).sum())
        flow["palindromic_excluded"] += int(pal.sum())
        flow["unresolved_allele_mismatch"] += int((~allele_matched).sum())
        flow["allele_flip_count"] += int((usable["effect_sign_EAS_to_EUR"] == -1).sum())
        flow["strand_resolved_count"] += int(usable["alignment"].str.contains("strand").sum())
        if usable.empty:
            continue
        usable["z_EAS_aligned_to_EUR"] = usable["z_EAS"] * usable["effect_sign_EAS_to_EUR"]
        usable["b_EAS_aligned_to_EUR"] = usable["b_EAS"] * usable["effect_sign_EAS_to_EUR"]
        usable["freq_EAS_aligned_to_EUR_A1"] = np.where(usable["effect_sign_EAS_to_EUR"] > 0, usable["freq_EAS"], 1 - usable["freq_EAS"])
        keep = [
            "key_EUR", "CHR_EUR", "POS_EUR", "SNP_EUR", "A1_EUR", "A2_EUR", "A1_EAS", "A2_EAS",
            "freq_EUR", "freq_EAS", "freq_EAS_aligned_to_EUR_A1", "b_EUR", "se_EUR", "p_EUR", "N_EUR", "z_EUR",
            "b_EAS_aligned_to_EUR", "se_EAS", "p_EAS", "N_EAS", "z_EAS_aligned_to_EUR", "alignment",
        ]
        usable = usable[keep].rename(columns={"key_EUR": "variant_key", "CHR_EUR": "CHR", "POS_EUR": "POS"})
        table = pa.Table.from_pandas(usable, preserve_index=False)
        if writer is None:
            writer = pq.ParquetWriter(out_dir / "EUR_EAS_HARMONIZED.parquet", table.schema, compression="zstd")
        writer.write_table(table)
        flow["final_usable_shared_snps"] += len(usable)
    if writer is not None:
        writer.close()
    else:
        raise RuntimeError("No harmonized rows were generated")

    denominator = flow["position_matched_eligible"]
    flow["mutually_available_nonpalindromic"] = flow["position_matched_eligible"] - flow["palindromic_excluded"]
    flow["match_rate_of_position_matched"] = flow["final_usable_shared_snps"] / denominator if denominator else math.nan
    flow["match_rate_of_mutually_available_nonpalindromic"] = flow["final_usable_shared_snps"] / flow["mutually_available_nonpalindromic"] if flow["mutually_available_nonpalindromic"] else math.nan
    flow["match_rate_of_min_eligible"] = flow["final_usable_shared_snps"] / min(flow["eur_eligible_unique_snp_rows"], flow["eas_eligible_unique_snp_rows"]) if min(flow["eur_eligible_unique_snp_rows"], flow["eas_eligible_unique_snp_rows"]) else math.nan
    pd.DataFrame([
        {"stage": "EUR original", "n": flow["eur_source_rows"]},
        {"stage": "EUR valid unique biallelic SNP", "n": flow["eur_eligible_unique_snp_rows"]},
        {"stage": "EAS valid unique biallelic SNP", "n": flow["eas_eligible_unique_snp_rows"]},
        {"stage": "matched at CHR:POS", "n": flow["position_matched_eligible"]},
        {"stage": "mutually available non-palindromic at CHR:POS", "n": flow["mutually_available_nonpalindromic"]},
        {"stage": "allele matched non-palindromic", "n": flow["allele_matched_nonpalindromic"]},
        {"stage": "palindromic excluded", "n": flow["palindromic_excluded"]},
        {"stage": "unresolved allele mismatch", "n": flow["unresolved_allele_mismatch"]},
        {"stage": "final usable shared SNPs", "n": flow["final_usable_shared_snps"]},
    ]).to_csv(result_dir / "EUR_EAS_HARMONIZATION.tsv", sep="\t", index=False)
    pd.DataFrame([flow]).to_csv(result_dir / "EUR_EAS_HARMONIZATION_METRICS.tsv", sep="\t", index=False)


if __name__ == "__main__":
    main()
