from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.io import ArtifactTracker


REQUIRED_STUDY_DOCS = {
    "study_log": Path("docs/STUDY_LOG.md"),
    "glossary": Path("docs/GLOSSARY.md"),
    "decisions": Path("docs/DECISIONS.md"),
    "checkpoints": Path("docs/CHECKPOINTS.md"),
}


class WarningCollector(logging.Handler):
    """Captura warnings del pipeline para incorporarlos al resumen del run."""

    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        if len(self.messages) < 50:
            self.messages.append(msg)


@dataclass
class StepTimer:
    started_at_utc: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    step_seconds: dict[str, float] = field(default_factory=dict)

    def record(self, step_name: str, seconds: float) -> None:
        self.step_seconds[step_name] = round(float(seconds), 3)


def _must_exist(path: Path) -> None:
    if not path.exists():
        raise SystemExit(
            f"ERROR Study Mode: falta el archivo obligatorio `{path}`.\n"
            "Crea el documento y vuelve a ejecutar el pipeline."
        )


def ensure_study_docs_exist() -> dict[str, Path]:
    paths = {name: path for name, path in REQUIRED_STUDY_DOCS.items()}
    for path in paths.values():
        _must_exist(path)
    return paths


def ensure_study_log_updated_for_run(study_log_path: Path, run_id: str) -> None:
    text = study_log_path.read_text(encoding="utf-8")
    run_pattern = re.compile(rf"Run ID:\s*{re.escape(run_id)}", flags=re.IGNORECASE)
    no_changes_pattern = re.compile(
        rf"NO_CHANGES:\s*{re.escape(run_id)}", flags=re.IGNORECASE
    )

    if run_pattern.search(text) or no_changes_pattern.search(text):
        return

    raise SystemExit(
        "ERROR Study Mode: docs/STUDY_LOG.md no contiene entrada para este run.\n"
        f"Run esperado: {run_id}\n"
        "Agrega una mini-lección con `Run ID: <valor>` o `NO_CHANGES: <valor>` y vuelve a ejecutar."
    )


def render_run_summary_markdown(
    *,
    run_id: str,
    source_report: dict[str, dict[str, Any]],
    clean_tables: dict[str, pd.DataFrame],
    warning_messages: list[str],
    tracker: ArtifactTracker,
    step_seconds: dict[str, float],
    started_at_utc: datetime,
    finished_at_utc: datetime,
) -> str:
    duration = (finished_at_utc - started_at_utc).total_seconds()
    artifact_df = pd.DataFrame(tracker.records)
    artifacts_count = int(len(artifact_df))
    artifacts_by_type = (
        artifact_df.groupby("artifact_type").size().to_dict()
        if not artifact_df.empty
        else {}
    )

    lines: list[str] = []
    lines.append(f"# Run Summary - {run_id}")
    lines.append("")
    lines.append("## Metadatos")
    lines.append(f"- Inicio UTC: {started_at_utc.isoformat()}")
    lines.append(f"- Fin UTC: {finished_at_utc.isoformat()}")
    lines.append(f"- Duración total (s): {duration:.2f}")
    lines.append("")
    lines.append("## Datasets cargados")
    for dataset, meta in source_report.items():
        lines.append(
            f"- {dataset}: fuente={meta.get('source')} filas_raw={meta.get('rows')} columnas={len(meta.get('columns', []))}"
        )
    lines.append("")
    lines.append("## Filas después de limpieza")
    for dataset, df in clean_tables.items():
        lines.append(f"- {dataset}: {len(df)} filas limpias")
    lines.append("")
    lines.append("## Artefactos generados")
    lines.append(f"- Total: {artifacts_count}")
    if artifacts_by_type:
        for art_type, count in artifacts_by_type.items():
            lines.append(f"- {art_type}: {count}")
    lines.append("")
    lines.append("## Tiempo por etapa (segundos)")
    for step_name, secs in step_seconds.items():
        lines.append(f"- {step_name}: {secs:.3f}")
    lines.append("")
    lines.append("## Key warnings")
    if warning_messages:
        for msg in warning_messages[:20]:
            lines.append(f"- {msg}")
    else:
        lines.append("- Sin warnings relevantes.")
    lines.append("")
    lines.append("## What changed in this run? (diff-style)")
    lines.append(f"+ Se generaron {artifacts_count} artefactos nuevos/actualizados.")
    lines.append(f"+ Se completaron {len(step_seconds)} etapas del pipeline.")
    if warning_messages:
        lines.append(
            f"- Se detectaron {len(warning_messages)} warning(s); revisar sección 'Key warnings'."
        )
    else:
        lines.append("+ No se detectaron warnings.")
    lines.append("")
    lines.append("## Verificación rápida")
    lines.append("1. Confirmar `reports/final_report.md` actualizado.")
    lines.append("2. Confirmar `outputs/tables/*.csv` para tablas de negocio.")
    lines.append("3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.")
    lines.append("")
    return "\n".join(lines)


def write_run_summary(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def append_run_summary_to_study_log(
    study_log_path: Path, run_id: str, run_summary_md: str
) -> None:
    original = study_log_path.read_text(encoding="utf-8")
    stamp = datetime.now(timezone.utc).isoformat()
    block = (
        "\n\n---\n"
        f"\n### Resumen automático del run `{run_id}` ({stamp})\n\n"
        f"{run_summary_md}\n"
    )
    study_log_path.write_text(original + block, encoding="utf-8")


def mark_checkpoint_complete(checkpoints_path: Path, run_id: str) -> None:
    existing = checkpoints_path.read_text(encoding="utf-8")
    line = f"- [x] Pipeline completado para Run ID: {run_id}"
    if line not in existing:
        checkpoints_path.write_text(existing + "\n" + line + "\n", encoding="utf-8")
