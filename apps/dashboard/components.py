from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px

# ---------------------------------------------------------------------------
# Column renaming maps  (technical → user-friendly Spanish)
# ---------------------------------------------------------------------------

_COLUMN_MAPS: dict[str, dict[str, str]] = {
    "sales": {
        "ticket_id": "Ticket",
        "date": "Fecha",
        "time": "Hora",
        "branch_name": "Sucursal",
        "category": "Categoría",
        "dish": "Platillo",
        "quantity": "Cantidad",
        "unit_price": "Precio Unitario",
        "total_sale": "Venta Total ($)",
        "total_with_tip": "Total + Propina ($)",
        "tip": "Propina ($)",
        "payment_method": "Método de Pago",
        "ingredient_cost": "Costo Ingrediente ($)",
        "day_of_week": "Día de la Semana",
        "daypart": "Franja Horaria",
        "hour": "Hora (int)",
        "year_month": "Año-Mes",
    },
    "branch_ranking": {
        "branch_id": "ID",
        "branch_name": "Sucursal",
        "total_revenue": "Ingresos Totales ($)",
        "total_profit_proxy": "Utilidad Proxy ($)",
        "avg_margin_proxy_pct": "Margen Promedio (%)",
        "tickets": "Tickets",
    },
    "inventory_kpis": {
        "branch_id": "ID",
        "branch_name": "Sucursal",
        "waste_cost_total": "Costo Merma Total ($)",
        "waste_qty_total": "Cantidad Merma",
        "shortage_rate": "Tasa de Quiebre (%)",
        "reorder_flag_rate": "Tasa Reorden (%)",
        "purchase_cost_total": "Costo Compra Total ($)",
    },
    "inventory_actions": {
        "branch_id": "ID",
        "ingredient": "Ingrediente",
        "current_stock": "Stock Actual",
        "reorder_point": "Punto de Reorden",
        "recommended_qty": "Cantidad Sugerida",
        "peak_month": "Mes Pico",
        "peak_forecast_qty": "Cantidad Pico",
        "priority": "Prioridad",
        "action": "Acción Recomendada",
        "waste_prevention": "Prevención de Merma",
    },
    "digital_branch": {
        "branch_id": "ID",
        "branch_name": "Sucursal",
        "city": "Ciudad",
        "mentions": "Menciones",
        "total_engagement": "Engagement Total",
        "avg_sentiment_score": "Sentimiento Prom.",
        "avg_engagement_rate": "Tasa Engagement",
        "conversion_rate": "Tasa Conversión (%)",
        "avg_response_hours": "Tiempo Respuesta (hrs)",
    },
    "forecast": {
        "branch_id": "ID",
        "branch_name": "Sucursal",
        "ingredient": "Ingrediente",
        "forecast_month": "Mes",
        "forecast_qty": "Cantidad Pronosticada",
        "model_method": "Método",
        "history_points": "Puntos Históricos",
    },
    "forecast_peak": {
        "branch_id": "ID",
        "branch_name": "Sucursal",
        "ingredient": "Ingrediente",
        "peak_month": "Mes Pico",
        "peak_forecast_qty": "Cantidad Pico",
        "model_method": "Método",
        "history_points": "Puntos Históricos",
    },
    "personas": {
        "segment_id": "ID Segmento",
        "customers": "Clientes",
        "recency_days_mean": "Recencia (días)",
        "frequency_mean": "Frecuencia (visitas/año)",
        "monetary_mean": "Gasto Promedio ($)",
        "loyalty_member_rate": "Tasa Lealtad (%)",
        "promotions_accept_rate": "Acepta Promociones (%)",
        "persona": "Segmento / Persona",
    },
    "segments": {
        "customer_id": "ID Cliente",
        "name": "Nombre",
        "preferred_branch": "Sucursal Preferida",
        "preferred_city": "Ciudad",
        "customer_category": "Categoría",
        "acquisition_channel": "Canal Adquisición",
        "loyalty_member": "Miembro Lealtad",
        "accepts_promotions": "Acepta Promociones",
        "loyalty_points": "Puntos Lealtad",
        "satisfaction_score": "Satisfacción",
        "nps_score": "NPS",
        "recency_days": "Recencia (días)",
        "frequency": "Frecuencia",
        "monetary": "Gasto Total ($)",
        "segment_id": "ID Segmento",
        "persona": "Segmento / Persona",
    },
    "reco_campaigns": {
        "branch_target": "Sucursal",
        "persona": "Segmento / Persona",
        "customers": "Clientes",
        "promo_acceptance_rate": "Tasa Aceptación (%)",
        "campaign_message": "Mensaje de Campaña",
        "recommended_channel": "Canal Recomendado",
    },
    "reco_dishes": {
        "branch_id": "ID",
        "branch_name": "Sucursal",
        "daypart": "Franja Horaria",
        "dish": "Platillo",
        "category": "Categoría",
        "revenue": "Ingresos ($)",
        "qty": "Cantidad",
        "avg_margin_proxy_pct": "Margen (%)",
        "avg_sentiment_score": "Sentimiento",
        "score_qty": "Score Volumen",
        "score_margin": "Score Margen",
        "score_sentiment": "Score Sentimiento",
        "promotion_score": "Score Promoción",
        "recommended_action": "Acción Recomendada",
    },
    "digital_sentiment": {
        "platform": "Plataforma",
        "sentiment": "Sentimiento",
        "records": "Registros",
    },
}

