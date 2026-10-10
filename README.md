# 🧪 GHControl - ERP de Gestão e Segurança Laboratorial

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.0+-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791?logo=postgresql&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?logo=tailwind-css&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-Deployed-black?logo=vercel&logoColor=white)

O **GHControl** é uma aplicação web robusta desenvolvida como Trabalho de Conclusão de Curso (TCC) para o curso Técnico em Química do **SENAI**. 

Nascido para automatizar o inventário de reagentes, o sistema evoluiu para um **ERP Laboratorial Completo**, centralizando o controle de substâncias químicas, equipamentos de proteção (EPI/EPC) e vidrarias, mitigando riscos através de normas de segurança e garantindo total rastreabilidade (Audit Trail).

## ✨ Funcionalidades Principais

### 🧪 Módulo de Reagentes e Inteligência Química
*   **Motor de Compatibilidade GHS:** Algoritmo que impede o armazenamento de substâncias incompatíveis no mesmo armário (ex: bloqueia inflamáveis com comburentes).
*   **Conversão Automática de Unidades:** Entrada em L/kg e baixa fracionada em mL/g com dedução perfeita do saldo.
*   **Busca Avançada:** Filtros rápidos por Código de Barras (padrão), CAS ou Nome do Reagente.
*   **Gestão de Validades:** Alertas visuais e automáticos no Dashboard para itens vencidos ou próximos ao vencimento.

### 🦺 Módulo de Segurança do Trabalho (EPI / EPC)
*   **Controle de EPIs:** Rastreabilidade de estoque, controle de validade e Certificado de Aprovação (CA) dos equipamentos individuais.
*   **Gestão de EPCs:** Monitoramento de status e cronograma automatizado de próximas inspeções para equipamentos coletivos (ex: Chuveiros de Emergência, Capelas).

### ⚗️ Módulo de Vidrarias
*   **Classificação Técnica:** Separação estrutural entre vidrarias Graduadas e Volumétricas.
*   **Controle de Calibração:** Exibição dinâmica de dados de calibração exclusivos para peças volumétricas (Classe A/B, tolerância).
*   **Registro de Quebras:** Histórico detalhado de saídas/quebras para reposição de inventário.

### 🔐 Segurança de Dados e Auditoria
*   **Controle de Acesso Baseado em Cargos (RBAC):**
    *   **Administradores/Técnicos:** Acesso total a cadastros e movimentações.
    *   **Alunos/Usuários Comuns:** Interface estritamente *Read-Only*, com botões de ação ocultos em Front-end e rotas bloqueadas no Back-end.
*   **Trilha de Auditoria (Logs):** Tela administrativa dedicada (`/auditoria/logs/`) que rastreia quem, quando e o que foi modificado no sistema.
*   **Soft Delete:** Proteção contra exclusão acidental. Usuários e históricos nunca são apagados do banco, mantendo a integridade da auditoria.

### 📊 Interface e UX
*   **Dashboard Analítico:** Gráficos interativos renderizados com **Chart.js** (com cores dinâmicas) mapeando a distribuição física do estoque.
*   **Design Responsivo e Moderno:** Interface estilizada com **Tailwind CSS**, paleta institucional em tons de azul, menu lateral (Sidebar) retrátil e foco total na usabilidade em bancada.

## 🛠️ Stack Tecnológica e Arquitetura

O projeto foi construído focado em segurança, escalabilidade e operação *Serverless*:

*   **Back-end:** Python & Django Framework (Padrão MVT)
*   **Front-end:** HTML5, Tailwind CSS, JavaScript (Chart.js)
*   **Banco de Dados (Produção):** PostgreSQL hospedado na **Neon DB**
*   **Hospedagem/Deploy:** Plataforma **Vercel** (Serverless) com roteamento via `vercel.json` e estáticos otimizados via `whitenoise`.

## 🎓 Sobre o Projeto
Este projeto atua como uma barreira de segurança sistêmica. Ao unir regras de reatividade química, normas de segurança do trabalho e engenharia de software na nuvem, o GHControl protege a integridade física do laboratório e a previsibilidade do orçamento da instituição.
