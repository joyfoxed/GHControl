# 🧪 GHControl - Sistema de Gestão de Estoque e Segurança Química

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.0+-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791?logo=postgresql&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?logo=tailwind-css&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-Deployed-black?logo=vercel&logoColor=white)

O **GHControl** é uma aplicação web desenvolvida como Trabalho de Conclusão de Curso (TCC) para o curso Técnico em Química do **SENAI**. 

O sistema automatiza o gerenciamento do inventário de reagentes em laboratórios, mitigando riscos de acidentes através da aplicação automatizada de diretrizes de segurança da norma **GHS (Sistema Globalmente Harmonizado)** e do **Mapa de Compatibilidade Química**.

## ✨ Principais Funcionalidades

*   **🛡️ Motor de Compatibilidade Química:** Algoritmo no back-end que impede o armazenamento conjunto de substâncias incompatíveis (ex: bloqueia a alocação de inflamáveis com comburentes ou explosivos no mesmo armário).
*   **⚖️ Conversão Automática de Unidades:** O laboratório cadastra em larga escala (Litros/Kilogramas) e o sistema converte e deduz automaticamente os consumos fracionados (mL/gramas) garantindo a integridade do saldo.
*   **⏳ Inteligência de Validades:** Alertas visuais cronométricos e automáticos no Dashboard para reagentes vencidos (vermelho) ou próximos ao vencimento (amarelo).
*   **🔐 Controle de Acesso Baseado em Cargos (RBAC):** 
    *   **Administradores/Técnicos:** Acesso total a cadastros, baixas, movimentações e histórico.
    *   **Alunos/Usuários Comuns:** Interface estritamente *Read-Only* (Apenas Leitura) para consulta de frascos e FISPQs, sem permissão de alteração no banco.
*   **📄 Geração de Relatórios e Auditoria:** Emissão de inventário formatado para impressão em PDF e rastreabilidade total de quem movimentou cada mililitro no laboratório.
*   **📱 Interface Moderna e Busca Ágil:** Design responsivo, suporte a leitura de código de barras e renderização de pictogramas de risco GHS com link direto para a FISPQ original.

## 🛠️ Stack Tecnológica e Arquitetura

O projeto foi construído focado em segurança, escalabilidade e operação *Serverless*:

*   **Back-end:** Python & Django Framework (Padrão MVT)
*   **Front-end:** HTML5, Tailwind CSS e Chart.js (Dashboard Interativo)
*   **Banco de Dados (Produção):** PostgreSQL hospedado na **Neon DB**
*   **Hospedagem/Deploy:** Plataforma **Vercel** (Serverless) com suporte a arquivos estáticos via `whitenoise`.

🎓 Sobre o Projeto
Este projeto foi desenvolvido com foco estrito em resolver um problema real de gestão laboratorial: a perda de rastreabilidade de frascos e o risco iminente de reações perigosas por armazenamento inadequado. O GHControl atua como uma barreira de segurança sistêmica, protegendo tanto a integridade física do laboratório quanto o orçamento da instituição.
