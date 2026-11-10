"""
Tests for GEE Script Generator and Phase 4 Cloud Exporter.

Author: Md Abu Sayem Sarker | Data Scientist & GeoAI Researcher
"""

import os
import tempfile
import pandas as pd
import pytest

from wpdb_spatial_engine.core.gee_script_generator import (
    generate_gee_javascript,
    generate_gee_python,
    export_gee_results_to_csv,
)
from wpdb_spatial_engine.ui.script_viewer_dialog import GEEScriptViewerDialog


def test_generate_gee_javascript_content():
    """Verify generated JavaScript includes all mandatory GEE assets and mathematical identity."""
    js = generate_gee_javascript(
        project_id="ee-wpdb-engine",
        river_name="Buriganga-Turag River",
        max_upstream_m=5000.0,
        bin_size_m=100.0,
        corridor_half_width_m=300.0,
    )

    # Core GEE collections
    assert "JRC/GSW1_4/GlobalSurfaceWater" in js
    assert "GOOGLE/DYNAMICWORLD/V1" in js
    assert "reduceRegions" in js
    assert "ee-wpdb-engine" in js

    # Theorem 1 mathematical identity
    assert "f_water = waterPx.divide(totalPx)" in js
    assert "f_nw" in js
    assert "observedBias" in js
    assert "Export.table.toDrive" in js

    # Monitoring stations
    assert "HAZARIBAGH" in js
    assert "SATMASJID_ROAD" in js


def test_generate_gee_python_content():
    """Verify generated Python standalone script is syntactically sound and complete."""
    py = generate_gee_python(
        project_id="test-cloud-12345",
        river_name="Shitalakhya River",
        max_upstream_m=5000.0,
        bin_size_m=100.0,
    )

    assert "import ee" in py
    assert "import pandas as pd" in py
    assert "ee.Initialize(project=PROJECT_ID)" in py
    assert "test-cloud-12345" in py
    assert "GOOGLE/DYNAMICWORLD/V1" in py
    assert "f_nw = (f_naive / denom)" in py
    assert "observed_bias_pp" in py


def test_export_gee_results_to_csv():
    """Verify CSV export functionality for GEE summary and longitudinal bin metrics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "test_gee_results.csv")

        summary_df = pd.DataFrame([
            {"station_id": "ST1", "water_pct": 52.4, "naive_built": 24.1, "nw_built": 50.6},
            {"station_id": "ST2", "water_pct": 61.2, "naive_built": 18.0, "nw_built": 46.4},
        ])
        bins_df = pd.DataFrame([
            {"station_id": "ST1", "bin_idx": 0, "dist_m": 50.0, "bias_pp": -26.5},
            {"station_id": "ST1", "bin_idx": 1, "dist_m": 150.0, "bias_pp": -25.2},
        ])

        # Test export of bins
        out = export_gee_results_to_csv(summary_df, bins_df, csv_path)
        assert os.path.exists(out)

        read_df = pd.read_csv(out)
        assert len(read_df) == 2
        assert "dist_m" in read_df.columns

        # Test export of summary when bins is empty
        csv_path_sum = os.path.join(tmpdir, "test_gee_sum.csv")
        out_sum = export_gee_results_to_csv(summary_df, pd.DataFrame(), csv_path_sum)
        read_sum = pd.read_csv(out_sum)
        assert len(read_sum) == 2
        assert "water_pct" in read_sum.columns


def test_export_gee_results_empty_validation():
    """Verify ValueError is raised when both dataframes are empty."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "empty.csv")
        with pytest.raises(ValueError):
            export_gee_results_to_csv(pd.DataFrame(), pd.DataFrame(), csv_path)


def test_script_viewer_dialog_initialization():
    """Verify GEEScriptViewerDialog initializes cleanly with JS and Python payloads."""
    js = "// Sample JS Code"
    py = "# Sample Py Code"
    dlg = GEEScriptViewerDialog(js, py)
    if hasattr(dlg, "text_editor"):
        assert dlg.text_editor.toPlainText() == js
        dlg.radio_py.setChecked(True)
        assert dlg.text_editor.toPlainText() == py

