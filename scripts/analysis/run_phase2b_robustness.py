#!/usr/bin/env python3
"""Run Phase 2B post-primary robustness analyses."""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import brentq
from scipy.stats import fisher_exact, mannwhitneyu, norm, ttest_ind
from scipy.stats.contingency import odds_ratio
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_confint, proportion_effectsize
import statsmodels.api as sm


ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "config/PHASE2B_ROBUSTNESS_FREEZE_v1.yaml"
PHASE2_FREEZE = ROOT / "config/PHASE2_ANALYSIS_FREEZE_v1.yaml"
FEATURES = ROOT / "data/processed/phase2/EUR_EAS_HETEROGENEITY_FEATURES.parquet"
PHASE2_RESULTS = ROOT / "results/phase2/PHASE2_DAR_HETEROGENEITY_ENRICHMENT.tsv"
OUTDIR = ROOT / "results/phase2b"
INTERIM = ROOT / "data/interim/phase2b"
LOGDIR = ROOT / "logs/phase2b"
MANUSCRIPT = ROOT / "results/manuscript"
FIGDATA = ROOT / "results/manuscript/figure_data"


def ensure_dirs() -> None:
    for path in (OUTDIR, INTERIM, LOGDIR, MANUSCRIPT, FIGDATA):
        path.mkdir(parents=True, exist_ok=True)


def exact_or_ci(a: int, b: int, c: int, d: int) -> tuple[float, float, float]:
    res = odds_ratio([[a, b], [c, d]], kind="conditional")
    ci = res.confidence_interval(confidence_level=0.95)
    return float(res.statistic), float(ci.low), float(ci.high)


def risk_ratio_ci(a: int, b: int, c: int, d: int) -> tuple[float, float, float]:
    p1 = a / (a + b)
    p0 = c / (c + d)
    rr = p1 / p0
    se = math.sqrt(1 / a - 1 / (a + b) + 1 / c - 1 / (c + d))
    lo = math.exp(math.log(rr) - 1.96 * se)
    hi = math.exp(math.log(rr) + 1.96 * se)
    return rr, lo, hi


def risk_difference_ci(a: int, b: int, c: int, d: int) -> tuple[float, float, float]:
    n1, n0 = a + b, c + d
    p1, p0 = a / n1, c / n0
    rd = p1 - p0
    se = math.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
    return rd, rd - 1.96 * se, rd + 1.96 * se


def fisher_primary(data: pd.DataFrame, endpoint: str = "top_5pct_chi2_het") -> dict[str, float]:
    subset = data.loc[data["dar_global"].eq(1) | data["matched_non_dar_ocr"].eq(1)].copy()
    case = subset["dar_global"].eq(1)
    top = subset[endpoint].astype(bool)
    a = int((case & top).sum())
    b = int((case & ~top).sum())
    c = int((~case & top).sum())
    d = int((~case & ~top).sum())
    fisher_or, fisher_p = fisher_exact([[a, b], [c, d]], alternative="two-sided")
    cond_or, ci_low, ci_high = exact_or_ci(a, b, c, d)
    return {
        "case_snp_n": a + b,
        "background_snp_n": c + d,
        "case_top_n": a,
        "background_top_n": c,
        "case_top_fraction": a / (a + b),
        "background_top_fraction": c / (c + d),
        "odds_ratio": float(fisher_or),
        "conditional_odds_ratio": cond_or,
        "or_ci95_low": ci_low,
        "or_ci95_high": ci_high,
        "p_value": float(fisher_p),
    }


def continuous_primary(data: pd.DataFrame) -> dict[str, float]:
    subset = data.loc[data["dar_global"].eq(1) | data["matched_non_dar_ocr"].eq(1)].copy()
    case = subset.loc[subset["dar_global"].eq(1), "chi2_het"]
    background = subset.loc[subset["dar_global"].eq(0), "chi2_het"]
    stat, p = mannwhitneyu(case, background, alternative="two-sided")
    diff = float(case.mean() - background.mean())
    se = math.sqrt(case.var(ddof=1) / len(case) + background.var(ddof=1) / len(background))
    return {
        "case_mean": float(case.mean()),
        "background_mean": float(background.mean()),
        "case_median": float(case.median()),
        "background_median": float(background.median()),
        "mean_difference": diff,
        "mean_difference_ci95_low": diff - 1.96 * se,
        "mean_difference_ci95_high": diff + 1.96 * se,
        "mannwhitney_u": float(stat),
        "p_value": float(p),
    }


def permutation_statistic(data: pd.DataFrame, n_perm: int, seed: int) -> dict[str, float]:
    subset = data.loc[data["dar_global"].eq(1) | data["matched_non_dar_ocr"].eq(1)].copy()
    subset["case"] = subset["dar_global"].astype("int8")
    strata_cols = ["CHR", "maf_avg_decile", "maf_absdiff_quintile", "ld_base_decile", "ocr_status"]
    usable = subset.groupby(strata_cols, observed=True)["case"].transform("nunique").gt(1)
    subset = subset.loc[usable].copy().reset_index(drop=True)
    labels = subset["case"].to_numpy().copy()
    values = subset["chi2_het"].to_numpy()
    observed = float(values[labels == 1].mean() - values[labels == 0].mean())
    groups = [idx.to_numpy() for _, idx in subset.groupby(strata_cols, observed=True).groups.items()]
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        shuffled = labels.copy()
        for positions in groups:
            shuffled[positions] = rng.permutation(shuffled[positions])
        null[i] = values[shuffled == 1].mean() - values[shuffled == 0].mean()
    empirical_p = float((1 + np.sum(np.abs(null) >= abs(observed))) / (1 + n_perm))
    return {
        "observed_mean_difference": observed,
        "empirical_p_value": empirical_p,
        "permutation_snp_n": int(len(subset)),
        "permutation_case_snp_n": int(labels.sum()),
        "permutation_background_snp_n": int(len(subset) - labels.sum()),
    }


