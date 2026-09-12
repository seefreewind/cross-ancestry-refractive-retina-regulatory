#!/usr/bin/env python3
"""Build final publication-oriented Human Genetics figures and tables.

This script restructures existing frozen outputs into a 3-main-figure,
2-main-table package. It does not run new discovery analyses, redefine
thresholds, or alter frozen effect estimates.
"""

from __future__ import annotations

import math
import shutil
import zipfile
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill


ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "figures" / "human_genetics"
FINAL_FIG_DIR = ROOT / "figures" / "human_genetics_final"
ARCHIVE_DIR = ROOT / "figures" / "archive"
PACKAGE_DIR = ROOT / "submission" / "human_genetics_figtab_final"
TABLE_DIR = PACKAGE_DIR / "tables"


NEUTRAL = "#3d3d3d"
LIGHT_NEUTRAL = "#d9d9d9"
FILL = "#f5f7f9"
ACCENT = "#3f6f8f"
ACCENT_LIGHT = "#9eb6c9"
TAIL = "#d8c7a2"


def fmt_n(value: float | int | str) -> str:
    if isinstance(value, str):
        try:
            value = float(value.replace(",", ""))
        except ValueError:
            return value
    return f"{int(round(float(value))):,}"


def fmt3(value: float) -> str:
    return f"{float(value):.3f}"


def pct(value: float) -> str:
    return f"{100 * float(value):.2f}%"


def ci_text(lo: float, hi: float) -> str:
    return f"{fmt3(lo)}–{fmt3(hi)}"


def odds_ci_from_counts(a: float, n1: float, c: float, n0: float) -> tuple[float, float, float]:
    """Wald log-OR CI from frozen 2x2 counts, used only for table display."""
    b = n1 - a
    d = n0 - c
    or_value = (a * d) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return or_value, math.exp(math.log(or_value) - 1.96 * se), math.exp(math.log(or_value) + 1.96 * se)


def load_inputs() -> dict[str, pd.DataFrame]:
    return {
        "maf": pd.read_csv(ROOT / "results/presubmission/SLDXR_MAF_SENSITIVITY.tsv", sep="\t"),
        "global": pd.read_csv(ROOT / "results/phase1c/SLDXR_GLOBAL_ANNOTATION_PILOT.tsv", sep="\t"),
        "power_counts": pd.read_csv(ROOT / "results/phase1c/SLDXR_DAR_POWER_COUNTS.tsv", sep="\t"),
        "primary": pd.read_csv(ROOT / "results/phase2b/PRIMARY_EFFECT_SIZE_PRECISION.tsv", sep="\t"),
        "hetero": pd.read_csv(ROOT / "results/phase2/PHASE2_DAR_HETEROGENEITY_ENRICHMENT.tsv", sep="\t"),
        "perm": pd.read_csv(ROOT / "results/phase2/PHASE2_DAR_MATCHED_PERMUTATION_NULL.tsv", sep="\t"),
        "perm_audit": pd.read_csv(ROOT / "results/phase2b/MATCHED_PERMUTATION_BALANCE_AUDIT.tsv", sep="\t"),
        "block": pd.read_csv(ROOT / "results/phase2b/LD_BLOCK_ROBUSTNESS.tsv", sep="\t"),
        "precision": pd.read_csv(ROOT / "results/phase2b/PRIMARY_EFFECT_SIZE_PRECISION.tsv", sep="\t"),
        "power": pd.read_csv(ROOT / "results/phase2b/DAR_POWER_BOUNDS.tsv", sep="\t"),
        "boundary": pd.read_csv(ROOT / "results/phase2b/EQUIVALENCE_BOUNDARY.tsv", sep="\t"),
        "ld_pruned": pd.read_csv(ROOT / "results/phase2b/LD_PRUNED_HETEROGENEITY_SENSITIVITY.tsv", sep="\t"),
        "ld_universe": pd.read_csv(ROOT / "results/phase2b/LD_PRUNED_SNP_UNIVERSE.tsv", sep="\t"),
        "table1_old": pd.read_csv(ROOT / "submission/tables/Table1_GWAS_analysis_characteristics.tsv", sep="\t"),
        "score_universe": pd.read_csv(ROOT / "results/phase1c/SLDXR_ALL_SCORE_UNIVERSE_ALIGNMENT.tsv", sep="\t"),
    }


def setup_dirs() -> None:
    for directory in (FINAL_FIG_DIR, ARCHIVE_DIR, TABLE_DIR, PACKAGE_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        old = FIG_DIR / f"Figure4_precision_robustness.{ext}"
        if old.exists():
            shutil.copy2(old, ARCHIVE_DIR / f"Figure4_precision_robustness_original.{ext}")


def save_all(fig: plt.Figure, stem: Path) -> None:
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=600, bbox_inches="tight")
    plt.close(fig)


