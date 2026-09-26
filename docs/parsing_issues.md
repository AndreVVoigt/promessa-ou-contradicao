# Observações da extração:

## Todas as extrações contém cabeçalho e/ou número da página em quase toda página. Além de vários '\n' a serem limpos.

- PRES_01 - Duas colunas causa texto repetido. Corrigido usando block ao invés de text.
- PRES_02 - OK.
- PRES_03 - Contém sumário e páginas que dividem as partes da proposta (um mini sumário da parte). Mantido.
- PRES_04 - Página do cabeçalho = page.number-1.
- PRES_05 - OK.
- PRES_06 - OK.
- PRES_07 - Contém sumário.
- PRES_08 - OK.
- PRES_09 - Contém sumário.
- PRES_10 - OK.
- PRES_11 - Contém bullet points.
- PRES_12 - Contém bullet points.
- PRES_13 - Contém bullet points e páginas 'vazias'.

## Limpeza
- Cabeçalhos e números de páginas removidos.
- Quebras de linha e tabulações normalizadas.
- Sumários mantidos.
- Páginas vazias mantidas para não ficar com "página perdida"

## Observações do chunking 

- Cada chunk carrega chunk_id, document_id, page e text
- O chunk_id é fixo e previsível: documento + página + posição na página 
- Páginas "vazias" (como as do PRES_13) simplesmente não geram chunk nenhum, não dá erro, só não aparece nada pra elas no resultado final
- Documentos com sumário (PRES_03, PRES_07, PRES_09) são chunkados normalmente
- De vez em quando aparece um chunk bem curtinho no fim de um texto grande, é normal, faz parte de como o corte funciona