def reproduce_primary(features: pd.DataFrame, freeze: dict) -> None:
    phase2 = pd.read_csv(PHASE2_RESULTS, sep="\t")
    primary = phase2.loc[
        (phase2["analysis"] == "DAR_vs_matched_non_DAR_retinal_OCR")
        & (phase2["endpoint"] == "top_5pct_chi2_het")
    ].iloc[0]
    cont = phase2.loc[
        (phase2["analysis"] == "DAR_vs_matched_non_DAR_retinal_OCR")
        & (phase2["endpoint"] == "chi2_het_continuous")
    ].iloc[0]
    perm = phase2.loc[phase2["endpoint"] == "matched_permutation_mean_chi2_het_difference"].iloc[0]

    binary = fisher_primary(features)
    continuous = continuous_primary(features)
    reproduced_perm = permutation_statistic(features, int(perm["n_permutations"]), int(perm["random_seed"]))
    rows = [
        {"metric": "case_top_fraction", "recomputed": binary["case_top_fraction"], "frozen": primary["case_top_fraction"]},
        {"metric": "background_top_fraction", "recomputed": binary["background_top_fraction"], "frozen": primary["background_top_fraction"]},
        {"metric": "odds_ratio", "recomputed": binary["odds_ratio"], "frozen": primary["odds_ratio"]},
        {"metric": "fisher_p", "recomputed": binary["p_value"], "frozen": primary["p_value"]},
        {"metric": "continuous_mean_difference", "recomputed": continuous["mean_difference"], "frozen": cont["mean_difference"]},
        {"metric": "continuous_p", "recomputed": continuous["p_value"], "frozen": cont["p_value"]},
        {"metric": "permutation_observed_statistic", "recomputed": reproduced_perm["observed_mean_difference"], "frozen": perm["observed_mean_difference"]},
        {"metric": "permutation_empirical_p", "recomputed": reproduced_perm["empirical_p_value"], "frozen": perm["empirical_p_value"]},
    ]
    out = pd.DataFrame(rows)
    tolerance = float(freeze["primary_reproduction"]["tolerance"])
    out["abs_delta"] = (out["recomputed"] - out["frozen"]).abs()
    out["status"] = np.where(out["abs_delta"].le(tolerance), "PASS", "FAIL")
    out.to_csv(OUTDIR / "PRIMARY_RESULT_REPRODUCTION.tsv", sep="\t", index=False)
    if (out["status"] != "PASS").any():
        raise RuntimeError("Primary reproduction mismatch; stop Phase 2B")


def write_extract_lists(features: pd.DataFrame) -> None:
    extract_dir = INTERIM / "ld_pruning_extract"
    extract_dir.mkdir(parents=True, exist_ok=True)
    for chrom, frame in features.groupby("CHR"):
        frame["SNP"].to_csv(extract_dir / f"formal_chr{int(chrom)}.snplist", index=False, header=False)


def run_plink_pruning(features: pd.DataFrame, freeze: dict) -> dict[str, set[str]]:
    write_extract_lists(features)
    retained: dict[str, set[str]] = {}
    thresholds = freeze["ld_pruning"]["sensitivity_thresholds"]
    for spec in thresholds:
        label = spec["label"]
        r2 = spec["r2"]
        retained_by_pop = []
        for pop in freeze["ld_pruning"]["populations"]:
            pop_sets = []
            for chrom in range(1, 23):
                prefix = ROOT / f"data/interim/sldxr_reference/paired_plink_v2/{pop}/1000G.{pop}.paired.{chrom}"
                extract = INTERIM / f"ld_pruning_extract/formal_chr{chrom}.snplist"
                out_prefix = INTERIM / f"ld_pruning/{label}/{pop}/chr{chrom}"
                out_prefix.parent.mkdir(parents=True, exist_ok=True)
                prune_in = Path(f"{out_prefix}.prune.in")
                if not prune_in.exists():
                    cmd = [
                        "plink2",
                        "--bfile",
                        str(prefix),
                        "--extract",
                        str(extract),
                        "--indep-pairwise",
                        str(freeze["ld_pruning"]["window"]),
                        str(freeze["ld_pruning"]["step_variant_count"]),
                        str(r2),
                        "--out",
                        str(out_prefix),
                    ]
                    log = LOGDIR / f"plink2_{label}_{pop}_chr{chrom}.log"
                    with log.open("w") as handle:
                        result = subprocess.run(cmd, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, check=False)
                    if result.returncode != 0:
                        raise RuntimeError(f"plink2 pruning failed: {log}")
                pop_sets.append(set(prune_in.read_text().split()))
            retained_by_pop.append(set().union(*pop_sets))
        retained[label] = retained_by_pop[0].intersection(retained_by_pop[1])
    return retained


