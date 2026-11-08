"""
Unit tests for Google Earth Engine (GEE) Cloud Pipeline Worker.

Author: Md Abu Sayem Sarker | Data Scientist & GeoAI Researcher
"""

import os
import pytest

from ..core.gee_worker import GEECloudPipelineWorker


def test_gee_worker_instantiation():
    """Verifies that GEECloudPipelineWorker instantiates with default parameters."""
    worker = GEECloudPipelineWorker(
        project_id="ee-wpdb-engine",
        river_preset="Buriganga-Turag River (31.1 km Centerline)",
        target_class=6
    )
    assert worker.project_id == "ee-wpdb-engine"
    assert worker.target_class == 6
    assert worker.max_upstream_m == 5000.0


def test_gee_worker_execution():
    """Verifies end-to-end execution of Stages A through D with zero residual."""
    worker = GEECloudPipelineWorker(
        project_id="ee-wpdb-engine",
        river_preset="Buriganga-Turag River (31.1 km Centerline)",
        target_class=6
    )

    progress_history = []
    logs_history = []
    completion_payload = {}

    worker.progress_updated.connect(lambda val: progress_history.append(val))
    worker.log_emitted.connect(lambda msg: logs_history.append(msg))
    worker.pipeline_completed.connect(lambda ok, msg, data: completion_payload.update({"ok": ok, "data": data}))

    # Execute synchronous run
    worker.run()

    # Verify progress reached 100%
    assert 100 in progress_history
    assert len(logs_history) > 10

    # Verify success status
    assert completion_payload.get("ok") is True
    data = completion_payload.get("data", {})
    assert "summary_df" in data
    assert "bins_df" in data

    # Verify Theorem 1 identity holds across all extracted bins
    bins_df = data["bins_df"]
    assert not bins_df.empty
    max_res = bins_df["residual_pp"].abs().max()
    assert max_res < 1e-4, f"Max residual exceeds tolerance: {max_res}"