# Columns to hide from user-facing tables (internal IDs)
_HIDE_COLS = {"branch_id", "segment_id"}


def friendly_df(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Return a copy with user-friendly column names and hidden ID columns."""
    if df.empty:
        return df
    work = df.drop(columns=[c for c in _HIDE_COLS if c in df.columns], errors="ignore")
    rename_map = _COLUMN_MAPS.get(table_name, {})
    work = work.rename(columns={k: v for k, v in rename_map.items() if k in work.columns})
    # Format percentage columns (values stored as 0–1 ratios)
    for col in work.columns:
        if "(%" in col and work[col].dtype in ("float64", "float32"):
            work[col] = (work[col] * 100).round(1)
    # Format monetary columns
    for col in work.columns:
        if "($)" in col and work[col].dtype in ("float64", "float32"):
            work[col] = work[col].round(0)
    return work


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Chart builders
# ---------------------------------------------------------------------------


def sales_trend_chart(df: pd.DataFrame):
    if df.empty:
        return None
    trend = df.groupby("date", dropna=False)["total_sale"].sum().reset_index()
    fig = px.line(
        trend, x="date", y="total_sale",
        title="Tendencia de Ventas Diarias ($MXN)",
        labels={"date": "Fecha", "total_sale": "Venta Total ($MXN)"},
    )
    fig.update_layout(hovermode="x unified")
    return fig


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
        table, x="hour", y="day_of_week", z="total_sale",
        title="Mapa de Calor: Ventas por Hora y Día de la Semana",
        labels={"hour": "Hora del Día", "day_of_week": "Día", "total_sale": "Venta Total ($)"},
    )


def branch_ranking_chart(branch_ranking: pd.DataFrame):
    if branch_ranking.empty:
        return None
    sorted_df = branch_ranking.sort_values("total_profit_proxy", ascending=False)
    fig = px.bar(
        sorted_df,
        x="branch_name",
        y="total_profit_proxy",
        title="Ranking de Sucursales por Utilidad Proxy ($MXN)",
        labels={"branch_name": "Sucursal", "total_profit_proxy": "Utilidad Proxy ($MXN)"},
        color="total_profit_proxy",
        color_continuous_scale="RdYlGn",
    )
    fig.update_layout(showlegend=False)
    return fig


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
        title="Pronóstico de Demanda Mensual por Ingrediente",
        labels={
            "forecast_month": "Mes",
            "forecast_qty": "Cantidad Pronosticada",
            "ingredient": "Ingrediente",
            "branch_name": "Sucursal",
        },
    )


def segment_chart(personas: pd.DataFrame):
    if personas.empty:
        return None
    return px.bar(
        personas,
        x="persona",
        y="customers",
        color="persona",
        title="Segmentos de Clientes (Personas)",
        labels={"persona": "Segmento / Persona", "customers": "Clientes"},
    )