def set_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7,
            "axes.labelsize": 7,
            "xtick.labelsize": 6.5,
            "ytick.labelsize": 6.5,
            "axes.linewidth": 0.7,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def box(ax: plt.Axes, x: float, y: float, w: float, h: float, text: str, fc: str = FILL, fontsize: float = 7.0) -> None:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        facecolor=fc,
        edgecolor=ACCENT,
        linewidth=0.9,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=NEUTRAL, linespacing=1.22, fontsize=fontsize)


def arrow(ax: plt.Axes, xy1: tuple[float, float], xy2: tuple[float, float]) -> None:
    ax.annotate("", xy=xy2, xytext=xy1, arrowprops=dict(arrowstyle="-|>", lw=0.8, color=NEUTRAL, shrinkA=4, shrinkB=4))


def figure1() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.12, 0.93, "Data", ha="center", va="center", fontsize=8.5, weight="bold", color=NEUTRAL)
    ax.text(0.49, 0.93, "Analytical framework", ha="center", va="center", fontsize=8.5, weight="bold", color=NEUTRAL)
    ax.text(0.82, 0.93, "Scientific questions", ha="center", va="center", fontsize=8.5, weight="bold", color=NEUTRAL)

    box(ax, 0.035, 0.69, 0.18, 0.12, "EUR GWAS\nPublic no-23andMe\nrefractive error")
    box(ax, 0.035, 0.47, 0.18, 0.12, "EAS GWAS\nPublic EAS\nrefractive error")
    box(ax, 0.035, 0.23, 0.18, 0.15, "Retinal regulatory atlas\nBroad retinal OCR\nAncestry-associated DAR")

    box(
        ax,
        0.32,
        0.34,
        0.27,
        0.34,
        "Cross-ancestry harmonization\nAllele alignment\nReference anchoring\nPaired-reference checks\n\n3,262,168 harmonized SNPs\n3,112,573 analysis SNPs",
        fc="#f7f7f7",
        fontsize=6.8,
    )

    box(ax, 0.69, 0.56, 0.27, 0.25, "Cross-ancestry sharing\nGenome-wide → broad retinal OCR\nS-LDXR", fontsize=6.6)
    box(ax, 0.69, 0.24, 0.27, 0.27, "Ancestry-linked heterogeneity\nDAR vs matched non-DAR retinal OCR\nAssociation-effect heterogeneity", fontsize=6.4)

    for y in (0.75, 0.53, 0.30):
        arrow(ax, (0.215, y), (0.32, 0.54))
    arrow(ax, (0.59, 0.56), (0.69, 0.69))
    arrow(ax, (0.59, 0.46), (0.69, 0.38))

    ax.text(0.82, 0.13, "Matched permutation • block robustness • effect-size precision", ha="center", va="center", fontsize=6.5, color="#666666")
    save_all(fig, FINAL_FIG_DIR / "Figure1_study_design")


def figure2(d: dict[str, pd.DataFrame]) -> None:
    maf = d["maf"]
    rows = [
        ("Genome-wide", 0.05, "Method-standard"),
        ("All retinal OCR", 0.05, "Method-standard"),
        ("Genome-wide", 0.01, "Supporting sensitivity"),
        ("All retinal OCR", 0.01, "Supporting sensitivity"),
    ]
    records = []
    for label, threshold, role in rows:
        key = "genomewide" if label == "Genome-wide" else "all_retinal_OCR"
        row = maf.loc[(maf["analysis"] == key) & (maf["maf_threshold"].round(2) == threshold)].iloc[0]
        records.append((label, threshold, role, float(row.GCORSQ), float(row.CI_low), float(row.CI_high)))

    fig, ax = plt.subplots(figsize=(4.9, 2.75))
    y = np.arange(len(records))[::-1]
    for i, (label, threshold, role, est, lo, hi) in enumerate(records):
        primary = threshold == 0.05
        color = ACCENT if primary else "#6f6f6f"
        alpha = 1.0 if primary else 0.70
        lw = 1.4 if primary else 0.9
        ms = 5.2 if primary else 3.8
        ax.errorbar(est, y[i], xerr=[[est - lo], [hi - est]], fmt="o", color=color, ecolor=color, capsize=2.4, lw=lw, ms=ms, alpha=alpha)
        ax.text(1.305, y[i], f"{fmt3(est)} ({ci_text(lo, hi)})", va="center", ha="left", fontsize=6.5, color=NEUTRAL, clip_on=False)
    ax.axvline(1, color="#777777", lw=0.75, ls=(0, (3, 3)))
    ax.set_yticks(y, [f"{r[0]}\nMAF >{r[1]:.2f}" for r in records])
    ax.set_xlabel("Squared cross-population genetic correlation (GCORSQ)")
    ax.set_xlim(0.70, 1.30)
    ax.set_ylim(-0.65, len(records) - 0.35)
    ax.tick_params(axis="y", length=0)
    ax.text(0.705, 3.38, "Method-standard", fontsize=6.5, color=ACCENT)
    ax.text(0.705, 1.38, "Supporting sensitivity", fontsize=6.5, color="#666666")
    save_all(fig, FINAL_FIG_DIR / "Figure2_cross_ancestry_architecture")


