import json
import os
import re
import math
import csv

def clean_n(text):
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = text.replace("\"", "")
    text = re.sub(r" +", " ", text)
    return text.strip()

def clean_cabecalho_page_num(text, document_id, page_num):


    if document_id == "PRES_01": 
        text = text.replace(f"P R O G RA M A D E G O V E R N O {page_num}", "")
    elif document_id == "PRES_02":
        page_02 = (f"{math.floor(page_num/10)} {page_num%10}" if page_num > 9 else f"{page_num}")
        text = text.replace(f"P L A N O I M P L A C ÁV E L ● R O M E U Z E M A | {page_02}", "")
    elif document_id == "PRES_03":
        text = text.replace(f"LI V R O A M A R E L O - M I SSÃ O 2 0 2 6 {page_num}", "")
    elif document_id == "PRES_04":
        text = text.replace(f"PSTU ELEIÇÕES 2026 | COM OS TRABALHADORES CONTRA O SISTEMA {page_num - 1}", "")
        text = text.replace(f"PSTU ELEIÇÕES 2026 | COM OS TRABALHADORES CONTRA O SISTEMA 0{page_num - 1}", "")
    elif document_id == "PRES_05":
        text = text.replace(f"{page_num} P R O G R A M A D E G O V E R N O", "")
        text = text.removeprefix(f"{page_num}")
    elif document_id == "PRES_06":
        text = text.replace(f"Partido Democrata · Brasil em Primeiro Lugar · Plano de Governo 2027–2030 — {page_num} —", "")
    elif document_id == "PRES_07":
        text = text.removeprefix(f"{page_num}")
    elif document_id == "PRES_08":
        text = text.removeprefix(f"{page_num}")
    elif document_id == "PRES_09":
        text = text.replace(f"Plano de Governo 2027 a 2030 · PSD · Caiado e Kassab {page_num}", "")
    elif document_id == "PRES_11":
        text = text.replace(f"Página {page_num}", "")
    elif document_id == "PRES_12":
        text = text.replace("PROGRAMA DE LUTA · ELEIÇÕES 2026", "")

    return text.strip()

def clean_text(document_id):
    with open(f"data/raw_silver/{document_id}.json", "r", encoding="utf-8") as f:
        document = json.load(f)

    for page in document["pages"]:
        page["text"] = clean_n(page["text"])
        page["text"] = clean_cabecalho_page_num(page["text"], document_id, page["page"])

    with open(f"data/clean_silver/{document_id}.json", "w", encoding="utf-8") as f:
        json.dump(document, f, ensure_ascii=False, indent=4)

    # Teste feito com um unico arquivo
    # filename = "PRES_01"
    # with open(f"data/raw_silver/{filename}.json", "r", encoding="utf-8") as f:
    #     document = json.load(f)

    # for page in document["pages"]:
    #     page["text"] = clean_n(page["text"])
    #     page["text"] = clean_cabecalho_page_num(page["text"], filename, page["page"])

    # with open(f"data/clean_silver/{filename}.json", "w", encoding="utf-8") as f:
    #     json.dump(document, f, ensure_ascii=False, indent=4)