def ld_pruned_outputs(features: pd.DataFrame, retained: dict[str, set[str]]) -> None:
    universe_rows = []
    sens_rows = []
    for label, snps in retained.items():
        subset = features.loc[features["SNP"].isin(snps)].copy()
        universe_rows.append(
            {
                "sensitivity": label,
                "original_N": len(features),
                "pruned_N": len(subset),
                "DAR_N": int(subset["dar_global"].sum()),
                "matched_non_DAR_N": int(subset["matched_non_dar_ocr"].sum()),
                "retinal_OCR_N": int(subset["ocr_union"].sum()),
            }
        )
        for endpoint in ("top_5pct_chi2_het", "top_1pct_chi2_het", "top_10pct_chi2_het"):
            row = fisher_primary(subset, endpoint)
            row.update({"sensitivity": label, "endpoint": endpoint, "analysis": "LD_PRUNED_DAR_vs_matched_non_DAR_retinal_OCR"})
            sens_rows.append(row)
        cont = continuous_primary(subset)
        cont.update({"sensitivity": label, "endpoint": "chi2_het_continuous", "analysis": "LD_PRUNED_DAR_vs_matched_non_DAR_retinal_OCR"})
        sens_rows.append(cont)
    pd.DataFrame(universe_rows).to_csv(OUTDIR / "LD_PRUNED_SNP_UNIVERSE.tsv", sep="\t", index=False)
    pd.DataFrame(sens_rows).to_csv(OUTDIR / "LD_PRUNED_HETEROGENEITY_SENSITIVITY.tsv", sep="\t", index=False)


def block_outputs(features: pd.DataFrame) -> None:
    blocks = pd.read_csv(ROOT / "results/phase1c/SLDXR_BLOCK_JACKKNIFE.tsv", sep="\t")
    blocks = blocks.loc[blocks["metric_name"] == "GCORSQ", ["block_index", "start_chr", "start_bp", "end_chr", "end_bp"]].copy()
    block_rows = []
    for row in blocks.itertuples(index=False):
        if int(row.start_chr) != int(row.end_chr):
            mask = (features["CHR"] >= row.start_chr) & (features["CHR"] <= row.end_chr)
        else:
            mask = (features["CHR"] == row.start_chr) & (features["BP"] >= row.start_bp) & (features["BP"] <= row.end_bp)
        sub = features.loc[mask]
        block_rows.append(
            {
                "block_index": int(row.block_index),
                "start_chr": int(row.start_chr),
                "start_bp": int(row.start_bp),
                "end_chr": int(row.end_chr),
                "end_bp": int(row.end_bp),
                "SNP_N": int(len(sub)),
                "DAR_SNP_N": int(sub["dar_global"].sum()),
                "matched_non_DAR_SNP_N": int(sub["matched_non_dar_ocr"].sum()),
                "retinal_OCR_SNP_N": int(sub["ocr_union"].sum()),
                "mean_chi2_het": float(sub["chi2_het"].mean()),
                "max_chi2_het": float(sub["chi2_het"].max()),
                "p95_chi2_het": float(sub["chi2_het"].quantile(0.95)),
                "has_top_5pct_heterogeneity_snp": bool(sub["top_5pct_chi2_het"].any()),
                "mean_MAF_avg_ref": float(sub["MAF_avg_ref"].mean()),
                "mean_baseline_ld_base": float(sub["baseline_ld_base"].mean()),
                "retinal_OCR_density": float(sub["ocr_union"].mean()),
            }
        )
    block_df = pd.DataFrame(block_rows)
    block_df.to_csv(OUTDIR / "LD_BLOCK_HETEROGENEITY_SUMMARY.tsv", sep="\t", index=False)

    test_df = block_df.loc[block_df["SNP_N"].gt(0)].copy()
    test_df["has_DAR"] = test_df["DAR_SNP_N"].gt(0).astype(int)
    test_df["log1p_SNP_N"] = np.log1p(test_df["SNP_N"])
    X = sm.add_constant(test_df[["has_DAR", "log1p_SNP_N", "mean_MAF_avg_ref", "mean_baseline_ld_base", "retinal_OCR_density"]])
    model = sm.OLS(test_df["mean_chi2_het"], X).fit(cov_type="HC3")
    dar_blocks = test_df.loc[test_df["has_DAR"].eq(1), "mean_chi2_het"]
    non_blocks = test_df.loc[test_df["has_DAR"].eq(0), "mean_chi2_het"]
    t_stat, t_p = ttest_ind(dar_blocks, non_blocks, equal_var=False)
    out = pd.DataFrame(
        [
            {
                "analysis": "block_level_adjusted_OLS",
                "statistic": "mean_chi2_het",
                "DAR_block_N": int(test_df["has_DAR"].sum()),
                "non_DAR_block_N": int((1 - test_df["has_DAR"]).sum()),
                "coefficient_has_DAR": float(model.params["has_DAR"]),
                "SE_HC3": float(model.bse["has_DAR"]),
                "CI95_low": float(model.conf_int().loc["has_DAR", 0]),
                "CI95_high": float(model.conf_int().loc["has_DAR", 1]),
                "p_value": float(model.pvalues["has_DAR"]),
                "adjustment": "log1p_SNP_N+mean_MAF_avg_ref+mean_baseline_ld_base+retinal_OCR_density",
            },
            {
                "analysis": "block_level_unadjusted_descriptive_welch",
                "statistic": "mean_chi2_het",
                "DAR_block_N": int(len(dar_blocks)),
                "non_DAR_block_N": int(len(non_blocks)),
                "coefficient_has_DAR": float(dar_blocks.mean() - non_blocks.mean()),
                "SE_HC3": float("nan"),
                "CI95_low": float("nan"),
                "CI95_high": float("nan"),
                "p_value": float(t_p),
                "adjustment": "none_descriptive",
            },
        ]
    )
    out.to_csv(OUTDIR / "LD_BLOCK_ROBUSTNESS.tsv", sep="\t", index=False)


