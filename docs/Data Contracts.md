# Contrato de Dados — "Promessa ou Contradição?"

**Versão:** v1 · **Mantido por:** DE-3 (André Voigt, Arthur Sean) · **Atualizado:** 26/09/2026

Versão oficial dos contratos de dados do projeto. Se você produz dados consumidos
por outra equipe, eles precisam chegar neste formato.

Escopo da v1: planos de governo de candidatos à Presidência e a Governador.

Em todo o documento, **"não vazio"** significa: não nulo e não vazio após remover
espaços em branco das pontas.

---

## O que mudou da v0 para a v1

- `document_id` passa a ser derivado da candidatura oficial do TSE (`SQ_CANDIDATO`)
- Uma candidatura pode ter mais de um PDF (`_01`, `_02`)
- Manifest ganha `candidate_id`
- Silver ganha `chunk_index`; `section` passa a ser coluna obrigatória (valor pode ser nulo)
- Aceita Governadores (`GOV_`)
- `dataset_version` passa para `bronze_v1` e `silver_v1`

---

## 1. Convenção de IDs

| Entidade | Padrão | Exemplo | Regex |
|---|---|---|---|
| Candidatura | `{SQ_CANDIDATO}` | `280002538811` | `^\d+$` |
| Documento | `{CARGO}_{SQ_CANDIDATO}_{NN}` | `PRES_280002538811_01` | `^(PRES\|GOV)_\d+_\d{2}$` |
| Chunk | `{document_id}_p{PPP}_c{CCC}` | `PRES_280002538811_01_p014_c003` | `^(PRES\|GOV)_\d+_\d{2}_p\d{3}_c\d{3}$` |

- `CARGO` é `PRES` ou `GOV`.
- `NN` é a parte do documento, como vem no nome do arquivo do TSE: `_01`, `_02`...
- `PPP` e `CCC` têm três dígitos, com zeros à esquerda. O primeiro chunk da página é `c001`.

Se a mesma candidatura tiver mais de um PDF, o `candidate_id` é igual e o
`document_id` muda só no final:

```
candidate_id = 280002538811
document_id  = PRES_280002538811_01
document_id  = PRES_280002538811_02
```

**Estáveis:** rodar o pipeline de novo sobre a mesma entrada produz os mesmos IDs.
O ID vem da candidatura oficial e da posição no documento, nunca da ordem de execução.

**Legíveis:** `PRES_280002538811_01_p014_c003` é o terceiro chunk da página 14 da
parte 01 do plano da candidatura 280002538811 à Presidência.

**Proibido:** contador global sequencial.

---

## 2. `data/bronze/metadata/documents.csv` — manifest

**Produzido por:** DE-1 · **Consumido por:** DE-2, DE-3

| Campo | Tipo | Obrig. | Regra de validação | Exemplo |
|---|---|---|---|---|
| `document_id` | string | sim | Único no arquivo. Formato da seção 1. | `PRES_280002538811_01` |
| `candidate_id` | string | sim | `SQ_CANDIDATO`. Repete se a candidatura tiver mais de um PDF. | `280002538811` |
| `candidate` | string | sim | Não vazio. Nome de urna, como consta no cadastro do TSE. | `Fulano de Tal` |
| `party` | string | sim | Não vazio. Sigla em maiúsculas. | `PDA` |
| `office` | enum | sim | Em {`PRESIDENTE`, `GOVERNADOR`}. Sensível a maiúsculas. | `PRESIDENTE` |
| `state` | string | sim | UF de duas letras maiúsculas, ou `BR` para Presidência. | `BR` |
| `source_url` | string | sim | Não vazio. Começa com `https://`. | `https://cdn.tse.jus.br/.../proposta_governo_2026_BR.zip` |
| `original_filename` | string \| null | não | Nome exato dentro do ZIP do TSE. Nulo se `status != ok`. | `2026BR280002538811_01.pdf` |
| `filename` | string \| null | não | Igual a `document_id` + `.pdf`. Nulo se `status != ok`. | `PRES_280002538811_01.pdf` |
| `download_timestamp` | timestamp | sim | ISO 8601 em UTC. Não pode ser futuro. | `2026-09-26T10:56:35Z` |
| `dataset_version` | string | sim | `^bronze_v\d+$`. Constante no arquivo. | `bronze_v1` |
| `status` | enum | sim | Em {`ok`, `erro_download`, `arquivo_vazio`, `url_invalida`}. Sensível a maiúsculas. | `ok` |

Os PDFs ficam em `data/bronze/_extraido/<UF>/<filename>`.

Linhas com `status != ok` registram candidaturas sem PDF. Elas ficam no manifest,
não têm arquivo, e o DE-2 as ignora.

---

## 3. `data/silver/chunks.parquet`

**Produzido por:** DE-2 · **Validado por:** DE-3 · **Consumido por:** extração, RAG, evaluation

| Campo | Tipo | Obrig. | Regra de validação | Exemplo |
|---|---|---|---|---|
| `chunk_id` | string | sim | Único no dataset. Formato da seção 1. O trecho antes de `_p` é igual a `document_id`. | `PRES_280002538811_01_p014_c003` |
| `document_id` | string | sim | Existe no manifest, com `status = ok`. Repete. | `PRES_280002538811_01` |
| `page` | int | sim | Inteiro ≥ 1. Igual ao `PPP` do `chunk_id`. | `14` |
| `section` | string \| null | sim (coluna) | A coluna precisa existir. O valor pode ser nulo. String vazia não é aceita. | `Saúde` |
| `chunk_index` | int | sim | Inteiro ≥ 1. Igual ao `CCC` do `chunk_id`. | `3` |
| `text` | string | sim | Não vazio. | `Ampliar em 30% o número de equipes...` |
| `n_chars` | int | sim | Igual ao comprimento de `text`. | `90` |
| `dataset_version` | string | sim | `^silver_v\d+$`. Constante no arquivo. | `silver_v1` |


---

## 4. Estrutura de pastas

```
data/
├── bronze/     
├── silver/     
└── mock/       
src/
├── acquisition/   # DE-1
├── parsing/       # DE-2
└── quality/       # DE-3
schemas/           # DE-3
tests/
scripts/
docs/
├── data_contracts.md    # DE-3
└── parsing_issues.md    # DE-2
```

---

## 5. Como alterar este contrato

Detalhar uma regra já implícita é manutenção e não exige acordo. Acrescentar,
remover ou mudar o tipo de um campo exige acordo do grupo.

1. Propor no grupo e esperar manifestação de quem produz e de quem consome.
2. Incrementar `dataset_version`.
3. Atualizar os mocks e os schemas junto com este documento.

