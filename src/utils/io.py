from __future__ import annotations

import pickle
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def _supports_parquet() -> bool:
    try:
        import pyarrow  # noqa: F401

        return True
    except Exception:
        return False


@dataclass
class ArtifactTracker:
    records: list[dict[str, Any]] = field(default_factory=list)

    def register(
        self,
        path: Path,
        artifact_type: str,
        module: str,
        fmt: str,
        rows: int | None = None,
    ) -> None:
        self.records.append(
            {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "path": str(path.as_posix()),
                "artifact_type": artifact_type,
                "module": module,
                "format": fmt,
                "rows": rows,
            }
        )

    def save_manifest(self, manifest_path: Path) -> None:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(self.records)
        df.to_csv(manifest_path, index=False)


def write_table(
    df: pd.DataFrame,
    path_base: Path,
    *,
    logger,
    tracker: ArtifactTracker | None = None,
    module: str = "unknown",
    artifact_type: str = "table",
    index: bool = False,
    allow_csv_fallback: bool = True,
) -> Path:
    """
    Guarda una tabla en parquet por defecto.
    Si parquet no está disponible, cae a CSV (si allow_csv_fallback=True).
    """
    path_base.parent.mkdir(parents=True, exist_ok=True)
    parquet_path = path_base.with_suffix(".parquet")
    csv_path = path_base.with_suffix(".csv")

    if _supports_parquet():
        try:
            df.to_parquet(parquet_path, index=index)
            if tracker:
                tracker.register(
                    parquet_path, artifact_type, module, "parquet", len(df)
                )
            return parquet_path
        except Exception as exc:
            logger.warning(
                "No fue posible escribir parquet en %s. Error: %s",
                parquet_path,
                exc,
            )

    if not allow_csv_fallback:
        raise RuntimeError(
            "No se pudo escribir parquet y allow_csv_fallback=False. "
            "Instala pyarrow o activa fallback."
        )

    logger.warning(
        "pyarrow no disponible o error de parquet. Se escribe CSV como fallback: %s",
        csv_path,
    )
    df.to_csv(csv_path, index=index, encoding="utf-8")
    if tracker:
        tracker.register(csv_path, artifact_type, module, "csv", len(df))
    return csv_path


def read_table(path_base: Path, logger) -> pd.DataFrame:
    parquet_path = path_base.with_suffix(".parquet")
    csv_path = path_base.with_suffix(".csv")

    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    if csv_path.exists():
        return pd.read_csv(csv_path)

    logger.warning("No se encontró tabla en parquet ni csv para %s", path_base)
    return pd.DataFrame()


def save_plotly_figure(
    fig,
    output_path: Path,
    *,
    tracker: ArtifactTracker | None = None,
    module: str = "unknown",
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(output_path, include_plotlyjs="cdn")
    if tracker:
        tracker.register(output_path, "chart", module, "html", None)


def save_pickle(
    obj: Any,
    output_path: Path,
    *,
    tracker: ArtifactTracker | None = None,
    module: str = "unknown",
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as file:
        pickle.dump(obj, file)
    if tracker:
        tracker.register(output_path, "model", module, "pkl", None)