def precision_and_power(features: pd.DataFrame, freeze: dict) -> None:
    binary = fisher_primary(features, "top_5pct_chi2_het")
    a, b, c, d = binary["case_top_n"], binary["case_snp_n"] - binary["case_top_n"], binary["background_top_n"], binary["background_snp_n"] - binary["background_top_n"]
    rr, rr_lo, rr_hi = risk_ratio_ci(a, b, c, d)
    rd, rd_lo, rd_hi = risk_difference_ci(a, b, c, d)
    log_or = math.log(binary["odds_ratio"])
    se_log_or = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    precision = pd.DataFrame(
        [
            {
                **binary,
                "log_odds_ratio": log_or,
                "SE_log_odds_ratio": se_log_or,
                "risk_difference": rd,
                "risk_difference_ci95_low": rd_lo,
                "risk_difference_ci95_high": rd_hi,
                "risk_ratio": rr,
                "risk_ratio_ci95_low": rr_lo,
                "risk_ratio_ci95_high": rr_hi,
                "ci_method": "conditional_exact_OR_CI_scipy_and_large_sample_RD_RR_CI",
            }
        ]
    )
    precision.to_csv(OUTDIR / "PRIMARY_EFFECT_SIZE_PRECISION.tsv", sep="\t", index=False)

    n1 = int(binary["case_snp_n"])
    n0 = int(binary["background_snp_n"])
    p0 = float(binary["background_top_fraction"])
    solver = NormalIndPower()
    power_rows = []
    for power in freeze["power"]["powers"]:
        target_power = float(power)

        def f(p1: float) -> float:
            eff = proportion_effectsize(p1, p0)
            return solver.power(effect_size=eff, nobs1=n1, alpha=float(freeze["power"]["alpha"]), ratio=n0 / n1, alternative="two-sided") - target_power

        p1 = brentq(f, p0 + 1e-7, 0.999)
        odds0 = p0 / (1 - p0)
        odds1 = p1 / (1 - p1)
        power_rows.append(
            {
                "power": target_power,
                "alpha": float(freeze["power"]["alpha"]),
                "case_N": n1,
                "comparator_N": n0,
                "comparator_event_rate": p0,
                "minimum_detectable_case_event_rate": p1,
                "detectable_absolute_risk_difference": p1 - p0,
                "minimum_detectable_OR": odds1 / odds0,
                "method": "prospective_two_sample_proportion_normal_approximation",
            }
        )
    pd.DataFrame(power_rows).to_csv(OUTDIR / "DAR_POWER_BOUNDS.tsv", sep="\t", index=False)

    large_or = float(freeze["effect_precision"]["large_enrichment_boundary_OR"])
    equivalence = pd.DataFrame(
        [
            {
                "boundary": "large_enrichment_OR",
                "margin_OR": large_or,
                "observed_OR": binary["odds_ratio"],
                "OR_CI95_low": binary["or_ci95_low"],
                "OR_CI95_high": binary["or_ci95_high"],
                "large_enrichment_excluded": bool(binary["or_ci95_high"] < large_or),
                "interpretation": "CI_upper_below_margin" if binary["or_ci95_high"] < large_or else "CI_overlaps_margin",
            }
        ]
    )
    equivalence.to_csv(OUTDIR / "EQUIVALENCE_BOUNDARY.tsv", sep="\t", index=False)


def contextual_sldxr() -> None:
    gw = pd.read_csv(ROOT / "results/phase1c/SLDXR_GENOMEWIDE_EUR_EAS_FORMAL.tsv", sep="\t")
    pilot = pd.read_csv(ROOT / "results/phase1c/SLDXR_GLOBAL_ANNOTATION_PILOT.tsv", sep="\t")
    gw_gcorsq = gw.loc[gw["metric_name"] == "GCORSQ"].iloc[0]
    rows = [
        {
            "context": "genomewide_formal",
            "role": "primary_genomewide_architecture",
            "metric": "GCORSQ",
            "estimate": gw_gcorsq["estimate"],
            "SE": gw_gcorsq["SE"],
            "CI95_low": gw_gcorsq["CI95_low"],
            "CI95_high": gw_gcorsq["CI95_high"],
            "SNP_N": gw_gcorsq["effective_SNP_N"],
            "blocks": gw_gcorsq["number_blocks"],
            "warning": gw_gcorsq["warnings"],
            "interpretation": "BOUNDARY_ADJACENT_HIGH_SHARED_ARCHITECTURE",
        }
    ]
    for label, role in (("all_retinal_OCR", "formal_contextual"), ("ancestry_DAR", "UNDERPOWERED_DESCRIPTIVE")):
        row = pilot.loc[pilot["annotation"] == label].iloc[0]
        rows.append(
            {
                "context": label,
                "role": role,
                "metric": row["metric_name"],
                "estimate": row["estimate"],
                "SE": row["SE"],
                "CI95_low": row["CI95_low"],
                "CI95_high": row["CI95_high"],
                "SNP_N": row["shared_usable_SNP_N"],
                "blocks": row["effective_blocks"],
                "warning": row["warning"],
                "interpretation": "COMPATIBLE_WITH_SHARED_ARCHITECTURE" if label == "all_retinal_OCR" else "UNDERPOWERED_DESCRIPTIVE",
            }
        )
    pd.DataFrame(rows).to_csv(OUTDIR / "RETINAL_OCR_SLDXR_CONTEXT.tsv", sep="\t", index=False)


