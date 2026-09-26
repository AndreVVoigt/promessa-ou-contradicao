"""Metadados dos candidatos (cadastro do TSE) e geração do manifest documents.csv."""

import csv
import io
import logging
import zipfile
from datetime import datetime, timezone
from pathlib import Path

TARGET_OFFICES = {"GOVERNADOR", "PRESIDENTE"}

DATASET_VERSION = "bronze_v0"

MANIFEST_FIELDS = [
    "document_id", "candidate", "party", "office", "state", "source_url",
    "original_filename", "filename", "download_timestamp", "dataset_version", "status",
]


def load_valid_candidates_metadata(candidates_zip: Path) -> dict:
    """
    Lê consulta_cand_2026.zip e devolve um dicionário de SQ_CANDIDATO
    com os metadados necessários para o manifest.
    """
    candidates = {}
    with zipfile.ZipFile(candidates_zip) as z:
        csv_names = [n for n in z.namelist() if n.lower().endswith(".csv")]
        for name in csv_names:
            with z.open(name) as f:
                text_stream = io.TextIOWrapper(f, encoding="latin-1", errors="replace")
                reader = csv.DictReader(text_stream, delimiter=";")
                for row in reader:
                    office = (row.get("DS_CARGO") or "").strip().upper()
                    if office in TARGET_OFFICES:
                        sq = row.get("SQ_CANDIDATO")
                        prefix = "PRES" if office == "PRESIDENTE" else "GOV"
                        # id é formado por um prefixo PRES ou GOV e o número único do candidato gerado pelo tse
                        doc_id = f"{prefix}_{sq}"

                        candidates[sq] = {
                            "document_id": doc_id,
                            "candidate": row.get("NM_URNA_CANDIDATO") or row.get("NM_CANDIDATO"),
                            "party": row.get("SG_PARTIDO"),
                            "office": office,
                            "state": row.get("SG_UF"),
                            "status": "arquivo_vazio",
                            "original_filename": "NULL",
                            "filename": "NULL",
                        }
    logging.info("cadastro de candidatos: %d candidaturas a governador/presidente", len(candidates))
    return candidates


def write_manifest(candidates: dict, states: list[str], manifest_path: Path, proposal_url_template: str) -> None:
    """Grava o manifest com 1 linha por PDF extraído (ou 1 linha por candidato sem PDF)."""
    download_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(manifest_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()

        for cand in sorted(candidates.values(), key=lambda x: x["document_id"]):
            if cand["state"] not in states:
                continue

            if "extracted_docs" in cand:
                for doc in cand["extracted_docs"]:
                    writer.writerow({
                        "document_id": doc["document_id"],
                        "candidate": cand["candidate"],
                        "party": cand["party"],
                        "office": cand["office"],
                        "state": cand["state"],
                        "source_url": doc["source_url"],
                        "original_filename": doc["original_filename"],
                        "filename": doc["filename"],
                        "download_timestamp": download_timestamp,
                        "dataset_version": DATASET_VERSION,
                        "status": doc["status"],
                    })
            else:
                if "source_url" not in cand:
                    cand["source_url"] = proposal_url_template.format(uf=cand["state"])

                writer.writerow({
                    "document_id": cand["document_id"],  # fica sem sufixo
                    "candidate": cand["candidate"],
                    "party": cand["party"],
                    "office": cand["office"],
                    "state": cand["state"],
                    "source_url": cand["source_url"],
                    "original_filename": "NULL",
                    "filename": "NULL",
                    "download_timestamp": download_timestamp,
                    "dataset_version": DATASET_VERSION,
                    "status": cand["status"],
                })
