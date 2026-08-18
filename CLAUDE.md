# CLAUDE.md

Este arquivo orienta qualquer agente de IA (Claude Code, Cowork ou outro) que for trabalhar neste repositório.

## Antes de Qualquer Tarefa

Este projeto é construído sobre a Engineering Platform, mas **não é uma aplicação de negócio** — é o **Núcleo Compartilhado da Plataforma** (Platform Core): a implementação de referência dos módulos genéricos (bootstrap, autenticação, segurança, observabilidade) que qualquer aplicação derivada da Engineering Platform consome como dependência, em vez de reescrever a cada novo projeto.

As regras arquiteturais, padrões e decisões que governam este repositório vivem no repositório Engineering-Handbook (https://github.com/BrennoBaptista/engineering-handbook), a fonte única de verdade (Single Source of Truth). Este repositório está sujeito às mesmas regras de qualquer código Python/TypeScript da plataforma (RA-005, RA-008, SEC-001, TEST-001, CODE-001, GIT-001) — a única diferença é que o "domínio" deste repositório é a própria infraestrutura reutilizável, não uma regra de negócio.

Diferente de uma aplicação consumidora, este repositório **não** mantém o Handbook como submódulo git: `handbook-app-core` é ele próprio instalado como dependência Git por outros repositórios (via `uv`/`pnpm`), e um submódulo apontando para um repositório privado quebraria essa instalação em qualquer ambiente sem credenciais (ex.: CI de um app consumidor). Para consultar o Handbook durante o desenvolvimento deste repositório, clone-o separadamente ao lado deste projeto.

1. Clone o Engineering-Handbook separadamente e leia `playbook/PB-005 - Checklist de Onboarding para Agentes de IA.md` antes de começar qualquer tarefa.
2. Não presuma uma decisão que não esteja documentada no Handbook. Se a documentação for omissa ou parecer conflitante, sinalize a lacuna em vez de decidir silenciosamente (PB-005, Seção 8).
3. **Critério de fronteira (o que entra aqui, o que não entra):** só pertence a este repositório o que for agnóstico de domínio e reutilizável por qualquer aplicação derivada da plataforma — bootstrap de aplicação, autenticação/autorização, segurança transversal, observabilidade, utilitários de dados. Nenhuma regra de negócio, nenhum módulo de domínio (`orders`, `products`, etc.) e nenhuma decisão específica de um cliente/implantação deverá existir aqui — isso pertence sempre ao repositório da aplicação consumidora.

## Hierarquia dos Documentos

Em caso de conflito entre documentos, a ordem de prioridade é (README.md do Handbook, Seção "Hierarquia dos Documentos"):

```text
ADR > Reference Architecture > Standards > Playbook > Templates
```

## Atualizando o Handbook

O Handbook não é editado a partir daqui. Alterações de regra, padrão ou arquitetura devem ser propostas no repositório do Handbook (ver `PB-004 - Como Escrever um ADR.md`) e só depois de aprovadas e publicadas lá é que este repositório passa a segui-las — sem necessidade de nenhum passo de sincronização local, já que não há submódulo apontando para ele.

## Este Repositório

`handbook-app-core` — Núcleo Compartilhado da Engineering Platform. Contém dois pacotes, consumidos por qualquer aplicação derivada via dependência Git (URL + tag de versão, sem registro de pacotes próprio — ver ADR correspondente no Handbook):

- **`core-backend/`** — pacote Python (bootstrap de aplicação FastAPI, autenticação delegada a Identity Provider, segurança transversal, observabilidade/logging estruturado, utilitários de dados).
- **`core-frontend/`** — pacote npm (configuração de cliente OIDC, providers de aplicação React, cliente HTTP com contrato de erro já tratado).

Nenhuma aplicação de negócio deverá ser construída dentro deste repositório. Módulos de domínio (`orders`, `products`, etc.) sempre vivem no repositório da aplicação que consome este núcleo.