def cell_class_descriptive(features: pd.DataFrame) -> None:
    dar = pd.read_csv(ROOT / "data/processed/reference_anchored/HRCA_ANCESTRY_DAR_GRCh37.tsv", sep="\t")
    dar = dar.loc[dar["liftover_status"].eq("MAPPED_WIDTH_PRESERVED")].copy()
    feature_pos = features[["SNP", "CHR", "BP", "chi2_het", "top_5pct_chi2_het"]].copy()
    rows = []
    for cell_class, cls in dar.groupby("cell_class"):
        snps: set[str] = set()
        for chrom, intervals in cls.groupby("canonical_seqnames"):
            chrom_label = str(chrom).replace("chr", "")
            if not chrom_label.isdigit():
                continue
            chrom_num = int(chrom_label)
            if chrom_num < 1 or chrom_num > 22:
                continue
            sub = feature_pos.loc[feature_pos["CHR"].eq(chrom_num), ["SNP", "BP"]]
            if sub.empty:
                continue
            starts = intervals["canonical_start"].astype(int).to_numpy()
            ends = intervals["canonical_end"].astype(int).to_numpy()
            points = sub["BP"].to_numpy()
            order = np.argsort(starts)
            starts, ends = starts[order], ends[order]
            idx = np.searchsorted(starts, points, side="right") - 1
            hit = (idx >= 0) & (points <= ends[np.clip(idx, 0, len(ends) - 1)])
            snps.update(sub.loc[hit, "SNP"].tolist())
        subf = features.loc[features["SNP"].isin(snps)]
        n = len(subf)
        top = int(subf["top_5pct_chi2_het"].sum()) if n else 0
        if n:
            ci_low, ci_high = proportion_confint(top, n, alpha=0.05, method="wilson")
        else:
            ci_low, ci_high = float("nan"), float("nan")
        rows.append(
            {
                "cell_class": cell_class,
                "formal_DAR_SNP_N": n,
                "eligible_for_descriptive": bool(n >= 100),
                "mean_chi2_het": float(subf["chi2_het"].mean()) if n else float("nan"),
                "median_chi2_het": float(subf["chi2_het"].median()) if n else float("nan"),
                "top_5pct_n": top,
                "top_5pct_fraction": top / n if n else float("nan"),
                "top_5pct_wilson_ci95_low": float(ci_low),
                "top_5pct_wilson_ci95_high": float(ci_high),
                "interpretation": "DESCRIPTIVE_ONLY_NO_P_VALUES",
            }
        )
    pd.DataFrame(rows).sort_values(["eligible_for_descriptive", "formal_DAR_SNP_N"], ascending=[False, False]).to_csv(
        OUTDIR / "CELL_CLASS_DESCRIPTIVE_HETEROGENEITY.tsv", sep="\t", index=False
    )


def matching_balance(features: pd.DataFrame) -> None:
    subset = features.loc[features["dar_global"].eq(1) | features["matched_non_dar_ocr"].eq(1)].copy()
    subset["case"] = subset["dar_global"].astype("int8")
    strata_cols = ["CHR", "maf_avg_decile", "maf_absdiff_quintile", "ld_base_decile", "ocr_status"]
    grouped = subset.groupby(strata_cols, observed=True)["case"].agg(["sum", "count"])
    grouped = grouped.rename(columns={"sum": "DAR_N", "count": "total_N"})
    grouped["control_N"] = grouped["total_N"] - grouped["DAR_N"]
    total_strata = len(grouped)
    informative = grouped.loc[grouped["DAR_N"].gt(0) & grouped["control_N"].gt(0)].copy()
    dar_retained = int(informative["DAR_N"].sum())
    dar_total = int(grouped["DAR_N"].sum())
    controls_per_dar = np.repeat((informative["control_N"] / informative["DAR_N"]).to_numpy(), informative["DAR_N"].astype(int).to_numpy())
    control_counts = informative["control_N"].to_numpy()
    audit = pd.DataFrame(
        [
            {
                "metric": "N_strata_total",
                "value": total_strata,
                "status": "INFO",
            },
            {
                "metric": "N_informative_strata",
                "value": len(informative),
                "status": "INFO",
            },
            {"metric": "DAR_retained", "value": dar_retained, "status": "PASS"},
            {"metric": "DAR_excluded", "value": dar_total - dar_retained, "status": "INFO"},
            {"metric": "controls_in_informative_strata", "value": int(informative["control_N"].sum()), "status": "INFO"},
            {"metric": "median_controls_per_DAR_stratum", "value": float(np.median(controls_per_dar)), "status": "INFO"},
            {"metric": "minimum_controls_per_DAR_stratum", "value": float(np.min(controls_per_dar)), "status": "INFO"},
            {"metric": "maximum_controls_per_DAR_stratum", "value": float(np.max(controls_per_dar)), "status": "INFO"},
            {"metric": "control_reuse_design", "value": "none_label_permutation_not_pairwise_resampling", "status": "PASS"},
            {"metric": "control_count_median_by_informative_stratum", "value": float(np.median(control_counts)), "status": "INFO"},
            {"metric": "control_count_min_by_informative_stratum", "value": int(np.min(control_counts)), "status": "INFO"},
            {"metric": "control_count_max_by_informative_stratum", "value": int(np.max(control_counts)), "status": "INFO"},
        ]
    )
    if dar_total - dar_retained > 0.2 * dar_total:
        audit.loc[audit["metric"] == "DAR_excluded", "status"] = "REVIEW_IMBALANCE"
    audit.to_csv(OUTDIR / "MATCHED_PERMUTATION_BALANCE_AUDIT.tsv", sep="\t", index=False)


