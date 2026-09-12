#!/usr/bin/env python3
"""Build the Phase 2 EUR-EAS SNP-level heterogeneity feature matrix."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "config/PHASE2_ANALYSIS_FREEZE_v1.yaml"
OUT = ROOT / "data/processed/phase2/EUR_EAS_HETEROGENEITY_FEATURES.parquet"
QC_OUT = ROOT / "results/phase2/PHASE2_HETEROGENEITY_FEATURE_QC.tsv"


def qcut_codes(values: pd.Series, q: int, prefix: str) -> pd.Series:
    ranked = values.rank(method="first")
    codes = pd.qcut(ranked, q=q, labels=False, duplicates="drop")
    return prefix + codes.astype("int16").astype(str)


def read_binary_annotation(prefix: Path, column: str) -> pd.DataFrame:
    frames = []
    for chrom in range(1, 23):
        path = prefix / f"{chrom}.annot.gz"
        frame = pd.read_csv(path, sep="\t", compression="gzip", usecols=["CHR", "BP", "SNP", column])
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def read_frequency(prefix: Path, population: str) -> pd.DataFrame:
    frames = []
    for chrom in range(1, 23):
        path = Path(f"{prefix}{chrom}.frq")
        frame = pd.read_csv(path, sep=r"\s+", usecols=["SNP", "MAF"])
        frame = frame.rename(columns={"MAF": f"MAF_{population}"})
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def read_baseline_base_scores(prefix: Path) -> pd.DataFrame:
    frames = []
    for chrom in range(1, 23):
        path = Path(f"{prefix}{chrom}_pop1.gz")
        frame = pd.read_csv(path, sep="\t", compression="gzip", usecols=["CHR", "SNP", "BP", "base"])
        frame = frame.rename(columns={"base": "baseline_ld_base"})
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    freeze = yaml.safe_load(FREEZE.read_text())
    inputs = freeze["input_files"]

    formal = pd.read_csv(
        ROOT / inputs["formal_sldxr_eas_sumstats"],
        sep=r"\s+",
        compression="gzip",
        usecols=["SNP", "CHR", "BP"],
    )
    formal["CHR"] = formal["CHR"].astype("int16")
    formal["BP"] = formal["BP"].astype("int64")
    if formal["SNP"].duplicated().any():
        raise RuntimeError("Formal S-LDXR sumstats contain duplicated SNP IDs")

    harmonized = pd.read_parquet(
        ROOT / inputs["harmonized_effects"],
        columns=[
            "SNP_EUR",
            "CHR",
            "POS",
            "b_EUR",
            "se_EUR",
            "p_EUR",
            "N_EUR",
            "b_EAS_aligned_to_EUR",
            "se_EAS",
            "p_EAS",
            "N_EAS",
            "alignment",
        ],
    ).rename(columns={"SNP_EUR": "SNP", "POS": "BP"})
    harmonized["CHR"] = harmonized["CHR"].astype("int16")
    harmonized["BP"] = harmonized["BP"].astype("int64")
    harmonized = harmonized.drop_duplicates("SNP", keep="first")

    features = formal.merge(harmonized, on=["SNP", "CHR", "BP"], how="inner", validate="one_to_one")
    if len(features) != len(formal):
        raise RuntimeError(f"Formal/harmonized overlap {len(features)} != formal SNPs {len(formal)}")

    denominator = np.sqrt(features["se_EUR"].to_numpy() ** 2 + features["se_EAS"].to_numpy() ** 2)
    if np.any(~np.isfinite(denominator)) or np.any(denominator <= 0):
        raise RuntimeError("Invalid heterogeneity denominator")
    features["z_het"] = (features["b_EUR"] - features["b_EAS_aligned_to_EUR"]) / denominator
    features["chi2_het"] = features["z_het"] ** 2
    features["abs_beta_diff"] = (features["b_EUR"] - features["b_EAS_aligned_to_EUR"]).abs()

    dar = read_binary_annotation(ROOT / inputs["dar_annotation_prefix"], "dar_global")
    ocr = read_binary_annotation(ROOT / inputs["ocr_union_annotation_prefix"], "ocr_union")
    matched = read_binary_annotation(ROOT / inputs["matched_non_dar_annotation_prefix"], "matched_non_dar_ocr")
    eas_frq = read_frequency(ROOT / inputs["eas_frequency_prefix"], "EAS_ref")
    eur_frq = read_frequency(ROOT / inputs["eur_frequency_prefix"], "EUR_ref")
    base = read_baseline_base_scores(ROOT / inputs["baseline_ld_score_prefix"])

    for annot, label in ((dar, "DAR"), (ocr, "OCR"), (matched, "matched non-DAR")):
        if annot["SNP"].duplicated().any():
            raise RuntimeError(f"{label} annotation contains duplicated SNP IDs")

    features = (
        features.merge(dar[["SNP", "dar_global"]], on="SNP", how="left", validate="one_to_one")
        .merge(ocr[["SNP", "ocr_union"]], on="SNP", how="left", validate="one_to_one")
        .merge(matched[["SNP", "matched_non_dar_ocr"]], on="SNP", how="left", validate="one_to_one")
        .merge(eas_frq, on="SNP", how="left", validate="one_to_one")
        .merge(eur_frq, on="SNP", how="left", validate="one_to_one")
        .merge(base[["SNP", "baseline_ld_base"]], on="SNP", how="left", validate="one_to_one")
    )

    binary_cols = ["dar_global", "ocr_union", "matched_non_dar_ocr"]
    features[binary_cols] = features[binary_cols].fillna(0).astype("int8")
    required_numeric = ["MAF_EAS_ref", "MAF_EUR_ref", "baseline_ld_base", "chi2_het"]
    if features[required_numeric].isna().any().any():
        missing = features[required_numeric].isna().sum().to_dict()
        raise RuntimeError(f"Missing required numeric features: {missing}")

    features["MAF_avg_ref"] = (features["MAF_EAS_ref"] + features["MAF_EUR_ref"]) / 2.0
    features["MAF_absdiff_ref"] = (features["MAF_EAS_ref"] - features["MAF_EUR_ref"]).abs()
    features["maf_avg_decile"] = qcut_codes(features["MAF_avg_ref"], 10, "mafavg")
    features["maf_absdiff_quintile"] = qcut_codes(features["MAF_absdiff_ref"], 5, "mafdiff")
    features["ld_base_decile"] = qcut_codes(features["baseline_ld_base"], 10, "ld")
    features["ocr_status"] = np.where(features["ocr_union"].eq(1), "ocr1", "ocr0")
    features["top_1pct_chi2_het"] = features["chi2_het"] >= features["chi2_het"].quantile(0.99)
    features["top_5pct_chi2_het"] = features["chi2_het"] >= features["chi2_het"].quantile(0.95)
    features["top_10pct_chi2_het"] = features["chi2_het"] >= features["chi2_het"].quantile(0.90)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    QC_OUT.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(OUT, index=False)

    qc_rows = [
        {"metric": "formal_snp_n", "value": len(formal), "status": "PASS"},
        {"metric": "feature_snp_n", "value": len(features), "status": "PASS"},
        {"metric": "dar_snp_n", "value": int(features["dar_global"].sum()), "status": "PASS"},
        {"metric": "ocr_union_snp_n", "value": int(features["ocr_union"].sum()), "status": "PASS"},
        {"metric": "matched_non_dar_snp_n", "value": int(features["matched_non_dar_ocr"].sum()), "status": "PASS"},
        {"metric": "chi2_het_finite_n", "value": int(np.isfinite(features["chi2_het"]).sum()), "status": "PASS"},
        {"metric": "top_5pct_threshold", "value": float(features["chi2_het"].quantile(0.95)), "status": "PASS"},
    ]
    if int(features["dar_global"].sum()) < int(freeze["primary_enrichment_test"]["minimum_case_snp_n"]):
        qc_rows[2]["status"] = "FAIL_LOW_DAR_SNP_N"
    pd.DataFrame(qc_rows).to_csv(QC_OUT, sep="\t", index=False)
    print(f"wrote={OUT}")
    print(f"wrote={QC_OUT}")


if __name__ == "__main__":
    main()
