from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _sentiment_to_score(series: pd.Series) -> pd.Series:
    mapping = {"positivo": 1.0, "neutro": 0.0, "negativo": -1.0}
    return series.astype(str).str.lower().map(mapping).fillna(0.0)


def _build_branch_day_hour_pandas(sales: pd.DataFrame) -> pd.DataFrame:
    work = sales.copy()
    if "date" in work and not pd.api.types.is_datetime64_any_dtype(work["date"]):
        work["date"] = pd.to_datetime(work["date"], errors="coerce")

    for col in ["total_sale", "quantity", "ingredient_cost", "gross_margin", "tip"]:
        if col not in work:
            work[col] = 0.0
        work[col] = pd.to_numeric(work[col], errors="coerce").fillna(0.0)

    if "ticket_id" not in work:
        work["ticket_id"] = np.arange(len(work)).astype(str)
    if "hour" not in work:
        work["hour"] = np.nan
    if "daypart" not in work:
        work["daypart"] = "Sin dato"
    if "payment_method" not in work:
        work["payment_method"] = "Sin dato"
    if "city" not in work:
        work["city"] = "Sin dato"
    if "year_month" not in work and "date" in work:
        work["year_month"] = work["date"].dt.to_period("M").astype(str)

    grouped = (
        work.groupby(
            [
                "branch_id",
                "branch_name",
                "city",
                "date",
                "year_month",
                "hour",
                "daypart",
            ],
            dropna=False,
        )
        .agg(
            tickets=("ticket_id", "nunique"),
            total_quantity=("quantity", "sum"),
            revenue=("total_sale", "sum"),
            ingredient_cost=("ingredient_cost", "sum"),
            gross_margin=("gross_margin", "sum"),
            tips=("tip", "sum"),
        )
        .reset_index()
    )
    grouped["avg_ticket"] = grouped["revenue"] / grouped["tickets"].replace(0, np.nan)
    grouped["avg_ticket"] = grouped["avg_ticket"].fillna(0.0)
    return grouped


def _build_branch_day_hour_polars(sales: pd.DataFrame, logger) -> pd.DataFrame:
    try:
        import polars as pl
    except Exception as exc:
        logger.warning(
            "POLARS=1 activo, pero polars no está disponible: %s. Se usa pandas.", exc
        )
        return _build_branch_day_hour_pandas(sales)

    work = sales.copy()
    if "date" in work and not pd.api.types.is_datetime64_any_dtype(work["date"]):
        work["date"] = pd.to_datetime(work["date"], errors="coerce")

    for col in ["total_sale", "quantity", "ingredient_cost", "gross_margin", "tip"]:
        if col not in work:
            work[col] = 0.0
        work[col] = pd.to_numeric(work[col], errors="coerce").fillna(0.0)

    if "ticket_id" not in work:
        work["ticket_id"] = np.arange(len(work)).astype(str)
    if "hour" not in work:
        work["hour"] = np.nan
    if "daypart" not in work:
        work["daypart"] = "Sin dato"
    if "payment_method" not in work:
        work["payment_method"] = "Sin dato"
    if "city" not in work:
        work["city"] = "Sin dato"
    if "year_month" not in work and "date" in work:
        work["year_month"] = work["date"].dt.to_period("M").astype(str)

    pl_df = pl.from_pandas(work)
    grouped = (
        pl_df.group_by(
            [
                "branch_id",
                "branch_name",
                "city",
                "date",
                "year_month",
                "hour",
                "daypart",
            ]
        )
        .agg(
            pl.col("ticket_id").n_unique().alias("tickets"),
            pl.col("quantity").sum().alias("total_quantity"),
            pl.col("total_sale").sum().alias("revenue"),
            pl.col("ingredient_cost").sum().alias("ingredient_cost"),
            pl.col("gross_margin").sum().alias("gross_margin"),
            pl.col("tip").sum().alias("tips"),
        )
        .with_columns(
            (pl.col("revenue") / pl.col("tickets"))
            .fill_nan(0.0)
            .fill_null(0.0)
            .alias("avg_ticket")
        )
        .to_pandas()
    )
    return grouped