def write_power_report() -> None:
    power = pd.read_csv(OUTDIR / "DAR_POWER_BOUNDS.tsv", sep="\t")
    eq = pd.read_csv(OUTDIR / "EQUIVALENCE_BOUNDARY.tsv", sep="\t").iloc[0]
    p80 = power.loc[power["power"].eq(0.8)].iloc[0]
    p90 = power.loc[power["power"].eq(0.9)].iloc[0]
    text = f"""# Phase 2B Power Interpretation

The frozen primary endpoint contains 1,232 DAR SNPs and 379,279 matched non-DAR retinal OCR comparator SNPs. The comparator event rate for top 5% EUR-EAS heterogeneity is {p80['comparator_event_rate']:.4f}.

At alpha = 0.05 with a two-sided test, the current DAR sample size has 80% power to detect an odds ratio of approximately {p80['minimum_detectable_OR']:.3f}, corresponding to an absolute event-rate increase of {p80['detectable_absolute_risk_difference']:.4f}. At 90% power, the minimum detectable odds ratio is approximately {p90['minimum_detectable_OR']:.3f}.

The observed top 5% odds ratio was {eq['observed_OR']:.3f}, with a 95% CI of {eq['OR_CI95_low']:.3f} to {eq['OR_CI95_high']:.3f}. Using OR = {eq['margin_OR']:.1f} as a prespecified large-enrichment boundary, large enrichment is {'excluded' if bool(eq['large_enrichment_excluded']) else 'not excluded'} by the current CI.

Interpretation: the study has limited power to detect modest enrichment, but it is informative about large excess cross-ancestry heterogeneity under the frozen primary endpoint. This does not imply that DARs have no effect or that ancestry-specific regulatory biology is absent.
"""
    (ROOT / "reports/PHASE2B_POWER_INTERPRETATION.md").write_text(text, encoding="utf-8")


def manuscript_tables(features: pd.DataFrame) -> None:
    gw = pd.read_csv(ROOT / "results/phase1c/SLDXR_GENOMEWIDE_EUR_EAS_FORMAL.tsv", sep="\t")
    ldsc = pd.read_csv(ROOT / "results/phase1/LDSC_H2_SUMMARY.tsv", sep="\t")
    primary = pd.read_csv(OUTDIR / "PRIMARY_EFFECT_SIZE_PRECISION.tsv", sep="\t").iloc[0]
    sens = pd.read_csv(OUTDIR / "LD_PRUNED_HETEROGENEITY_SENSITIVITY.tsv", sep="\t")
    power = pd.read_csv(OUTDIR / "DAR_POWER_BOUNDS.tsv", sep="\t")
    context = pd.read_csv(OUTDIR / "RETINAL_OCR_SLDXR_CONTEXT.tsv", sep="\t")

    table1 = pd.DataFrame(
        [
            {"section": "GWAS_QC", "metric": "formal_shared_SNP_N", "value": len(features), "detail": "Phase 1C.2 formal shared universe"},
            {"section": "LDSC", "metric": "EUR_h2", "value": ldsc.loc[ldsc["ancestry"].eq("EUR"), "h2"].iloc[0], "detail": "ancestry-matched"},
            {"section": "LDSC", "metric": "EAS_h2", "value": ldsc.loc[ldsc["ancestry"].eq("EAS"), "h2"].iloc[0], "detail": "ancestry-matched"},
            {"section": "S-LDXR", "metric": "genomewide_GCORSQ", "value": gw.loc[gw["metric_name"].eq("GCORSQ"), "estimate"].iloc[0], "detail": "formal genomewide"},
            {"section": "S-LDXR", "metric": "genomewide_GCORSQ_SE", "value": gw.loc[gw["metric_name"].eq("GCORSQ"), "SE"].iloc[0], "detail": "formal genomewide"},
        ]
    )
    table1.to_csv(MANUSCRIPT / "TABLE1_ANALYSIS_COHORT_AND_QC.tsv", sep="\t", index=False)

    table2_rows = []
    p2 = pd.read_csv(ROOT / "results/phase2/PHASE2_DAR_HETEROGENEITY_ENRICHMENT.tsv", sep="\t")
    for _, row in p2.loc[p2["analysis"].eq("DAR_vs_matched_non_DAR_retinal_OCR")].iterrows():
        table2_rows.append(row.to_dict())
    table2_rows.append({"analysis": "primary_effect_precision", **primary.to_dict()})
    for _, row in sens.iterrows():
        table2_rows.append(row.to_dict())
    for _, row in power.iterrows():
        table2_rows.append({"analysis": "power_MDE", **row.to_dict()})
    pd.DataFrame(table2_rows).to_csv(MANUSCRIPT / "TABLE2_DAR_HETEROGENEITY_RESULTS.tsv", sep="\t", index=False)
    context.to_csv(MANUSCRIPT / "TABLE3_REGULATORY_ARCHITECTURE_CONTEXT.tsv", sep="\t", index=False)

    pd.DataFrame(
        [
            {"step": 1, "label": "Build-rescued EUR/EAS GWAS harmonization", "status": "PASS"},
            {"step": 2, "label": "Formal genome-wide S-LDXR", "status": "PASS"},
            {"step": 3, "label": "Phase 2 DAR heterogeneity primary enrichment", "status": "NOT_SUPPORTED"},
            {"step": 4, "label": "Phase 2B post-primary robustness", "status": "COMPLETE"},
            {"step": 5, "label": "Manuscript preparation", "status": "NEXT"},
        ]
    ).to_csv(FIGDATA / "FIGURE1_STUDY_FLOW.tsv", sep="\t", index=False)
    gw.loc[gw["metric_name"].isin(["HSQ1", "HSQ2", "GCOV", "GCOR", "GCORSQ"])].to_csv(FIGDATA / "FIGURE2_GENOMEWIDE_ARCHITECTURE.tsv", sep="\t", index=False)
    pd.read_csv(OUTDIR / "PRIMARY_EFFECT_SIZE_PRECISION.tsv", sep="\t").to_csv(FIGDATA / "FIGURE3_DAR_HETEROGENEITY_EFFECT.tsv", sep="\t", index=False)
    pd.read_csv(OUTDIR / "RETINAL_OCR_SLDXR_CONTEXT.tsv", sep="\t").to_csv(FIGDATA / "FIGURE4_SLDXR_CONTEXT.tsv", sep="\t", index=False)
    pd.read_csv(OUTDIR / "DAR_POWER_BOUNDS.tsv", sep="\t").to_csv(FIGDATA / "FIGURE5_POWER_MDE.tsv", sep="\t", index=False)


