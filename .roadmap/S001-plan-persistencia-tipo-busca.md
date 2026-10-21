# S001 — Persistência do tipo de busca na barra

> Ao buscar no estoque, o tipo escolhido (Código de Barras / Nome / CAS) permanece em toda a navegação da sessão até o utilizador trocar no seletor.

## Contexto
Hoje o `<select name="tipo">` em `base.html` volta sempre para **Código de Barras** após cada busca. Quem pesquisa por Nome ou CAS precisa reescolher o filtro a cada tentativa — atrito no laboratório (especialmente ao bipar/digitar vários termos seguidos).

## O que faz (Escopo e RBAC)
- **Técnicos e Alunos (já autenticados):** mesma regra — qualquer utilizador com acesso à barra vê e usa o tipo memorizado.
- Sem novas permissões; a busca continua `@login_required` como hoje.
- Comportamentos:
  - 1 resultado → detalhe do frasco: tipo mantido na barra.
  - 0 resultados → mensagem e volta: tipo mantido.
  - Desktop e mobile: **dois selects sincronizados**.

## Como faz (Django MVT)
- **Models:** nenhum (sem migração Neon).
- **Views (`busca_estoque`):** opcionalmente reforçar default a partir da sessão se `tipo` vier vazio; lógica de filtro atual (exato em código de barras; parcial em nome/CAS) permanece.
- **Templates (`estoque/base.html`):**
  - Remover `selected` fixo em Código de Barras.
  - Marcar a opção ativa com o valor memorizado.
  - JS leve: gravar `tipo` em **sessionStorage** (ou sessão Django) ao mudar o select / ao submeter; ao carregar qualquer página do layout, aplicar o valor nos dois formulários (desktop + mobile).
- **Escopo da memória:** só enquanto a aba/sessão do browser estiver ativa; fechar o browser volta ao default `codigo_barras`.

## Restrições (Vercel & GHS)
- Sem ficheiros locais / ImageField.
- Sem alteração a regras GHS.
- Preferência em `sessionStorage` no cliente (sem nova tabela; compatível com Serverless).

## Riscos
- Selects desktop/mobile dessincronizados → mitigar com um único script no `base.html` que atualiza ambos.
- Página de resultados sem passar `tipo` no contexto → mitigar lendo sessionStorage + refletir `tipo` na URL/contexto quando útil.
