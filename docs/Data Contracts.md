# Contrato de Dados — "Promessa ou Contradição?"

**Versão:** v0 · **Mantido por:** DE-3 (André Voigt, Arthur Sean) · **Atualizado:** 15/09/2026

Versão oficial dos contratos de dados do projeto. Se você produz dados consumidos
por outra equipe, eles precisam chegar neste formato.

Escopo da v0: planos de governo de candidatos à Presidência.

Em todo o documento, **"não vazio"** significa: não nulo e não vazio após remover
espaços em branco das pontas.

---

## 1. Convenção de IDs

| Entidade | Padrão | Exemplo | Regex |
|---|---|---|---|
| Documento | `{CARGO}_{NNN}` | `PRES_001` | `^PRES_\d{3}$` |
| Chunk | `{document_id}_p{PPP}_c{CCC}` | `PRES_001_p014_c003` | `^PRES_\d{3}_p\d{3}_c\d{3}$` |

`NNN`, `PPP` e `CCC` têm três dígitos, com zeros à esquerda.

**Estáveis:** rodar o pipeline de novo sobre a mesma entrada produz os mesmos IDs.
O ID é derivado de propriedades do documento (cargo, página, ordem do chunk na
página), nunca da ordem de execução.

**Legíveis:** dá para saber a origem só olhando. `PRES_001_p014_c003` é o terceiro
chunk da página 14 do documento `PRES_001`.

**Proibido:** contador global sequencial. Se um documento novo entra no meio, todos
os IDs seguintes mudam e as anotações da equipe de Evaluation passam a apontar para
o trecho errado.

---

## 2. `data/bronze/metadata/documents.csv` — manifest

**Produzido por:** DE-1 · **Consumido por:** DE-2, DE-3

| Campo | Tipo | Obrig. | Regra de validação | Exemplo |
|---|---|---|---|---|
| `document_id` | string | sim | Único no arquivo. `^PRES_\d{3}$`. | `PRES_001` |
| `candidate` | string | sim | Não vazio. Nome como consta no plano, sem normalização. | `Ana Ribeiro Matos` |
| `party` | string | sim | Não vazio. Sigla em maiúsculas. | `PDA` |
| `office` | enum | sim | Em {`PRESIDENTE`, `GOVERNADOR`}. Sensível a maiúsculas. | `PRESIDENTE` |
| `state` | string | sim | Duas letras maiúsculas ou `BR`. | `BR` |
| `source_url` | string | sim | Não vazio. Começa com `https://`. | `https://divulgacandcontas.tse.jus.br/...` |
| `original_filename` | string | sim | Não vazio. Nome exato de origem, com extensão. | `2026BR280002500143_01.pdf` |
| `filename` | string | sim | Não vazio. Único no arquivo. Sem espaços nem acentos. | `PRES_001.pdf` |
| `download_timestamp` | timestamp | sim |  Não pode ser futuro. | `2026-09-10T13:04:22Z` |
| `dataset_version` | string | sim | `^bronze_v\d+$`. Constante no arquivo. | `bronze_v0` |
| `status` | enum | sim | Em {`ok`, `erro_download`, `arquivo_vazio`, `url_invalida`}. Sensível a maiúsculas. | `ok` |

Linhas com `status != ok` ficam no manifest e não têm arquivo correspondente em
`data/bronze/raw/`.

---

## 3. `data/silver/chunks.parquet`

**Produzido por:** DE-2 · **Validado por:** DE-3 · **Consumido por:** extração, RAG, evaluation

| Campo | Tipo | Obrig. | Regra de validação | Exemplo |
|---|---|---|---|---|
| `chunk_id` | string | sim | Único no dataset. `^PRES_\d{3}_p\d{3}_c\d{3}$`. O trecho antes de `_p` é igual a `document_id`. | `PRES_001_p014_c003` |
| `document_id` | string | sim | Existe no manifest. Repete: um documento tem muitos chunks. | `PRES_001` |
| `page` | int | sim | Inteiro ≥ 1. Igual, como número, ao `PPP` do `chunk_id`. | `14` |
| `section` | string \| null | não | Nulo aceito na v0. Se preenchido, não vazio. String vazia não é aceita. | `Saúde` |
| `text` | string | sim | Não vazio. | `Ampliar em 30% o número de equipes...` |
| `n_chars` | int | sim | Inteiro ≥ 1. Igual ao comprimento de `text`. | `90` |
| `dataset_version` | string | sim | `^silver_v\d+$`. Constante no arquivo. | `silver_v0` |

**Limites conhecidos da v0**

- Página máxima não é validável: o manifest não registra a contagem de páginas do
  documento. Proposta ao DE-1: acrescentar `n_pages`.
- Cobertura de páginas não é validada. Página sem camada de texto não produz chunk,
  e isso é legítimo.
- A validação é estrutural. Ordem de leitura embaralhada, hifenização e cabeçalho
  repetido passam nos checks.

---

## 4. Estrutura de pastas

```
data/
├── seed_v0/    # entregue no kickoff — read-only
├── bronze/     # DE-1
├── silver/     # DE-2
└── mock/       # mocks — versionado no git
src/
├── acquisition/   # DE-1
├── parsing/       # DE-2
└── quality/       # DE-3
docs/
├── data_contracts.md    # DE-3
└── parsing_issues.md    # DE-2
```

`data/mock/` vai para o git. `data/bronze/` e `data/silver/` não.

---

## 5. Como alterar este contrato

Detalhar uma regra já implícita é manutenção e não exige acordo. Acrescentar,
remover ou mudar o tipo de um campo exige acordo do grupo.

1. Propor no grupo e esperar manifestação de quem produz e de quem consome.
2. Incrementar `dataset_version`.
3. Atualizar os mocks, que são a versão executável deste documento.

Alteração sem aviso faz o mock da outra dupla continuar passando nos checks antigos,
e a divergência só aparece na integração.