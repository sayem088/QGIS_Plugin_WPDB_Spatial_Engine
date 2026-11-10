"""
Unit tests for core WPDB mathematical formula and identity.
Author: Md Abu Sayem Sarker
"""

import pytest
import math
from wpdb_spatial_engine.core.formula import (
    calculate_wpdb_correction,
    calculate_from_pixel_counts,
    verify_analytical_identity,
    normalize_proportion,
)


def test_normalize_proportion():
    assert normalize_proportion(0.45) == 0.45
    assert normalize_proportion(0.0) == 0.0
    assert normalize_proportion(1.0) == 1.0
    # Percentages
    assert normalize_proportion(45.0, allow_percentage=True) == 0.45
    assert normalize_proportion(100.0, allow_percentage=True) == 1.0

    with pytest.raises(ValueError):
        normalize_proportion(-0.1)

    with pytest.raises(ValueError):
        normalize_proportion(105.0)


def test_closed_form_identity():
    """Verify that Δf == -f_water * f_corrected exactly."""
    res = calculate_wpdb_correction(f_naive=0.35, f_water=0.50, is_percentage=False)
    # Corrected = 0.35 / (1 - 0.50) = 0.70
    assert math.isclose(res["f_corrected"], 0.70, rel_tol=1e-9)
    # Observed bias = 0.35 - 0.70 = -0.35
    assert math.isclose(res["wpdb_bias"], -0.35, rel_tol=1e-9)
    # Predicted bias = - 0.50 * 0.70 = -0.35
    assert math.isclose(res["wpdb_predicted"], -0.35, rel_tol=1e-9)
    # Residual error must be 0.00
    assert res["residual"] <= 1e-12


def test_percentage_mode():
    """Verify calculation in 0-100 percentage point mode."""
    res = calculate_wpdb_correction(f_naive=35.0, f_water=50.0, is_percentage=True)
    assert math.isclose(res["f_corrected"], 70.0, rel_tol=1e-9)
    assert math.isclose(res["wpdb_bias"], -35.0, rel_tol=1e-9)
    assert math.isclose(res["wpdb_predicted"], -35.0, rel_tol=1e-9)
    assert res["residual"] <= 1e-10


def test_zero_water_boundary():
    """If there is no water, bias should be exactly zero."""
    res = calculate_wpdb_correction(f_naive=0.42, f_water=0.0)
    assert math.isclose(res["f_corrected"], 0.42, rel_tol=1e-9)
    assert math.isclose(res["wpdb_bias"], 0.0, abs_tol=1e-12)
    assert math.isclose(res["wpdb_predicted"], 0.0, abs_tol=1e-12)
    assert res["residual"] == 0.0


def test_zero_target_boundary():
    """If target land cover is zero, bias is zero."""
    res = calculate_wpdb_correction(f_naive=0.0, f_water=0.60)
    assert res["f_corrected"] == 0.0
    assert res["wpdb_bias"] == 0.0
    assert res["wpdb_predicted"] == 0.0
    assert res["residual"] == 0.0


def test_pixel_count_calculation():
    """Verify raw pixel count normalization."""
    # 350 built, 500 water, 1000 total -> 500 non-water
    res = calculate_from_pixel_counts(a_target=350, a_water=500, a_total=1000)
    assert res["a_nonwater"] == 500
    assert res["f_naive_pct"] == 35.0
    assert res["f_water_pct"] == 50.0
    assert res["f_corrected_pct"] == 70.0
    assert res["wpdb_bias_pp"] == -35.0
    assert res["residual_pp"] <= 1e-10


def test_invalid_water_fraction():
    """Water fraction >= 100% must raise ValueError."""
    with pytest.raises(ValueError):
        calculate_wpdb_correction(f_naive=0.20, f_water=1.0)

    with pytest.raises(ValueError):
        calculate_wpdb_correction(f_naive=0.20, f_water=1.05)


def test_verify_identity_helper():
    valid, residual = verify_analytical_identity(
        f_water=0.5630,
        f_corrected=0.8087,
        observed_bias=-0.4588,
        tolerance=0.01
    )
    assert valid is True
    assert residual <= 0.01

