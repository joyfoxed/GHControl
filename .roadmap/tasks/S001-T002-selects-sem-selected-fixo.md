# S001-T002 — Remover `selected` fixo nos selects

**Fase:** Frontend  
**Status:** [x] Concluído

## Descrição
Nos dois formulários de busca em `estoque/templates/estoque/base.html` (desktop e mobile), remover o atributo `selected` hardcoded em Código de Barras. Adicionar um atributo comum (ex.: `data-busca-tipo`) nos `<select name="tipo">` para o script da T003 os encontrar. Não alterar classes Tailwind nem layout.

## Critérios de aceitação
- Nenhum `<option>` tem `selected` fixo no HTML estático.
- Ambos os selects têm marcador identificável para JS.
- Aparência visual inalterada.

## Ficheiros envolvidos
- `estoque/templates/estoque/base.html`

## Dependências
- Nenhuma (pode correr em paralelo com T001)
