"""Módulos não acessam internals de outros módulos diretamente (TEST-001,
Seção 8; RA-005, Seção 41 — Componentes Públicos e Privados). Complementa os
contratos do import-linter (`test_dependency_layers.py`), que cobrem camadas
internas e bibliotecas externas, mas não esta regra de fronteira entre
módulos irmãos.

Hoje `platform_core.modules` contém apenas `auth` — este teste já cobre
qualquer módulo adicional que venha a ser incorporado ao núcleo no futuro,
sem exigir configuração adicional (mesmo padrão do PB-001, Passo 8)."""

from __future__ import annotations

import ast
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
_MODULES_ROOT = _SRC_ROOT / "platform_core" / "modules"


def _owning_module(py_file: Path) -> str:
    return py_file.relative_to(_MODULES_ROOT).parts[0]


def _imported_module_paths(py_file: Path) -> list[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imports.append(node.module)
    return imports


def test_modules_when_importing_other_modules_should_only_use_public_boundary():
    violations: list[str] = []

    for py_file in _MODULES_ROOT.rglob("*.py"):
        owning_module = _owning_module(py_file)

        for imported in _imported_module_paths(py_file):
            parts = imported.split(".")
            if len(parts) < 3 or parts[0] != "platform_core" or parts[1] != "modules":
                continue

            imported_module = parts[2]
            if imported_module == owning_module:
                continue  # import dentro do próprio módulo — permitido

            if len(parts) > 3:
                relative_path = py_file.relative_to(_SRC_ROOT)
                violations.append(
                    f"{relative_path}: importa '{imported}' — deveria importar "
                    f"apenas 'platform_core.modules.{imported_module}' (fronteira "
                    f"pública, RA-005 Seção 41), não seus internals."
                )

    assert not violations, "Violação de fronteira entre módulos:\n" + "\n".join(
        violations
    )
