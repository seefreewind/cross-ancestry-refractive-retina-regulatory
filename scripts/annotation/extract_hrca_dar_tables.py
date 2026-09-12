#!/usr/bin/env python3
"""Extract HRCA ancestry-DAR tables and OCR count table from the large XLSX."""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from inspect_hrca_xlsx import NS_MAIN, col_index, load_required_shared_strings, shared_ids, workbook_sheets


ROOT = Path(__file__).resolve().parents[2]
XLSX = ROOT / "data/raw/retina/HRCA_41588_2025_2454_MOESM4_retry1.xlsx"
DAR_OUT = ROOT / "data/processed/HRCA_ANCESTRY_DAR.tsv"
COUNTS_OUT = ROOT / "data/processed/HRCA_OCR_COUNTS.tsv"
AUDIT_OUT = ROOT / "results/phase0/ANCESTRY_DAR_AUDIT.tsv"


def cell_value(cell, strings: dict[int, str]) -> str:
    value = cell.find(f"{{{NS_MAIN}}}v")
    if value is None:
        inline = cell.find(f"{{{NS_MAIN}}}is")
        if inline is None:
            return ""
        return "".join(
            node.text or ""
            for node in inline.iter()
            if node.tag.rsplit("}", 1)[-1] == "t"
        )
    if cell.attrib.get("t") == "s":
        return strings.get(int(value.text), f"[shared:{value.text}]")
    return value.text or ""


def row_values(row, strings: dict[int, str]) -> dict[int, str]:
    out = {}
    for cell in row:
        if cell.tag.rsplit("}", 1)[-1] == "c":
            out[col_index(cell.attrib.get("r", "A1"))] = cell_value(cell, strings)
    return out


def rows(path: str, z: ZipFile, strings: dict[int, str]):
    for _, row in ET.iterparse(z.open(path), events=("end",)):
        if row.tag.rsplit("}", 1)[-1] != "row":
            continue
        values = row_values(row, strings)
        row_no = int(row.attrib.get("r", "0"))
        row.clear()
        if values:
            yield row_no, values


def find_header(sheet_rows):
    cached = []
    for row_no, values in sheet_rows:
        cached.append((row_no, values))
        text = {v.strip().lower() for v in values.values() if v.strip()}
        if {"seqnames", "start", "end"}.issubset(text) or {"cell type", "number of peaks"}.issubset(text):
            return row_no, values, sheet_rows
    raise ValueError("header not found")


def sheet_cell_class(name: str) -> str:
    match = re.search(r"Table S19([A-G]) - ([^ ]+) hg38", name)
    if not match:
        return ""
    aliases = {"BC": "Bipolar", "AC": "Amacrine", "HC": "Horizontal", "MG": "Muller_glia", "RGC": "RGC"}
    return aliases.get(match.group(2), match.group(2))


