from __future__ import annotations

import unicodedata
from typing import Any

import numpy as np
import pandas as pd


YES_VALUES = {"si", "sí", "yes", "true", "1", "y"}
NO_VALUES = {"no", "false", "0", "n"}


def _normalize_token(value: str) -> str:
    norm = unicodedata.normalize("NFKD", str(value))
    ascii_text = norm.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower().strip()
    return "".join(ch if ch.isalnum() else "_" for ch in ascii_text).strip("_")


def _to_numeric(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace(" ", "", regex=False)
        .replace({"": np.nan, "nan": np.nan, "None": np.nan})
    )
    return pd.to_numeric(cleaned, errors="coerce")


def _to_boolean(series: pd.Series) -> pd.Series:
    def convert(value: Any) -> Any:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return np.nan
        norm = _normalize_token(str(value))
        if norm in YES_VALUES:
            return True
        if norm in NO_VALUES:
            return False
        return np.nan

    return series.map(convert)


def _to_string(series: pd.Series) -> pd.Series:
    """Convierte a string preservando nulos para evitar conflictos de serialización."""
    return series.astype("string")


def _build_rename_map(df: pd.DataFrame, dataset_map: dict[str, Any]) -> dict[str, str]:
    available = {_normalize_token(column): column for column in df.columns}
    rename_map: dict[str, str] = {}
    columns_map = dataset_map.get("columns", {})

    for canonical, aliases in columns_map.items():
        candidates = [canonical, *aliases]
        for candidate in candidates:
            key = _normalize_token(candidate)
            if key in available:
                rename_map[available[key]] = canonical
                break
    return rename_map


def _infer_daypart(hour: float | int | None) -> str:
    if hour is None or pd.isna(hour):
        return "Sin dato"
    h = int(hour)
    if 6 <= h < 12:
        return "Mañana"
    if 12 <= h < 17:
        return "Comida"
    if 17 <= h < 21:
        return "Tarde"
    return "Noche"


def _standardize_columns(df: pd.DataFrame, dataset_map: dict[str, Any]) -> pd.DataFrame:
    rename_map = _build_rename_map(df, dataset_map)
    standardized = df.rename(columns=rename_map).copy()
    # Normaliza columnas no mapeadas a snake_case para trazabilidad.
    standardized.columns = [_normalize_token(column) for column in standardized.columns]
    standardized = standardized.loc[:, ~standardized.columns.duplicated()]
    return standardized


