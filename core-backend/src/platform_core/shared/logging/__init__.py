"""Logging estruturado (OBS-001, Seção 4) — abstração técnica fundamental
(RA-005, Seção 65.1), disponível a qualquer módulo.

Uso, seguindo o exemplo da própria OBS-001 (Seção 4):

    logger = get_logger(__name__)
    logger.info("Product created", extra={"event": "product_created", "product_id": str(product.id)})

Nunca passe senha, token ou dado sensível via `extra=` — RN-OBS-002, sem
exceção (OBS-001, Seção 6)."""

from __future__ import annotations

import logging

__all__ = ["get_logger"]


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
