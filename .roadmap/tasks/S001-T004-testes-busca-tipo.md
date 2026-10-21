# S001-T004 — Testes da busca por tipo

**Fase:** Testes  
**Status:** [x] Concluído

## Descrição
Em `estoque/tests.py`, garantir cobertura de `busca_estoque` com `tipo=nome`, `tipo=cas` e `tipo=codigo_barras` (e default sem `tipo`), incluindo contexto `busca_tipo_key` quando há múltiplos resultados.

## Critérios de aceitação
- Suíte passa.
- Casos cobrem filtro correto por tipo e presença de `busca_tipo_key` na resposta de lista múltipla.

## Ficheiros envolvidos
- `estoque/tests.py`

## Dependências
- S001-T001
