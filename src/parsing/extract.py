import pymupdf
import csv
import json
import os

def extract_text(state, filename, document_id):
    doc = pymupdf.open(f"data/bronze/_extraido/{state}/{filename}")

    document = {
        "document_id": document_id,
        "pages": []
    }

    for page in doc:
        text = page.get_text("blocks")
            
        document["pages"].append({
            "page": page.number+1,
            "text": text
        })

    doc.close()

    os.makedirs(f"data/silver/raw_silver/{state}", exist_ok=True)

    with open(f"data/silver/raw_silver/{state}/{document_id}.json", "w", encoding="utf-8") as f:
        json.dump(document, f, ensure_ascii=False, indent=4)