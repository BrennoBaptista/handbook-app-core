# handbook-app-core

Núcleo Compartilhado da Engineering Platform — implementação de referência dos módulos genéricos (bootstrap, autenticação delegada, segurança transversal, observabilidade) que qualquer aplicação derivada da plataforma consome como dependência, em vez de reescrever a cada novo projeto.

As regras arquiteturais que governam este repositório vivem no repositório Engineering-Handbook (https://github.com/BrennoBaptista/engineering-handbook) — não referenciado aqui como submódulo git, já que este repositório é ele próprio instalado como dependência Git por outros repositórios, e um submódulo apontando para um repositório privado quebraria essa instalação em ambientes sem credenciais (CI de um app consumidor). Ver `CLAUDE.md` para o critério de fronteira entre o que pertence a este repositório e o que pertence a uma aplicação consumidora.

---

## Pacotes

| Pacote | Linguagem | Conteúdo |
|---|---|---|
| [`core-backend/`](core-backend/) | Python | Bootstrap de aplicação FastAPI, autenticação (Keycloak/OIDC), segurança transversal, logging estruturado, rate limiting, utilitários de dados. |
| [`core-frontend/`](core-frontend/) | TypeScript | Cliente OIDC, providers de aplicação React, cliente HTTP com contrato de erro. |

## Consumo

Cada pacote é consumido via dependência Git direta (URL do repositório + tag de versão), sem registro de pacotes dedicado — ver ADR-027 no Engineering-Handbook para a justificativa dessa escolha.

## Versionamento

Segue GIT-001 (Versionamento de Releases — SemVer). Mudanças que quebram compatibilidade com aplicações já consumindo uma versão anterior exigem `MAJOR` bump e, sempre que possível, um período de transição documentado no changelog da release.
