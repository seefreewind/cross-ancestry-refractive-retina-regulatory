#!/usr/bin/env python3
"""Signed-Z concordance sanity checks for the harmonized EUR/EAS set."""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, binomtest


def concordance(df: pd.DataFrame, label: str) -> dict:
    d = df.dropna(subset=["z_EUR", "z_EAS_aligned_to_EUR"])
    signs = np.sign(d["z_EUR"]) == np.sign(d["z_EAS_aligned_to_EUR"])
    return {
        "set": label,
        "n": len(d),
        "pearson_r": pearsonr(d["z_EUR"], d["z_EAS_aligned_to_EUR"])[0] if len(d) > 2 else np.nan,
        "spearman_r": spearmanr(d["z_EUR"], d["z_EAS_aligned_to_EUR"])[0] if len(d) > 2 else np.nan,
        "same_direction_n": int(signs.sum()),
        "same_direction_fraction": float(signs.mean()) if len(d) else np.nan,
        "same_direction_binom_p_two_sided": float(binomtest(int(signs.sum()), len(d), 0.5).pvalue) if len(d) else np.nan,
    }


def select_position_independent_leads(d: pd.DataFrame, window_bp: int = 250_000) -> pd.DataFrame:
    """Approximate locus leads by non-overlapping positional windows.

    This is intentionally labelled position-based, not LD-independent, because
    a validated ancestry-specific LD reference is not yet available in Phase 0.
    """
    d = d.sort_values(["CHR", "POS", "p_EUR", "p_EAS"]).copy()
    selected = []
    last_by_chr = {}
    for _, row in d.iterrows():
        chrom = str(row["CHR"])
        pos = int(row["POS"])
        if chrom not in last_by_chr or pos - last_by_chr[chrom] > window_bp:
            selected.append(row)
            last_by_chr[chrom] = pos
    return pd.DataFrame(selected)


def main() -> None:
    ws = Path(__file__).resolve().parents[2]
    inp = ws / "data" / "processed" / "EUR_EAS_HARMONIZED.parquet"
    out = ws / "results" / "phase0"
    d = pd.read_parquet(inp)
    d["p_EUR"] = pd.to_numeric(d["p_EUR"], errors="coerce")
    d["p_EAS"] = pd.to_numeric(d["p_EAS"], errors="coerce")
    rows = [concordance(d, "all_shared_nonpalindromic")]
    eur_sig = d[d["p_EUR"] < 5e-8].copy()
    eas_sig = d[d["p_EAS"] < 5e-8].copy()
    rows.append(concordance(eur_sig, "EUR_genomewide_significant_in_EAS"))
    rows.append(concordance(eas_sig, "EAS_genomewide_significant_in_EUR"))
    lead_pool = d[(d["p_EUR"] < 5e-8) | (d["p_EAS"] < 5e-8)].copy()
    lead = select_position_independent_leads(lead_pool)
    rows.append(concordance(lead, "position_based_250kb_leads_not_LD_independent"))
    pd.DataFrame(rows).to_csv(out / "EUR_EAS_EFFECT_CONCORDANCE.tsv", sep="\t", index=False)
    lead.to_csv(out / "EUR_EAS_POSITION_BASED_LEADS.tsv", sep="\t", index=False)
    with (ws / "reports" / "EFFECT_DIRECTION_AUDIT.md").open("w") as f:
        f.write("# EUR–EAS Effect Direction Audit\n\n")
        f.write("This is a QC sanity check, not formal genetic correlation. EAS z-scores were aligned to the EUR A1 allele using the CHR:POS harmonization table. Palindromic SNPs were excluded from the primary harmonized set.\n\n")
        f.write("The last row uses a 250-kb position-based lead selection because a validated ancestry-specific LD reference was not yet available in Phase 0; it must not be described as LD-independent.\n\n")
        f.write(pd.DataFrame(rows).to_markdown(index=False))
        f.write("\n")


if __name__ == "__main__":
    main()
