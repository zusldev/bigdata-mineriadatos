from __future__ import annotations

# ruff: noqa: E402

import argparse
import os
import time
import warnings
from datetime import datetime, timezone
from typing import Any

import pandas as pd

# Evita warning de loky/joblib en entornos donde no detecta cores físicos.
if "LOKY_MAX_CPU_COUNT" not in os.environ:
    os.environ["LOKY_MAX_CPU_COUNT"] = "1"
warnings.filterwarnings(
    "ignore",
    message=r"Could not find the number of physical cores.*",
    category=UserWarning,
)

from src.analysis.digital import run_digital_analysis
from src.analysis.inventory import run_inventory_analysis
from src.analysis.profitability import run_profitability_analysis
from src.data.clean import clean_datasets
from src.data.load import load_raw_datasets, profile_raw_tables
from src.data.validate import validate_datasets
from src.eda.eda import run_eda
from src.features.build_features import build_features
from src.models.forecast import run_forecast
from src.models.segmentation import run_segmentation
from src.pipeline.study_mode import (
    StepTimer,
    WarningCollector,
    append_run_summary_to_study_log,
    ensure_study_docs_exist,
    ensure_study_log_updated_for_run,
    mark_checkpoint_complete,
    render_run_summary_markdown,
    write_run_summary,
)
from src.reco.recommendations import run_recommendations
from src.report.generate_report import generate_documents_and_reports
from src.utils.config import load_recipe_map, load_schema_map, load_settings
from src.utils.io import ArtifactTracker, write_table
from src.utils.logger import get_logger
from src.utils.paths import (
    MANIFEST_PATH,
    PROCESSED_DIR,
    RUN_SUMMARY_PATH,
    ensure_directories,
)
from src.utils.seed import set_global_seed


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline integral Sabor Mexicano")
    parser.add_argument("--seed", type=int, default=None, help="Semilla determinística")
    parser.add_argument(
        "--forecast-horizon",
        type=int,
        default=None,
        help="Horizonte de pronóstico en meses",
    )
    parser.add_argument(
        "--top-ingredients",
        type=int,
        default=None,
        help="Top ingredientes a pronosticar",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Identificador del run para la rutina Study Log (ej. 2026-02-11-a).",
    )
    return parser.parse_args()


def _runtime_overrides(args: argparse.Namespace) -> dict[str, Any]:
    runtime: dict[str, Any] = {}
    if args.seed is not None:
        runtime["seed"] = args.seed
    if args.forecast_horizon is not None:
        runtime["forecast_horizon"] = args.forecast_horizon
    if args.top_ingredients is not None:
        runtime["top_ingredients"] = args.top_ingredients
    return {"runtime": runtime} if runtime else {}


def _persist_processed_tables(
    clean_tables: dict[str, pd.DataFrame],
    feature_tables: dict[str, pd.DataFrame],
    *,
    allow_csv_fallback: bool,
    tracker: ArtifactTracker,
    logger,
) -> None:
    for dataset_name, table in clean_tables.items():
        write_table(
            table,
            PROCESSED_DIR / f"{dataset_name}_clean",
            logger=logger,
            tracker=tracker,
            module="pipeline",
            artifact_type="processed_table",
            allow_csv_fallback=allow_csv_fallback,
        )
    for table_name, table in feature_tables.items():
        write_table(
            table,
            PROCESSED_DIR / table_name,
            logger=logger,
            tracker=tracker,
            module="pipeline",
            artifact_type="feature_table",
            allow_csv_fallback=allow_csv_fallback,
        )


