from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.utils.io import ArtifactTracker, save_pickle


def _save_csv(
    df: pd.DataFrame, path: Path, tracker: ArtifactTracker | None, module: str
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    if tracker:
        tracker.register(path, "table", module, "csv", len(df))


def _top_ingredients(inventory: pd.DataFrame, top_n: int) -> list[str]:
    impact = (
        inventory.groupby("ingredient", dropna=False)
        .agg(
            total_cost=("total_purchase_cost", "sum"), total_qty=("qty_ordered", "sum")
        )
        .reset_index()
    )
    if impact.empty:
        return []
    impact["score"] = impact["total_cost"].rank(pct=True) + impact["total_qty"].rank(
        pct=True
    )
    return (
        impact.sort_values("score", ascending=False).head(top_n)["ingredient"].tolist()
    )


def _forecast_series(
    series: pd.Series, horizon: int
) -> tuple[np.ndarray, str, dict[str, Any]]:
    clean_series = series.dropna().astype(float)
    if len(clean_series) == 0:
        return np.zeros(horizon), "zero", {"reason": "serie_vacia"}
    if len(clean_series) < 3 or clean_series.nunique() <= 1:
        mean_value = float(clean_series.mean())
        return (
            np.repeat(max(0.0, mean_value), horizon),
            "mean",
            {"history_points": len(clean_series)},
        )

    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        model = ExponentialSmoothing(
            clean_series,
            trend="add",
            seasonal=None,
            initialization_method="estimated",
        ).fit(optimized=True)
        pred = model.forecast(horizon)
        pred = np.clip(np.asarray(pred, dtype=float), a_min=0.0, a_max=None)
        return pred, "exp_smoothing", {"history_points": len(clean_series)}
    except Exception:
        rolling = clean_series.rolling(3).mean().iloc[-1]
        if pd.isna(rolling):
            rolling = clean_series.mean()
        pred = np.repeat(max(0.0, float(rolling)), horizon)
        return pred, "rolling_mean", {"history_points": len(clean_series)}


def run_forecast(
    clean_tables: dict[str, pd.DataFrame],
    *,
    settings: dict[str, Any],
    horizon: int,
    top_ingredients: int,
    tracker: ArtifactTracker | None,
    logger,
) -> dict[str, pd.DataFrame]:
    module = "models.forecast"
    outputs_tables = Path(settings["paths"]["outputs_tables"])
    outputs_models = Path(settings["paths"]["outputs_models"])

    inventory = clean_tables.get("inventory", pd.DataFrame()).copy()
    if inventory.empty:
        logger.warning("No hay inventario para pronóstico.")
        return {}

    inventory["date"] = pd.to_datetime(inventory.get("date"), errors="coerce")
    inventory = inventory.dropna(subset=["date"])
    inventory["month_start"] = inventory["date"].dt.to_period("M").dt.to_timestamp()
    for col in ["qty_ordered", "total_purchase_cost"]:
        inventory[col] = pd.to_numeric(inventory.get(col), errors="coerce").fillna(0.0)

    selected_ingredients = _top_ingredients(inventory, top_n=top_ingredients)
    scoped = inventory[inventory["ingredient"].isin(selected_ingredients)].copy()

    if scoped.empty:
        logger.warning("No se encontró inventario para ingredientes top.")
        return {}

    monthly = (
        scoped.groupby(
            ["branch_id", "branch_name", "ingredient", "month_start"], dropna=False
        )["qty_ordered"]
        .sum()
        .reset_index()
    )

    forecasts = []
    model_metadata = {}

    for (branch_id, branch_name, ingredient), group in monthly.groupby(
        ["branch_id", "branch_name", "ingredient"], dropna=False
    ):
        idx = pd.date_range(
            group["month_start"].min(), group["month_start"].max(), freq="MS"
        )
        series = group.set_index("month_start")["qty_ordered"].reindex(
            idx, fill_value=0.0
        )
        pred_values, method, metadata = _forecast_series(series, horizon=horizon)

        forecast_idx = pd.date_range(
            idx.max() + pd.offsets.MonthBegin(1), periods=horizon, freq="MS"
        )
        for dt, value in zip(forecast_idx, pred_values):
            forecasts.append(
                {
                    "branch_id": branch_id,
                    "branch_name": branch_name,
                    "ingredient": ingredient,
                    "forecast_month": dt.strftime("%Y-%m"),
                    "forecast_qty": round(float(value), 2),
                    "model_method": method,
                    "history_points": len(series),
                }
            )
        model_metadata[f"{branch_id}|{ingredient}"] = {
            "method": method,
            "history_points": len(series),
            "last_observed_month": str(idx.max().date()),
            **metadata,
        }

    forecast_df = pd.DataFrame(forecasts).sort_values(
        ["branch_id", "ingredient", "forecast_month"]
    )
    peak_months = (
        forecast_df.sort_values("forecast_qty", ascending=False)
        .groupby(["branch_id", "branch_name", "ingredient"], dropna=False)
        .head(1)
        .reset_index(drop=True)
        .rename(
            columns={
                "forecast_month": "peak_month",
                "forecast_qty": "peak_forecast_qty",
            }
        )
    )

    _save_csv(
        forecast_df, outputs_tables / "forecast_monthly_demand.csv", tracker, module
    )
    _save_csv(peak_months, outputs_tables / "forecast_peak_months.csv", tracker, module)
    save_pickle(
        model_metadata,
        outputs_models / "forecast_models.pkl",
        tracker=tracker,
        module=module,
    )

    return {
        "forecast_monthly_demand": forecast_df,
        "forecast_peak_months": peak_months,
    }
