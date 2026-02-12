from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

OUTPUTS_DIR = ROOT_DIR / "outputs"
OUTPUTS_CHARTS_DIR = OUTPUTS_DIR / "charts"
OUTPUTS_TABLES_DIR = OUTPUTS_DIR / "tables"
OUTPUTS_MODELS_DIR = OUTPUTS_DIR / "models"
OUTPUTS_MANIFESTS_DIR = OUTPUTS_DIR / "manifests"
OUTPUTS_LOGS_DIR = OUTPUTS_DIR / "logs"

REPORTS_DIR = ROOT_DIR / "reports"
DOCS_DIR = ROOT_DIR / "docs"
APPS_DIR = ROOT_DIR / "apps"

MANIFEST_PATH = OUTPUTS_MANIFESTS_DIR / "artifacts_manifest.csv"
LOG_PATH = OUTPUTS_MANIFESTS_DIR / "pipeline.log"
RUN_SUMMARY_PATH = OUTPUTS_LOGS_DIR / "run_summary.md"


def ensure_directories() -> None:
    """Garantiza que todas las rutas de escritura existan."""
    dirs = [
        PROCESSED_DIR,
        OUTPUTS_CHARTS_DIR,
        OUTPUTS_TABLES_DIR,
        OUTPUTS_MODELS_DIR,
        OUTPUTS_MANIFESTS_DIR,
        OUTPUTS_LOGS_DIR,
        REPORTS_DIR,
        DOCS_DIR,
        RAW_DIR / "csv",
    ]
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
