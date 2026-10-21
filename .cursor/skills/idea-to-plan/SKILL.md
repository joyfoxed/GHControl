---
name: idea-to-plan
description: Conduz uma conversa interativa que parte de uma ideia informal do utilizador e, através de perguntas guiadas, monta um plano técnico focado na arquitetura Django (MVT) do GHControl. O plano é gravado na pasta `.roadmap/` no padrão `S001-plan-slug.md`. O plano segue uma estrutura enxuta (Contexto, O que faz, Como faz, Restrições, Riscos) focado no ecossistema Web (Tailwind, Neon DB, Vercel Serverless) e regras de RBAC. Otimizado para criar novos módulos, dashboards, regras GHS e views de relatórios. Use sempre que o utilizador disser "quero criar o módulo X", "tenho uma ideia para gerir Y", "ajuda a especificar esta funcionalidade". Diferente de `spec-to-microtasks` — este skill produz o plano, o outro consome o plano e gera as microtasks.
---

# Idea → Plan (Arquiteto Django GHControl)

Conduz uma conversa guiada que transforma uma ideia informal num plano técnico de engenharia focado no padrão Django MVT, Tailwind CSS e Serverless.

## O que este skill faz

Pega numa ideia inicial (um novo módulo, um filtro avançado, uma regra de bloqueio de reagentes, um log de auditoria) e monta um plano técnico estruturado:

- **Contexto** — Qual app do Django vai receber isto? Que dor do laboratório resolve?
- **O que faz** — Escopo funcional. Quem acede? Alunos ou apenas Técnicos (RBAC)?
- **Como faz** — Abordagem técnica: que models (PostgreSQL), views (CBV ou FBV) e templates (`.html`) serão afetados?
- **Restrições** — Respeitar a Vercel (sem arquivos físicos). Respeitar Tailwind (UI). 
- **Riscos** — Riscos na base de dados (on_delete), quebra de responsividade visual.

O plano é guardado em `.roadmap/S<NNN>-plan-<slug>.md`. 

## Princípio central: pergunte até ter tudo

Este skill **não chuta e não preenche com TBD**. Num projeto de ERP, inventar um Model sem saber os campos exatos corrompe o banco Neon DB. Se o utilizador disser "quero um controle de chaves do laboratório", pergunte quais são os campos necessários antes de gerar o plano.

## Fluxo de execução

### 1. Capture a ideia inicial

Antes de qualquer pergunta, identifique:
- **App de destino** — Vai para `estoque/`, `equipamentos/`, `vidrarias/` ou um app novo?
- **O impacto no utilizador** — É algo visual (Tailwind), lógico (GHS/Matemática) ou de segurança (RBAC)?

### 2. Conduza a conversa por secção (Exemplo de Abordagem GHControl)

**Rodada 1 (Contexto & Modelos):**
> "Entendi! Para construir isso no Django, precisamos pensar no banco de dados primeiro.
> Quais serão os campos principais dessa nova funcionalidade? Algum ForeignKey (relacionamento) com Reagentes ou EPIs já existentes?"

**Rodada 2 (Segurança & RBAC):**
> "Perfeito. Agora sobre acessos:
> 1. Alunos (Somente Leitura) podem ver essa nova tela?
> 2. Quem pode adicionar/excluir dados? Todos os Técnicos (`is_staff`) ou exige uma permissão customizada?"

**Rodada 3 (UI & Tailwind):**
> "Sobre a Interface:
> 1. Teremos um Dashboard com Chart.js ou apenas uma tabela listando as informações?
> 2. Quer que a barra lateral de pesquisa seja incluída?"

### 3. Critérios de "completo" por secção

**O que faz está completo quando:**
- Está claro o que o Aluno pode ver e o que o Técnico pode fazer.

**Como faz está completo quando:**
- Estão listados os `models.py` (e seus campos).
- Estão listadas as `views.py` (necessidade de `@staff_member_required`).
- Estão mapeados os `templates/*.html` necessários.

**Restrições está completo quando:**
- A ausência de uso de ImageField/FileField local (regra Vercel) está explícita.
- O Soft Delete (Audit Trail) está considerado.

### 4. Reflita o entendimento antes de gravar

Quando as respostas forem dadas, **antes de criar o ficheiro**, mostre um resumo do plano em Markdown e pergunte: "É isso? Quer ajustar algo antes de eu salvar?". Só grava o ficheiro após confirmação.

### 5. Grave o ficheiro no padrão correto

**Onde salvar:** `<projeto>/.roadmap/S<NNN>-plan-<slug>.md`.
**Identificador:** Leia a pasta `.roadmap/` e incremente o número. Comece com `S001` se estiver vazia.

**Estrutura do ficheiro:**

# S<NNN> — <Título Feature da>

> Resumo da funcionalidade no GHControl.

## Contexto
Por que existe, que dor laboratorial resolve.

## O que faz (Escopo e RBAC)
- **Técnicos (is_staff):** o que podem fazer.
- **Alunos (Read-Only):** o que podem ver.

## Como faz (Django MVT)
- **Models (`models.py`):** (campos exatos que serão criados/migrados)
- **Views (`views.py`):** (funções e rotas)
- **Templates (`.html`):** (layouts e gráficos Chart.js)

## Restrições (Vercel & GHS)
- Proibição de arquivos locais, limitações matemáticas GHS.

## Riscos
- Risco principal e mitigação (ex: quebra de migração PostgreSQL).

### 6. Após gravar
- Mostre ao utilizador: 
> 1. O caminho do ficheiro guardado.
> 2. Instrua-o: "Agora, se quiser que eu execute o código aos poucos de forma segura, peça para gerar as microtasks usando a skill spec-to-microtasks!"