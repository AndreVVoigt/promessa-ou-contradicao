import json
import os
import csv
import pandas as pd
from chunking import gerar_chunks
from clean import clean_text
from extract import extract_text


def ler_documentos(pasta_entrada):
    documentos = []

    for estado in os.listdir(pasta_entrada):
        pasta_estado = os.path.join(pasta_entrada, estado)

        if not os.path.isdir(pasta_estado):
            continue

        for nome_arquivo in os.listdir(pasta_estado):
            if not nome_arquivo.endswith(".json"):
                continue

            caminho_completo = os.path.join(pasta_estado, nome_arquivo)

            with open(caminho_completo, "r", encoding="utf-8") as arquivo:
                documento = json.load(arquivo)

            documentos.append(documento)

    return documentos


def construir_silver(pasta_entrada, caminho_saida):
    documentos = ler_documentos(pasta_entrada)
    todos_os_chunks = []

    for documento in documentos:
        doc_id = documento["document_id"]
        paginas = documento["pages"]

        chunks_do_doc = gerar_chunks(doc_id, paginas)

        for chunk in chunks_do_doc:
            todos_os_chunks.append(chunk)

    tabela = pd.DataFrame(todos_os_chunks)
    tabela["n_chars"] = tabela["text"].str.len()

    tabela.to_parquet(caminho_saida, index=False)

    print("Chunks gerados:", len(tabela))
    print("Salvo em:", caminho_saida)


if __name__ == "__main__":
    os.makedirs(f"data/silver/raw_silver", exist_ok=True)
    os.makedirs(f"data/silver/clean_silver", exist_ok=True)

    with open(
        "data/bronze/metadata/documents.csv",
        "r",
        encoding="utf-8"
    ) as csvfile:

        reader = csv.DictReader(csvfile)

        for row in reader:
            state = row["state"]
            filename = row["filename"]
            document_id = row["document_id"]

            extract_text(state, filename, document_id)
            clean_text(state, document_id)

    construir_silver(
        pasta_entrada="data/silver/clean_silver",
        caminho_saida="data/silver/chunks.parquet",
    )