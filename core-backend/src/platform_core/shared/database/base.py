"""Registro declarativo do SQLAlchemy compartilhado por todos os módulos.

Abstração técnica fundamental (RA-005, Seção 65.1) — não é um modelo de
domínio. Cada aplicação consumidora declara seus próprios modelos ORM
privados em infrastructure/persistence/, herdando apenas desta Base para
que o Alembic da aplicação enxergue os metadados de todos os seus módulos
num único registro."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
