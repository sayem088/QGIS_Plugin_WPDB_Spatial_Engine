"""
Automated unit test for QGIS ZIP package structure and compliance.
Author: Md Abu Sayem Sarker
"""

import os
import zipfile
import pytest

DIST_ZIP = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dist", "wpdb_spatial_engine.zip"))


def test_dist_zip_package():
    """Verify that the distributable ZIP package exists and contains all required QGIS components."""
    assert os.path.exists(DIST_ZIP), f"ZIP package missing at {DIST_ZIP}. Run build_package.py first."

    with zipfile.ZipFile(DIST_ZIP, "r") as zf:
        names = zf.namelist()

        # All entries must start with wpdb_spatial_engine/
        for n in names:
            assert n.startswith("wpdb_spatial_engine/"), f"Non-compliant path in archive: {n}"

        # Core required files
        assert "wpdb_spatial_engine/metadata.txt" in names
        assert "wpdb_spatial_engine/icon.png" in names
        assert "wpdb_spatial_engine/logo.png" in names
        assert "wpdb_spatial_engine/__init__.py" in names
        assert "wpdb_spatial_engine/plugin.py" in names
        assert "wpdb_spatial_engine/core/formula.py" in names
        assert "wpdb_spatial_engine/core/table_corrector.py" in names
        assert "wpdb_spatial_engine/core/spatial_corrector.py" in names
        assert "wpdb_spatial_engine/core/corridor_engine.py" in names
        assert "wpdb_spatial_engine/core/gee_worker.py" in names
        assert "wpdb_spatial_engine/core/gee_script_generator.py" in names
        assert "wpdb_spatial_engine/ui/wpdb_dialog_base.ui" in names
        assert "wpdb_spatial_engine/ui/wpdb_dialog.py" in names
        assert "wpdb_spatial_engine/ui/style.qss" in names
        assert "wpdb_spatial_engine/sample_data/sample_dhaka_11_stations.csv" in names

        # No pycache or git files
        for n in names:
            assert "__pycache__" not in n
            assert not n.endswith(".pyc")
