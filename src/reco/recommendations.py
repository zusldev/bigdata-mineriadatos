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


def _normalize(series: pd.Series) -> pd.Series:
    if series.empty:
        return series
    min_v = series.min()
    max_v = series.max()
    if pd.isna(min_v) or pd.isna(max_v) or min_v == max_v:
        return pd.Series(np.ones(len(series)), index=series.index)
    return (series - min_v) / (max_v - min_v)


def _campaign_message(persona: str) -> str:
    persona = str(persona)
    if persona == "Leales Premium":
        return "Ofrecer experiencias VIP, maridajes premium y beneficios exclusivos de lealtad."
    if persona == "Frecuentes Recientes":
        return "Promociones de frecuencia (2x1 en horarios valle) para sostener recurrencia semanal."
    if persona == "Socios de Valor":
        return (
            "Impulsar programa de puntos y combos familiares con valor percibido alto."
        )
    if persona == "En Riesgo de Churn":
        return "Campaña de recuperación: cupón de regreso y recordatorio personalizado."
    return "Promociones de entrada y menú destacado para aumentar ticket y visitas."


def run_recommendations(
    clean_tables: dict[str, pd.DataFrame],
    feature_tables: dict[str, pd.DataFrame],
    analysis_outputs: dict[str, pd.DataFrame],
    model_outputs: dict[str, pd.DataFrame],
    *,
    settings: dict[str, Any],
    tracker: ArtifactTracker | None,
    logger,
) -> dict[str, pd.DataFrame]:
    module = "reco.recommendations"
    outputs_tables = Path(settings["paths"]["outputs_tables"])

    sales = clean_tables.get("sales", pd.DataFrame()).copy()
    profitability_dish = analysis_outputs.get(
        "profitability_dish_ranking", pd.DataFrame()
    ).copy()
    digital_branch = analysis_outputs.get(
        "digital_branch_summary", pd.DataFrame()
    ).copy()
    inventory_reorder = analysis_outputs.get(
        "inventory_reorder_policy", pd.DataFrame()
    ).copy()
    customer_segments = model_outputs.get("customer_segments", pd.DataFrame()).copy()
    forecast_peak = model_outputs.get("forecast_peak_months", pd.DataFrame()).copy()

    outputs: dict[str, pd.DataFrame] = {}

    if not sales.empty:
        sales["date"] = pd.to_datetime(sales.get("date"), errors="coerce")
        for col in ["total_sale", "quantity"]:
            sales[col] = pd.to_numeric(sales.get(col), errors="coerce").fillna(0.0)
        if "daypart" not in sales:
            sales["daypart"] = "Sin dato"

        promo_base = (
            sales.groupby(
                ["branch_id", "branch_name", "daypart", "dish", "category"],
                dropna=False,
            )
            .agg(
                revenue=("total_sale", "sum"),
                qty=("quantity", "sum"),
            )
            .reset_index()
        )

        if not profitability_dish.empty and {"dish", "avg_margin_proxy_pct"}.issubset(
            profitability_dish.columns
        ):
            promo_base = promo_base.merge(
                profitability_dish[["dish", "avg_margin_proxy_pct"]].drop_duplicates(
                    "dish"
                ),
                on="dish",
                how="left",
            )
        else:
            promo_base["avg_margin_proxy_pct"] = np.nan

        if not digital_branch.empty and {"branch_id", "avg_sentiment_score"}.issubset(
            digital_branch.columns
        ):
            promo_base = promo_base.merge(
                digital_branch[["branch_id", "avg_sentiment_score"]].drop_duplicates(
                    "branch_id"
                ),
                on="branch_id",
                how="left",
            )
        else:
            promo_base["avg_sentiment_score"] = 0.0

        promo_base["score_qty"] = _normalize(promo_base["qty"])
        promo_base["score_margin"] = _normalize(
            promo_base["avg_margin_proxy_pct"].fillna(
                promo_base["avg_margin_proxy_pct"].median()
            )
        )
        promo_base["score_sentiment"] = _normalize(
            promo_base["avg_sentiment_score"].fillna(0.0)
        )
        promo_base["promotion_score"] = (
            0.45 * promo_base["score_qty"]
            + 0.40 * promo_base["score_margin"]
            + 0.15 * promo_base["score_sentiment"]
        )

        dish_promotions = (
            promo_base.sort_values("promotion_score", ascending=False)
            .groupby(["branch_id", "branch_name", "daypart"], dropna=False)
            .head(3)
            .reset_index(drop=True)
        )
        dish_promotions["recommended_action"] = (
            "Promover en franja "
            + dish_promotions["daypart"].astype(str)
            + " con bundle y CTA digital."
        )
        _save_csv(
            dish_promotions,
            outputs_tables / "recommendations_dish_promotions.csv",
            tracker,
            module,
        )
        outputs["recommendations_dish_promotions"] = dish_promotions

    if not customer_segments.empty:
        segments_cols = [
            "segment_id",
            "persona",
            "preferred_branch",
            "preferred_city",
            "accepts_promotions",
        ]
        existing_cols = [c for c in segments_cols if c in customer_segments.columns]
        seg = customer_segments[existing_cols].copy()
        if "accepts_promotions" in seg.columns:
            seg["accepts_promotions"] = (
                seg["accepts_promotions"].astype(float).fillna(0.0)
            )
        else:
            seg["accepts_promotions"] = 0.0
        if "preferred_branch" not in seg.columns:
            seg["preferred_branch"] = "Sin dato"
        if "persona" not in seg.columns:
            seg["persona"] = "Base General"

        campaign = (
            seg.groupby(["preferred_branch", "persona"], dropna=False)
            .agg(
                customers=("persona", "count"),
                promo_acceptance_rate=("accepts_promotions", "mean"),
            )
            .reset_index()
            .sort_values(["customers", "promo_acceptance_rate"], ascending=False)
        )
        campaign["campaign_message"] = campaign["persona"].map(_campaign_message)
        campaign["recommended_channel"] = np.where(
            campaign["promo_acceptance_rate"] >= 0.5,
            "WhatsApp + App + Email",
            "Redes sociales + Remarketing",
        )
        campaign = campaign.rename(columns={"preferred_branch": "branch_target"})

        _save_csv(
            campaign,
            outputs_tables / "recommendations_branch_campaigns.csv",
            tracker,
            module,
        )
        outputs["recommendations_branch_campaigns"] = campaign

    if not inventory_reorder.empty:
        inv_actions = inventory_reorder.copy()
        if not forecast_peak.empty and {
            "branch_id",
            "ingredient",
            "peak_month",
            "peak_forecast_qty",
        }.issubset(forecast_peak.columns):
            inv_actions = inv_actions.merge(
                forecast_peak[
                    ["branch_id", "ingredient", "peak_month", "peak_forecast_qty"]
                ],
                on=["branch_id", "ingredient"],
                how="left",
            )
        else:
            inv_actions["peak_month"] = np.nan
            inv_actions["peak_forecast_qty"] = np.nan

        recommended_reorder = (
            inv_actions["recommended_reorder"].astype(bool)
            if "recommended_reorder" in inv_actions.columns
            else pd.Series(False, index=inv_actions.index)
        )
        recommended_qty = (
            pd.to_numeric(inv_actions["recommended_qty"], errors="coerce").fillna(0.0)
            if "recommended_qty" in inv_actions.columns
            else pd.Series(0.0, index=inv_actions.index)
        )

        inv_actions["priority"] = np.where(
            recommended_reorder & (recommended_qty > 0),
            "Alta",
            "Media",
        )
        inv_actions["action"] = np.where(
            inv_actions["priority"] == "Alta",
            "Reordenar de inmediato y validar proveedor alterno.",
            "Monitorear consumo y ajustar punto de reorden semanalmente.",
        )
        inv_actions["waste_prevention"] = (
            "Ajustar tamaño de lote y rotación FEFO para reducir merma."
        )

        inventory_actions = inv_actions[
            [
                "branch_id",
                "ingredient",
                "current_stock",
                "reorder_point",
                "recommended_qty",
                "peak_month",
                "peak_forecast_qty",
                "priority",
                "action",
                "waste_prevention",
            ]
        ].copy()
        _save_csv(
            inventory_actions,
            outputs_tables / "recommendations_inventory_actions.csv",
            tracker,
            module,
        )
        outputs["recommendations_inventory_actions"] = inventory_actions

    if not outputs:
        logger.warning(
            "No se generaron recomendaciones por falta de datos aguas arriba."
        )
    return outputs
