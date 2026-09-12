#!/usr/bin/env python3
"""Extract and audit the paired EUR/EAS reference inputs for S-LDXR."""

from __future__ import annotations

import argparse
import hashlib
import re
import os
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/ld_reference"
INTERIM = ROOT / "data/interim/sldxr_reference"
QC_OUT = ROOT / "results/phase1c/SLDXR_REFERENCE_QC.tsv"
PAIRING_QC = ROOT / "results/phase1c/SLDXR_PANEL_PAIRING.tsv"
PLINK2 = os.environ.get("PLINK2", "plink2")

ARCHIVES = {
    "EUR": ("1000G_Phase3_plinkfiles.tgz", 288277344, "a7773ab485827b533cb300c76356d76b"),
    "EAS": ("1000G_Phase3_EAS_plinkfiles.tgz", 322780480, "abf52fba6416622ea0757ca9aca51a87"),
}


def companion(prefix: Path, extension: str) -> Path:
    """Append PLINK companion extensions without replacing numeric chr suffixes."""
    return prefix.parent / f"{prefix.name}{extension}"


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_archive(path: Path, expected_size: int, expected_md5: str) -> None:
    if not path.exists() or path.stat().st_size != expected_size or md5(path) != expected_md5:
        raise RuntimeError(f"Invalid or incomplete archive: {path}")
    check = subprocess.run(["gzip", "-t", str(path)], check=False)
    if check.returncode != 0:
        raise RuntimeError(f"gzip validation failed: {path}")


def extract_archive(population: str) -> Path:
    filename, expected_size, expected_md5 = ARCHIVES[population]
    archive = RAW / filename
    validate_archive(archive, expected_size, expected_md5)
    out = INTERIM / f"{population.lower()}_plink"
    out.mkdir(parents=True, exist_ok=True)
    if len(list(out.rglob("[!.]*.bed"))) < 22:
        subprocess.run(["tar", "-xzf", str(archive), "-C", str(out)], check=True)
    return out


def locate_bfiles(directory: Path, population: str) -> dict[int, Path]:
    found: dict[int, Path] = {}
    for bed in sorted(directory.rglob("[!.]*.bed")):
        prefix = bed.with_suffix("")
        if not all(path.exists() for path in (companion(prefix, ".bim"), companion(prefix, ".fam"))):
            continue
        match = re.search(r"(?:^|\.)([0-9]+)$", prefix.name)
        if not match:
            continue
        chrom = int(match.group(1))
        if 1 <= chrom <= 22 and chrom not in found:
            found[chrom] = prefix
    missing = sorted(set(range(1, 23)) - set(found))
    if missing:
        raise RuntimeError(f"{population} PLINK bundle is missing chromosomes: {missing}")
    return found


def read_bim(prefix: Path) -> pd.DataFrame:
    return pd.read_csv(
        companion(prefix, ".bim"),
        sep=r"\s+",
        header=None,
        names=["CHR", "SNP", "CM", "BP", "A1", "A2"],
        dtype={"CHR": str, "SNP": str, "CM": float, "BP": "Int64", "A1": str, "A2": str},
        engine="python",
    )


def make_freq(prefix: Path, population: str, chrom: int) -> Path:
    raw_dir = INTERIM / "frequency_raw"
    out_dir = INTERIM / "frequency"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_prefix = raw_dir / f"{population}.{chrom}"
    afreq = companion(raw_prefix, ".afreq")
    if not afreq.exists():
        subprocess.run([PLINK2, "--bfile", str(prefix), "--freq", "--out", str(raw_prefix)], check=True)
    table = pd.read_csv(afreq, sep=r"\s+", dtype=str, engine="python")
    id_col = "ID"
    freq_col = next((col for col in ("ALT_FREQS", "ALT1_FREQ", "ALT_FREQ") if col in table.columns), None)
    if freq_col is None or id_col not in table.columns:
        raise RuntimeError(f"Unexpected PLINK2 frequency columns in {afreq}: {list(table.columns)}")
    table["ALT_FREQ"] = pd.to_numeric(table[freq_col].astype(str).str.split(",").str[0], errors="coerce")
    if "OBS_CT" in table.columns:
        table["NCHROBS"] = pd.to_numeric(table["OBS_CT"], errors="coerce")
    else:
        table["NCHROBS"] = pd.NA
    bim = read_bim(prefix)
    merged = bim.merge(table[[id_col, "ALT_FREQ", "NCHROBS"]], left_on="SNP", right_on=id_col, how="left", validate="one_to_one")
    if merged["ALT_FREQ"].isna().any():
        raise RuntimeError(f"Missing allele frequencies for {population} chr{chrom}: {int(merged['ALT_FREQ'].isna().sum())}")
    alt = merged["ALT_FREQ"].astype(float)
    merged["MAF"] = alt.where(alt <= 0.5, 1.0 - alt)
    out = out_dir / f"{population}.{chrom}.frq"
    merged[["CHR", "SNP", "A1", "A2", "MAF", "NCHROBS"]].to_csv(out, sep="\t", index=False, float_format="%.10g")
    return out


