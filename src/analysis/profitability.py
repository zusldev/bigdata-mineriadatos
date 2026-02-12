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


def _estimate_ingredient_cost(
    sales: pd.DataFrame, recipe_map: dict[str, Any]
) -> pd.Series:
    dish_cost_map = recipe_map.get("dish_cost_per_unit", {})
    category_ratio = recipe_map.get("category_cost_ratio", {})

    explicit_cost = pd.to_numeric(sales.get("ingredient_cost"), errors="coerce")
    quantity = pd.to_numeric(sales.get("quantity"), errors="coerce").fillna(0.0)
    unit_price = pd.to_numeric(sales.get("unit_price"), errors="coerce").fillna(0.0)
    total_sale = pd.to_numeric(sales.get("total_sale"), errors="coerce").fillna(
        unit_price * quantity
    )

    dish_estimate = (
        sales.get("dish", pd.Series(index=sales.index, dtype=object)).map(dish_cost_map)
        * quantity
    )
    ratio_estimate = (
        sales.get("category", pd.Series(index=sales.index, dtype=object))
        .map(category_ratio)
        .fillna(0.35)
        .astype(float)
        * total_sale
    )
    estimated = explicit_cost.fillna(dish_estimate).fillna(ratio_estimate)
    return estimated


def run_profitability_analysis(
    clean_tables: dict[str, pd.DataFrame],
    *,
    recipe_map: dict[str, Any],
    settings: dict[str, Any],
    tracker: ArtifactTracker | None,
    logger,
) -> dict[str, pd.DataFrame]:
    module = "analysis.profitability"
    outputs_tables = Path(settings["paths"]["outputs_tables"])

    sales = clean_tables.get("sales", pd.DataFrame()).copy()
    branches = clean_tables.get("branches", pd.DataFrame()).copy()

    if sales.empty:
        logger.warning("No hay ventas para análisis de rentabilidad.")
        return {}

    sales["date"] = pd.to_datetime(sales.get("date"), errors="coerce")
    sales["year_month"] = sales["date"].dt.to_period("M").astype(str)
    sales["quantity"] = pd.to_numeric(sales.get("quantity"), errors="coerce").fillna(
        0.0
    )
    sales["unit_price"] = pd.to_numeric(
        sales.get("unit_price"), errors="coerce"
    ).fillna(0.0)
    sales["total_sale"] = pd.to_numeric(
        sales.get("total_sale"), errors="coerce"
    ).fillna(sales["unit_price"] * sales["quantity"])
    sales["estimated_ingredient_cost"] = _estimate_ingredient_cost(
        sales, recipe_map=recipe_map
    )
    sales["ticket_id"] = sales.get(
        "ticket_id", pd.Series(np.arange(len(sales)).astype(str), index=sales.index)
    )

    monthly_tickets = (
        sales.groupby(["branch_id", "year_month"], dropna=False)["ticket_id"]
        .nunique()
        .reset_index(name="monthly_tickets")
    )
    branch_costs = (
        branches[["branch_id", "operational_cost_total"]].copy()
        if {"branch_id", "operational_cost_total"}.issubset(branches.columns)
        else pd.DataFrame(columns=["branch_id", "operational_cost_total"])
    )
    branch_costs["operational_cost_total"] = pd.to_numeric(
        branch_costs["operational_cost_total"], errors="coerce"
    ).fillna(0.0)

    sales = sales.merge(monthly_tickets, on=["branch_id", "year_month"], how="left")
    sales = sales.merge(branch_costs, on="branch_id", how="left")
    sales["operational_cost_total"] = sales["operational_cost_total"].fillna(0.0)
    sales["monthly_tickets"] = sales["monthly_tickets"].replace(0, np.nan)
    sales["op_cost_alloc_per_ticket"] = (
        sales["operational_cost_total"] / sales["monthly_tickets"]
    ).fillna(0.0)

    sales["profit_proxy"] = (
        sales["total_sale"]
        - sales["estimated_ingredient_cost"]
        - sales["op_cost_alloc_per_ticket"]
    )
    sales["margin_proxy_pct"] = np.where(
        sales["total_sale"] > 0,
        100 * sales["profit_proxy"] / sales["total_sale"],
        0.0,
    )

    branch_ranking = (
        sales.groupby(["branch_id", "branch_name"], dropna=False)
        .agg(
            total_revenue=("total_sale", "sum"),
            total_profit_proxy=("profit_proxy", "sum"),
            avg_margin_proxy_pct=("margin_proxy_pct", "mean"),
            tickets=("ticket_id", "nunique"),
        )
        .reset_index()
        .sort_values("total_profit_proxy", ascending=False)
    )

    dish_ranking = (
        sales.groupby(["dish", "category"], dropna=False)
        .agg(
            total_revenue=("total_sale", "sum"),
            total_profit_proxy=("profit_proxy", "sum"),
            total_quantity=("quantity", "sum"),
            avg_margin_proxy_pct=("margin_proxy_pct", "mean"),
        )
        .reset_index()
        .sort_values("total_profit_proxy", ascending=False)
    )

    drivers = (
        sales.groupby(["branch_id", "branch_name", "category"], dropna=False)
        .agg(
            revenue=("total_sale", "sum"),
            ingredient_cost=("estimated_ingredient_cost", "sum"),
            op_alloc=("op_cost_alloc_per_ticket", "sum"),
            profit_proxy=("profit_proxy", "sum"),
        )
        .reset_index()
    )

    _save_csv(
        branch_ranking,
        outputs_tables / "profitability_branch_ranking.csv",
        tracker,
        module,
    )
    _save_csv(
        dish_ranking, outputs_tables / "profitability_dish_ranking.csv", tracker, module
    )
    _save_csv(drivers, outputs_tables / "profitability_drivers.csv", tracker, module)

    return {
        "profitability_branch_ranking": branch_ranking,
        "profitability_dish_ranking": dish_ranking,
        "profitability_drivers": drivers,
        "profitability_line_level": sales,
    }
