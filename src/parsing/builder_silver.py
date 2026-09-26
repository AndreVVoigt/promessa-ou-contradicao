import json
import os
import csv
import pandas as pd
from chunking import gerar_chunks
from clean import clean_text
from extract import extract_text


#Pega cada arquivo da pasta e separa em documentos
def ler_documentos(pasta_entrada):
    documentos = []


    for nome_arquivo in os.listdir(pasta_entrada):
        if not nome_arquivo.endswith(".json"):
            continue


        caminho_completo = os.path.join(pasta_entrada, nome_arquivo)


        arquivo = open(caminho_completo, "r", encoding="utf-8")
        documento = json.load(arquivo)
        arquivo.close()


        documentos.append(documento)


    return documentos


# Gera os chunks
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
    with open("data/metadata/documents.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            filename = row["filename"]
            document_id = row["document_id"]

            extract_text(filename, document_id)
            clean_text(document_id)

    construir_silver(
        pasta_entrada="data/clean_silver",
        caminho_saida="data/silver/chunks.parquet",
    )

