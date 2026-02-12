from __future__ import annotations

import shutil
from collections import defaultdict
from pathlib import Path
from uuid import uuid4

import pytest


@pytest.fixture(autouse=True)
def _set_loky_cpu_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOKY_MAX_CPU_COUNT", "1")


@pytest.fixture
def tmp_path() -> Path:
    """
    Fixture temporal local para evitar dependencias del plugin tmpdir
    en entornos Windows con ACL restrictivas.
    """
    base_dir = Path("outputs") / "test_tmp"
    base_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = base_dir / f"case_{uuid4().hex[:8]}"
    temp_dir.mkdir(parents=True, exist_ok=False)
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def pytest_terminal_summary(terminalreporter, exitstatus: int, config) -> None:
    """
    Resumen extendido para `make test`:
    - total ejecutados y estado general,
    - desglose por archivo,
    - lista de pruebas que pasaron.
    """
    categories = ["passed", "failed", "skipped", "error", "xfailed", "xpassed"]
    stats = terminalreporter.stats

    def _count(name: str) -> int:
        return len(stats.get(name, []))

    total = sum(_count(name) for name in categories)
    passed = _count("passed")
    failed = _count("failed")
    errored = _count("error")
    skipped = _count("skipped")
    xfailed = _count("xfailed")
    xpassed = _count("xpassed")

    per_file: dict[str, dict[str, int]] = defaultdict(
        lambda: {"passed": 0, "failed": 0, "skipped": 0, "error": 0}
    )
    passed_tests: list[str] = []

    for status in ("passed", "failed", "skipped", "error"):
        for report in stats.get(status, []):
            nodeid = getattr(report, "nodeid", None)
            when = getattr(report, "when", "")
            if not nodeid:
                continue
            if when not in {"call", "setup", "teardown"}:
                continue

            test_file = nodeid.split("::", 1)[0]
            per_file[test_file][status] += 1

            if status == "passed" and when == "call":
                passed_tests.append(nodeid)

    terminalreporter.write_sep("=", "Feedback de pruebas")
    terminalreporter.write_line(f"Total ejecutadas: {total}")
    terminalreporter.write_line(f"Pasaron: {passed}")
    terminalreporter.write_line(f"Fallaron: {failed}")
    terminalreporter.write_line(f"Errores: {errored}")
    terminalreporter.write_line(f"Saltadas: {skipped}")
    if xfailed or xpassed:
        terminalreporter.write_line(f"XFailed: {xfailed} | XPassed: {xpassed}")

    if per_file:
        terminalreporter.write_line("")
        terminalreporter.write_line("Detalle por archivo:")
        for file_name in sorted(per_file):
            detail = per_file[file_name]
            terminalreporter.write_line(
                f"- {file_name}: "
                f"passed={detail['passed']}, "
                f"failed={detail['failed']}, "
                f"error={detail['error']}, "
                f"skipped={detail['skipped']}"
            )

    if passed_tests:
        terminalreporter.write_line("")
        terminalreporter.write_line("Pruebas que pasaron:")
        for nodeid in sorted(passed_tests):
            terminalreporter.write_line(f"  OK {nodeid}")

    terminalreporter.write_line("")
    if exitstatus == 0 and failed == 0 and errored == 0:
        terminalreporter.write_line("Resultado final: TODO BIEN - suite en verde.")
    else:
        terminalreporter.write_line(
            "Resultado final: HAY FALLAS - revisa el detalle anterior."
        )
