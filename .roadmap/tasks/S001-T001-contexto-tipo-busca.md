# S001-T001 — Passar chave `tipo` no contexto da lista

**Fase:** Backend  
**Status:** [x] Concluído

## Descrição
Em `busca_estoque` (`estoque/views.py`), ao renderizar `lista_estoque.html` com múltiplos resultados, incluir no contexto o valor bruto do filtro (ex.: `busca_tipo_key`: `nome` | `cas` | `codigo_barras`), além do rótulo já existente (`busca_tipo`).

## Critérios de aceitação
- Contexto da lista inclui `busca_tipo_key` com um dos valores válidos.
- Comportamento de filtro (exato/parcial) e redirects (0 ou 1 resultado) permanecem iguais.

## Ficheiros envolvidos
- `estoque/views.py`

## Dependências
- Nenhuma
