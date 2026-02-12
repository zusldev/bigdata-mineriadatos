from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px

from src.utils.io import ArtifactTracker, save_plotly_figure


def _save_csv(
    df: pd.DataFrame, path: Path, tracker: ArtifactTracker | None, module: str
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    if tracker:
        tracker.register(path, "table", module, "csv", len(df))


def _safe_sales_columns(sales: pd.DataFrame) -> pd.DataFrame:
    if sales.empty:
        return sales
    work = sales.copy()
    work["date"] = pd.to_datetime(work.get("date"), errors="coerce")
    for col in ["total_sale", "quantity", "gross_margin", "tip"]:
        if col not in work:
            work[col] = 0.0
        work[col] = pd.to_numeric(work[col], errors="coerce").fillna(0.0)
    if "hour" not in work:
        work["hour"] = pd.to_datetime(
            work.get("time"), format="%H:%M", errors="coerce"
        ).dt.hour
    if "day_of_week" not in work:
        work["day_of_week"] = work["date"].dt.day_name()
    if "daypart" not in work:
        work["daypart"] = "Sin dato"
    return work


def run_eda(
    clean_tables: dict[str, pd.DataFrame],
    feature_tables: dict[str, pd.DataFrame],
    *,
    settings: dict[str, Any],
    tracker: ArtifactTracker | None,
    logger,
) -> dict[str, Path]:
    outputs_charts = Path(settings["paths"]["outputs_charts"])
    outputs_tables = Path(settings["paths"]["outputs_tables"])
    outputs_charts.mkdir(parents=True, exist_ok=True)
    outputs_tables.mkdir(parents=True, exist_ok=True)

    sales = _safe_sales_columns(clean_tables.get("sales", pd.DataFrame()))
    inventory = clean_tables.get("inventory", pd.DataFrame()).copy()
    digital = clean_tables.get("digital", pd.DataFrame()).copy()
    branch_day_hour = feature_tables.get(
        "analytics_branch_day_hour", pd.DataFrame()
    ).copy()

    generated: dict[str, Path] = {}
    module = "eda"

    if not sales.empty:
        daily = sales.groupby("date", dropna=False)["total_sale"].sum().reset_index()
        fig_daily = px.line(
            daily, x="date", y="total_sale", title="Tendencia diaria de ventas"
        )
        path_daily = outputs_charts / "sales_trend_daily.html"
        save_plotly_figure(fig_daily, path_daily, tracker=tracker, module=module)
        generated["sales_trend_daily"] = path_daily

        sales["year_month"] = sales["date"].dt.to_period("M").astype(str)
        monthly = (
            sales.groupby("year_month", dropna=False)["total_sale"].sum().reset_index()
        )
        fig_monthly = px.bar(
            monthly, x="year_month", y="total_sale", title="Ventas mensuales"
        )
        path_monthly = outputs_charts / "sales_trend_monthly.html"
        save_plotly_figure(fig_monthly, path_monthly, tracker=tracker, module=module)
        generated["sales_trend_monthly"] = path_monthly

        by_city = (
            sales.groupby("city", dropna=False)["total_sale"]
            .sum()
            .reset_index()
            .sort_values("total_sale", ascending=False)
        )
        fig_city = px.bar(by_city, x="city", y="total_sale", title="Ventas por ciudad")
        path_city = outputs_charts / "sales_by_city.html"
        save_plotly_figure(fig_city, path_city, tracker=tracker, module=module)
        generated["sales_by_city"] = path_city
        _save_csv(by_city, outputs_tables / "sales_by_city.csv", tracker, module)

        by_hour_day = (
            sales.groupby(["day_of_week", "hour"], dropna=False)["total_sale"]
            .sum()
            .reset_index()
            .rename(columns={"total_sale": "revenue"})
        )
        fig_hour_day = px.density_heatmap(
            by_hour_day,
            x="hour",
            y="day_of_week",
            z="revenue",
            color_continuous_scale="Sunset",
            title="Mapa de calor de ventas por hora y día",
        )
        path_hour_day = outputs_charts / "sales_by_hour_day.html"
        save_plotly_figure(fig_hour_day, path_hour_day, tracker=tracker, module=module)
        generated["sales_by_hour_day"] = path_hour_day
        _save_csv(
            by_hour_day, outputs_tables / "sales_by_hour_day.csv", tracker, module
        )

        dish_region_daypart = (
            sales.groupby(["city", "daypart", "dish"], dropna=False)
            .agg(total_qty=("quantity", "sum"), total_revenue=("total_sale", "sum"))
            .reset_index()
            .sort_values(
                ["city", "daypart", "total_revenue"], ascending=[True, True, False]
            )
        )
        top_dishes = (
            dish_region_daypart.groupby(["city", "daypart"], dropna=False)
            .head(5)
            .reset_index(drop=True)
        )
        _save_csv(
            top_dishes,
            outputs_tables / "top_dishes_by_region_daypart.csv",
            tracker,
            module,
        )
        fig_top_dishes = px.bar(
            top_dishes,
            x="dish",
            y="total_revenue",
            color="daypart",
            facet_col="city",
            facet_col_wrap=3,
            title="Top platillos por ciudad y franja horaria",
        )
        path_top_dishes = outputs_charts / "top_dishes_by_region_daypart.html"
        save_plotly_figure(
            fig_top_dishes, path_top_dishes, tracker=tracker, module=module
        )
        generated["top_dishes_by_region_daypart"] = path_top_dishes

        branch_ranking = (
            sales.groupby(["branch_id", "branch_name"], dropna=False)
            .agg(
                total_revenue=("total_sale", "sum"),
                total_margin=("gross_margin", "sum"),
                tickets=("ticket_id", "nunique"),
            )
            .reset_index()
            .sort_values("total_revenue", ascending=False)
        )
        branch_ranking["avg_ticket"] = branch_ranking["total_revenue"] / branch_ranking[
            "tickets"
        ].replace(0, np.nan)
        branch_ranking["avg_ticket"] = branch_ranking["avg_ticket"].fillna(0.0)
        _save_csv(
            branch_ranking,
            outputs_tables / "branch_ranking_sales_margin.csv",
            tracker,
            module,
        )
        fig_branch_rank = px.bar(
            branch_ranking,
            x="branch_name",
            y="total_revenue",
            color="total_margin",
            title="Ranking de sucursales por ventas y margen",
        )
        path_branch_rank = outputs_charts / "branch_ranking_sales_margin.html"
        save_plotly_figure(
            fig_branch_rank, path_branch_rank, tracker=tracker, module=module
        )
        generated["branch_ranking_sales_margin"] = path_branch_rank

        payment_mix = (
            sales.groupby("payment_method", dropna=False)["total_sale"]
            .sum()
            .reset_index()
        )
        _save_csv(
            payment_mix, outputs_tables / "payment_method_mix.csv", tracker, module
        )
        fig_payment = px.pie(
            payment_mix,
            names="payment_method",
            values="total_sale",
            title="Mix de métodos de pago",
        )
        path_payment = outputs_charts / "payment_method_mix.html"
        save_plotly_figure(fig_payment, path_payment, tracker=tracker, module=module)
        generated["payment_method_mix"] = path_payment

    if not inventory.empty:
        inventory["waste_cost"] = pd.to_numeric(
            inventory.get("waste_cost"), errors="coerce"
        ).fillna(0.0)
        inventory["is_shortage"] = pd.to_numeric(
            inventory.get("current_stock"), errors="coerce"
        ).fillna(np.inf) < pd.to_numeric(
            inventory.get("min_stock"), errors="coerce"
        ).fillna(
            -np.inf
        )
        waste_shortage = (
            inventory.groupby(["branch_name", "ingredient"], dropna=False)
            .agg(
                total_waste_cost=("waste_cost", "sum"),
                shortage_rate=("is_shortage", "mean"),
            )
            .reset_index()
        )
        _save_csv(
            waste_shortage,
            outputs_tables / "inventory_waste_shortage_heatmap_table.csv",
            tracker,
            module,
        )
        fig_inventory = px.density_heatmap(
            waste_shortage,
            x="ingredient",
            y="branch_name",
            z="total_waste_cost",
            title="Costo de desperdicio por ingrediente y sucursal",
            color_continuous_scale="Reds",
        )
        path_inventory = outputs_charts / "inventory_waste_shortage_heatmap.html"
        save_plotly_figure(
            fig_inventory, path_inventory, tracker=tracker, module=module
        )
        generated["inventory_waste_shortage_heatmap"] = path_inventory

    if not digital.empty:
        digital["sentiment"] = digital.get("sentiment", "").astype(str).str.lower()
        sentiment_platform = (
            digital.groupby(["platform", "sentiment"], dropna=False)
            .size()
            .reset_index(name="records")
        )
        _save_csv(
            sentiment_platform,
            outputs_tables / "digital_sentiment_platform.csv",
            tracker,
            module,
        )
        fig_digital = px.bar(
            sentiment_platform,
            x="platform",
            y="records",
            color="sentiment",
            barmode="group",
            title="Sentimiento por plataforma digital",
        )
        path_digital = outputs_charts / "digital_sentiment_platform.html"
        save_plotly_figure(fig_digital, path_digital, tracker=tracker, module=module)
        generated["digital_sentiment_platform"] = path_digital

    if not branch_day_hour.empty:
        _save_csv(
            branch_day_hour,
            outputs_tables / "analytics_branch_day_hour.csv",
            tracker,
            module,
        )

    return generated
