"""Executa os contratos de dependência declarados em `core-backend/pyproject.toml`
([tool.importlinter]) como parte da suíte de testes (TEST-001, Seção 8). Os
contratos em si cobrem Clean Architecture por módulo e a proibição de
Domain/Application importarem bibliotecas concretas de infraestrutura — ver
`test_module_boundaries.py` para a regra de fronteira entre módulos, que o
import-linter não expressa diretamente."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def test_import_linter_contracts_are_kept():
    lint_imports = Path(sys.executable).with_name(
        "lint-imports.exe" if sys.platform == "win32" else "lint-imports"
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = str(_PACKAGE_ROOT / "src")

    result = subprocess.run(
        [str(lint_imports)],
        cwd=_PACKAGE_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