def build_branch_day_hour_table(
    sales: pd.DataFrame,
    branches: pd.DataFrame,
    digital: pd.DataFrame,
    *,
    use_polars: bool,
    logger,
) -> pd.DataFrame:
    if sales.empty:
        return pd.DataFrame()

    base = (
        _build_branch_day_hour_polars(sales, logger)
        if use_polars
        else _build_branch_day_hour_pandas(sales)
    )

    branch_dim_cols = [
        "branch_id",
        "socioeconomic_level",
        "capacity_people",
        "num_employees",
        "operational_cost_total",
        "city",
    ]
    existing_cols = [col for col in branch_dim_cols if col in branches.columns]
    if existing_cols:
        branch_dim = branches[existing_cols].drop_duplicates(subset=["branch_id"])
        base = base.merge(
            branch_dim, on="branch_id", how="left", suffixes=("", "_branch")
        )
        if "city_branch" in base.columns:
            base["city"] = base["city"].fillna(base["city_branch"])
            base = base.drop(columns=["city_branch"])

    if not digital.empty and {"branch_id", "date", "sentiment"}.issubset(
        digital.columns
    ):
        digital_work = digital.copy()
        digital_work["date"] = pd.to_datetime(digital_work["date"], errors="coerce")
        digital_work["sentiment_score"] = _sentiment_to_score(digital_work["sentiment"])
        if "conversion" in digital_work:
            digital_work["conversion_num"] = digital_work["conversion"].astype(float)
        else:
            digital_work["conversion_num"] = np.nan
        if "engagement" not in digital_work:
            digital_work["engagement"] = 0.0

        digital_daily = (
            digital_work.groupby(["branch_id", "date"], dropna=False)
            .agg(
                digital_engagement=("engagement", "sum"),
                digital_sentiment_score=("sentiment_score", "mean"),
                digital_conversion_rate=("conversion_num", "mean"),
            )
            .reset_index()
        )
        base = base.merge(digital_daily, on=["branch_id", "date"], how="left")

    for col in [
        "digital_engagement",
        "digital_sentiment_score",
        "digital_conversion_rate",
    ]:
        if col not in base:
            base[col] = 0.0
        base[col] = base[col].fillna(0.0)

    return base


def build_customer_proxy_table(
    customers: pd.DataFrame, reference_date: pd.Timestamp
) -> pd.DataFrame:
    if customers.empty:
        return pd.DataFrame()

    work = customers.copy()
    if "last_visit" in work:
        work["last_visit"] = pd.to_datetime(work["last_visit"], errors="coerce")
    else:
        work["last_visit"] = pd.NaT

    if pd.isna(reference_date):
        reference_date = pd.Timestamp.utcnow().normalize()

    if "estimated_total_spend" not in work:
        work["estimated_total_spend"] = np.nan
    if "avg_spend" not in work:
        work["avg_spend"] = np.nan
    if "visits_last_year" not in work:
        work["visits_last_year"] = 0
    if "loyalty_points" not in work:
        work["loyalty_points"] = np.nan
    if "satisfaction_score" not in work:
        work["satisfaction_score"] = np.nan
    if "nps_score" not in work:
        work["nps_score"] = np.nan

    work["frequency"] = pd.to_numeric(work["visits_last_year"], errors="coerce").fillna(
        0.0
    )
    monetary = pd.to_numeric(work["estimated_total_spend"], errors="coerce")
    fallback_monetary = (
        pd.to_numeric(work["avg_spend"], errors="coerce").fillna(0.0)
        * work["frequency"]
    )
    work["monetary"] = monetary.fillna(fallback_monetary)

    work["recency_days"] = (reference_date - work["last_visit"]).dt.days
    work["recency_days"] = (
        work["recency_days"].fillna(work["recency_days"].median()).clip(lower=0)
    )

    cols = [
        "customer_id",
        "name",
        "preferred_branch",
        "preferred_city",
        "customer_category",
        "acquisition_channel",
        "loyalty_member",
        "accepts_promotions",
        "loyalty_points",
        "satisfaction_score",
        "nps_score",
        "recency_days",
        "frequency",
        "monetary",
    ]
    existing_cols = [col for col in cols if col in work.columns]
    return work[existing_cols].copy()


def build_features(
    clean_tables: dict[str, pd.DataFrame],
    *,
    settings: dict[str, Any],
    logger,
) -> dict[str, pd.DataFrame]:
    runtime = settings.get("runtime", {})
    use_polars = bool(runtime.get("use_polars", False))

    sales = clean_tables.get("sales", pd.DataFrame())
    branches = clean_tables.get("branches", pd.DataFrame())
    customers = clean_tables.get("customers", pd.DataFrame())
    digital = clean_tables.get("digital", pd.DataFrame())

    reference_date = (
        pd.to_datetime(sales["date"], errors="coerce").max()
        if "date" in sales
        else pd.NaT
    )
    branch_day_hour = build_branch_day_hour_table(
        sales=sales,
        branches=branches,
        digital=digital,
        use_polars=use_polars,
        logger=logger,
    )
    customer_proxy = build_customer_proxy_table(
        customers, reference_date=reference_date
    )

    return {
        "analytics_branch_day_hour": branch_day_hour,
        "analytics_customer_proxy": customer_proxy,
    }
