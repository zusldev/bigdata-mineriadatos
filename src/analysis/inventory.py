from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.utils.io import ArtifactTracker


LEAD_TIME_MAP = {
    "diario": 1,
    "semanal": 7,
    "quincenal": 15,
    "mensual": 30,
}


def _save_csv(
    df: pd.DataFrame, path: Path, tracker: ArtifactTracker | None, module: str
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    if tracker:
        tracker.register(path, "table", module, "csv", len(df))


def run_inventory_analysis(
    clean_tables: dict[str, pd.DataFrame],
    *,
    settings: dict[str, Any],
    tracker: ArtifactTracker | None,
    logger,
) -> dict[str, pd.DataFrame]:
    module = "analysis.inventory"
    outputs_tables = Path(settings["paths"]["outputs_tables"])
    z_value = settings.get("analysis", {}).get("safety_stock_z_value", 1.65)

    inventory = clean_tables.get("inventory", pd.DataFrame()).copy()
    if inventory.empty:
        logger.warning("No hay inventarios para análisis.")
        return {}

    inventory["date"] = pd.to_datetime(inventory.get("date"), errors="coerce")
    for col in [
        "qty_ordered",
        "qty_wasted",
        "waste_cost",
        "current_stock",
        "min_stock",
        "total_purchase_cost",
    ]:
        inventory[col] = pd.to_numeric(inventory.get(col), errors="coerce").fillna(0.0)

    if "needs_reorder" in inventory:
        needs_reorder = inventory["needs_reorder"].astype(float).fillna(0.0)
    else:
        needs_reorder = (
            (inventory["current_stock"] < inventory["min_stock"]).astype(float)
            if {"current_stock", "min_stock"}.issubset(inventory.columns)
            else 0.0
        )
    inventory["needs_reorder_num"] = needs_reorder

    inventory["is_shortage"] = inventory["current_stock"] < inventory["min_stock"]
    inventory["waste_ratio"] = np.where(
        inventory["qty_ordered"] > 0,
        inventory["qty_wasted"] / inventory["qty_ordered"],
        0.0,
    )

    waste_drivers = (
        inventory.groupby(
            [
                "branch_id",
                "branch_name",
                "ingredient",
                "ingredient_category",
                "waste_reason",
            ],
            dropna=False,
        )
        .agg(
            total_waste_qty=("qty_wasted", "sum"),
            total_waste_cost=("waste_cost", "sum"),
            avg_waste_ratio=("waste_ratio", "mean"),
        )
        .reset_index()
        .sort_values("total_waste_cost", ascending=False)
    )

    shortage_summary = (
        inventory.groupby(["branch_id", "branch_name", "ingredient"], dropna=False)
        .agg(
            shortage_events=("is_shortage", "sum"),
            records=(
                ("record_id", "count")
                if "record_id" in inventory.columns
                else ("is_shortage", "count")
            ),
            shortage_rate=("is_shortage", "mean"),
            avg_stock=("current_stock", "mean"),
            avg_min_stock=("min_stock", "mean"),
        )
        .reset_index()
        .sort_values("shortage_rate", ascending=False)
    )

    freq_norm = (
        inventory.get(
            "reorder_frequency", pd.Series(index=inventory.index, dtype=object)
        )
        .astype(str)
        .str.lower()
    )
    inventory["lead_time_days"] = freq_norm.map(LEAD_TIME_MAP).fillna(7).astype(float)

    daily_demand = (
        inventory.groupby(["branch_id", "ingredient", "date"], dropna=False)[
            "qty_ordered"
        ]
        .sum()
        .reset_index()
    )
    demand_stats = (
        daily_demand.groupby(["branch_id", "ingredient"], dropna=False)["qty_ordered"]
        .agg(["mean", "std"])
        .reset_index()
        .rename(columns={"mean": "avg_daily_demand", "std": "std_daily_demand"})
    )
    demand_stats["std_daily_demand"] = demand_stats["std_daily_demand"].fillna(0.0)

    lead_time = (
        inventory.groupby(["branch_id", "ingredient"], dropna=False)["lead_time_days"]
        .mean()
        .reset_index()
    )
    stock_last = (
        inventory.sort_values("date")
        .groupby(["branch_id", "ingredient"], dropna=False)
        .tail(1)[
            [
                "branch_id",
                "ingredient",
                "current_stock",
                "min_stock",
                "needs_reorder_num",
            ]
        ]
    )

    reorder_policy = demand_stats.merge(
        lead_time, on=["branch_id", "ingredient"], how="left"
    ).merge(stock_last, on=["branch_id", "ingredient"], how="left")
    reorder_policy["lead_time_days"] = reorder_policy["lead_time_days"].fillna(7.0)
    reorder_policy["safety_stock"] = (
        z_value
        * reorder_policy["std_daily_demand"]
        * np.sqrt(reorder_policy["lead_time_days"])
    )
    reorder_policy["reorder_point"] = (
        reorder_policy["avg_daily_demand"] * reorder_policy["lead_time_days"]
        + reorder_policy["safety_stock"]
    )
    reorder_policy["recommended_reorder"] = (
        reorder_policy["current_stock"] < reorder_policy["reorder_point"]
    )
    reorder_policy["recommended_qty"] = (
        (reorder_policy["reorder_point"] - reorder_policy["current_stock"])
        .clip(lower=0)
        .round(2)
    )

    branch_kpis = (
        inventory.groupby(["branch_id", "branch_name"], dropna=False)
        .agg(
            waste_cost_total=("waste_cost", "sum"),
            waste_qty_total=("qty_wasted", "sum"),
            shortage_rate=("is_shortage", "mean"),
            reorder_flag_rate=("needs_reorder_num", "mean"),
            purchase_cost_total=("total_purchase_cost", "sum"),
        )
        .reset_index()
    )

    _save_csv(
        waste_drivers, outputs_tables / "inventory_waste_drivers.csv", tracker, module
    )
    _save_csv(
        shortage_summary,
        outputs_tables / "inventory_shortage_summary.csv",
        tracker,
        module,
    )
    _save_csv(
        reorder_policy, outputs_tables / "inventory_reorder_policy.csv", tracker, module
    )
    _save_csv(
        branch_kpis, outputs_tables / "inventory_branch_kpis.csv", tracker, module
    )

    return {
        "inventory_waste_drivers": waste_drivers,
        "inventory_shortage_summary": shortage_summary,
        "inventory_reorder_policy": reorder_policy,
        "inventory_branch_kpis": branch_kpis,
    }