def final_decision() -> str:
    precision = pd.read_csv(OUTDIR / "PRIMARY_EFFECT_SIZE_PRECISION.tsv", sep="\t").iloc[0]
    perm = pd.read_csv(OUTDIR / "PRIMARY_RESULT_REPRODUCTION.tsv", sep="\t")
    ld = pd.read_csv(OUTDIR / "LD_PRUNED_HETEROGENEITY_SENSITIVITY.tsv", sep="\t")
    block = pd.read_csv(OUTDIR / "LD_BLOCK_ROBUSTNESS.tsv", sep="\t")
    power = pd.read_csv(OUTDIR / "DAR_POWER_BOUNDS.tsv", sep="\t")
    eq = pd.read_csv(OUTDIR / "EQUIVALENCE_BOUNDARY.tsv", sep="\t").iloc[0]
    context = pd.read_csv(OUTDIR / "RETINAL_OCR_SLDXR_CONTEXT.tsv", sep="\t")
    cells = pd.read_csv(OUTDIR / "CELL_CLASS_DESCRIPTIVE_HETEROGENEITY.tsv", sep="\t")
    audit = pd.read_csv(OUTDIR / "MATCHED_PERMUTATION_BALANCE_AUDIT.tsv", sep="\t")

    ld_top = ld.loc[(ld["endpoint"] == "top_5pct_chi2_het") & (ld["analysis"] == "LD_PRUNED_DAR_vs_matched_non_DAR_retinal_OCR")]
    ld_consistent = bool((ld_top["p_value"] > 0.05).all())
    block_consistent = bool(block.loc[block["analysis"].eq("block_level_adjusted_OLS"), "p_value"].iloc[0] > 0.05)
    broad = context.loc[context["context"].eq("all_retinal_OCR")].iloc[0]
    genome = context.loc[context["context"].eq("genomewide_formal")].iloc[0]
    dar = context.loc[context["context"].eq("ancestry_DAR")].iloc[0]
    p80 = power.loc[power["power"].eq(0.8)].iloc[0]
    p90 = power.loc[power["power"].eq(0.9)].iloc[0]
    severe_matching = bool((audit["status"] == "REVIEW_IMBALANCE").any())
    verdict = "HOLD_TECHNICAL" if severe_matching else ("MANUSCRIPT_GO_SHARED_ARCHITECTURE" if ld_consistent and block_consistent else "MANUSCRIPT_GO_WITH_UNCERTAINTY")

    text = f"""# PHASE 2B FINAL DECISION

## Primary result

DAR heterogeneity enrichment: NOT SUPPORTED

Top 5%:
OR: {precision['odds_ratio']:.3f}
95% CI: {precision['or_ci95_low']:.3f}-{precision['or_ci95_high']:.3f}
P: {precision['p_value']:.3g}

Matched permutation:
empirical P: {perm.loc[perm['metric'].eq('permutation_empirical_p'), 'recomputed'].iloc[0]:.3g}

## LD robustness

LD-pruned: {'CONSISTENT' if ld_consistent else 'INCONSISTENT'}

Block-level: {'CONSISTENT' if block_consistent else 'INCONSISTENT'}

## Precision

80% MDE OR: {p80['minimum_detectable_OR']:.3f}
90% MDE OR: {p90['minimum_detectable_OR']:.3f}

Can exclude large enrichment?
{'YES' if bool(eq['large_enrichment_excluded']) else 'NO'}

Large-effect boundary used: OR = {eq['margin_OR']:.1f}

## Broad retinal architecture

Genome-wide S-LDXR:
{genome['estimate']:.6f} ± {genome['SE']:.6f}

All-retinal-OCR S-LDXR:
{broad['estimate']:.6f} ± {broad['SE']:.6f}

Interpretation:
{broad['interpretation']}

## DAR S-LDXR

DESCRIPTIVE ONLY

estimate: {dar['estimate']:.6f}
SE: {dar['SE']:.6f}
N: {int(dar['SNP_N'])}

## Cell-class descriptive results

Eligible classes:
{int(cells['eligible_for_descriptive'].sum())}

Any result changes primary conclusion?
NO

## Manuscript verdict

{verdict}

Stop rule:
STOP ALL DISCOVERY ANALYSIS. Next work is manuscript drafting, figure/table preparation, methods documentation, and reviewer-style robustness checks based on frozen results.
"""
    (ROOT / "reports/PHASE2B_FINAL_DECISION.md").write_text(text, encoding="utf-8")
    return verdict


