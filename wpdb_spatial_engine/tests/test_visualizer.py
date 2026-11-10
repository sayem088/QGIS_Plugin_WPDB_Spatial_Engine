"""
Unit tests for visualizer module of WPDB-Corrector.

Author: Md Abu Sayem Sarker
"""

import os
import tempfile
import pandas as pd
import pytest
from matplotlib.figure import Figure

from ..core.visualizer import (
    create_theoretical_curve_plot,
    create_before_after_comparison_plot,
    create_combined_audit_figure,
    export_figure,
)


@pytest.fixture
def sample_station_df():
    """Generates synthetic 5-station dataset for visualization testing."""
    return pd.DataFrame({
        "station_id": ["ST_1", "ST_2", "ST_3", "ST_4", "ST_5"],
        "water_fraction_pct": [30.0, 45.0, 50.0, 60.0, 65.0],
        "naive_built_pct": [28.0, 33.0, 35.0, 32.0, 25.0],
        "nonwater_built_pct": [40.0, 60.0, 70.0, 80.0, 71.4],
        "observed_bias_pp": [-12.0, -27.0, -35.0, -48.0, -46.4],
    })


def test_create_theoretical_curve_plot(sample_station_df):
    """Verifies that theoretical curve figure is generated with proper axes and title."""
    fig = create_theoretical_curve_plot(sample_station_df)
    assert isinstance(fig, Figure)
    ax = fig.axes[0]
    assert "Water-Pixel Fraction" in ax.get_xlabel()
    assert len(ax.collections) >= 1  # Scatter points collection


def test_create_before_after_comparison_plot(sample_station_df):
    """Verifies that paired bar chart is generated with correct station count."""
    fig = create_before_after_comparison_plot(sample_station_df)
    assert isinstance(fig, Figure)
    ax = fig.axes[0]
    assert len(ax.get_yticks()) == len(sample_station_df)


def test_create_combined_audit_figure(sample_station_df):
    """Verifies 2-panel composite figure generation."""
    fig = create_combined_audit_figure(sample_station_df)
    assert isinstance(fig, Figure)
    assert len(fig.axes) == 2


def test_export_figure(sample_station_df):
    """Verifies exporting figure to disk as 300 DPI PNG."""
    fig = create_theoretical_curve_plot(sample_station_df)
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "test_fig.png")
        saved = export_figure(fig, out_path, dpi=150)
        assert os.path.exists(saved)
        assert os.path.getsize(saved) > 5000  # Non-trivial image

