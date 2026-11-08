"""
Unit tests for the River Corridor Extractor and Normalizer engine (Stages B-D).

Author: Md Abu Sayem Sarker | Data Scientist & GeoAI Researcher
"""

import os
import pandas as pd
import pytest
from shapely.geometry import Polygon

from ..core.corridor_engine import RiverCenterline, WPDBFlowCorridorPipeline

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_data"))
BURIGANGA_GEOJSON = os.path.join(SAMPLE_DIR, "buriganga_centerline.geojson")
STATIONS_CSV = os.path.join(SAMPLE_DIR, "buriganga_stations.csv")


@pytest.fixture
def centerline():
    """Loads Buriganga centerline fixture."""
    assert os.path.exists(BURIGANGA_GEOJSON), "Buriganga centerline GeoJSON missing!"
    return RiverCenterline.from_geojson(BURIGANGA_GEOJSON)


def test_centerline_geometry(centerline):
    """Verifies centerline metric length and coordinate count."""
    assert len(centerline.coords) > 100
    # Buriganga centerline is ~31 km
    assert 25000.0 < centerline.total_length_m < 35000.0


def test_station_snapping(centerline):
    """Verifies linear referencing and snapping of Mirpur Bridge."""
    # Mirpur Bridge coords: 23.783754, 90.335107
    snap = centerline.snap_station(lon=90.335107, lat=23.783754)
    assert "snapped_lat" in snap
    assert "snapped_lon" in snap
    assert snap["snap_distance_m"] < 100.0  # Within 100 meters
    assert 2000.0 < snap["along_channel_m"] < 5000.0


def test_corridor_bin_generation(centerline):
    """Verifies that 50 longitudinal bins of 100m are generated for a downstream station."""
    pipeline = WPDBFlowCorridorPipeline(
        centerline=centerline,
        max_upstream_m=5000.0,
        bin_size_m=100.0,
        corridor_width_m=300.0,
        target_class_value=6
    )
    # Hazaribagh is ~13 km along channel, so it can trace a full 5.0 km upstream
    bins = pipeline.generate_station_bins(station_id="HAZARIBAGH", lon=90.357232, lat=23.726392)
    assert len(bins) == 50
    assert bins[0]["bin_index"] == 1
    assert bins[-1]["bin_index"] == 50
    assert isinstance(bins[0]["geometry"], Polygon)


def test_pipeline_execution(centerline):
    """Verifies end-to-end processing across stations with zero residual identity."""
    pipeline = WPDBFlowCorridorPipeline(
        centerline=centerline,
        max_upstream_m=5000.0,
        bin_size_m=100.0,
        corridor_width_m=300.0
    )
    df_st = pd.read_csv(STATIONS_CSV).head(3)
    df_bins, df_summary = pipeline.process_stations_dataframe(df_st)

    assert not df_bins.empty
    assert not df_summary.empty
    assert len(df_summary) == 3

    # Theorem 1 Identity verification on all bins: |observed - predicted| < 1e-4
    residuals = df_bins["residual_pp"].abs()
    assert (residuals < 1e-4).all(), f"Max residual: {residuals.max()}"

