#!/usr/bin/env python3
"""Stream the 700k-row HRCA S12 union OCR coordinate table."""

from __future__ import annotations

import csv
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from inspect_hrca_xlsx import NS_MAIN, col_index, load_required_shared_strings, workbook_sheets


ROOT = Path(__file__).resolve().parents[2]
XLSX = ROOT / "data/raw/retina/HRCA_41588_2025_2454_MOESM4_retry1.xlsx"
OUT = ROOT / "data/processed/HRCA_UNION_OCR.tsv"


def main() -> None:
    with ZipFile(XLSX) as z:
        sheet = workbook_sheets(z)["Table S12K - Union_peakset hg38"]
        tmp = OUT.with_suffix(".tmp.tsv")
        wanted: set[int] = set()
        n = 0
        with tmp.open("w", newline="") as fh:
            writer = csv.writer(fh, delimiter="\t")
            writer.writerow(["chrom_id", "start", "end", "width"])
            for _, row in ET.iterparse(z.open(sheet), events=("end",)):
                if row.tag.rsplit("}", 1)[-1] != "row":
                    continue
                row_no = int(row.attrib.get("r", "0"))
                values = {}
                for cell in row:
                    if cell.tag.rsplit("}", 1)[-1] != "c":
                        continue
                    col = col_index(cell.attrib.get("r", "A1"))
                    if col > 4:
                        continue
                    value = cell.find(f"{{{NS_MAIN}}}v")
                    if value is None or value.text is None:
                        continue
                    if cell.attrib.get("t") == "s":
                        values[col] = int(value.text)
                        if col == 1:
                            wanted.add(int(value.text))
                    else:
                        values[col] = value.text
                if row_no > 1 and {1, 2, 3}.issubset(values):
                    writer.writerow([values[1], values[2], values[3], values.get(4, "")])
                    n += 1
                    if n % 100000 == 0:
                        print(f"rows={n}", flush=True)
                row.clear()
        strings = load_required_shared_strings(z, wanted)
        with tmp.open() as src, OUT.open("w", newline="") as dst:
            reader = csv.DictReader(src, delimiter="\t")
            writer = csv.DictWriter(dst, fieldnames=["seqnames", "start", "end", "width"], delimiter="\t")
            writer.writeheader()
            for rec in reader:
                writer.writerow({
                    "seqnames": strings.get(int(rec["chrom_id"]), f"[shared:{rec['chrom_id']} ]"),
                    "start": rec["start"], "end": rec["end"], "width": rec["width"],
                })
        tmp.unlink()
        print(f"extracted_rows={n} chrom_ids={len(wanted)} resolved={len(strings)}")


if __name__ == "__main__":
    main()
