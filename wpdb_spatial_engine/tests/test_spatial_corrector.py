"""
Automated unit tests for spatial buffer and raster masking engine.
Author: Md Abu Sayem Sarker
"""

import numpy as np
import pytest
from wpdb_spatial_engine.core.spatial_corrector import (
    compute_buffer_metrics,
    extract_from_raster_arrays,
    WPDBSpatialProcessor,
)


def test_compute_buffer_metrics():
    # 5,000 water, 3,500 built, 10,000 total -> 5,000 nonwater
    res = compute_buffer_metrics(water_pixels=5000, target_pixels=3500, total_pixels=10000)
    assert res["f_water_pct"] == 50.0
    assert res["f_naive_pct"] == 35.0
    assert res["f_corrected_pct"] == 70.0
    assert res["wpdb_bias_pp"] == -35.0
    assert res["residual_pp"] <= 1e-10


def test_extract_from_synthetic_raster():
    """Simulate a 100x100 raster scene with water and built-up land."""
    shape = (100, 100)
    water_arr = np.zeros(shape, dtype=np.uint8)
    lulc_arr = np.zeros(shape, dtype=np.uint8)

    # Set top half (5,000 pixels) as water
    water_arr[:50, :] = 1
    lulc_arr[:50, :] = 0  # water label

    # In bottom half (5,000 non-water pixels), set 3,500 as built-up (class 1)
    lulc_arr[50:85, :] = 1  # 35 rows * 100 cols = 3,500 built pixels
    # Remaining 1,500 pixels are other vegetation (class 2)
    lulc_arr[85:, :] = 2

    res = extract_from_raster_arrays(
        water_array=water_arr,
        lulc_array=lulc_arr,
        target_val=1,
        water_val=1
    )

    assert res["a_total"] == 10000
    assert res["a_water"] == 5000
    assert res["a_target"] == 3500
    assert res["a_nonwater"] == 5000
    assert res["f_water_pct"] == 50.0
    assert res["f_naive_pct"] == 35.0
    assert res["f_corrected_pct"] == 70.0
    assert res["wpdb_bias_pp"] == -35.0
    assert res["residual_pp"] <= 1e-10


def test_hazaribagh_synthetic_simulation():
    """Simulate Hazaribagh's 62.1% water and 33.66% naive built-up proportion."""
    shape = (100, 100)
    water_arr = np.zeros(shape, dtype=np.uint8)
    lulc_arr = np.zeros(shape, dtype=np.uint8)

    # 6,210 water pixels
    water_flat = water_arr.ravel()
    water_flat[:6210] = 1

    # 3,366 built-up pixels
    lulc_flat = lulc_arr.ravel()
    lulc_flat[6210:6210 + 3366] = 1

    res = extract_from_raster_arrays(
        water_array=water_arr,
        lulc_array=lulc_arr,
        target_val=1,
        water_val=1
    )

    assert abs(res["f_water_pct"] - 62.10) < 1e-6
    assert abs(res["f_naive_pct"] - 33.66) < 1e-6
    # Corrected should be 33.66 / (1 - 0.6210) = 88.81%
    assert abs(res["f_corrected_pct"] - 88.81) < 0.05
    assert abs(res["wpdb_bias_pp"] - (-55.15)) < 0.05
    assert res["residual_pp"] <= 1e-10


def test_circular_buffer_mask():
    """Test raster extraction with an explicit circular buffer mask."""
    shape = (100, 100)
    water_arr = np.zeros(shape, dtype=np.uint8)
    lulc_arr = np.zeros(shape, dtype=np.uint8)

    # Left half is water
    water_arr[:, :50] = 1
    # Right half is built
    lulc_arr[:, 50:] = 1

    # Create a circular mask centered at (50, 50) with radius 20
    y, x = np.ogrid[:100, :100]
    circ_mask = ((x - 50) ** 2 + (y - 50) ** 2) <= (20 ** 2)

    res = extract_from_raster_arrays(
        water_array=water_arr,
        lulc_array=lulc_arr,
        target_val=1,
        water_val=1,
        mask=circ_mask
    )

    # Symmetrical circle split in half by river -> ~50% water, ~50% built-up
    assert abs(res["f_water_pct"] - 50.0) < 3.0
    # True non-water terrestrial density is ~100%
    assert abs(res["f_corrected_pct"] - 100.0) < 5.0
    assert res["residual_pp"] <= 1e-10


def test_spatial_processor_batch():
    """Test batch processing across multiple station masks."""
    shape = (100, 100)
    water_arr = np.zeros(shape, dtype=np.uint8)
    lulc_arr = np.zeros(shape, dtype=np.uint8)

    water_arr[:50, :] = 1
    lulc_arr[50:85, :] = 1

    mask1 = np.ones(shape, dtype=bool)
    mask2 = np.ones(shape, dtype=bool)

    processor = WPDBSpatialProcessor()
    df = processor.process_arrays_batch(
        station_names=["STATION_A", "STATION_B"],
        water_array=water_arr,
        lulc_array=lulc_arr,
        buffer_masks=[mask1, mask2],
        target_val=1,
        water_val=1,
        target_name="built"
    )

    assert len(df) == 2
    assert "nonwater_built_pct" in df.columns
    assert "wpdb_bias_pp" in df.columns
    assert df["nonwater_built_pct"].iloc[0] == 70.0
    assert processor.summary_stats["mean_bias"] == -35.0
