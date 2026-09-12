#!/usr/bin/env python3
"""Create same-SNP, same-order, allele-aligned EUR/EAS PLINK panels for S-LDXR."""

from __future__ import annotations

import hashlib
import re
import os
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
INTERIM = ROOT / "data/interim/sldxr_reference"
OUT = INTERIM / "paired_plink_v2"
TEMP = INTERIM / "paired_pgen_v2"
LISTS = INTERIM / "paired_variant_lists"
QC_OUT = ROOT / "results/phase1c/SLDXR_PANEL_PAIRING.tsv"
PLINK2 = os.environ.get("PLINK2", "plink2")


def companion(prefix: Path, extension: str) -> Path:
    return prefix.parent / f"{prefix.name}{extension}"


def locate_original(population: str, chromosome: int) -> Path:
    root = INTERIM / f"{population.lower()}_plink"
    hits = sorted(root.rglob(f"1000G.{population}.QC.{chromosome}.bed"))
    if len(hits) != 1:
        raise RuntimeError(f"Expected one original {population} chr{chromosome} BED, found {len(hits)}")
    return hits[0].with_suffix("")


def read_bim(prefix: Path) -> pd.DataFrame:
    return pd.read_csv(
        companion(prefix, ".bim"),
        sep=r"\s+",
        header=None,
        names=["CHR", "SNP", "CM", "BP", "A1", "A2"],
        dtype={"CHR": str, "SNP": str, "CM": float, "BP": "Int64", "A1": str, "A2": str},
        engine="python",
    )


def ordered_hash(table: pd.DataFrame) -> str:
    payload = "\n".join(f"{snp}\t{bp}\t{a1}\t{a2}" for snp, bp, a1, a2 in zip(table["SNP"], table["BP"], table["A1"], table["A2"]))
    return hashlib.sha256(payload.encode()).hexdigest()