def main() -> None:
    args = _parse_args()
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    study_paths = ensure_study_docs_exist()
    ensure_study_log_updated_for_run(Path("docs/GLOSSARY.md"), run_id)

    step_timer = StepTimer()
    run_started = datetime.now(timezone.utc)

    overrides = _runtime_overrides(args)
    settings = load_settings(overrides=overrides)
    schema_map = load_schema_map()
    recipe_map = load_recipe_map()

    ensure_directories()
    logger = get_logger()
    warning_collector = WarningCollector()
    logger.addHandler(warning_collector)
    tracker = ArtifactTracker()

    runtime = settings.get("runtime", {})
    seed = int(runtime.get("seed", 42))
    horizon = int(runtime.get("forecast_horizon", 6))
    top_ingredients = int(runtime.get("top_ingredients", 12))
    allow_csv_fallback = bool(runtime.get("allow_csv_fallback", True))

    set_global_seed(seed)
    logger.info(
        "Iniciando pipeline run_id=%s seed=%s horizon=%s top_ingredients=%s",
        run_id,
        seed,
        horizon,
        top_ingredients,
    )

    # Fase 1
    t0 = time.perf_counter()
    raw_tables, source_report = load_raw_datasets(settings=settings, logger=logger)
    raw_profile = profile_raw_tables(raw_tables)
    clean_tables, _clean_report = clean_datasets(
        raw_tables, schema_map=schema_map, logger=logger
    )
    validation_report = validate_datasets(
        clean_tables, schema_map=schema_map, logger=logger
    )

    # Guarda validación también en manifest vía tabla.
    validation_df = pd.DataFrame(
        [
            {
                "dataset": dataset_name,
                "status": meta.get("status"),
                "missing_required": ", ".join(meta.get("missing_required", [])),
                "duplicate_rows": meta.get("duplicate_rows"),
            }
            for dataset_name, meta in validation_report.items()
        ]
    )
    write_table(
        validation_df,
        PROCESSED_DIR / "validation_report",
        logger=logger,
        tracker=tracker,
        module="pipeline",
        artifact_type="validation_report",
        allow_csv_fallback=allow_csv_fallback,
    )

    feature_tables = build_features(clean_tables, settings=settings, logger=logger)
    _persist_processed_tables(
        clean_tables=clean_tables,
        feature_tables=feature_tables,
        allow_csv_fallback=allow_csv_fallback,
        tracker=tracker,
        logger=logger,
    )

    run_eda(
        clean_tables=clean_tables,
        feature_tables=feature_tables,
        settings=settings,
        tracker=tracker,
        logger=logger,
    )
    step_timer.record("fase_1_ingesta_limpieza_eda", time.perf_counter() - t0)

    # Fase 2
    t0 = time.perf_counter()
    profitability_outputs = run_profitability_analysis(
        clean_tables,
        recipe_map=recipe_map,
        settings=settings,
        tracker=tracker,
        logger=logger,
    )
    inventory_outputs = run_inventory_analysis(
        clean_tables,
        settings=settings,
        tracker=tracker,
        logger=logger,
    )
    digital_outputs = run_digital_analysis(
        clean_tables,
        settings=settings,
        tracker=tracker,
        logger=logger,
    )
    analysis_outputs: dict[str, pd.DataFrame] = {}
    analysis_outputs.update(profitability_outputs)
    analysis_outputs.update(inventory_outputs)
    analysis_outputs.update(digital_outputs)
    step_timer.record("fase_2_analisis_negocio", time.perf_counter() - t0)

    # Fase 3
    t0 = time.perf_counter()
    forecast_outputs = run_forecast(
        clean_tables,
        settings=settings,
        horizon=horizon,
        top_ingredients=top_ingredients,
        tracker=tracker,
        logger=logger,
    )
    segmentation_outputs = run_segmentation(
        feature_tables,
        settings=settings,
        tracker=tracker,
        logger=logger,
    )
    model_outputs: dict[str, pd.DataFrame] = {}
    model_outputs.update(forecast_outputs)
    model_outputs.update(segmentation_outputs)
    step_timer.record("fase_3_modelado", time.perf_counter() - t0)

    # Fase 4
    t0 = time.perf_counter()
    reco_outputs = run_recommendations(
        clean_tables,
        feature_tables,
        analysis_outputs,
        model_outputs,
        settings=settings,
        tracker=tracker,
        logger=logger,
    )
    model_outputs.update(reco_outputs)

    generate_documents_and_reports(
        settings=settings,
        raw_profile=raw_profile,
        source_report=source_report,
        clean_tables=clean_tables,
        analysis_outputs=analysis_outputs,
        model_outputs=model_outputs,
        tracker=tracker,
        logger=logger,
    )
    step_timer.record("fase_4_recomendaciones_reportes", time.perf_counter() - t0)

    run_finished = datetime.now(timezone.utc)
    summary_md = render_run_summary_markdown(
        run_id=run_id,
        source_report=source_report,
        clean_tables=clean_tables,
        warning_messages=warning_collector.messages,
        tracker=tracker,
        step_seconds=step_timer.step_seconds,
        started_at_utc=run_started,
        finished_at_utc=run_finished,
    )
    write_run_summary(RUN_SUMMARY_PATH, summary_md)
    append_run_summary_to_study_log(Path("."), run_id, summary_md)
    mark_checkpoint_complete(Path("."), run_id)

    tracker.save_manifest(MANIFEST_PATH)
    logger.info(
        "Pipeline finalizado correctamente. Manifest: %s | Run summary: %s",
        MANIFEST_PATH,
        RUN_SUMMARY_PATH,
    )


if __name__ == "__main__":
    main()