def figure_s1(d: dict[str, pd.DataFrame]) -> None:
    row = d["global"].loc[d["global"]["annotation"] == "ancestry_DAR"].iloc[0]
    est = float(row.estimate)
    se = float(row.SE)
    lo, hi = est - 1.96 * se, est + 1.96 * se
    fig, ax = plt.subplots(figsize=(4.8, 1.7))
    ax.errorbar(est, 0, xerr=[[est - lo], [hi - est]], fmt="o", color=ACCENT_LIGHT, ecolor=ACCENT_LIGHT, capsize=2.4, lw=1.1, ms=4.5)
    ax.axvline(1, color="#777777", lw=0.75, ls=(0, (3, 3)))
    ax.set_yticks([0], ["Ancestry-DAR\nMAF >0.01"])
    ax.set_xlabel("Squared cross-population genetic correlation (GCORSQ)")
    ax.set_xlim(-0.75, 1.85)
    ax.set_ylim(-0.45, 0.45)
    ax.text(est, 0.18, f"{fmt3(est)}; SE {fmt3(se)}", ha="center", va="bottom", fontsize=6.5, color=NEUTRAL)
    ax.text(1.02, -0.24, "Underpowered descriptive estimate", ha="center", va="top", fontsize=6.5, color="#666666")
    save_all(fig, FINAL_FIG_DIR / "FigureS1_descriptive_ancestry_DAR_SLDXR")


