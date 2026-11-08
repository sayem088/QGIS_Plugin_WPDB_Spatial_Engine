"""
Automated unit tests for WPDB Table Corrector against Dhaka 11-station ground-truth.
Author: Md Abu Sayem Sarker
"""

import os
import pytest
import pandas as pd
from wpdb_spatial_engine.core.table_corrector import WPDBTableCorrector

SAMPLE_CSV = os.path.join(
    os.path.dirname(__file__), "..", "sample_data", "sample_dhaka_11_stations.csv"
)


def test_table_corrector_ground_truth_dhaka():
    """Validates the table corrector against IEEE CSDE 2026 Table 1 values."""
    assert os.path.exists(SAMPLE_CSV), f"Sample CSV not found at {SAMPLE_CSV}"

    corrector = WPDBTableCorrector.from_csv(SAMPLE_CSV)
    detected = corrector.detect_columns()
    assert detected["water"] == "water_fraction_pct"
    assert detected["target"] == "naive_built_pct"

    df_res = corrector.process(
        water_col="water_fraction_pct",
        target_col="naive_built_pct",
        target_name="built",
        is_percentage=True
    )

    # Check Hazaribagh restoration
    hazaribagh = df_res[df_res["station_id"] == "HAZARIBAGH"].iloc[0]
    assert abs(hazaribagh["built_corrected_pct"] - 88.80) < 0.1
    assert abs(hazaribagh["wpdb_bias_pp"] - (-55.14)) < 0.1
    assert hazaribagh["identity_residual_pp"] <= 0.01

    # Check Satmasjid Road peak distortion
    satmasjid = df_res[df_res["station_id"] == "SATMASJID_ROAD"].iloc[0]
    assert abs(satmasjid["built_corrected_pct"] - 88.12) < 0.1
    assert abs(satmasjid["wpdb_bias_pp"] - (-56.34)) < 0.1
    assert satmasjid["identity_residual_pp"] <= 0.01

    # Check Mirpur Bridge
    mirpur = df_res[df_res["station_id"] == "MIRPUR_BRIDGE"].iloc[0]
    assert abs(mirpur["built_corrected_pct"] - 63.22) < 0.1
    assert abs(mirpur["wpdb_bias_pp"] - (-27.19)) < 0.1
    assert mirpur["identity_residual_pp"] <= 0.01

    # Check overall summary statistics
    stats = corrector.summary_stats
    assert stats["n_stations"] == 11
    # Average bias must be ~ -46.93 pp
    assert abs(stats["mean_bias"] - (-46.93)) < 0.2
    # Maximum residual across all 11 stations must be <= 0.01 pp
    assert stats["max_residual"] <= 0.01

    # Check text report
    report = corrector.get_summary_report()
    assert "WATER-PIXEL DILUTION BIAS (WPDB) CORRECTION REPORT" in report
    assert "VERIFIED (|ε| <= 0.01)" in report


def test_table_corrector_missing_columns():
    """Verify clean error when required columns are absent."""
    df_dummy = pd.DataFrame({"colA": [1, 2], "colB": [3, 4]})
    corrector = WPDBTableCorrector(df_dummy)
    with pytest.raises(ValueError):
        corrector.process(water_col="non_existent", target_col="colA")


def test_table_save_csv(tmp_path):
    """Verify corrected table can be saved to disk."""
    corrector = WPDBTableCorrector.from_csv(SAMPLE_CSV)
    corrector.process(water_col="water_fraction_pct", target_col="naive_built_pct")
    out_file = str(tmp_path / "output_corrected.csv")
    corrector.save_csv(out_file)
    assert os.path.exists(out_file)
    df_saved = pd.read_csv(out_file)
    assert "built_corrected_pct" in df_saved.columns
    assert "wpdb_bias_pp" in df_saved.columns

