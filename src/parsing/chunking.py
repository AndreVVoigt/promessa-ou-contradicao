import re

#Definimos uma valor base para os chunks
def dividir_texto(texto, tamanho_max_chunk = 1000):
    if len(texto) <= tamanho_max_chunk:
        return [texto.strip()]

    #Caso não seja possível dividir o texto pelos chunks padrões
    #Iremos dividir o texto por parágrafos, frases e palavras
    partes = texto.split("\n\n")

    # Se ainda nao funcionar, usaremos a pontuação
    if len(partes) == 1:
        partes = re.split(r'(?<=[.!?]) +', texto)

     # Se não houver parágrafos, tentamos separar por frases
    if len(partes) == 1:
        partes = texto.split(" ")

    chunks_prontos = []
    chunk_atual = ""

    for parte in partes:

        parte = parte.strip()

        if not parte:
            continue

        if not chunk_atual:
            if len(parte) <= tamanho_max_chunk:
                chunk_atual = parte
            else:
                for i in range(0, len(parte), tamanho_max_chunk):
                    pedaço = parte[i:i + tamanho_max_chunk]

                    if i + tamanho_max_chunk >= len(parte):
                        chunk_atual = pedaço
                    else:
                        chunks_prontos.append(pedaço)

            

        elif len(chunk_atual) + len(parte) + 1 <= tamanho_max_chunk:
            chunk_atual += " " + parte

        else: #Se não couber iniciamos um novo chunk e adicionamos o anterior que está pronto na lista
            chunks_prontos.append(chunk_atual.strip())

            if len(parte) > tamanho_max_chunk:
                for i in range(0, len(parte), tamanho_max_chunk):
                    pedaço = parte[i:i + tamanho_max_chunk]

                    if i + tamanho_max_chunk >= len(parte):
                        chunk_atual = pedaço
                    else:
                        chunks_prontos.append(pedaço)
            else:
                chunk_atual = parte

    if chunk_atual:
        chunks_prontos.append(chunk_atual.strip())
    return chunks_prontos

def gerar_chunks(documento_id, paginas, tamanho_max_chunks=1000):
    chunks_finais = []

    for pagina in paginas:
        numero_pagina = pagina["page"]
        texto_da_pagina = pagina["text"]


        pedacos = dividir_texto(texto_da_pagina, tamanho_max_chunks)

        for indice, pedaco in enumerate(pedacos):
            id_do_chunk = documento_id + "_p" + str(numero_pagina) + "_c" + str(indice)

            chunk = {
                "chunk_id": id_do_chunk,
                "document_id": documento_id,
                "page": numero_pagina,
                "text": pedaco,
            }

            chunks_finais.append(chunk)

    return chunks_finais