def main() -> None:
    s19_names = [
        "Table S19A - Rod hg38", "Table S19B - RGC hg38", "Table S19C - MG hg38",
        "Table S19D - HC hg38", "Table S19E - Cone hg38", "Table S19F - BC hg38",
        "Table S19G - AC hg38",
    ]
    s12_name = "Table S12A - Peak numbers"

    with ZipFile(XLSX) as z:
        sheets = workbook_sheets(z)
        names = s19_names + [s12_name]
        paths = [sheets[n] for n in names]
        strings = load_required_shared_strings(z, shared_ids(z, paths))

        DAR_OUT.parent.mkdir(parents=True, exist_ok=True)
        COUNTS_OUT.parent.mkdir(parents=True, exist_ok=True)
        AUDIT_OUT.parent.mkdir(parents=True, exist_ok=True)

        dar_header = [
            "cell_class", "seqnames", "start", "end", "width", "strand", "score",
            "replicateScoreQuantile", "groupScoreQuantile", "Reproducibility", "GroupReplicate",
            "distToGeneStart", "nearestGene", "peakType", "distToTSS", "nearestTSS", "GC",
            "idx", "N", "peak", "self_reported_ethnicity", "Log2FC", "FDR", "MeanDiff",
            "source_sheet", "build",
        ]
        with DAR_OUT.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=dar_header, delimiter="\t", extrasaction="ignore")
            writer.writeheader()
            for name in s19_names:
                it = rows(sheets[name], z, strings)
                header_no, header_vals, remainder = find_header(it)
                headers = {col: value for col, value in header_vals.items() if value}
                for row_no, values in remainder:
                    if row_no <= header_no:
                        continue
                    record = {headers.get(col, f"col_{col}"): value for col, value in values.items()}
                    if not record.get("seqnames"):
                        continue
                    if "FRD" in record and "FDR" not in record:
                        record["FDR"] = record.pop("FRD")
                    if "self-reported ethnicity" in record:
                        record["self_reported_ethnicity"] = record.pop("self-reported ethnicity")
                    record.update({"cell_class": sheet_cell_class(name), "source_sheet": name, "build": "hg38"})
                    writer.writerow(record)

        with COUNTS_OUT.open("w", newline="") as fh:
            writer = csv.writer(fh, delimiter="\t")
            writer.writerow(["cell_class_source", "cell_class", "number_of_peaks", "source_sheet", "build"])
            it = rows(sheets[s12_name], z, strings)
            header_no, header_vals, remainder = find_header(it)
            headers = {col: value for col, value in header_vals.items() if value}
            for row_no, values in remainder:
                if row_no <= header_no:
                    continue
                rec = {headers.get(col, f"col_{col}"): value for col, value in values.items()}
                if not rec.get("Cell type"):
                    continue
                aliases = {"AC": "Amacrine", "Astrocyte": "Astrocyte", "BC": "Bipolar", "Cone": "Cone", "HC": "Horizontal", "MG": "Muller_glia", "Microglia": "Microglia", "RGC": "RGC", "Rod": "Rod"}
                writer.writerow([rec.get("Cell type", ""), aliases.get(rec.get("Cell type", ""), rec.get("Cell type", "")), rec.get("Number of peaks", ""), s12_name, "hg38"])

    # Compact audit table with counts and ancestry direction.
    rows_by_class: dict[str, list[dict[str, str]]] = defaultdict(list)
    with DAR_OUT.open() as fh:
        for rec in csv.DictReader(fh, delimiter="\t"):
            rows_by_class[rec["cell_class"]].append(rec)
    with AUDIT_OUT.open("w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["cell_class", "ancestry_label", "n_DAR_rows", "n_unique_intervals", "n_fdr_le_0.05", "n_log2fc_ge_0.5", "n_fdr_le_0.05_and_log2fc_ge_0.5", "min_fdr", "median_log2fc", "build", "source"])
        for cell_class in sorted(rows_by_class):
            recs = rows_by_class[cell_class]
            ancestry_counts = Counter(r["self_reported_ethnicity"] for r in recs)
            for ancestry, n in sorted(ancestry_counts.items()):
                subset = [r for r in recs if r["self_reported_ethnicity"] == ancestry]
                fdr = [float(r["FDR"]) for r in subset if r.get("FDR")]
                lfc = [float(r["Log2FC"]) for r in subset if r.get("Log2FC")]
                writer.writerow([
                    cell_class, ancestry, n,
                    len({(r["seqnames"], r["start"], r["end"]) for r in subset}),
                    sum(x <= 0.05 for x in fdr), sum(x >= 0.5 for x in lfc),
                    sum(x <= 0.05 and y >= 0.5 for x, y in zip(fdr, lfc)),
                    min(fdr) if fdr else "", sorted(lfc)[len(lfc) // 2] if lfc else "", "hg38",
                    "HRCA Supplementary Table S19",
                ])


if __name__ == "__main__":
    main()
