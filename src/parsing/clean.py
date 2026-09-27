import json
import re
import csv
import os

def clean_n(text):
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = text.replace("\"", "")
    text = re.sub(r" +", " ", text)
    return text.strip()

def normalize_cabecalho(text):
    text = clean_n(text)
    text = re.sub(r"^\d+\s+", "", text)
    text = re.sub(r"\s+\d+\s*$", "", text)
    return text.strip()

def clean_page_num(text, page_num):
    text = clean_n(text)
    text = re.sub(rf"^{page_num}\s*", "", text)
    return text.strip()

def clean_text(state, document_id):
    with open(f"data/silver/raw_silver/{state}/{document_id}.json", "r", encoding="utf-8") as f:
        document = json.load(f)

    cabecalhos = set()

    for page in document["pages"]:
        blocks = page["text"]
        if not blocks:
            page["text"] = ""
            continue

        page_num = page["page"]

        for block in blocks:
            block[4] = clean_page_num(block[4], page_num)

        if blocks:
            cabecalho = normalize_cabecalho(blocks[0][4])
            if cabecalho in cabecalhos:
                blocks = blocks[1:]
            else:
                cabecalhos.add(cabecalho)

        textos = []

        for block in blocks:
            texto = clean_n(block[4])
            if texto:
                textos.append(texto)

        page["text"] = " ".join(textos)

    os.makedirs(f"data/silver/clean_silver/{state}", exist_ok=True)

    with open(f"data/silver/clean_silver/{state}/{document_id}.json", "w", encoding="utf-8") as f:
        json.dump(document, f, ensure_ascii=False, indent=4)