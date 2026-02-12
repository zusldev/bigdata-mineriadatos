from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.utils.io import ArtifactTracker, save_pickle


def _save_csv(
    df: pd.DataFrame, path: Path, tracker: ArtifactTracker | None, module: str
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    if tracker:
        tracker.register(path, "table", module, "csv", len(df))


def _label_persona(row: pd.Series) -> str:
    recency = row.get("recency_days_mean", np.nan)
    frequency = row.get("frequency_mean", np.nan)
    monetary = row.get("monetary_mean", np.nan)
    loyalty = row.get("loyalty_member_rate", np.nan)

    if np.isfinite(monetary) and np.isfinite(frequency) and np.isfinite(recency):
        if monetary >= row.get("monetary_q75", monetary) and frequency >= row.get(
            "frequency_q75", frequency
        ):
            return "Leales Premium"
        if recency <= row.get("recency_q25", recency) and frequency >= row.get(
            "frequency_q50", frequency
        ):
            return "Frecuentes Recientes"
        if loyalty >= 0.5 and monetary >= row.get("monetary_q50", monetary):
            return "Socios de Valor"
        if recency > row.get("recency_q75", recency) and frequency < row.get(
            "frequency_q50", frequency
        ):
            return "En Riesgo de Churn"
    return "Ocasionales Sensibles a Promoción"


def run_segmentation(
    feature_tables: dict[str, pd.DataFrame],
    *,
    settings: dict[str, Any],
    tracker: ArtifactTracker | None,
    logger,
) -> dict[str, pd.DataFrame]:
    module = "models.segmentation"
    outputs_tables = Path(settings["paths"]["outputs_tables"])
    outputs_models = Path(settings["paths"]["outputs_models"])

    customers = feature_tables.get("analytics_customer_proxy", pd.DataFrame()).copy()
    if customers.empty:
        logger.warning("No hay datos de clientes para segmentación.")
        return {}

    required = {"recency_days", "frequency", "monetary"}
    if not required.issubset(set(customers.columns)):
        logger.warning(
            "Segmentación omitida: faltan columnas RFM proxy (%s).", required
        )
        return {}

    numeric_cols = [
        col
        for col in [
            "recency_days",
            "frequency",
            "monetary",
            "loyalty_points",
            "satisfaction_score",
            "nps_score",
        ]
        if col in customers.columns
    ]
    categorical_cols = [
        col
        for col in ["customer_category", "preferred_city", "preferred_branch"]
        if col in customers.columns
    ]
    bool_cols = [
        col
        for col in ["loyalty_member", "accepts_promotions"]
        if col in customers.columns
    ]

    for col in numeric_cols:
        customers[col] = pd.to_numeric(customers[col], errors="coerce")
        customers[col] = customers[col].fillna(customers[col].median())
    for col in bool_cols:
        customers[col] = customers[col].astype(float).fillna(0.0)
    for col in categorical_cols:
        customers[col] = customers[col].astype(str).fillna("Sin dato")

    feature_cols = numeric_cols + bool_cols + categorical_cols
    model_df = customers[feature_cols].copy()

    transformer = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols + bool_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ],
        remainder="drop",
    )

    X = transformer.fit_transform(model_df)

    n_samples = len(customers)
    candidate_ks = [k for k in range(3, 7) if 1 < k < n_samples]
    if not candidate_ks:
        customers["segment_id"] = 0
        segments = customers.copy()
        summary = pd.DataFrame(
            [
                {
                    "segment_id": 0,
                    "customers": n_samples,
                    "recency_days_mean": customers["recency_days"].mean(),
                    "frequency_mean": customers["frequency"].mean(),
                    "monetary_mean": customers["monetary"].mean(),
                    "loyalty_member_rate": customers.get(
                        "loyalty_member", pd.Series(dtype=float)
                    ).mean(),
                    "persona": "Base General",
                }
            ]
        )
        _save_csv(segments, outputs_tables / "customer_segments.csv", tracker, module)
        _save_csv(
            summary, outputs_tables / "customer_personas_summary.csv", tracker, module
        )
        save_pickle(
            {"kmeans": None, "transformer": transformer, "k": 1},
            outputs_models / "segmentation_kmeans.pkl",
            tracker=tracker,
            module=module,
        )
        return {"customer_segments": segments, "customer_personas_summary": summary}

    best_score = -np.inf
    best_k = candidate_ks[0]
    best_model = None

    for k in candidate_ks:
        model = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = model.fit_predict(X)
        if len(set(labels)) <= 1:
            score = -1.0
        else:
            score = silhouette_score(X, labels)
        if score > best_score:
            best_score = score
            best_k = k
            best_model = model

    if best_model is None:
        best_model = KMeans(n_clusters=3, random_state=42, n_init=20).fit(X)
        best_k = 3
        best_score = -1.0

    labels = best_model.predict(X)
    segments = customers.copy()
    segments["segment_id"] = labels

    summary = (
        segments.groupby("segment_id", dropna=False)
        .agg(
            customers=("segment_id", "count"),
            recency_days_mean=("recency_days", "mean"),
            frequency_mean=("frequency", "mean"),
            monetary_mean=("monetary", "mean"),
            loyalty_member_rate=(
                ("loyalty_member", "mean")
                if "loyalty_member" in segments.columns
                else ("segment_id", "size")
            ),
            promotions_accept_rate=(
                ("accepts_promotions", "mean")
                if "accepts_promotions" in segments.columns
                else ("segment_id", "size")
            ),
        )
        .reset_index()
    )

    summary["recency_q25"] = summary["recency_days_mean"].quantile(0.25)
    summary["recency_q75"] = summary["recency_days_mean"].quantile(0.75)
    summary["frequency_q50"] = summary["frequency_mean"].quantile(0.50)
    summary["frequency_q75"] = summary["frequency_mean"].quantile(0.75)
    summary["monetary_q50"] = summary["monetary_mean"].quantile(0.50)
    summary["monetary_q75"] = summary["monetary_mean"].quantile(0.75)
    summary["persona"] = summary.apply(_label_persona, axis=1)
    summary = summary.drop(
        columns=[
            "recency_q25",
            "recency_q75",
            "frequency_q50",
            "frequency_q75",
            "monetary_q50",
            "monetary_q75",
        ]
    )

    persona_map = summary.set_index("segment_id")["persona"].to_dict()
    segments["persona"] = segments["segment_id"].map(persona_map)

    model_payload = {
        "transformer": transformer,
        "kmeans": best_model,
        "k": best_k,
        "silhouette_score": float(best_score),
        "feature_cols": feature_cols,
    }

    _save_csv(segments, outputs_tables / "customer_segments.csv", tracker, module)
    _save_csv(
        summary, outputs_tables / "customer_personas_summary.csv", tracker, module
    )
    save_pickle(
        model_payload,
        outputs_models / "segmentation_kmeans.pkl",
        tracker=tracker,
        module=module,
    )

    return {
        "customer_segments": segments,
        "customer_personas_summary": summary,
    }
