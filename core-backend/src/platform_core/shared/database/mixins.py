"""Mixins técnicos compartilhados (RA-005, Seção 65.1)."""

from __future__ import annotations

import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Toda tabela deverá possuir created_at/updated_at em UTC (RA-007,
    Seção 4), independentemente de a entidade de domínio expor esses campos
    diretamente. Modelos ORM de qualquer módulo herdam este mixin em vez de
    redeclarar as duas colunas."""

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