def make_chr_pair(chromosome: int) -> dict[str, object]:
    eur_prefix = locate_original("EUR", chromosome)
    eas_prefix = locate_original("EAS", chromosome)
    eur = read_bim(eur_prefix)
    eas = read_bim(eas_prefix)
    if eur["SNP"].duplicated().any() or eas["SNP"].duplicated().any():
        raise RuntimeError(f"Duplicate SNP IDs in original panel on chr{chromosome}")

    merged = eur.merge(eas, on="SNP", suffixes=("_EUR", "_EAS"), how="inner", validate="one_to_one")
    if merged.empty:
        raise RuntimeError(f"No shared SNPs on chr{chromosome}")
    compatible = (
        ((merged["A1_EUR"] == merged["A1_EAS"]) & (merged["A2_EUR"] == merged["A2_EAS"]))
        | ((merged["A1_EUR"] == merged["A2_EAS"]) & (merged["A2_EUR"] == merged["A1_EAS"]))
    )
    n_allele_incompatible = int((~compatible).sum())
    incompatible_path = LISTS / f"chr{chromosome}.allele_incompatible.tsv"
    incompatible_path.parent.mkdir(parents=True, exist_ok=True)
    merged.loc[~compatible, ["SNP", "BP_EUR", "A1_EUR", "A2_EUR", "BP_EAS", "A1_EAS", "A2_EAS"]].to_csv(
        incompatible_path, sep="\t", index=False
    )
    if n_allele_incompatible:
        # A shared rsID with incompatible allele sets cannot be safely
        # harmonized. Exclude it from both derived panels and retain the
        # complete audit table above; never modify the source panels.
        merged = merged.loc[compatible].copy()
    if merged.empty:
        raise RuntimeError(f"No allele-compatible shared SNPs on chr{chromosome}")
    bp_diff = int((merged["BP_EUR"] != merged["BP_EAS"]).sum())

    # Both source panels are position-sorted; use the EUR order as the canonical order.
    eur_common = eur[eur["SNP"].isin(set(merged["SNP"]))].copy().reset_index(drop=True)
    eas_common = eas[eas["SNP"].isin(set(merged["SNP"]))].copy().reset_index(drop=True)
    if not eur_common["SNP"].reset_index(drop=True).equals(eas_common["SNP"].reset_index(drop=True)):
        # The two source panels can sort a small set of shared rsIDs
        # differently when their released BP fields differ.  The EUR order
        # is frozen as the canonical order below through a shared GRCh37 map.
        order_diff = True
    else:
        order_diff = False

    LISTS.mkdir(parents=True, exist_ok=True)
    extract_list = LISTS / f"chr{chromosome}.snps.txt"
    eur_common["SNP"].to_csv(extract_list, index=False, header=False)
    canonical_map = LISTS / f"chr{chromosome}.canonical_map.txt"
    eur_common[["BP", "SNP"]].to_csv(canonical_map, sep="\t", index=False, header=False)
    eas_update = LISTS / f"chr{chromosome}.EAS_to_EUR.alleles.txt"
    eas_map = merged.set_index("SNP").loc[eur_common["SNP"], ["A1_EAS", "A2_EAS", "A1_EUR", "A2_EUR"]]
    eas_map.to_csv(eas_update, sep="\t", index=True, header=False)

    outputs: dict[str, Path] = {}
    for population, source in (("EUR", eur_prefix), ("EAS", eas_prefix)):
        out_prefix = OUT / population / f"1000G.{population}.paired.{chromosome}"
        pgen_prefix = TEMP / population / f"1000G.{population}.paired.{chromosome}"
        out_prefix.parent.mkdir(parents=True, exist_ok=True)
        pgen_prefix.parent.mkdir(parents=True, exist_ok=True)
        outputs[population] = out_prefix
        required = [companion(out_prefix, ext) for ext in (".bed", ".bim", ".fam")]
        if all(path.exists() for path in required):
            continue
        command = [
            PLINK2,
            "--bfile", str(source),
            "--extract", str(extract_list),
            "--update-map", str(canonical_map), "1", "2",
        ]
        if population == "EAS":
            command.extend(["--update-alleles", str(eas_update)])
        command.extend(["--make-pgen", "--sort-vars", "natural", "--out", str(pgen_prefix)])
        subprocess.run(command, cwd=ROOT, check=True)
        subprocess.run([PLINK2, "--pfile", str(pgen_prefix), "--make-bed", "--out", str(out_prefix)], cwd=ROOT, check=True)

    eur_pair = read_bim(outputs["EUR"])
    eas_pair = read_bim(outputs["EAS"])
    same = eur_pair[["SNP", "BP", "A1", "A2"]].reset_index(drop=True).equals(
        eas_pair[["SNP", "BP", "A1", "A2"]].reset_index(drop=True)
    )
    if not same:
        raise RuntimeError(f"Paired output order/alleles still differ on chr{chromosome}")
    reversed_count = int((merged["A1_EUR"] == merged["A2_EAS"]).sum())
    return {
        "chromosome": chromosome,
        "n_eur_original": len(eur),
        "n_eas_original": len(eas),
        "n_shared_raw": len(merged) + n_allele_incompatible,
        "n_shared": len(merged),
        "n_allele_incompatible_excluded": n_allele_incompatible,
        "n_source_bp_different": bp_diff,
        "n_eas_allele_reversed": reversed_count,
        "source_order_different": order_diff,
        "eur_original_order_sha256": ordered_hash(eur_common),
        "paired_order_sha256": ordered_hash(eur_pair),
        "status": "PASS",
        "eur_bfile_prefix": str(outputs["EUR"]),
        "eas_bfile_prefix": str(outputs["EAS"]),
    }


def main() -> None:
    rows = [make_chr_pair(chromosome) for chromosome in range(1, 23)]
    QC_OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(QC_OUT, sep="\t", index=False)
    print(f"wrote={QC_OUT} rows={len(rows)} shared_snps={sum(int(row['n_shared']) for row in rows)}")


if __name__ == "__main__":
    main()
