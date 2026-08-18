"""Núcleo Compartilhado da Engineering Platform (backend).

Implementação de referência dos módulos genéricos que qualquer aplicação
derivada da plataforma consome como dependência: bootstrap de aplicação
FastAPI, autenticação delegada a um Identity Provider, segurança
transversal, observabilidade e utilitários de dados.

Nenhuma regra de negócio ou módulo de domínio pertence a este pacote — ver
CLAUDE.md, na raiz do repositório, para o critério de fronteira.
"""
