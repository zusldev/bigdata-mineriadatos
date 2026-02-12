from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


DATASET_SPECS = {
    "sales": {
        "sheet": "Ventas",
        "source_names": ["ventas", "ventascsv", "sales", "transactions"],
    },
    "customers": {
        "sheet": "Clientes",
        "source_names": ["clientes", "customers", "customer"],
    },
    "branches": {
        "sheet": "Sucursales",
        "source_names": ["sucursales", "branches", "stores"],
    },
    "inventory": {
        "sheet": "Inventarios",
        "source_names": ["inventarios", "inventory", "stock"],
    },
    "digital": {
        "sheet": "Canales_Digitales",
        "source_names": ["canales_digitales", "digital", "social", "marketing"],
    },
}


def _dataset_match_score(file_path: Path, source_names: list[str]) -> int:
    stem = file_path.stem.lower()
    best = 0
    for name in source_names:
        if stem == name:
            return 100
        if name in stem:
            best = max(best, 10 + len(name))
    return best


def _load_json(path: Path, use_polars: bool, logger) -> pd.DataFrame:
    if use_polars:
        try:
            import polars as pl

            return pl.read_json(path).to_pandas()
        except Exception as exc:
            logger.warning(
                "No se pudo leer JSON con Polars en %s: %s. Se usa pandas.", path, exc
            )

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if isinstance(payload, dict):
        # Caso API: {"data":[...]} u otros wrappers.
        list_candidates = [v for v in payload.values() if isinstance(v, list)]
        if list_candidates:
            payload = list_candidates[0]
        else:
            payload = [payload]
    if not isinstance(payload, list):
        payload = [payload]
    return pd.json_normalize(payload)


def _load_csv(path: Path, use_polars: bool, logger) -> pd.DataFrame:
    if use_polars:
        try:
            import polars as pl

            return pl.read_csv(path).to_pandas()
        except Exception as exc:
            logger.warning(
                "No se pudo leer CSV con Polars en %s: %s. Se usa pandas.", path, exc
            )
    return pd.read_csv(path)


def _xlsx_signature(df: pd.DataFrame) -> str:
    sample = df.head(20).to_json(date_format="iso", orient="split", default_handler=str)
    cols = "|".join(df.columns.astype(str).tolist())
    payload = f"{cols}|rows={len(df)}|sample={sample}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _select_best_xlsx(
    xlsx_files: list[Path],
    sheet_name: str,
    logger,
) -> tuple[pd.DataFrame | None, dict[str, Any]]:
    signatures_seen: dict[str, Path] = {}
    candidates: list[tuple[pd.DataFrame, Path, str]] = []
    errors: list[str] = []

    for file_path in sorted(xlsx_files):
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            signature = _xlsx_signature(df)
            candidates.append((df, file_path, signature))
            if signature in signatures_seen:
                logger.info(
                    "Workbook duplicado detectado para hoja %s: %s ~ %s",
                    sheet_name,
                    file_path.name,
                    signatures_seen[signature].name,
                )
            else:
                signatures_seen[signature] = file_path
        except Exception as exc:
            errors.append(f"{file_path.name}: {exc}")

    if not candidates:
        return None, {"selected_file": None, "errors": errors, "duplicates_found": 0}

    unique_by_signature: dict[str, tuple[pd.DataFrame, Path, str]] = {}
    for df, file_path, signature in candidates:
        # Conserva el de mayor filas por firma.
        current = unique_by_signature.get(signature)
        if current is None or len(df) > len(current[0]):
            unique_by_signature[signature] = (df, file_path, signature)

    unique_candidates = list(unique_by_signature.values())
    selected = sorted(
        unique_candidates, key=lambda item: (len(item[0]), item[1].name), reverse=True
    )[0]

    return selected[0], {
        "selected_file": str(selected[1]),
        "errors": errors,
        "duplicates_found": max(0, len(candidates) - len(unique_candidates)),
    }


def _pick_file(files: list[Path], source_names: list[str]) -> Path | None:
    scored = [
        (file_path, _dataset_match_score(file_path, source_names))
        for file_path in files
    ]
    scored = [item for item in scored if item[1] > 0]
    if not scored:
        return None
    scored.sort(key=lambda item: (item[1], item[0].name), reverse=True)
    return scored[0][0]


def load_raw_datasets(
    settings: dict[str, Any], logger
) -> tuple[dict[str, pd.DataFrame], dict[str, dict[str, Any]]]:
    runtime = settings.get("runtime", {})
    paths = settings.get("paths", {})
    use_polars = bool(runtime.get("use_polars", False))

    raw_json = Path(paths.get("raw_json", "data/raw/json"))
    raw_csv = Path(paths.get("raw_csv", "data/raw/csv"))
    raw_xlsx = Path(paths.get("raw_xlsx", "data/raw/xlsx"))

    json_files = list(raw_json.glob("*.json")) if raw_json.exists() else []
    csv_files = list(raw_csv.glob("*.csv")) if raw_csv.exists() else []
    xlsx_files = list(raw_xlsx.glob("*.xlsx")) if raw_xlsx.exists() else []

    tables: dict[str, pd.DataFrame] = {}
    source_report: dict[str, dict[str, Any]] = {}

    for dataset_name, spec in DATASET_SPECS.items():
        source_names = spec["source_names"]
        sheet_name = spec["sheet"]

        chosen_json = _pick_file(json_files, source_names)
        chosen_csv = _pick_file(csv_files, source_names)
        selected_source = None
        metadata: dict[str, Any] = {"dataset": dataset_name, "source": None}

        if chosen_json is not None:
            df = _load_json(chosen_json, use_polars=use_polars, logger=logger)
            selected_source = "json"
            metadata["source_file"] = str(chosen_json)
        elif chosen_csv is not None:
            df = _load_csv(chosen_csv, use_polars=use_polars, logger=logger)
            selected_source = "csv"
            metadata["source_file"] = str(chosen_csv)
        else:
            df, xlsx_meta = _select_best_xlsx(
                xlsx_files, sheet_name=sheet_name, logger=logger
            )
            selected_source = "xlsx"
            metadata.update(xlsx_meta)
            if df is None:
                logger.warning(
                    "No fue posible cargar dataset '%s'. Se genera dataframe vacío.",
                    dataset_name,
                )
                df = pd.DataFrame()

        metadata["source"] = selected_source
        metadata["rows"] = len(df)
        metadata["columns"] = df.columns.astype(str).tolist()
        source_report[dataset_name] = metadata
        tables[dataset_name] = df

        logger.info(
            "Dataset cargado: %s | fuente=%s | filas=%s | columnas=%s",
            dataset_name,
            selected_source,
            len(df),
            len(df.columns),
        )

    return tables, source_report


def profile_raw_tables(
    raw_tables: dict[str, pd.DataFrame],
) -> dict[str, dict[str, Any]]:
    profile: dict[str, dict[str, Any]] = {}
    for name, df in raw_tables.items():
        if df.empty:
            profile[name] = {"rows": 0, "columns": [], "missing_pct": {}, "sample": {}}
            continue

        missing_pct = (df.isna().mean() * 100).round(2).to_dict()
        profile[name] = {
            "rows": int(len(df)),
            "columns": df.columns.astype(str).tolist(),
            "missing_pct": missing_pct,
            "sample": df.head(1).to_dict(orient="records")[0] if len(df) else {},
        }
    return profile
