from __future__ import annotations

from typing import Any

import pandas as pd


def validate_datasets(
    clean_tables: dict[str, pd.DataFrame],
    schema_map: dict[str, Any],
    logger,
) -> dict[str, dict[str, Any]]:
    datasets_cfg = schema_map.get("datasets", {})
    report: dict[str, dict[str, Any]] = {}

    for dataset_name, df in clean_tables.items():
        cfg = datasets_cfg.get(dataset_name, {})
        required_columns = cfg.get("required_columns", [])
        missing_required = [
            column for column in required_columns if column not in df.columns
        ]

        duplicate_rows = int(df.duplicated().sum()) if not df.empty else 0
        null_critical = {}
        for column in required_columns:
            if column in df.columns and len(df) > 0:
                null_critical[column] = round(float(df[column].isna().mean() * 100), 2)

        status = "ok"
        if missing_required:
            status = "warning"
            logger.warning(
                "Faltan columnas requeridas en %s: %s", dataset_name, missing_required
            )

        report[dataset_name] = {
            "status": status,
            "rows": int(len(df)),
            "columns": df.columns.tolist(),
            "missing_required": missing_required,
            "duplicate_rows": duplicate_rows,
            "null_pct_required": null_critical,
        }

    return report
