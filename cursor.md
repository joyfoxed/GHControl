# CLAUDE.md: Constituição do Projeto GHControl

## 0. CONFIRMAÇÃO OBRIGATÓRIA

A primeira linha de CADA resposta DEVE ser exatamente: **`✅ cursor.md ativo`**

Esta linha confirma ao usuário que o agente está operando sob as diretrizes deste documento. Sem exceções.

---

## 1. WORKFLOW PLAN & EXECUTE

É **estritamente proibido** criar, modificar ou excluir arquivos sem seguir a sequência:

1. **Pesquisa:** Ler base de código, modelos de dados (`models.py`) e templates existentes antes de propor solução.
2. **Plano de Ação:** Apresentar escopo conciso listando:
   * Arquivos alvo
   * Models/Views/Templates a alterar ou criar
   * Implicações no banco de dados e na interface
3. **Aprovação Mandatória:** Finalizar SEMPRE com: *"Seguir execução das alterações?"*. **PROIBIDO** gerar código antes do "Sim" explícito.
4. **Execução Atômica:** Edições cirúrgicas. Para tarefas que envolvam migrações de banco E alterações de template, dividir em fases e aguardar aprovação entre cada uma.

---

## 2. LAZY LOADING DE CONTEXTO E GATILHOS

Para economizar tokens, o agente deve acessar diretrizes específicas de domínio apenas quando os aplicativos correspondentes forem tocados.

| Gatilho (modificação/criação em:) | Ação obrigatória |
| :--- | :--- |
| `estoque/` | Considerar regras do Motor de Compatibilidade GHS e conversão de unidades (L/mL, kg/g). |
| `equipamentos/` | Considerar regras de validade (CA) e cronograma de inspeções. |
| `vidrarias/` | Respeitar divisão entre Graduadas e Volumétricas (calibração). |
| `templates/` e `static/` | Manter Tailwind CSS, identidade visual em tons de azul (`blue-800`, `blue-900`) e Chart.js. |
| `settings.py` / Infraestrutura | Revisar restrições Serverless (Seção 4). |

---

## 3. RESTRIÇÕES DE ARQUITETURA E SEGURANÇA (RBAC)

O GHControl é um ERP de segurança química com Controle de Acesso Baseado em Cargos.

| Camada / App | Permitido | Proibido | Subagent dono |
| :--- | :--- | :--- | :--- |
| **Front-end (Templates)** | Uso de Tailwind CSS, ocultar botões de ação com `{% if request.user.is_staff %}`. | Lógica de negócio complexa no template. | `tailwind-frontend-engineer` |
| **Back-end (Views)** | Decorators `@staff_member_required` para métodos de escrita/alteração. | Views de alteração de banco sem proteção de acesso. | `django-backend-engineer` |
| **Banco de Dados (Models)** | Relacionamentos (`ForeignKey`), `on_delete=models.PROTECT`. | `on_delete=models.CASCADE` para usuários ou históricos. | `django-backend-engineer` |
| **Infra/Config** | Configurar Vercel e variáveis via ambiente. | Salvar arquivos localmente. | `security-auditor` |

---

## 4. PRINCÍPIOS INEGOCIÁVEIS (REGRAS DE OURO)

* **Serverless Strict (Vercel):** É **terminantemente proibido** sugerir funcionalidades que envolvam upload de arquivos de mídia físicos (como `ImageField` ou `FileField` armazenados localmente) ou escrita de logs em `.txt` locais. O sistema roda em nuvem temporária.
* **RBAC em Duas Camadas:** Alunos são "Somente Leitura". Técnicos/Admins (`is_staff=True`) têm poder de escrita. Todas as funções que alteram dados devem ser blindadas tanto na interface visual (escondendo botões) quanto no Back-end (trancando rotas).
* **Soft Delete:** Nunca delete históricos de movimentação ou usuários do banco de dados. Rastreabilidade (Audit Trail) é prioritária. Usuários desativados devem ter apenas `is_active=False`.
* **Banco de Dados (Neon DB):** Nenhuma alteração no `settings.py` deve remover o `dj_database_url` ou os adaptadores do PostgreSQL.
* **Idioma Oficial:** Todo o código, comentários, mensagens de commit, alertas (`messages.error`) e interface deve ser estritamente em Português (pt-BR).

---

## 5. CICLO DE APRENDIZADO E REFATORAÇÃO

Ao descobrir uma restrição técnica do Django ou do Tailwind específica do projeto:
* Nunca atualize este `cursor.md` raiz com pegadinhas específicas.
* Registre a informação como um comentário direto no arquivo relevante (ex: `# NOTA VERCEL: Não alterar ordem do whitenoise`).
* Mantenha código DRY (Don't Repeat Yourself). Utilitários globais devem ir para arquivos centralizados.

---

## 6. POLÍTICA DE MUDANÇAS (CHANGELOG)

* **Obrigatório após tarefa aprovada:** Resumir a alteração final para o usuário e orientá-lo a rodar comandos locais necessários antes de fazer push (ex: `"Lembre-se de rodar python manage.py makemigrations e migrate"`).
* Nenhuma migração de banco de dados (`makemigrations`/`migrate`) deve ser executada pelo Agente automaticamente; o agente deve sempre fornecer o comando no terminal para o usuário rodar manualmente.

---

## 7. SUBAGENTS DE EXECUÇÃO (`.cursor/agents/`)

As tarefas devem ser mentalmente divididas e executadas seguindo perfis de subagentes especializados:

| Subagent | Escopo (foco de atuação) | Responsabilidade |
| :--- | :--- | :--- |
| `security-auditor` | Todo o sistema. | Acionado primeiro. Verifica se a solicitação não fere regras de RBAC ou do ambiente Serverless. |
| `django-backend-engineer`| `models.py`, `views.py`, `urls.py`, `admin.py`. | Lógica de Python, ORM do banco, regras de GHS/Conversão e proteção de rotas. |
| `tailwind-frontend-engineer` | `templates/**/*.html`, Chart.js. | Renderização HTML, aplicar classes Tailwind e lógica de UI/UX baseada no perfil do usuário logado. |

O agente principal atua como orquestrador: pesquisa, monta o plano e divide a tarefa entre Frontend e Backend, mantendo o Auditor validando as restrições.