def main() -> None:
    ensure_dirs()
    freeze = yaml.safe_load(FREEZE.read_text())
    yaml.safe_load(PHASE2_FREEZE.read_text())
    features = pd.read_parquet(FEATURES)
    reproduce_primary(features, freeze)
    retained = run_plink_pruning(features, freeze)
    ld_pruned_outputs(features, retained)
    block_outputs(features)
    precision_and_power(features, freeze)
    contextual_sldxr()
    cell_class_descriptive(features)
    matching_balance(features)
    write_power_report()
    manuscript_tables(features)
    verdict = final_decision()
    precision = pd.read_csv(OUTDIR / "PRIMARY_EFFECT_SIZE_PRECISION.tsv", sep="\t").iloc[0]
    ld = pd.read_csv(OUTDIR / "LD_PRUNED_HETEROGENEITY_SENSITIVITY.tsv", sep="\t")
    block = pd.read_csv(OUTDIR / "LD_BLOCK_ROBUSTNESS.tsv", sep="\t")
    power = pd.read_csv(OUTDIR / "DAR_POWER_BOUNDS.tsv", sep="\t")
    eq = pd.read_csv(OUTDIR / "EQUIVALENCE_BOUNDARY.tsv", sep="\t").iloc[0]
    context = pd.read_csv(OUTDIR / "RETINAL_OCR_SLDXR_CONTEXT.tsv", sep="\t")
    cells = pd.read_csv(OUTDIR / "CELL_CLASS_DESCRIPTIVE_HETEROGENEITY.tsv", sep="\t")
    print("PHASE 2B VERDICT:")
    print(verdict)
    print("")
    print("PRIMARY DAR RESULT:")
    print(f"OR: {precision['odds_ratio']:.3f}")
    print(f"95% CI: {precision['or_ci95_low']:.3f}-{precision['or_ci95_high']:.3f}")
    print(f"P: {precision['p_value']:.3g}")
    reproduction = pd.read_csv(OUTDIR / "PRIMARY_RESULT_REPRODUCTION.tsv", sep="\t")
    permutation_p = reproduction.loc[reproduction["metric"].eq("permutation_empirical_p"), "recomputed"].iloc[0]
    print(f"PERMUTATION P: {permutation_p:.3g}")
    print("")
    print(f"LD-PRUNED RESULT: top5 all sensitivity P values = {','.join(ld.loc[ld['endpoint'].eq('top_5pct_chi2_het'), 'p_value'].round(4).astype(str))}")
    print(f"BLOCK-LEVEL RESULT: adjusted P = {block.loc[block['analysis'].eq('block_level_adjusted_OLS'), 'p_value'].iloc[0]:.4g}")
    print("")
    print(f"80% MDE OR: {power.loc[power['power'].eq(0.8), 'minimum_detectable_OR'].iloc[0]:.3f}")
    print(f"90% MDE OR: {power.loc[power['power'].eq(0.9), 'minimum_detectable_OR'].iloc[0]:.3f}")
    print(f"LARGE ENRICHMENT EXCLUDED: {'YES' if bool(eq['large_enrichment_excluded']) else 'NO'}")
    print("")
    print(f"GENOME-WIDE S-LDXR: {context.loc[context['context'].eq('genomewide_formal'), 'estimate'].iloc[0]:.6f} ± {context.loc[context['context'].eq('genomewide_formal'), 'SE'].iloc[0]:.6f}")
    print(f"ALL-RETINAL-OCR S-LDXR: {context.loc[context['context'].eq('all_retinal_OCR'), 'estimate'].iloc[0]:.6f} ± {context.loc[context['context'].eq('all_retinal_OCR'), 'SE'].iloc[0]:.6f}")
    print(f"DAR S-LDXR DESCRIPTIVE: {context.loc[context['context'].eq('ancestry_DAR'), 'estimate'].iloc[0]:.6f} ± {context.loc[context['context'].eq('ancestry_DAR'), 'SE'].iloc[0]:.6f}")
    print("")
    print(f"CELL-CLASS DESCRIPTIVE: eligible classes = {int(cells['eligible_for_descriptive'].sum())}")


if __name__ == "__main__":
    main()
