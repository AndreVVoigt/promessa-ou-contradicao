import pandas as pd
from .resultado import ResultadoCheck

OFFICE_PERMITIDOS = {"PRESIDENTE", "GOVERNADOR"}
STATE_PERMITIDOS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO", "BR",
}


def _ids_de(df: pd.DataFrame, coluna_id: str) -> list[str]:

    # Devolve lista de IDs de um DataFrame, com marcação de nulos.

    ids = []
    for indice, valor in df[coluna_id].items():
        ids.append(str(valor) if pd.notna(valor) else f"<linha {indice}: id nulo>")
    return ids


# check 1
def chunk_id_nao_nulo_e_unico(chunks: pd.DataFrame) -> ResultadoCheck:

    # chunk_id precisa ser não nulo e único.

    nome = "chunk_id não nulo e único"

    nulos = chunks[chunks["chunk_id"].isna()]
    duplicados = chunks[chunks["chunk_id"].duplicated(keep=False) & chunks["chunk_id"].notna()]

    ids = [f"<linha {i}: nulo>" for i in nulos.index]
    ids += sorted(duplicados["chunk_id"].unique().tolist())

    total = len(nulos) + len(duplicados)

    return ResultadoCheck(
        nome=nome,
        passou=total == 0,
        violacoes=total,
        ids=ids,
        detalhe=f"{len(nulos)} nulo(s), {len(duplicados)} linha(s) com ID repetido",
    )


# check 2
def document_id_existe_no_manifest(
    chunks: pd.DataFrame, manifest: pd.DataFrame
) -> ResultadoCheck:
    
    # document_id de cada chunk precisa existir no manifest.

    nome = "document_id existe no manifest"

    conhecidos = set(manifest["document_id"].dropna())
    orfaos = chunks[~chunks["document_id"].isin(conhecidos) | chunks["document_id"].isna()]

    faltantes = sorted(orfaos["document_id"].dropna().unique().tolist())

    return ResultadoCheck(
        nome=nome,
        passou=len(orfaos) == 0,
        violacoes=len(orfaos),
        ids=_ids_de(orfaos, "chunk_id"),
        detalhe=(
            f"document_id não encontrado no manifest: {', '.join(faltantes)}"
            if faltantes else ""
        ),
    )


# check 3
def page_maior_ou_igual_a_um(chunks: pd.DataFrame) -> ResultadoCheck:

    # page precisa ser >= 1. Não é permitido nulo nem zero nem negativo.

    nome = "page >= 1"

    invalidos = chunks[chunks["page"].isna() | (chunks["page"] < 1)]

    return ResultadoCheck(
        nome=nome,
        passou=len(invalidos) == 0,
        violacoes=len(invalidos),
        ids=_ids_de(invalidos, "chunk_id"),
        detalhe=(
            f"valores encontrados: {sorted(invalidos['page'].dropna().unique().tolist())}"
            if len(invalidos) else ""
        ),
    )


# check 4
def text_nao_vazio(chunks: pd.DataFrame) -> ResultadoCheck:

    # text precisa ser não nulo e não vazio (apenas espaços em branco).

    nome = "text não vazio"

    texto = chunks["text"]
    vazios = chunks[texto.isna() | (texto.fillna("").str.strip() == "")]

    return ResultadoCheck(
        nome=nome,
        passou=len(vazios) == 0,
        violacoes=len(vazios),
        ids=_ids_de(vazios, "chunk_id"),
        detalhe=f"{len(vazios)} chunk(s) sem conteúdo aproveitável" if len(vazios) else "",
    )


# check 5
def office_e_state_permitidos(manifest: pd.DataFrame) -> ResultadoCheck:

    # office e state precisam estar entre os valores permitidos.

    nome = "office e state em valores permitidos"

    office_invalido = manifest[~manifest["office"].isin(OFFICE_PERMITIDOS)]
    state_invalido = manifest[~manifest["state"].isin(STATE_PERMITIDOS)]

    ids = _ids_de(office_invalido, "document_id") + _ids_de(state_invalido, "document_id")
    total = len(office_invalido) + len(state_invalido)

    detalhes = []
    if len(office_invalido):
        valores = office_invalido["office"].unique().tolist()
        detalhes.append(f"office inválido: {valores}")
    if len(state_invalido):
        valores = state_invalido["state"].unique().tolist()
        detalhes.append(f"state inválido: {valores}")

    return ResultadoCheck(
        nome=nome,
        passou=total == 0,
        violacoes=total,
        ids=ids,
        detalhe="; ".join(detalhes),
    )
