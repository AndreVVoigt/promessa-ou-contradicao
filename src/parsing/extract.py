import pymupdf
import csv
import json
import os

def extract_text(filename, document_id):
    doc = pymupdf.open(f"data/seed_v0/{filename}")

    document = {
        "document_id": document_id,
        "pages": []
    }

    for page in doc:
        if document_id == "PRES_01":
            blocks = page.get_text("blocks")
            text = ""
            for block in blocks:
                text += block[4]
        else:
            text = page.get_text()
            
        document["pages"].append({
            "page": page.number+1,
            "text": text
        })

    doc.close()

    with open(f"data/raw_silver/{document_id}.json", "w", encoding="utf-8") as f:
        json.dump(document, f, ensure_ascii=False, indent=4)

    # Teste feito com um unico arquivo
    # doc = pymupdf.open(f"data/seed_v0/2026BR280002538811_01.pdf")

    # document = {
    #     "document_id": "2026BR280002538811_01",
    #     "pages": []
    # }

    # for page in doc:
    #     blocks = page.get_text("blocks")
    #     text = ""
    #     for block in blocks:
    #         text += block[4]

    #     document["pages"].append({
    #         "page": page.number+1,
    #         "text": text
    #     })

    # doc.close()

    # with open(f"data/raw_silver/2026BR280002538811_01.json", "w", encoding="utf-8") as f:
    #     json.dump(document, f, ensure_ascii=False, indent=4)