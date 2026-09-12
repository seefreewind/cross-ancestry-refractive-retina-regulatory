#!/usr/bin/env python3
"""Hard-gate paired-panel annotations and S-LDXR score universes.

This validation distinguishes the full paired-panel universe from the exact
MAF-filtered subset written by S-LDXR's ``--print-snps`` option.  A score file
passes ``EXACT_PANEL_MATCH`` only when its ordered CHR:BP:SNP keys equal that
deterministic filtered subset of the paired panel.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
REFERENCE_QC = ROOT / "results/phase1c/SLDXR_REFERENCE_QC.tsv"
ALIGNED_ANNOT_ROOT = ROOT / "data/interim/sldxr_annotations/baseline_paired"
ALIGNED_SCORE_ROOT = ROOT / "data/interim/sldxr_scores_aligned"
SCORE_ROOT = ROOT / "data/interim/sldxr_scores"
FREQ_ROOT = ROOT / "data/interim/sldxr_reference/frequency"

ROW_IDENTITY_OUT = ROOT / "results/phase1c/SLDXR_BASELINE_ROW_IDENTITY.tsv"
NUMERICAL_OUT = ROOT / "results/phase1c/SLDXR_ALIGNED_BASELINE_NUMERICAL_QC.tsv"
UNIVERSE_OUT = ROOT / "results/phase1c/SLDXR_ALL_SCORE_UNIVERSE_ALIGNMENT.tsv"
BASELINE_SCORE_QC_OUT = ROOT / "results/phase1c/SLDXR_SCORE_QC_ALIGNED_BASELINE.tsv"

SCORE_KINDS = {
    "baseline": ALIGNED_SCORE_ROOT,
    "weights": SCORE_ROOT,
    "dar_global": SCORE_ROOT,
    "ocr_union": SCORE_ROOT,
    "matched_non_dar_ocr": SCORE_ROOT,
}
SUFFIXES = ("pop1", "pop2", "te")


def ordered_key_hash(frame: pd.DataFrame) -> str:
    digest = hashlib.sha256()
    for chrom, bp, snp in frame[["CHR", "BP", "SNP"]].itertuples(index=False, name=None):
        digest.update(f"{int(chrom)}:{int(bp)}:{snp}\n".encode())
    return digest.hexdigest()


def panel_prefix(chrom: int) -> Path:
    qc = pd.read_csv(REFERENCE_QC, sep="\t")
    row = qc.loc[(qc["population"] == "EUR") & (qc["chromosome"] == chrom)]
    if len(row) != 1:
        raise RuntimeError(f"Missing unique EUR paired-panel prefix for chr{chrom}")
    return Path(row.iloc[0]["bfile_prefix"])


def read_panel(chrom: int) -> pd.DataFrame:
    prefix = panel_prefix(chrom)
    return pd.read_csv(
        Path(f"{prefix}.bim"),
        sep=r"\s+",
        header=None,
        names=["CHR", "SNP", "CM", "BP", "A1", "A2"],
        usecols=[0, 1, 3],
        dtype={"CHR": int, "SNP": str, "BP": int},
    )[["CHR", "BP", "SNP"]]


def read_annotation(chrom: int) -> pd.DataFrame:
    return pd.read_csv(
        ALIGNED_ANNOT_ROOT / f"{chrom}.annot.gz",
        sep="\t",
        compression="gzip",
        usecols=["CHR", "BP", "SNP"],
        dtype={"CHR": int, "BP": int, "SNP": str},
    )[["CHR", "BP", "SNP"]]


def expected_score_universe(chrom: int, panel: pd.DataFrame) -> pd.DataFrame:
    eas = pd.read_csv(FREQ_ROOT / f"EAS.{chrom}.frq", sep="\t", usecols=["SNP", "MAF"])
    eur = pd.read_csv(FREQ_ROOT / f"EUR.{chrom}.frq", sep="\t", usecols=["SNP", "MAF"])
    if len(eas) != len(panel) or len(eur) != len(panel):
        raise RuntimeError(f"Frequency row count differs from paired panel on chr{chrom}")
    if not eas["SNP"].equals(panel["SNP"]) or not eur["SNP"].equals(panel["SNP"]):
        raise RuntimeError(f"Frequency SNP order differs from paired panel on chr{chrom}")
    keep = (eas["MAF"].to_numpy() > 0.01) & (eur["MAF"].to_numpy() > 0.01)
    return panel.loc[keep].reset_index(drop=True)


def score_path(kind: str, chrom: int, suffix: str) -> Path:
    return SCORE_KINDS[kind] / f"{kind}_chr.{chrom}_{suffix}.gz"


def read_score_keys(path: Path) -> tuple[pd.DataFrame, list[str]]:
    frame = pd.read_csv(
        path,
        sep="\t",
        compression="gzip",
        usecols=["CHR", "SNP", "BP"],
        dtype={"CHR": int, "SNP": str, "BP": int},
    )[["CHR", "BP", "SNP"]]
    with gzip.open(path, "rt") as handle:
        header = handle.readline().rstrip("\n").split("\t")
    return frame, header


def gzip_ok(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    return subprocess.run(["gzip", "-t", str(path)], check=False).returncode == 0


def scan_numeric(path: Path, chunksize: int = 20000) -> dict[str, object]:
    result: dict[str, object] = {
        "rows": 0,
        "nan_count": 0,
        "inf_count": 0,
        "negative_count": 0,
        "extreme_abs_gt_1e8": 0,
        "max_abs": np.nan,
        "constant_columns": "",
        "n_constant_columns": 0,
        "parse_error": "",
    }
    global_min: np.ndarray | None = None
    global_max: np.ndarray | None = None
    numeric_names: list[str] = []
    try:
        for chunk in pd.read_csv(path, sep="\t", compression="gzip", chunksize=chunksize):
            numeric_names = list(chunk.columns[3:])
            values = chunk.iloc[:, 3:].to_numpy(dtype=np.float64, copy=False)
            result["rows"] = int(result["rows"]) + len(chunk)
            result["nan_count"] = int(result["nan_count"]) + int(np.isnan(values).sum())
            result["inf_count"] = int(result["inf_count"]) + int(np.isinf(values).sum())
            finite = np.isfinite(values)
            result["negative_count"] = int(result["negative_count"]) + int(((values < 0) & finite).sum())
            result["extreme_abs_gt_1e8"] = int(result["extreme_abs_gt_1e8"]) + int(((np.abs(values) > 1e8) & finite).sum())
            if finite.any():
                local_abs = float(np.nanmax(np.where(finite, np.abs(values), np.nan)))
                current = result["max_abs"]
                result["max_abs"] = local_abs if pd.isna(current) else max(float(current), local_abs)
            chunk_min = np.nanmin(np.where(finite, values, np.nan), axis=0)
            chunk_max = np.nanmax(np.where(finite, values, np.nan), axis=0)
            global_min = chunk_min if global_min is None else np.fmin(global_min, chunk_min)
            global_max = chunk_max if global_max is None else np.fmax(global_max, chunk_max)
        if global_min is not None and global_max is not None:
            constant = [name for name, lo, hi in zip(numeric_names, global_min, global_max) if lo == hi]
            result["constant_columns"] = ";".join(constant)
            result["n_constant_columns"] = len(constant)
    except Exception as exc:
        result["parse_error"] = repr(exc)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-numerical", action="store_true")
    args = parser.parse_args()

    row_identity = []
    universe_rows = []
    numerical_rows = []
    baseline_rows = []
    expected_headers: dict[tuple[str, str], list[str]] = {}

    for chrom in range(1, 23):
        panel = read_panel(chrom)
        annot = read_annotation(chrom)
        expected = expected_score_universe(chrom, panel)
        panel_hash = ordered_key_hash(panel)
        annot_hash = ordered_key_hash(annot)
        expected_hash = ordered_key_hash(expected)
        n_key_mismatch = int(
            len(panel) != len(annot)
            or not panel[["CHR", "BP", "SNP"]].equals(annot[["CHR", "BP", "SNP"]])
        )
        chr_mismatch = int((panel["CHR"].to_numpy() != annot["CHR"].to_numpy()).sum()) if len(panel) == len(annot) else -1
        bp_mismatch = int((panel["BP"].to_numpy() != annot["BP"].to_numpy()).sum()) if len(panel) == len(annot) else -1
        snp_mismatch = int((panel["SNP"].to_numpy() != annot["SNP"].to_numpy()).sum()) if len(panel) == len(annot) else -1

        baseline_score_hashes: dict[str, str] = {}
        baseline_score_matches: dict[str, bool] = {}
        for kind, root in SCORE_KINDS.items():
            for suffix in SUFFIXES:
                path = score_path(kind, chrom, suffix)
                base = {
                    "annotation": kind,
                    "chromosome": chrom,
                    "population_score": suffix,
                    "paired_panel_rows": len(panel),
                    "expected_score_rows": len(expected),
                    "score_filter": "MAF_EAS>0.01_AND_MAF_EUR>0.01",
                    "score_path": str(path),
                }
                if not path.exists():
                    universe_rows.append({**base, "score_rows": 0, "expected_order_sha256": expected_hash, "score_order_sha256": "", "duplicate_snps": -1, "chr_mismatch": -1, "bp_mismatch": -1, "snp_id_mismatch": -1, "order_mismatch": -1, "EXACT_PANEL_MATCH": False, "status": "MISSING"})
                    if kind == "baseline":
                        baseline_score_matches[suffix] = False
                    continue
                try:
                    score, header = read_score_keys(path)
                    header_key = (kind, suffix)
                    if header_key not in expected_headers:
                        expected_headers[header_key] = header
                    header_match = header == expected_headers[header_key]
                    same_len = len(score) == len(expected)
                    score_hash = ordered_key_hash(score)
                    exact = same_len and score.equals(expected) and header_match
                    values = {
                        "score_rows": len(score),
                        "expected_order_sha256": expected_hash,
                        "score_order_sha256": score_hash,
                        "duplicate_snps": int(score["SNP"].duplicated().sum()),
                        "chr_mismatch": int((score["CHR"].to_numpy() != expected["CHR"].to_numpy()).sum()) if same_len else -1,
                        "bp_mismatch": int((score["BP"].to_numpy() != expected["BP"].to_numpy()).sum()) if same_len else -1,
                        "snp_id_mismatch": int((score["SNP"].to_numpy() != expected["SNP"].to_numpy()).sum()) if same_len else -1,
                        "order_mismatch": 0 if exact else 1,
                        "EXACT_PANEL_MATCH": exact,
                        "status": "PASS" if exact else "FAIL",
                    }
                    universe_rows.append({**base, **values})
                    if kind == "baseline":
                        baseline_score_hashes[suffix] = score_hash
                        baseline_score_matches[suffix] = exact
                        if not args.skip_numerical:
                            numeric = scan_numeric(path)
                            numeric_pass = (
                                gzip_ok(path)
                                and numeric["parse_error"] == ""
                                and numeric["rows"] == len(expected)
                                and numeric["nan_count"] == 0
                                and numeric["inf_count"] == 0
                                and numeric["extreme_abs_gt_1e8"] == 0
                            )
                            numerical_rows.append(
                                {
                                    "chromosome": chrom,
                                    "population_score": suffix,
                                    "score_rows": numeric["rows"],
                                    "expected_rows": len(expected),
                                    "annotation_columns": len(header) - 3,
                                    "gzip_integrity": gzip_ok(path),
                                    "header_consistent": header_match,
                                    "nan_count": numeric["nan_count"],
                                    "inf_count": numeric["inf_count"],
                                    "negative_count": numeric["negative_count"],
                                    "negative_value_policy": "ALLOWED_FOR_FINITE_SAMPLE_BIAS_CORRECTED_LD_SCORES",
                                    "max_abs": numeric["max_abs"],
                                    "extreme_abs_gt_1e8": numeric["extreme_abs_gt_1e8"],
                                    "constant_columns": numeric["constant_columns"],
                                    "n_constant_columns": numeric["n_constant_columns"],
                                    "parse_error": numeric["parse_error"],
                                    "status": "PASS" if numeric_pass and header_match else "FAIL",
                                }
                            )
                except Exception as exc:
                    universe_rows.append({**base, "score_rows": -1, "expected_order_sha256": expected_hash, "score_order_sha256": "", "duplicate_snps": -1, "chr_mismatch": -1, "bp_mismatch": -1, "snp_id_mismatch": -1, "order_mismatch": -1, "EXACT_PANEL_MATCH": False, "status": f"ERROR:{exc!r}"})
                    if kind == "baseline":
                        baseline_score_matches[suffix] = False

        identity_pass = (
            len(panel) == len(annot)
            and panel_hash == annot_hash
            and panel["SNP"].duplicated().sum() == 0
            and annot["SNP"].duplicated().sum() == 0
            and chr_mismatch == 0
            and bp_mismatch == 0
            and snp_mismatch == 0
            and all(baseline_score_matches.get(suffix, False) for suffix in SUFFIXES)
        )
        row_identity.append(
            {
                "chromosome": chrom,
                "panel_rows": len(panel),
                "annotation_rows": len(annot),
                "expected_score_rows": len(expected),
                "panel_duplicate_snps": int(panel["SNP"].duplicated().sum()),
                "annotation_duplicate_snps": int(annot["SNP"].duplicated().sum()),
                "missing_snps": int((~panel["SNP"].isin(annot["SNP"])).sum()),
                "chr_mismatch": chr_mismatch,
                "bp_mismatch": bp_mismatch,
                "snp_id_mismatch": snp_mismatch,
                "order_mismatch": n_key_mismatch,
                "panel_order_sha256": panel_hash,
                "annotation_order_sha256": annot_hash,
                "expected_score_order_sha256": expected_hash,
                "score_pop1_order_sha256": baseline_score_hashes.get("pop1", ""),
                "score_pop2_order_sha256": baseline_score_hashes.get("pop2", ""),
                "score_te_order_sha256": baseline_score_hashes.get("te", ""),
                "status": "PASS" if identity_pass else "FAIL",
            }
        )
        baseline_rows.append(
            {
                "chromosome": chrom,
                "panel_rows": len(panel),
                "annotation_rows": len(annot),
                "score_input_rows": len(panel),
                "score_output_rows": len(expected),
                "score_output_status": "PASS" if all(baseline_score_matches.get(s, False) for s in SUFFIXES) else "FAIL",
                "annotation_columns": 97,
                "missing_snps": int((~panel["SNP"].isin(annot["SNP"])).sum()),
                "duplicate_snps": int(annot["SNP"].duplicated().sum()),
                "chr_mismatch": chr_mismatch,
                "bp_mismatch": bp_mismatch,
                "order_match": panel_hash == annot_hash,
                "status": "PASS" if identity_pass else "FAIL",
            }
        )

    ROW_IDENTITY_OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(row_identity).to_csv(ROW_IDENTITY_OUT, sep="\t", index=False)
    pd.DataFrame(universe_rows).to_csv(UNIVERSE_OUT, sep="\t", index=False)
    pd.DataFrame(baseline_rows).to_csv(BASELINE_SCORE_QC_OUT, sep="\t", index=False)
    if not args.skip_numerical:
        pd.DataFrame(numerical_rows).to_csv(NUMERICAL_OUT, sep="\t", index=False)

    identity_ok = all(row["status"] == "PASS" for row in row_identity) and len(row_identity) == 22
    universe_ok = all(row["status"] == "PASS" for row in universe_rows)
    numerical_ok = args.skip_numerical or (len(numerical_rows) == 66 and all(row["status"] == "PASS" for row in numerical_rows))
    print(f"ALIGNMENT_22_OF_22={identity_ok}")
    print(f"ALL_SCORE_UNIVERSE_QC={universe_ok}")
    print(f"BASELINE_NUMERICAL_QC={numerical_ok}")
    if not (identity_ok and universe_ok and numerical_ok):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
