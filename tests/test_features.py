from __future__ import annotations

import pandas as pd

from src.features.build_features import build_features


def test_build_features_outputs_expected_tables():
    sales = pd.DataFrame(
        {
            "ticket_id": ["T1", "T2"],
            "date": ["2025-01-01", "2025-01-01"],
            "time": ["13:00", "14:00"],
            "hour": [13, 14],
            "daypart": ["Comida", "Comida"],
            "year_month": ["2025-01", "2025-01"],
            "branch_id": ["S1", "S1"],
            "branch_name": ["Centro", "Centro"],
            "city": ["CDMX", "CDMX"],
            "quantity": [1, 2],
            "total_sale": [100, 300],
            "ingredient_cost": [30, 90],
            "gross_margin": [70, 210],
            "tip": [10, 20],
        }
    )
    branches = pd.DataFrame(
        {
            "branch_id": ["S1"],
            "socioeconomic_level": ["Alto"],
            "capacity_people": [100],
            "num_employees": [20],
            "operational_cost_total": [10000],
            "city": ["CDMX"],
        }
    )
    digital = pd.DataFrame(
        {
            "branch_id": ["S1"],
            "date": ["2025-01-01"],
            "sentiment": ["positivo"],
            "engagement": [100],
            "conversion": [True],
        }
    )
    customers = pd.DataFrame(
        {
            "customer_id": ["C1"],
            "last_visit": ["2025-01-01"],
            "visits_last_year": [5],
            "estimated_total_spend": [1200],
            "avg_spend": [240],
            "loyalty_member": [True],
        }
    )

    settings = {"runtime": {"use_polars": False}}

    class DummyLogger:
        def info(self, *args, **kwargs): ...
        def warning(self, *args, **kwargs): ...

    outputs = build_features(
        {
            "sales": sales,
            "branches": branches,
            "digital": digital,
            "customers": customers,
        },
        settings=settings,
        logger=DummyLogger(),
    )
    assert "analytics_branch_day_hour" in outputs
    assert "analytics_customer_proxy" in outputs
    assert len(outputs["analytics_branch_day_hour"]) == 2
    assert len(outputs["analytics_customer_proxy"]) == 1
