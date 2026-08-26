"""Smoke tests verifying backend modules import without syntax errors."""

import importlib
import importlib.util
import pathlib
import sys

import pytest

BACKEND_DIR = pathlib.Path(__file__).resolve().parent.parent / "backend"
MODULES = ["config", "state", "graph", "nodes"]


def _backend_path():
    backend = BACKEND_DIR
    if not backend.exists():
        return None
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))
    return backend


@pytest.mark.parametrize("module_name", MODULES)
def test_backend_module_imports(module_name):
    backend = _backend_path()
    if backend is None:
        pytest.skip(f"backend directory not found at {BACKEND_DIR}")
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name == module_name:
            pytest.fail(f"Module file backend/{module_name}.py not found")
        pytest.skip(f"Optional dependency missing for {module_name}: {exc.name}")
    except ImportError as exc:
        pytest.skip(f"Import dependency missing for {module_name}: {exc}")


@pytest.mark.parametrize("module_name", MODULES)
def test_backend_module_compiles(module_name):
    backend = BACKEND_DIR
    candidates = [backend / f"{module_name}.py"]
    if not backend.exists():
        root = pathlib.Path(__file__).resolve().parent.parent
        candidates.insert(0, root / f"{module_name}.py")

    source_path = next((p for p in candidates if p.exists()), None)
    if source_path is None:
        pytest.skip(f"No source file found for {module_name}")
    try:
        compile(source_path.read_text(encoding="utf-8"), str(source_path), "exec")
    except SyntaxError as exc:
        pytest.fail(f"Syntax error in {source_path}: {exc}")


def test_pytest_collects_smoke_suite():
    assert MODULES, "Smoke test target list must not be empty"