def figure3(d: dict[str, pd.DataFrame]) -> None:
    primary = d["primary"].iloc[0]
    power = d["power"]
    null = d["perm"]["null_mean_difference"].to_numpy()
    observed = float(d["hetero"].loc[d["hetero"]["analysis"] == "DAR_vs_matched_non_DAR_retinal_OCR", "observed_mean_difference"].dropna().iloc[0])
    empirical_p = float(d["hetero"].loc[d["hetero"]["analysis"] == "DAR_vs_matched_non_DAR_retinal_OCR", "empirical_p_value"].dropna().iloc[0])

    fig = plt.figure(figsize=(7.2, 5.0))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.12], height_ratios=[1, 1], hspace=0.55, wspace=0.36)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    dar_pct = float(primary.case_top_fraction) * 100
    bg_pct = float(primary.background_top_fraction) * 100
    x = np.array([0, 1])
    ax_a.scatter(x, [dar_pct, bg_pct], s=[38, 38], color=[ACCENT, "#777777"], zorder=3)
    ax_a.plot(x, [dar_pct, bg_pct], color=LIGHT_NEUTRAL, lw=0.9, zorder=1)
    ax_a.set_xticks(x, ["Ancestry-\nassociated DAR", "Matched non-DAR\nretinal OCR"])
    ax_a.set_ylabel("Proportion in top 5% heterogeneity")
    ax_a.set_ylim(4.6, 6.25)
    ax_a.set_yticks([4.8, 5.2, 5.6, 6.0], ["4.8%", "5.2%", "5.6%", "6.0%"])
    ax_a.text(0, dar_pct + 0.12, "5.76%\n71 / 1,232", ha="center", va="bottom", fontsize=6.1, color=NEUTRAL)
    ax_a.text(0.96, bg_pct + 0.12, "5.18%\n19,653 / 379,279", ha="center", va="bottom", fontsize=5.8, color=NEUTRAL)
    ax_a.text(-0.17, 1.03, "A", transform=ax_a.transAxes, weight="bold", fontsize=11)

    or_value, lo, hi, p = float(primary.odds_ratio), float(primary.or_ci95_low), float(primary.or_ci95_high), float(primary.p_value)
    ax_b.errorbar(or_value, 0, xerr=[[or_value - lo], [hi - or_value]], fmt="o", color=ACCENT, ecolor=ACCENT, capsize=2.4, lw=1.2, ms=5.0)
    ax_b.axvline(1, color="#777777", lw=0.75, ls=(0, (3, 3)))
    ax_b.set_yticks([])
    ax_b.set_xlabel("Odds ratio for top-5% heterogeneity")
    ax_b.set_xlim(0.78, 1.52)
    ax_b.set_ylim(-0.5, 0.5)
    ax_b.text(1.205, 0.17, f"{fmt3(or_value)} ({ci_text(lo, hi)})", ha="center", va="bottom", fontsize=6.5)
    ax_b.text(1.205, -0.18, f"P = {fmt3(p)}", ha="center", va="top", fontsize=6.5)
    ax_b.text(-0.14, 1.03, "B", transform=ax_b.transAxes, weight="bold", fontsize=11)

    bins = np.linspace(min(null.min(), -abs(observed)) - 0.01, max(null.max(), abs(observed)) + 0.01, 34)
    counts, edges = np.histogram(null, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    colors = [TAIL if abs(c) >= abs(observed) else "#d6e0e8" for c in centers]
    ax_c.bar(centers, counts, width=np.diff(edges), color=colors, edgecolor="white", linewidth=0.4, align="center")
    ax_c.axvline(observed, color=ACCENT, lw=1.4)
    ax_c.axvline(-observed, color=ACCENT, lw=0.9, ls=(0, (2, 2)))
    ax_c.text(observed, max(counts) * 0.90, "Observed", rotation=90, va="top", ha="right", fontsize=6.2, color=ACCENT)
    ax_c.text(0.02, 0.94, f"Two-sided empirical P = {fmt3(empirical_p)}", transform=ax_c.transAxes, ha="left", va="top", fontsize=6.5)
    ax_c.text(0.02, 0.82, "|null| ≥ |observed| shaded", transform=ax_c.transAxes, ha="left", va="top", fontsize=6.0, color="#666666")
    ax_c.set_xlabel("Matched-permutation mean χ²het difference")
    ax_c.set_ylabel("Permutation count")
    ax_c.text(-0.17, 1.03, "C", transform=ax_c.transAxes, weight="bold", fontsize=11)

    mde80 = float(power.loc[power["power"].round(1) == 0.8, "minimum_detectable_OR"].iloc[0])
    mde90 = float(power.loc[power["power"].round(1) == 0.9, "minimum_detectable_OR"].iloc[0])
    ax_d.errorbar(or_value, 0, xerr=[[or_value - lo], [hi - or_value]], fmt="o", color=NEUTRAL, ecolor=NEUTRAL, capsize=2.4, lw=1.2, ms=4.8)
    for xpos, label, color, style in [
        (1.0, "OR = 1", "#777777", (0, (3, 3))),
        (mde80, "80% MDE", ACCENT_LIGHT, (0, (2, 2))),
        (mde90, "90% MDE", ACCENT, (0, (2, 2))),
        (1.5, "OR = 1.5", "#555555", (0, (5, 2))),
    ]:
        ax_d.axvline(xpos, color=color, lw=0.8, ls=style)
        ax_d.text(xpos, 0.26, label, rotation=90, ha="right", va="bottom", fontsize=6.0, color=color)
    ax_d.set_yticks([0], ["Primary OR\n95% CI"])
    ax_d.set_xlabel("Odds ratio")
    ax_d.set_xlim(0.78, 1.55)
    ax_d.set_ylim(-0.42, 0.42)
    ax_d.text(or_value, -0.20, f"{fmt3(or_value)} ({ci_text(lo, hi)})", ha="center", va="top", fontsize=6.3)
    ax_d.text(1.423, -0.34, "CI upper = 1.423", ha="center", va="top", fontsize=6.0, color=NEUTRAL)
    ax_d.text(-0.14, 1.03, "D", transform=ax_d.transAxes, weight="bold", fontsize=11)

    save_all(fig, FINAL_FIG_DIR / "Figure3_DAR_heterogeneity_permutation_precision")


def write_audit(d: dict[str, pd.DataFrame]) -> None:
    audit = pd.DataFrame(
        [
            {
                "analysis": "Genome-wide S-LDXR",
                "threshold": "MAF >0.05",
                "reported_N": "3,112,573",
                "true_definition": "effective regression SNP count after GWAS, paired-reference, score, annotation, frequency, and MAF filters",
                "source_file": "results/presubmission/SLDXR_MAF_SENSITIVITY.tsv; results/phase1c/sldxr_formal/GCOR_baseline_blocks200_maf0p05_analytic.log",
                "script": "scripts/analysis/run_sldxr_formal.py; scripts/analysis/run_sldxr_genomewide_formal.py",
                "keep_in_main_table": "No; displayed in Figure 2 and retained in Supplementary Table S2",
            },
            {
                "analysis": "Genome-wide S-LDXR",
                "threshold": "MAF >0.01",
                "reported_N": "3,112,573",
                "true_definition": "effective regression SNP count in the formal score universe; unchanged because the aligned score universe was already MAF>0.01-filtered",
                "source_file": "results/presubmission/SLDXR_MAF_SENSITIVITY.tsv; results/phase1c/SLDXR_ALL_SCORE_UNIVERSE_ALIGNMENT.tsv",
                "script": "scripts/qc/validate_sldxr_aligned_scores.py; scripts/analysis/run_sldxr_formal.py",
                "keep_in_main_table": "No; retained in Supplementary Table S2",
            },
            {
                "analysis": "All retinal OCR S-LDXR",
                "threshold": "MAF >0.05",
                "reported_N": "544,077",
                "true_definition": "annotation SNP count in all-retinal OCRs passing ancestry-paired MAF>0.05 frequency filters, not the S-LDXR regression SNP count",
                "source_file": "results/phase1c/SLDXR_DAR_POWER_COUNTS.tsv; results/phase1c/SLDXR_GLOBAL_ANNOTATION_PILOT.tsv; results/presubmission/SLDXR_MAF_SENSITIVITY.tsv",
                "script": "scripts/analysis/run_sldxr_global_annotation_pilots.py",
                "keep_in_main_table": "No; relabeled as annotation SNP count in Supplementary Table S2",
            },
            {
                "analysis": "All retinal OCR S-LDXR",
                "threshold": "MAF >0.01",
                "reported_N": "380,615",
                "true_definition": "shared usable all-retinal-OCR annotation SNP count intersecting the formal analysis SNP universe; also the manuscript analysis-count used for DAR-context reporting",
                "source_file": "results/phase1c/SLDXR_DAR_POWER_COUNTS.tsv; results/phase1c/SLDXR_GLOBAL_ANNOTATION_PILOT.tsv; submission/tables/Table1_GWAS_analysis_characteristics.tsv",
                "script": "scripts/analysis/run_sldxr_global_annotation_pilots.py; scripts/annotation/build_sldxr_annotations.py",
                "keep_in_main_table": "Yes, in Table 1 as analysis-overlap annotation SNP count; not labeled SNP_N",
            },
            {
                "analysis": "Ancestry-DAR heterogeneity",
                "threshold": "MAF >0.01 / formal analysis universe",
                "reported_N": "1,232",
                "true_definition": "ancestry-DAR annotation SNP count intersecting the formal analysis SNP universe and used as the primary DAR heterogeneity test denominator",
                "source_file": "results/phase1c/SLDXR_DAR_POWER_COUNTS.tsv; results/phase2b/PRIMARY_EFFECT_SIZE_PRECISION.tsv",
                "script": "scripts/analysis/run_sldxr_global_annotation_pilots.py; scripts/analysis/run_phase2b_robustness.py",
                "keep_in_main_table": "Yes, in Table 1 and Table 2 as DAR events / N",
            },
        ]
    )
    audit.to_csv(PACKAGE_DIR / "FIGTAB_SNP_COUNT_AUDIT.tsv", sep="\t", index=False)

    md = ["# Figure/table SNP-count audit\n", "## Verdict\n", "`TABLE_LABEL_ERROR`\n"]
    md.append(
        "The conflicting values do not indicate a biological or computational contradiction. The old column name `SNP_N` mixed effective regression SNP counts with annotation-membership counts and formal analysis-overlap counts. The final tables therefore remove the ambiguous `SNP_N` label from main tables and use explicit labels such as `Analysis information`, `DAR events / N`, and `Annotation SNP count`.\n"
    )
    md.append("## Count trace\n")
    md.append(audit.to_markdown(index=False))
    md.append("\n## Final resolution\n")
    md.append("`COUNT_DEFINITION_RESOLVED` for the source counts; `TABLE_LABEL_ERROR` for the old manuscript-facing table label.")
    (ROOT / "reports" / "FIGTAB_SNP_COUNT_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def build_tables(d: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    old = d["table1_old"].set_index("item")
    table1 = pd.DataFrame(
        [
            ["EUR GWAS", "European", "Public no-23andMe refractive-error GWAS summary statistics", old.loc["EUR public analysis file", "value"], "Input GWAS"],
            ["EAS GWAS", "East Asian", "Public EAS refractive-error GWAS summary statistics", old.loc["EAS public analysis file", "value"], "Input GWAS"],
            ["Harmonized EUR-EAS SNP set", "EUR–EAS", "Effect-aligned shared set after allele and duplicate checks", "3,262,168 harmonized SNPs", "Harmonized effect-comparison set"],
            ["Cross-ancestry analysis SNP set", "EUR–EAS", "Exact paired-reference, frequency, score, and annotation alignment", "3,112,573 analysis SNPs", "S-LDXR and heterogeneity universe"],
            ["Broad retinal OCR", "Not ancestry-specific", "Union retinal open-chromatin annotation from retinal regulatory atlas", "380,615 analysis-overlap annotation SNPs", "Broad retinal regulatory context"],
            ["Ancestry-associated DAR", "Atlas-defined ancestry-associated regulatory annotation", "Differentially accessible retinal regions using the source atlas definition", "1,232 analysis-overlap annotation SNPs", "Primary tested annotation"],
            ["Matched non-DAR retinal OCR", "Not ancestry-specific comparator", "Retinal OCR SNPs not overlapping ancestry-DAR intervals", "379,279 analysis-overlap annotation SNPs", "Matched retinal comparator"],
        ],
        columns=["Resource / set", "Ancestry", "Source / definition", "Analysis information", "Role"],
    )

    hetero = d["hetero"]
    rows = []
    endpoint_names = {
        "top_5pct_chi2_het": "Primary: top 5% χ²het",
        "top_1pct_chi2_het": "Sensitivity: top 1% χ²het",
        "top_10pct_chi2_het": "Sensitivity: top 10% χ²het",
    }
    for endpoint in ("top_5pct_chi2_het", "top_1pct_chi2_het", "top_10pct_chi2_het"):
        row = hetero.loc[(hetero["analysis"] == "DAR_vs_matched_non_DAR_retinal_OCR") & (hetero["endpoint"] == endpoint)].iloc[0]
        or_value, lo, hi = odds_ci_from_counts(row.case_top_n, row.case_snp_n, row.background_top_n, row.background_snp_n)
        if endpoint == "top_5pct_chi2_het":
            lo = float(d["primary"].iloc[0].or_ci95_low)
            hi = float(d["primary"].iloc[0].or_ci95_high)
            or_value = float(d["primary"].iloc[0].odds_ratio)
        rows.append(
            [
                endpoint_names[endpoint],
                f"{fmt_n(row.case_top_n)} / {fmt_n(row.case_snp_n)} ({pct(row.case_top_fraction)})",
                f"{fmt_n(row.background_top_n)} / {fmt_n(row.background_snp_n)} ({pct(row.background_top_fraction)})",
                fmt3(or_value),
                ci_text(lo, hi),
                fmt3(row.p_value),
            ]
        )
    table2 = pd.DataFrame(rows, columns=["Endpoint", "DAR events / N (%)", "Matched non-DAR events / N (%)", "OR", "95% CI", "P"])

    table_s1 = old.reset_index().rename(columns={"item": "Field", "value": "Value", "analysis_role": "Analysis role", "note": "Note"})
    maf = d["maf"]
    global_counts = d["global"].set_index("annotation")
    s2_rows = []
    for label, key, threshold in [
        ("Genome-wide", "genomewide", 0.05),
        ("All retinal OCR", "all_retinal_OCR", 0.05),
        ("Genome-wide", "genomewide", 0.01),
        ("All retinal OCR", "all_retinal_OCR", 0.01),
    ]:
        row = maf.loc[(maf["analysis"] == key) & (maf["maf_threshold"].round(2) == threshold)].iloc[0]
        if key == "genomewide":
            count_label = "Effective regression SNP count"
        elif threshold == 0.05:
            count_label = "Annotation SNP count passing paired MAF>0.05"
        else:
            count_label = "Analysis-overlap annotation SNP count"
        s2_rows.append([label, f">{threshold:.2f}", count_label, fmt_n(row.SNP_N), "GCORSQ", fmt3(row.GCORSQ), fmt3(row.SE), ci_text(row.CI_low, row.CI_high), fmt_n(row.jackknife_blocks)])
    dar = global_counts.loc["ancestry_DAR"]
    s2_rows.append(["Ancestry-DAR descriptive", ">0.01", "Analysis-overlap annotation SNP count", fmt_n(dar.shared_usable_SNP_N), "GCORSQ", fmt3(dar.estimate), fmt3(dar.SE), ci_text(dar.CI95_low, dar.CI95_high), fmt_n(dar.effective_blocks)])
    table_s2 = pd.DataFrame(s2_rows, columns=["Analysis", "MAF threshold", "Count definition", "Count", "Metric", "Estimate", "SE", "95% CI", "Jackknife blocks"])

    cont = hetero.loc[(hetero["analysis"] == "DAR_vs_matched_non_DAR_retinal_OCR") & (hetero["endpoint"] == "chi2_het_continuous")].iloc[0]
    perm = hetero["empirical_p_value"].dropna().iloc[0]
    block = d["block"].iloc[0]
    ld = d["ld_pruned"]
    s3_rows = [
        ["Continuous χ²het", "Mean χ²het difference", "1,232", "379,279", fmt3(cont.mean_difference), "", fmt3(cont.p_value), "Mann-Whitney test"],
        ["Matched permutation", "Mean χ²het difference", "1,069 retained", "59,215 retained", fmt3(cont.observed_mean_difference), "", fmt3(perm), "1,000 matched label permutations"],
        ["Block robustness", "Mean χ²het by block", fmt_n(block.DAR_block_N), fmt_n(block.non_DAR_block_N), fmt3(block.coefficient_has_DAR), ci_text(block.CI95_low, block.CI95_high), fmt3(block.p_value), "Adjusted OLS"],
    ]
    for _, row in ld.loc[ld["endpoint"].str.contains("top_5pct", na=False)].iterrows():
        s3_rows.append([f"LD-pruned sensitivity ({row.sensitivity})", "Top 5% χ²het", fmt_n(row.case_snp_n), fmt_n(row.background_snp_n), fmt3(row.conditional_odds_ratio), ci_text(row.or_ci95_low, row.or_ci95_high), fmt3(row.p_value), "Label-blind LD pruning"])
    table_s3 = pd.DataFrame(s3_rows, columns=["Analysis", "Endpoint", "DAR N", "Comparator N", "Effect", "95% CI", "P", "Notes"])

    precision = d["precision"].iloc[0]
    power = d["power"]
    boundary = d["boundary"].iloc[0]
    table_s4 = pd.DataFrame(
        [
            ["Primary top-5% OR", fmt3(precision.odds_ratio), ci_text(precision.or_ci95_low, precision.or_ci95_high), fmt3(precision.p_value), "Frozen primary effect estimate"],
            ["Comparator event rate", pct(precision.background_top_fraction), "", "", f"{fmt_n(precision.background_top_n)} / {fmt_n(precision.background_snp_n)}"],
            ["80% MDE", fmt3(power.loc[power["power"].round(1) == 0.8, "minimum_detectable_OR"].iloc[0]), "", "", "Prospective two-sample proportion normal approximation"],
            ["90% MDE", fmt3(power.loc[power["power"].round(1) == 0.9, "minimum_detectable_OR"].iloc[0]), "", "", "Prospective two-sample proportion normal approximation"],
            ["Large-effect boundary", fmt3(boundary.margin_OR), "", "", "Reference boundary; CI upper below boundary"],
        ],
        columns=["Quantity", "Value", "95% CI", "P", "Notes"],
    )

    tables = {
        "Table1_GWAS_datasets_and_analytical_sets": table1,
        "Table2_DAR_heterogeneity_results": table2,
        "TableS1_Input_files_and_QC_characteristics": table_s1,
        "TableS2_Complete_SLDXR_estimates": table_s2,
        "TableS3_DAR_robustness_analyses": table_s3,
        "TableS4_Effect_size_precision": table_s4,
    }
    for name, table in tables.items():
        table.to_csv(TABLE_DIR / f"{name}.tsv", sep="\t", index=False)
    return tables


def write_excel(tables: dict[str, pd.DataFrame]) -> Path:
    xlsx = PACKAGE_DIR / "HUMAN_GENETICS_FINAL_FIGURES_TABLES.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        for name, table in tables.items():
            sheet = name.replace("Table", "T").replace("_", " ")[:31]
            table.to_excel(writer, index=False, sheet_name=sheet)
    wb = load_workbook(xlsx)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="3F6F8F")
            cell.alignment = Alignment(wrap_text=True, vertical="center")
        for column in ws.columns:
            letter = column[0].column_letter
            max_len = max(len("" if c.value is None else str(c.value)) for c in column)
            ws.column_dimensions[letter].width = min(max(max_len + 2, 12), 55)
            for cell in column:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
    wb.save(xlsx)
    return xlsx


def write_legends_and_readme() -> None:
    legends = """# Final Human Genetics figure legends

## Figure 1. Study design

Public EUR no-23andMe and EAS refractive-error GWAS summary statistics were combined with retinal regulatory annotations to test two questions: whether refractive-error genetic architecture is shared across EUR and EAS populations genome-wide and within broad retinal OCRs, and whether ancestry-associated retinal DARs concentrate EUR-EAS association-effect heterogeneity relative to matched non-DAR retinal OCRs. The harmonized EUR-EAS set contained 3,262,168 SNPs, and the aligned analysis universe contained 3,112,573 SNPs. Matched permutation, block robustness and effect-size precision analyses were used as validation checks.

## Figure 2. Genome-wide and retinal-OCR cross-ancestry sharing

Forest plot showing S-LDXR squared cross-population genetic correlation (GCORSQ) estimates and 95% confidence intervals. Method-standard MAF >0.05 estimates are shown with stronger visual weight for genome-wide and all-retinal-OCR analyses. MAF >0.01 estimates are shown as supporting sensitivity analyses. The vertical dashed line marks GCORSQ = 1.

## Figure 3. DAR heterogeneity, permutation and precision

(A) Proportion of SNPs in the top 5% of the genome-wide χ²het distribution for ancestry-associated DARs and matched non-DAR retinal OCRs. (B) Primary forest-style odds ratio for the top-5% heterogeneity endpoint. (C) Matched-permutation null distribution of mean χ²het difference; shaded bars indicate the two-sided empirical tail where |null| ≥ |observed|. (D) Primary odds ratio and 95% confidence interval with 80% and 90% minimum detectable odds ratios and the OR = 1.5 large-effect reference boundary. Block-level robustness was consistent with the primary inference (adjusted P = 0.3836).

## Supplementary Figure S1. Descriptive ancestry-DAR S-LDXR estimate

Underpowered descriptive S-LDXR estimate for the ancestry-DAR annotation. The estimate was GCORSQ = 0.571 with SE = 0.577 and is shown separately from the main cross-ancestry architecture figure because the sparse DAR annotation does not support the same inferential weight as genome-wide and all-retinal-OCR analyses.
"""
    (PACKAGE_DIR / "FINAL_FIGURE_LEGENDS.md").write_text(legends, encoding="utf-8")
    readme = """# Human Genetics final figure/table package

This package restructures the existing frozen project outputs into a publication-oriented display set:

- Main figures: Figure 1, Figure 2, Figure 3
- Supplementary figure: Figure S1
- Main tables: Table 1, Table 2
- Supplementary tables: Table S1–S4

No discovery analysis, threshold redefinition, DAR redefinition, subgroup analysis, cell-type analysis, locus analysis, enrichment analysis, or frozen effect-estimate change was performed in this restructuring step.
"""
    (PACKAGE_DIR / "README.md").write_text(readme, encoding="utf-8")


def copy_outputs_to_package() -> None:
    fig_package = PACKAGE_DIR / "figures"
    fig_package.mkdir(exist_ok=True)
    for stem in [
        "Figure1_study_design",
        "Figure2_cross_ancestry_architecture",
        "Figure3_DAR_heterogeneity_permutation_precision",
        "FigureS1_descriptive_ancestry_DAR_SLDXR",
    ]:
        for ext in ("pdf", "svg", "png"):
            shutil.copy2(FINAL_FIG_DIR / f"{stem}.{ext}", fig_package / f"{stem}.{ext}")


def write_zip() -> Path:
    zip_path = PACKAGE_DIR / "HUMAN_GENETICS_FINAL_FIGURES_TABLES.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for path in sorted(PACKAGE_DIR.rglob("*")):
            if path == zip_path or path.is_dir() or path.name.startswith("._") or path.name == ".DS_Store":
                continue
            z.write(path, path.relative_to(PACKAGE_DIR))
    return zip_path


def write_qa() -> None:
    rows = [
        ["Figure 1", "schematic-led composite", "Data → analytical framework → scientific questions", "No panel labels; balanced horizontal boxes; validation footer only", "yes"],
        ["Figure 2", "quantitative forest", "Genome-wide and broad retinal-OCR sharing", "DAR S-LDXR removed from main figure; primary vs sensitivity hierarchy encoded by size/weight", "yes"],
        ["Figure 3A", "dot comparison", "Top-5% heterogeneity proportions", "Dot comparison avoids bar-height exaggeration", "yes"],
        ["Figure 3B", "forest effect", "Primary top-5% OR", "OR=1 reference shown; estimate and P directly labeled", "yes"],
        ["Figure 3C", "permutation distribution", "Matched permutation support", "Observed statistic and two-sided tail shading displayed", "yes"],
        ["Figure 3D", "precision axis", "Effect-size precision", "CI, MDE markers and OR=1.5 boundary shown without equivalence language", "yes"],
        ["Figure S1", "quantitative forest", "Descriptive DAR S-LDXR", "Separated as underpowered descriptive estimate", "yes"],
    ]
    table = pd.DataFrame(rows, columns=["Panel", "Archetype", "Unique claim", "Check", "Pass"])
    md = ["# Final figure/table restructuring QA\n", "## Figure contract\n"]
    md.append(table.to_markdown(index=False))
    md.append("\n## Export contract\n")
    md.append("- PDF, SVG and 600-dpi PNG were exported for every final figure.")
    md.append("- Ambiguous main-table `SNP_N` labels were removed or relabeled.")
    md.append("- Original Figure 4 files were copied to `figures/archive/` with `_original` suffix.")
    (ROOT / "reports" / "FIGTAB_FINAL_RESTRUCTURING_QA.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> None:
    set_style()
    setup_dirs()
    d = load_inputs()
    write_audit(d)
    figure1()
    figure2(d)
    figure3(d)
    figure_s1(d)
    tables = build_tables(d)
    write_excel(tables)
    write_legends_and_readme()
    copy_outputs_to_package()
    write_qa()
    write_zip()
    print(PACKAGE_DIR)


if __name__ == "__main__":
    main()
