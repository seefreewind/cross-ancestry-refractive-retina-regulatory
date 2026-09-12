#!/usr/bin/env python3
"""Create an auditable inventory of the HRCA/GSE281526 resources."""

from pathlib import Path
import hashlib
import pandas as pd


def sha256(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ws = Path(__file__).resolve().parents[2]
    raw = ws / "data" / "raw" / "retina"
    rows = [
        {
            "resource": "HRCA atlas paper",
            "source": "Li et al. Nature Genetics 2026",
            "accession": "PMID:41578023; DOI:10.1038/s41588-025-02454-1",
            "file": "paper landing page and supplementary materials",
            "file_type": "publication/resource index",
            "genome_build": "GRCh38 reported for GSE281526 processed matrices; atlas-wide build for all integrated studies requires source audit",
            "n_donors": 125,
            "n_cells": 3900000,
            "modality": "snRNA-seq, scRNA-seq, snATAC-seq, multiome",
            "retinal_region": "fovea, macula, peripheral retina; atlas-wide integrated regions",
            "cell_resolution": ">130 cell types; major retinal classes",
            "ancestry_information": "diverse ancestral backgrounds; source definitions must be preserved from Supplementary Table 14/ancestry methods",
            "contains_OCR": "reported",
            "contains_DAR": "reported; confirmed in Supplementary Table S19",
            "contains_peak_gene_link": "reported",
            "contains_GRN": "reported",
            "download_status": "paper/source indexed",
            "sha256": "",
        },
        {
            "resource": "GSE281526",
            "source": "NCBI GEO",
            "accession": "GSE281526; BioProject PRJNA1180578",
            "file": "GSE281526 supplementary/raw matrices and 185 samples",
            "file_type": "GEO series / HDF5 matrices / raw sequencing",
            "genome_build": "GRCh38, GENCODE32 reported in GEO sample metadata",
            "n_donors": 59,
            "n_cells": "not available at series level; per-matrix metadata required",
            "modality": "snRNA-seq, snATAC-seq, multiome",
            "retinal_region": "peripheral retina, fovea centralis, macula lutea",
            "cell_resolution": "single nuclei/cells; labels in processed atlas resources",
            "ancestry_information": "diverse donor ancestry; exact genetic ancestry definition requires author tables/methods",
            "contains_OCR": "not in GEO raw matrix listing; reconstructable from fragments/processed resources",
            "contains_DAR": "not directly in GEO raw matrix listing",
            "contains_peak_gene_link": "not in GEO series listing",
            "contains_GRN": "not in GEO series listing",
            "download_status": "public accession; not reprocessed from FASTQ in Phase 0",
            "sha256": "",
        },
        {
            "resource": "HRCA supplementary information",
            "source": "Springer Nature supplementary file",
            "accession": "DOI:10.1038/s41588-025-02454-1; MOESM1",
            "file": "HRCA_41588_2025_2454_MOESM1.pdf",
            "file_type": "PDF supplementary figures, notes, methods",
            "genome_build": "to be extracted from methods; GEO states GRCh38 for GSE281526",
            "n_donors": "source-defined",
            "n_cells": "source-defined",
            "modality": "snRNA-seq, snATAC-seq, multiome",
            "retinal_region": "source-defined",
            "cell_resolution": "source-defined",
            "ancestry_information": "ancestry models and donor metadata to be extracted",
            "contains_OCR": "confirmed by supplementary table inventory/methods",
            "contains_DAR": "confirmed by Supplementary Table S19 and methods",
            "contains_peak_gene_link": "reported in paper; confirm supplementary files",
            "contains_GRN": "reported in paper; confirm supplementary files",
            "download_status": "downloaded; MinerU smoke/chunk extraction completed",
            "sha256": sha256(raw / "HRCA_41588_2025_2454_MOESM1.pdf"),
        },
        {
            "resource": "HRCA supplementary tables",
            "source": "Springer Nature supplementary file",
            "accession": "DOI:10.1038/s41588-025-02454-1; MOESM4",
            "file": "HRCA_41588_2025_2454_MOESM4_retry1.xlsx (original failed attempt preserved separately)",
            "file_type": "XLSX supplementary tables",
            "genome_build": "S12/S19 tables explicitly hg38; S20/S21 explicitly hg19",
            "n_donors": "source-defined",
            "n_cells": "source-defined",
            "modality": "multi-omic atlas",
            "retinal_region": "source-defined",
            "cell_resolution": "source-defined",
            "ancestry_information": "candidate source for ancestry metadata/DAR tables",
            "contains_OCR": "confirmed S12A/S12K",
            "contains_DAR": "confirmed S19A-S19G",
            "contains_peak_gene_link": "confirmed S19 nearest-gene fields",
            "contains_GRN": "not used in Phase 0",
            "download_status": "downloaded; ZIP_VALID; S12/S19 extracted",
            "sha256": sha256(raw / "HRCA_41588_2025_2454_MOESM4_retry1.xlsx"),
        },
        {
            "resource": "UCSC Cell Browser HRCA ATAC",
            "source": "RCHENLAB/HRCA resources",
            "accession": "UCSC dataset retina hrca atac",
            "file": "https://cells.ucsc.edu/?ds=retina+hrca+atac",
            "file_type": "interactive processed atlas",
            "genome_build": "requires browser/source metadata audit",
            "n_donors": "source-defined",
            "n_cells": "source-defined",
            "modality": "snATAC-seq / multiome",
            "retinal_region": "source-defined",
            "cell_resolution": "cell type/subclass",
            "ancestry_information": "source-defined",
            "contains_OCR": "likely processed tracks",
            "contains_DAR": "unknown until browser/data files are inspected",
            "contains_peak_gene_link": "unknown",
            "contains_GRN": "unknown",
            "download_status": "public link identified; not downloaded",
            "sha256": "",
        },
        {
            "resource": "HCA Human Eye Cell Atlas",
            "source": "Human Cell Atlas / Chen Lab",
            "accession": "HCA eye network",
            "file": "https://data.humancellatlas.org/hca-bio-networks/eye",
            "file_type": "data portal",
            "genome_build": "source-defined",
            "n_donors": "source-defined",
            "n_cells": "source-defined",
            "modality": "multi-omic atlas",
            "retinal_region": "source-defined",
            "cell_resolution": "cell type/subclass",
            "ancestry_information": "source-defined",
            "contains_OCR": "source-defined",
            "contains_DAR": "source-defined",
            "contains_peak_gene_link": "source-defined",
            "contains_GRN": "source-defined",
            "download_status": "public link identified; not downloaded",
            "sha256": "",
        },
    ]
    out = ws / "metadata" / "RETINA_RESOURCE_INVENTORY.tsv"
    pd.DataFrame(rows).to_csv(out, sep="\t", index=False)


if __name__ == "__main__":
    main()
