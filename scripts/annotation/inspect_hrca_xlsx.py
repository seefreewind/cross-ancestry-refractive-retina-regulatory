#!/usr/bin/env python3
"""Stream-inspect HRCA supplementary XLSX sheets without loading the workbook."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET


NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


def col_index(ref: str) -> int:
    letters = re.match(r"([A-Z]+)", ref).group(1)
    out = 0
    for char in letters:
        out = out * 26 + ord(char) - 64
    return out


def workbook_sheets(z: ZipFile) -> dict[str, str]:
    root = ET.fromstring(z.read("xl/workbook.xml"))
    rel_root = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rels = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rel_root.findall(f"{{{NS_PKG_REL}}}Relationship")
    }
    out = {}
    for sheet in root.find(f"{{{NS_MAIN}}}sheets"):
        target = rels[sheet.attrib[f"{{{NS_REL}}}id"]]
        if not target.startswith("xl/"):
            target = "xl/" + target
        out[sheet.attrib["name"]] = target
    return out


def shared_ids(z: ZipFile, sheet_paths: list[str]) -> set[int]:
    ids: set[int] = set()
    for path in sheet_paths:
        for _, elem in ET.iterparse(z.open(path), events=("end",)):
            tag = elem.tag.rsplit("}", 1)[-1]
            if tag == "c" and elem.attrib.get("t") == "s":
                v = elem.find(f"{{{NS_MAIN}}}v")
                if v is not None and v.text:
                    ids.add(int(v.text))
                elem.clear()
            elif tag == "row":
                elem.clear()
    return ids


def load_required_shared_strings(z: ZipFile, wanted: set[int]) -> dict[int, str]:
    out: dict[int, str] = {}
    index = 0
    parts: list[str] = []
    for _, elem in ET.iterparse(z.open("xl/sharedStrings.xml"), events=("end",)):
        tag = elem.tag.rsplit("}", 1)[-1]
        if tag == "t":
            parts.append(elem.text or "")
            elem.clear()
        elif tag == "si":
            if index in wanted:
                out[index] = "".join(parts)
            index += 1
            parts = []
            elem.clear()
            if len(out) == len(wanted):
                break
        elif tag in {"rPh", "phoneticPr"}:
            elem.clear()
    return out


def read_rows(z: ZipFile, path: str, strings: dict[int, str], max_rows: int):
    for _, row in ET.iterparse(z.open(path), events=("end",)):
        if row.tag.rsplit("}", 1)[-1] != "row":
            continue
        values = {}
        for cell in row:
            if cell.tag.rsplit("}", 1)[-1] != "c":
                continue
            ref = cell.attrib.get("r", "")
            value = cell.find(f"{{{NS_MAIN}}}v")
            if value is None:
                inline = cell.find(f"{{{NS_MAIN}}}is")
                text = "" if inline is None else "".join(
                    node.text or ""
                    for node in inline.iter()
                    if node.tag.rsplit("}", 1)[-1] == "t"
                )
            elif cell.attrib.get("t") == "s":
                text = strings.get(int(value.text), f"[shared:{value.text}]")
            else:
                text = value.text or ""
            values[col_index(ref)] = text
        row_no = int(row.attrib.get("r", "0"))
        if values:
            yield row_no, values
        row.clear()
        if max_rows and row_no >= max_rows:
            break


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx", type=Path)
    ap.add_argument("--sheet", action="append", required=True)
    ap.add_argument("--rows", type=int, default=8)
    args = ap.parse_args()

    with ZipFile(args.xlsx) as z:
        sheets = workbook_sheets(z)
        missing = [name for name in args.sheet if name not in sheets]
        if missing:
            raise SystemExit(f"Unknown sheet(s): {missing}")
        paths = [sheets[name] for name in args.sheet]
        wanted = shared_ids(z, paths)
        strings = load_required_shared_strings(z, wanted)
        print(f"shared_ids={len(wanted)} resolved={len(strings)}")
        for name, path in zip(args.sheet, paths):
            print(f"\nSHEET\t{name}\t{path}")
            for row_no, values in read_rows(z, path, strings, args.rows):
                ordered = [values[i] for i in sorted(values)]
                print(f"ROW\t{row_no}\t" + "\t".join(ordered))


if __name__ == "__main__":
    main()
