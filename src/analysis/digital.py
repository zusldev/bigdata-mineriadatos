from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.utils.io import ArtifactTracker


def _save_csv(
    df: pd.DataFrame, path: Path, tracker: ArtifactTracker | None, module: str
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    if tracker:
        tracker.register(path, "table", module, "csv", len(df))


def run_digital_analysis(
    clean_tables: dict[str, pd.DataFrame],
    *,
    settings: dict[str, Any],
    tracker: ArtifactTracker | None,
    logger,
) -> dict[str, pd.DataFrame]:
    module = "analysis.digital"
    outputs_tables = Path(settings["paths"]["outputs_tables"])
    digital = clean_tables.get("digital", pd.DataFrame()).copy()

    if digital.empty:
        logger.warning("No hay datos digitales para análisis.")
        return {}

    digital["date"] = pd.to_datetime(digital.get("date"), errors="coerce")
    for col in [
        "engagement",
        "reach",
        "engagement_rate",
        "campaign_cost",
        "response_hours",
    ]:
        digital[col] = pd.to_numeric(digital.get(col), errors="coerce").fillna(0.0)
    digital["sentiment"] = digital.get("sentiment", "").astype(str).str.lower()
    digital["sentiment_score"] = (
        digital["sentiment"]
        .map({"positivo": 1.0, "neutro": 0.0, "negativo": -1.0})
        .fillna(0.0)
    )
    if "conversion" in digital.columns:
        digital["conversion_num"] = digital["conversion"].astype(float).fillna(0.0)
    else:
        digital["conversion_num"] = 0.0

    branch_summary = (
        digital.groupby(["branch_id", "branch_name", "city"], dropna=False)
        .agg(
            mentions=(
                ("record_id", "count")
                if "record_id" in digital.columns
                else ("sentiment", "count")
            ),
            total_engagement=("engagement", "sum"),
            avg_sentiment_score=("sentiment_score", "mean"),
            avg_engagement_rate=("engagement_rate", "mean"),
            conversion_rate=("conversion_num", "mean"),
            avg_response_hours=("response_hours", "mean"),
        )
        .reset_index()
        .sort_values("total_engagement", ascending=False)
    )

    campaign_summary = (
        digital.groupby(["campaign", "platform"], dropna=False)
        .agg(
            interactions=("sentiment", "count"),
            total_engagement=("engagement", "sum"),
            total_reach=("reach", "sum"),
            conversion_rate=("conversion_num", "mean"),
            campaign_cost=("campaign_cost", "sum"),
        )
        .reset_index()
    )
    campaign_summary["engagement_per_cost"] = np.where(
        campaign_summary["campaign_cost"] > 0,
        campaign_summary["total_engagement"] / campaign_summary["campaign_cost"],
        np.nan,
    )

    platform_sentiment = (
        digital.groupby(["platform", "sentiment"], dropna=False)
        .size()
        .reset_index(name="records")
    )

    _save_csv(
        branch_summary, outputs_tables / "digital_branch_summary.csv", tracker, module
    )
    _save_csv(
        campaign_summary,
        outputs_tables / "digital_campaign_summary.csv",
        tracker,
        module,
    )
    _save_csv(
        platform_sentiment,
        outputs_tables / "digital_platform_sentiment.csv",
        tracker,
        module,
    )

    return {
        "digital_branch_summary": branch_summary,
        "digital_campaign_summary": campaign_summary,
        "digital_platform_sentiment": platform_sentiment,
    }
