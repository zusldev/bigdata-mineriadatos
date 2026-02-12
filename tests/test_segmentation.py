from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.models.segmentation import run_segmentation


def _sample_customers(n: int = 30) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    return pd.DataFrame(
        {
            "customer_id": [f"C{i:03d}" for i in range(n)],
            "recency_days": rng.integers(1, 120, size=n),
            "frequency": rng.integers(1, 20, size=n),
            "monetary": rng.normal(1200, 300, size=n).clip(100, 3000),
            "loyalty_points": rng.integers(0, 1000, size=n),
            "satisfaction_score": rng.integers(2, 6, size=n),
            "nps_score": rng.integers(1, 11, size=n),
            "loyalty_member": rng.integers(0, 2, size=n).astype(bool),
            "accepts_promotions": rng.integers(0, 2, size=n).astype(bool),
            "customer_category": rng.choice(["VIP", "Frecuente", "Regular"], size=n),
            "preferred_city": rng.choice(["CDMX", "Puebla"], size=n),
            "preferred_branch": rng.choice(["Centro", "Sur"], size=n),
        }
    )


def test_segmentation_reproducible_distribution(tmp_path: Path):
    data = _sample_customers(40)
    settings = {
        "paths": {
            "outputs_tables": str(tmp_path / "tables"),
            "outputs_models": str(tmp_path / "models"),
        }
    }

    class DummyLogger:
        def info(self, *args, **kwargs): ...
        def warning(self, *args, **kwargs): ...

    out_1 = run_segmentation(
        {"analytics_customer_proxy": data},
        settings=settings,
        tracker=None,
        logger=DummyLogger(),
    )
    out_2 = run_segmentation(
        {"analytics_customer_proxy": data},
        settings=settings,
        tracker=None,
        logger=DummyLogger(),
    )

    seg_1 = out_1["customer_segments"]["segment_id"].value_counts().sort_index()
    seg_2 = out_2["customer_segments"]["segment_id"].value_counts().sort_index()
    assert seg_1.equals(seg_2)
    assert not out_1["customer_personas_summary"].empty
