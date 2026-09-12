#!/usr/bin/env python3
"""Run Phase 2 DAR enrichment in EUR-EAS heterogeneity with matched permutations."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import fisher_exact, mannwhitneyu


ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "config/PHASE2_ANALYSIS_FREEZE_v1.yaml"
FEATURES = ROOT / "data/processed/phase2/EUR_EAS_HETEROGENEITY_FEATURES.parquet"
OUT = ROOT / "results/phase2/PHASE2_DAR_HETEROGENEITY_ENRICHMENT.tsv"
NULL_OUT = ROOT / "results/phase2/PHASE2_DAR_MATCHED_PERMUTATION_NULL.tsv"


def fisher_row(data: pd.DataFrame, annotation: str, endpoint: str, label: str) -> dict[str, object]:
    case = data[annotation].eq(1)
    top = data[endpoint].astype(bool)
    table = [[int((case & top).sum()), int((case & ~top).sum())], [int((~case & top).sum()), int((~case & ~top).sum())]]
    odds_ratio, p_value = fisher_exact(table, alternative="two-sided")
    return {
        "analysis": label,
        "endpoint": endpoint,
        "annotation": annotation,
        "case_snp_n": int(case.sum()),
        "background_snp_n": int((~case).sum()),
        "case_top_n": table[0][0],
        "background_top_n": table[1][0],
        "case_top_fraction": table[0][0] / max(1, int(case.sum())),
        "background_top_fraction": table[1][0] / max(1, int((~case).sum())),
        "odds_ratio": odds_ratio,
        "p_value": p_value,
    }


def continuous_row(data: pd.DataFrame, annotation: str, label: str) -> dict[str, object]:
    case = data.loc[data[annotation].eq(1), "chi2_het"]
    background = data.loc[data[annotation].eq(0), "chi2_het"]
    stat, p_value = mannwhitneyu(case, background, alternative="two-sided")
    return {
        "analysis": label,
        "endpoint": "chi2_het_continuous",
        "annotation": annotation,
        "case_snp_n": int(len(case)),
        "background_snp_n": int(len(background)),
        "case_mean": float(case.mean()),
        "background_mean": float(background.mean()),
        "case_median": float(case.median()),
        "background_median": float(background.median()),
        "mean_difference": float(case.mean() - background.mean()),
        "mannwhitney_u": float(stat),
        "p_value": float(p_value),
    }


def permutation_test(data: pd.DataFrame, n_perm: int, seed: int) -> tuple[float, float, int, int, int, pd.DataFrame]:
    subset = data.loc[data["dar_global"].eq(1) | data["matched_non_dar_ocr"].eq(1)].copy()
    if subset.empty:
        raise RuntimeError("No DAR or matched non-DAR SNPs available for permutation")
    subset["case"] = subset["dar_global"].astype("int8")
    strata_cols = ["CHR", "maf_avg_decile", "maf_absdiff_quintile", "ld_base_decile", "ocr_status"]
    usable = subset.groupby(strata_cols, observed=True)["case"].transform("nunique").gt(1)
    subset = subset.loc[usable].copy().reset_index(drop=True)
    if subset["case"].sum() == 0 or subset["case"].sum() == len(subset):
        raise RuntimeError("Permutation strata removed all comparable DAR/non-DAR variation")

    permutation_snp_n = int(len(subset))
    permutation_case_n = int(subset["case"].sum())
    permutation_background_n = int(len(subset) - subset["case"].sum())
    observed = float(subset.loc[subset["case"].eq(1), "chi2_het"].mean() - subset.loc[subset["case"].eq(0), "chi2_het"].mean())
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm, dtype=float)
    groups = [idx.to_numpy() for _, idx in subset.groupby(strata_cols, observed=True).groups.items()]
    labels = subset["case"].to_numpy().copy()
    values = subset["chi2_het"].to_numpy()

    for i in range(n_perm):
        shuffled = labels.copy()
        for positions in groups:
            shuffled[positions] = rng.permutation(shuffled[positions])
        null[i] = values[shuffled == 1].mean() - values[shuffled == 0].mean()

    empirical_p = float((1 + np.sum(np.abs(null) >= abs(observed))) / (1 + n_perm))
    null_frame = pd.DataFrame({"permutation": np.arange(1, n_perm + 1), "null_mean_difference": null})
    return observed, empirical_p, permutation_snp_n, permutation_case_n, permutation_background_n, null_frame


def main() -> None:
    freeze = yaml.safe_load(FREEZE.read_text())
    params = freeze["primary_enrichment_test"]
    features = pd.read_parquet(FEATURES)

    endpoints = [params["primary_binary_endpoint"], *params["sensitivity_binary_endpoints"]]
    rows: list[dict[str, object]] = []
    retinal = features.loc[features["matched_non_dar_ocr"].eq(1) | features["dar_global"].eq(1)].copy()

    for endpoint in endpoints:
        rows.append(fisher_row(features, "dar_global", endpoint, "DAR_vs_genomewide_formal_universe"))
        rows.append(fisher_row(features.loc[features["ocr_union"].eq(1)].copy(), "dar_global", endpoint, "DAR_vs_all_retinal_OCR"))
        rows.append(fisher_row(retinal, "dar_global", endpoint, "DAR_vs_matched_non_DAR_retinal_OCR"))
    rows.append(continuous_row(features, "dar_global", "DAR_vs_genomewide_formal_universe"))
    rows.append(continuous_row(features.loc[features["ocr_union"].eq(1)].copy(), "dar_global", "DAR_vs_all_retinal_OCR"))
    rows.append(continuous_row(retinal, "dar_global", "DAR_vs_matched_non_DAR_retinal_OCR"))

    observed, empirical_p, permutation_snp_n, permutation_case_n, permutation_background_n, null_frame = permutation_test(
        features,
        int(params["permutation"]["n_permutations"]),
        int(params["permutation"]["random_seed"]),
    )
    rows.append(
        {
            "analysis": "DAR_vs_matched_non_DAR_retinal_OCR",
            "endpoint": "matched_permutation_mean_chi2_het_difference",
            "annotation": "dar_global",
            "case_snp_n": int(retinal["dar_global"].sum()),
            "background_snp_n": int(retinal["matched_non_dar_ocr"].sum()),
            "observed_mean_difference": observed,
            "empirical_p_value": empirical_p,
            "permutation_snp_n": permutation_snp_n,
            "permutation_case_snp_n": permutation_case_n,
            "permutation_background_snp_n": permutation_background_n,
            "n_permutations": int(params["permutation"]["n_permutations"]),
            "random_seed": int(params["permutation"]["random_seed"]),
            "strata": "|".join(params["permutation"]["strata"]),
        }
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, sep="\t", index=False)
    null_frame.to_csv(NULL_OUT, sep="\t", index=False)
    print(f"wrote={OUT}")
    print(f"wrote={NULL_OUT}")


if __name__ == "__main__":
    main()
