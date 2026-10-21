# S001-T003 — sessionStorage + sync desktop/mobile

**Fase:** Frontend  
**Status:** [x] Concluído

## Descrição
Adicionar script leve no `base.html` (junto aos scripts existentes) que:
1. Lê/grava a chave de tipo de busca em `sessionStorage` (ex.: `ghcontrol_busca_tipo`).
2. No load da página, aplica o valor guardado (ou default `codigo_barras`) a **todos** os selects `[data-busca-tipo]`.
3. Ao mudar qualquer select ou ao submit do form, grava o valor e sincroniza o outro select.
4. Valores válidos: `codigo_barras`, `nome`, `cas`.

## Critérios de aceitação
- Após escolher Nome e navegar (detalhe, dashboard, erro de busca), o select continua em Nome.
- Desktop e mobile ficam sempre iguais.
- Fechar a aba/browser limpa a preferência (sessionStorage).

## Ficheiros envolvidos
- `estoque/templates/estoque/base.html`

## Dependências
- S001-T002
