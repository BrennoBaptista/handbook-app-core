"""Configuração do logging estruturado (OBS-001, Seção 4) — Composition
Root: único lugar que decide o handler/formatter, nenhum módulo configura
logging por conta própria."""

from __future__ import annotations

import logging
import sys

from platform_core.shared.logging.formatter import JsonFormatter


def configure_logging(service_name: str, environment: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        JsonFormatter(service_name=service_name, environment=environment)
    )

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)
