from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px


def load_csv_if_exists(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def filter_sales(
    sales: pd.DataFrame,
    *,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    branch: str,
    category: str,
    dish: str,
    payment_method: str,
) -> pd.DataFrame:
    if sales.empty:
        return sales
    work = sales.copy()
    work["date"] = pd.to_datetime(work.get("date"), errors="coerce")
    mask = (work["date"] >= start_date) & (work["date"] <= end_date)
    if branch != "Todas":
        mask &= work["branch_name"] == branch
    if category != "Todas":
        mask &= work["category"] == category
    if dish != "Todos":
        mask &= work["dish"] == dish
    if payment_method != "Todos":
        mask &= work["payment_method"] == payment_method
    return work.loc[mask].copy()


def sales_trend_chart(df: pd.DataFrame):
    if df.empty:
        return None
    trend = df.groupby("date", dropna=False)["total_sale"].sum().reset_index()
    return px.line(
        trend, x="date", y="total_sale", title="Tendencia de ventas (filtro aplicado)"
    )


def hourly_heatmap(df: pd.DataFrame):
    if df.empty:
        return None
    work = df.copy()
    work["hour"] = pd.to_datetime(
        work.get("time"), format="%H:%M", errors="coerce"
    ).dt.hour
    work["day_of_week"] = work.get("day_of_week", "N/D")
    table = (
        work.groupby(["day_of_week", "hour"], dropna=False)["total_sale"]
        .sum()
        .reset_index()
    )
    return px.density_heatmap(
        table, x="hour", y="day_of_week", z="total_sale", title="Ventas por hora y día"
    )


def branch_ranking_chart(branch_ranking: pd.DataFrame):
    if branch_ranking.empty:
        return None
    return px.bar(
        branch_ranking.sort_values("total_profit_proxy", ascending=False),
        x="branch_name",
        y="total_profit_proxy",
        title="Ranking de sucursales por utilidad proxy",
    )


def forecast_chart(forecast_df: pd.DataFrame):
    if forecast_df.empty:
        return None
    work = forecast_df.copy()
    work["forecast_month"] = pd.to_datetime(
        work["forecast_month"] + "-01", errors="coerce"
    )
    return px.line(
        work,
        x="forecast_month",
        y="forecast_qty",
        color="ingredient",
        facet_col="branch_name",
        facet_col_wrap=2,
        title="Pronóstico mensual por ingrediente y sucursal",
    )


def segment_chart(personas: pd.DataFrame):
    if personas.empty:
        return None
    return px.bar(
        personas,
        x="persona",
        y="customers",
        color="persona",
        title="Distribución de personas",
    )