def clean_dataset(
    dataset_name: str, df: pd.DataFrame, dataset_map: dict[str, Any], logger
) -> pd.DataFrame:
    clean_df = _standardize_columns(df, dataset_map)

    # Strings vacíos -> NaN para un manejo consistente.
    object_cols = clean_df.select_dtypes(include=["object", "string"]).columns
    for col in object_cols:
        series_str = clean_df[col].astype("string")
        blank_mask = series_str.str.fullmatch(r"\s*", na=False)
        clean_df[col] = series_str.mask(blank_mask, pd.NA)

    if dataset_name == "sales":
        for numeric_col in [
            "unit_price",
            "quantity",
            "total_sale",
            "ingredient_cost",
            "gross_margin",
            "tip",
            "total_with_tip",
        ]:
            if numeric_col in clean_df:
                clean_df[numeric_col] = _to_numeric(clean_df[numeric_col])

        if "date" in clean_df:
            clean_df["date"] = pd.to_datetime(clean_df["date"], errors="coerce")
        if "time" in clean_df:
            clean_df["time"] = clean_df["time"].astype(str).str.slice(0, 5)
            parsed_time = pd.to_datetime(
                clean_df["time"], format="%H:%M", errors="coerce"
            )
            clean_df["hour"] = parsed_time.dt.hour
        else:
            clean_df["hour"] = np.nan

        if "total_sale" not in clean_df and {"unit_price", "quantity"}.issubset(
            clean_df.columns
        ):
            clean_df["total_sale"] = clean_df["unit_price"] * clean_df["quantity"]
        if "total_sale" in clean_df:
            clean_df["total_sale"] = clean_df["total_sale"].fillna(
                clean_df.get("unit_price", 0) * clean_df.get("quantity", 0)
            )

        if "ingredient_cost" in clean_df:
            category_avg_cost = clean_df.groupby("category", dropna=False)[
                "ingredient_cost"
            ].transform("mean")
            clean_df["ingredient_cost"] = clean_df["ingredient_cost"].fillna(
                category_avg_cost
            )
            clean_df["ingredient_cost"] = clean_df["ingredient_cost"].fillna(
                clean_df["total_sale"] * 0.35
            )

        if "gross_margin" not in clean_df and {
            "total_sale",
            "ingredient_cost",
        }.issubset(clean_df.columns):
            clean_df["gross_margin"] = (
                clean_df["total_sale"] - clean_df["ingredient_cost"]
            )
        elif {"total_sale", "ingredient_cost", "gross_margin"}.issubset(
            clean_df.columns
        ):
            clean_df["gross_margin"] = clean_df["gross_margin"].fillna(
                clean_df["total_sale"] - clean_df["ingredient_cost"]
            )

        if "payment_method" in clean_df:
            clean_df["payment_method"] = (
                clean_df["payment_method"].astype(str).str.strip()
            )

        if "date" in clean_df:
            clean_df["year_month"] = clean_df["date"].dt.to_period("M").astype(str)
            if "month" not in clean_df:
                clean_df["month"] = clean_df["date"].dt.month_name()
            if "day_of_week" not in clean_df:
                clean_df["day_of_week"] = clean_df["date"].dt.day_name()
        clean_df["daypart"] = clean_df["hour"].apply(_infer_daypart)

    elif dataset_name == "customers":
        for numeric_col in [
            "visits_last_year",
            "avg_spend",
            "estimated_total_spend",
            "loyalty_points",
            "satisfaction_score",
            "nps_score",
        ]:
            if numeric_col in clean_df:
                clean_df[numeric_col] = _to_numeric(clean_df[numeric_col])
        for date_col in ["register_date", "last_visit"]:
            if date_col in clean_df:
                clean_df[date_col] = pd.to_datetime(clean_df[date_col], errors="coerce")
        for bool_col in ["loyalty_member", "accepts_promotions"]:
            if bool_col in clean_df:
                clean_df[bool_col] = _to_boolean(clean_df[bool_col])

        if "estimated_total_spend" in clean_df and {
            "avg_spend",
            "visits_last_year",
        }.issubset(clean_df.columns):
            calc_total = clean_df["avg_spend"] * clean_df["visits_last_year"]
            clean_df["estimated_total_spend"] = clean_df[
                "estimated_total_spend"
            ].fillna(calc_total)

    elif dataset_name == "branches":
        for numeric_col in [
            "capacity_people",
            "num_employees",
            "rent_monthly",
            "utilities_monthly",
            "payroll_monthly",
            "operational_cost_total",
            "avg_monthly_income",
            "operating_margin",
            "profitability_pct",
            "nearby_competitors",
            "opening_year",
            "years_operating",
        ]:
            if numeric_col in clean_df:
                clean_df[numeric_col] = _to_numeric(clean_df[numeric_col])

        # Evita mezcla int/str en campos textuales (ej. postal_code) que rompe parquet.
        for text_col in [
            "branch_id",
            "branch_name",
            "city",
            "address",
            "postal_code",
            "zone",
            "socioeconomic_level",
            "open_time",
            "close_time",
            "peak_hours",
            "nearby_poi",
            "parking",
        ]:
            if text_col in clean_df:
                clean_df[text_col] = _to_string(clean_df[text_col])

    elif dataset_name == "inventory":
        for numeric_col in [
            "qty_ordered",
            "unit_price",
            "total_purchase_cost",
            "qty_wasted",
            "waste_cost",
            "waste_pct",
            "current_stock",
            "min_stock",
            "shelf_life_days",
        ]:
            if numeric_col in clean_df:
                clean_df[numeric_col] = _to_numeric(clean_df[numeric_col])
        if "date" in clean_df:
            clean_df["date"] = pd.to_datetime(clean_df["date"], errors="coerce")
            clean_df["year_month"] = clean_df["date"].dt.to_period("M").astype(str)
        if "needs_reorder" in clean_df:
            clean_df["needs_reorder"] = _to_boolean(clean_df["needs_reorder"])
        if "waste_pct" in clean_df:
            clean_df["waste_pct"] = clean_df["waste_pct"].clip(lower=0)

    elif dataset_name == "digital":
        for numeric_col in [
            "rating",
            "reach",
            "engagement",
            "engagement_rate",
            "campaign_cost",
            "response_hours",
        ]:
            if numeric_col in clean_df:
                clean_df[numeric_col] = _to_numeric(clean_df[numeric_col])
        if "date" in clean_df:
            clean_df["date"] = pd.to_datetime(clean_df["date"], errors="coerce")
            clean_df["year_month"] = clean_df["date"].dt.to_period("M").astype(str)
        for bool_col in ["conversion", "responded"]:
            if bool_col in clean_df:
                clean_df[bool_col] = _to_boolean(clean_df[bool_col])
        if "sentiment" in clean_df:
            clean_df["sentiment"] = (
                clean_df["sentiment"].astype(str).str.strip().str.lower()
            )

    clean_df = clean_df.drop_duplicates()
    logger.info(
        "Dataset limpio: %s | filas=%s | columnas=%s",
        dataset_name,
        len(clean_df),
        len(clean_df.columns),
    )
    return clean_df


def clean_datasets(
    raw_tables: dict[str, pd.DataFrame],
    schema_map: dict[str, Any],
    logger,
) -> tuple[dict[str, pd.DataFrame], dict[str, dict[str, Any]]]:
    datasets_map = schema_map.get("datasets", {})
    cleaned: dict[str, pd.DataFrame] = {}
    report: dict[str, dict[str, Any]] = {}

    for dataset_name, df in raw_tables.items():
        dataset_cfg = datasets_map.get(dataset_name, {})
        cleaned_df = clean_dataset(dataset_name, df, dataset_cfg, logger=logger)
        cleaned[dataset_name] = cleaned_df
        report[dataset_name] = {
            "rows": len(cleaned_df),
            "columns": cleaned_df.columns.tolist(),
            "missing_pct": (
                (cleaned_df.isna().mean() * 100).round(2).to_dict()
                if len(cleaned_df)
                else {}
            ),
        }

    return cleaned, report