def ordered_hash(table: pd.DataFrame) -> str:
    payload = "\n".join(f"{snp}\t{bp}" for snp, bp in zip(table["SNP"], table["BP"]))
    return hashlib.sha256(payload.encode()).hexdigest()


def paired_bfiles() -> pd.DataFrame:
    if not PAIRING_QC.exists():
        raise FileNotFoundError(f"Run build_sldxr_paired_panel.py before preparing S-LDXR reference: {PAIRING_QC}")
    pairing = pd.read_csv(PAIRING_QC, sep="\t")
    required = {"chromosome", "status", "eur_bfile_prefix", "eas_bfile_prefix"}
    missing = required - set(pairing.columns)
    if missing:
        raise RuntimeError(f"Pairing QC is missing columns: {sorted(missing)}")
    if not (pairing["status"] == "PASS").all():
        bad = pairing.loc[pairing["status"] != "PASS", ["chromosome", "status"]]
        raise RuntimeError(f"Pairing QC contains non-PASS chromosomes:\n{bad.to_string(index=False)}")
    if pairing["chromosome"].nunique() != 22:
        raise RuntimeError("Pairing QC does not contain exactly 22 autosomes")
    return pairing


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-frequency", action="store_true", help="Only extract and audit PLINK bundles.")
    args = parser.parse_args()

    extracted = {population: extract_archive(population) for population in ARCHIVES}
    # Validate the original bundles and their chromosome completeness, then
    # use the derived same-SNP/same-order panels for all downstream S-LDXR work.
    original_bfiles = {population: locate_bfiles(directory, population) for population, directory in extracted.items()}
    pairing = paired_bfiles()
    bfiles: dict[str, dict[int, Path]] = {"EUR": {}, "EAS": {}}
    rows = []
    for chrom in range(1, 23):
        pair = pairing.loc[pairing["chromosome"] == chrom]
        if len(pair) != 1:
            raise RuntimeError(f"Missing unique pairing QC row for chromosome {chrom}")
        pair_row = pair.iloc[0]
        bfiles["EUR"][chrom] = Path(pair_row["eur_bfile_prefix"])
        bfiles["EAS"][chrom] = Path(pair_row["eas_bfile_prefix"])
        for population in ("EUR", "EAS"):
            prefix = bfiles[population][chrom]
            if not all(path.exists() for path in (companion(prefix, ".bed"), companion(prefix, ".bim"), companion(prefix, ".fam"))):
                raise RuntimeError(f"Missing paired PLINK companion files for {population} chr{chrom}: {prefix}")
        eur = read_bim(bfiles["EUR"][chrom])
        eas = read_bim(bfiles["EAS"][chrom])
        same_order = eur[["SNP", "BP"]].reset_index(drop=True).equals(eas[["SNP", "BP"]].reset_index(drop=True))
        rows.extend([
            {
                "population": population,
                "chromosome": chrom,
                "bfile_prefix": str(bfiles[population][chrom]),
                "n_snps": len(read_bim(bfiles[population][chrom])),
                "n_samples": sum(1 for line in companion(bfiles[population][chrom], ".fam").open()),
                "variant_order_sha256": ordered_hash(read_bim(bfiles[population][chrom])),
                "paired_variant_order_match": same_order,
                "source_n_shared_raw": int(pair_row.get("n_shared_raw", pair_row["n_shared"])),
                "source_allele_incompatible_excluded": int(pair_row.get("n_allele_incompatible_excluded", 0)),
                "source_bp_different": int(pair_row["n_source_bp_different"]),
                "source_order_different": bool(pair_row["source_order_different"]),
                "status": "PASS" if same_order else "FAIL",
            }
            for population in ("EUR", "EAS")
        ])
        if not same_order:
            raise RuntimeError(f"EUR/EAS PLINK variant order differs on chromosome {chrom}")

    if not args.skip_frequency:
        for population in ("EUR", "EAS"):
            for chrom in range(1, 23):
                make_freq(bfiles[population][chrom], population, chrom)
        print_snps = INTERIM / "print_snps_maf_gt_01.txt"
        with print_snps.open("w") as handle:
            for chrom in range(1, 23):
                eur = pd.read_csv(INTERIM / "frequency" / f"EUR.{chrom}.frq", sep="\t")
                eas = pd.read_csv(INTERIM / "frequency" / f"EAS.{chrom}.frq", sep="\t")
                merged = eur[["SNP", "MAF"]].merge(eas[["SNP", "MAF"]], on="SNP", suffixes=("_EUR", "_EAS"))
                keep = merged.loc[(merged["MAF_EUR"] > 0.01) & (merged["MAF_EAS"] > 0.01), "SNP"]
                keep.to_csv(handle, index=False, header=False)
        print(f"print_snps={print_snps} rows={sum(1 for _ in print_snps.open())}")

    QC_OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(QC_OUT, sep="\t", index=False)
    print(f"wrote={QC_OUT} rows={len(rows)}")


if __name__ == "__main__":
    main()
