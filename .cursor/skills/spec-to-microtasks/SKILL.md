---
name: spec-to-microtasks
description: Quebra um plano técnico (spec) do GHControl em microtasks muito pequenas (15-30 min cada), agrupadas por fase de desenvolvimento Django (Setup, Backend/Models, Frontend/Templates, Testes, Deploy), e serializa a saída em ficheiros markdown individuais dentro de `.roadmap/tasks/`, mais um índice em `.roadmap/`. Usar sempre que o utilizador fornecer um plano técnico ou pedir para "gerar tarefas", "criar plano de execução" ou "gerar roadmap". Otimizado para Django (MVT), Tailwind CSS, PostgreSQL (Neon DB) e ambiente Serverless (Vercel).
---

# Spec → Microtasks (O Tech Lead do GHControl)

Transforma planos técnicos (gerados pela skill `idea-to-plan`) em checklists de microtasks executáveis e seguras para a infraestrutura do GHControl.

## O que esta skill faz

Pega numa spec técnica (plano) e produz uma checklist de microtasks de 15-30 minutos cada — pequenas o suficiente para serem executadas passo-a-passo sem esgotar o contexto da IA e sem quebrar o sistema. Os ficheiros são guardados em `.roadmap/tasks/`.

**Foco da Stack:** As tarefas geradas DEVEM respeitar a arquitetura do GHControl: Django (Models, Views, Forms, Templates), Tailwind CSS, e restrições de deploy na Vercel (ex: ficheiros estáticos/media).

## Fluxo de execução

### 1. Leia a spec inteira primeiro
Procure por:
- **App alvo:** Em qual módulo do Django isto vai viver (estoque, equipamentos, admin, core)?
- **Modelos:** Novas tabelas ou novos campos no Neon DB?
- **Segurança (RBAC):** Quem pode aceder? Requer `@staff_member_required` ou `{% if request.user.is_staff %}`?
- **Restrições da Vercel:** Envolve upload de ficheiros ou geração de PDFs pesados?

### 2. Levante ambiguidades ANTES de gerar
Não gere tarefas sobre suposições erradas. Faça perguntas se:
- A spec menciona "guardar imagem" mas não especifica se será gerada uma URL externa ou Cloudinary (visto que Vercel não guarda ficheiros locais).
- O nível de acesso de uma View não estiver claro na spec.

### 3. Estruture as fases (MVT do Django)
Sempre organize a saída nestas fases, omitindo as que não se aplicam:
1. **Setup** — Registo de novas apps, URLs principais, instalação de pacotes.
2. **Backend (Models & Views)** — Alterações no `models.py`, `forms.py`, `views.py`, e geração de migrations (Neon DB).
3. **Frontend (Templates)** — Criação de ficheiros HTML em `templates/`, aplicação de Tailwind CSS estrito, integração de scripts JS (Chart.js, HTMX).
4. **Integração** — Conexão com lógicas complexas, como cálculos de GHS.
5. **Deploy** — Configurações específicas (coleta de estáticos para Vercel).

### 4. Quebre em microtasks de 15-30 minutos
As tarefas devem tocar num único conceito ou ficheiro.

❌ Task grande demais:
- [ ] Implementar cadastro de reagentes (Model, View e Template)

✅ Microtasks ajustadas:
- [ ] Adicionar campo `codigo_ghs` no model `Reagente` (`estoque/models.py`)
- [ ] Criar a view `ReagenteCreateView` restrita a staff (`estoque/views.py`)
- [ ] Adicionar a rota `reagente/novo` em `estoque/urls.py`
- [ ] Criar template `reagente_form.html` com as classes Tailwind padrão do projeto

### 5. Formato de saída e Ficheiros
A saída **sempre** é serializada em ficheiros.

**Identificador da Spec (S<NNN>):** Procure o maior número em `.roadmap/` e use-o para agrupar as tarefas (ex: S002).

**Ficheiro de controlo (Dashboard):** Crie `.roadmap/S<NNN>-roadmap-<slug>.md` listando todas as fases e links para as tarefas individuais.

**Ficheiros das microtasks:** Crie `.roadmap/tasks/S<NNN>-T<MMM>-<slug-curto>.md` para cada tarefa. Use esta estrutura pura em Markdown:

# S002-T004 — Criar view `ReagenteCreateView`

**Fase:** Backend
**Status:** [ ] Pendente

## Descrição
Criar a class-based view em `estoque/views.py` para adição de reagentes, garantindo que herda de `LoginRequiredMixin` e faz a verificação de staff.

## Critérios de aceitação
- View está protegida contra utilizadores não-staff.
- Form_valid redireciona para a lista de reagentes com mensagem de sucesso (messages).

## Ficheiros envolvidos
- `estoque/views.py`

## Dependências
- S002-T003 (Criação do Form)

## Após gerar
- Apresente ao utilizador um resumo indicando quantos ficheiros foram criados, o caminho do ficheiro de controlo (Roadmap) e as fases configuradas. Informe-o que pode começar a executar pedindo: "Cursor, executa a primeira tarefa do roadmap S."