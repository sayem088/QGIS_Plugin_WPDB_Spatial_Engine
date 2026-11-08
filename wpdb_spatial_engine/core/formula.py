"""
Mathematical formulation and algebraic identities for Water-Pixel Dilution Bias (WPDB).

Author: Md Abu Sayem Sarker
Reference: Sarker & Sakib (2026), "Water Pixel Dilution Bias: A Systematic
           Measurement Error in Riverine Spatial Feature Engineering", IEEE CSDE 2026.
"""

from typing import Dict, Tuple, Union
import math


def normalize_proportion(value: float, allow_percentage: bool = True) -> float:
    """
    Normalizes an input into a standard 0.0 - 1.0 proportion.
    If value > 1.0 and allow_percentage is True, treats as percentage (divided by 100).
    """
    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"Input value must be a valid finite number, got: {value}")
    
    if value < 0.0:
        raise ValueError(f"Proportion or percentage cannot be negative, got: {value}")
        
    if value > 1.0 and allow_percentage:
        if value > 100.0:
            raise ValueError(f"Percentage cannot exceed 100%, got: {value}")
        return value / 100.0
    
    if value > 1.0 and not allow_percentage:
        raise ValueError(f"Proportion cannot exceed 1.0, got: {value}")
        
    return float(value)


def calculate_wpdb_correction(
    f_naive: float,
    f_water: float,
    is_percentage: bool = False
) -> Dict[str, float]:
    """
    Calculates the non-water normalized terrestrial land cover fraction and 
    Water-Pixel Dilution Bias (WPDB) from naive land cover fraction and open water fraction.

    Governing Closed-Form Identity (Eq. 5):
        Δf_target = - f_water · f_target,nw
        f_target,nw = f_target,naive / (1 - f_water)

    Args:
        f_naive: Naive land cover fraction (target class / total buffer area).
        f_water: Open water surface fraction inside the extraction buffer.
        is_percentage: If True, inputs and outputs are in percentage (0-100),
                       otherwise in proportions (0-1).

    Returns:
        dict containing:
            - 'f_naive': input naive fraction
            - 'f_water': input water fraction
            - 'f_corrected': corrected non-water normalized fraction
            - 'wpdb_bias': dilution bias (f_naive - f_corrected)
            - 'wpdb_predicted': theoretical bias (- f_water * f_corrected)
            - 'residual': absolute discrepancy |observed - predicted|
    """
    w = normalize_proportion(f_water, allow_percentage=is_percentage)
    n = normalize_proportion(f_naive, allow_percentage=is_percentage)

    if w >= 1.0:
        raise ValueError("Water fraction cannot be 100% or greater (no terrestrial land exists).")

    # Invert the denominator error: f_target,nw = f_target,naive / (1 - f_water)
    corrected = n / (1.0 - w)
    
    # Cap slight floating point overshoots above 1.0
    if corrected > 1.0 and (corrected - 1.0) < 1e-6:
        corrected = 1.0
    elif corrected > 1.0:
        raise ValueError(
            f"Inconsistent inputs: naive fraction {f_naive} and water fraction {f_water} "
            f"yield non-water terrestrial fraction {corrected:.4f} > 1.0."
        )

    # Observed bias: f_naive - f_corrected (always negative or zero)
    observed_bias = n - corrected
    
    # Analytical prediction from closed-form identity: - f_water * f_corrected
    predicted_bias = - (w * corrected)
    
    # Exact algebraic residual error
    residual = abs(observed_bias - predicted_bias)

    scale = 100.0 if is_percentage else 1.0

    return {
        "f_naive": n * scale,
        "f_water": w * scale,
        "f_corrected": corrected * scale,
        "wpdb_bias": observed_bias * scale,
        "wpdb_predicted": predicted_bias * scale,
        "residual": residual * scale,
    }


def calculate_from_pixel_counts(
    a_target: float,
    a_water: float,
    a_total: float
) -> Dict[str, float]:
    """
    Computes naive fraction, corrected fraction, and dilution bias directly from raw pixel counts.

    Args:
        a_target: Pixel count of target terrestrial land cover (e.g. built-up).
        a_water: Pixel count of open water inside the buffer polygon.
        a_total: Total pixel count enclosed by the extraction buffer.

    Returns:
        dict with fractions, percentages, and verification metrics.
    """
    if a_total <= 0:
        raise ValueError(f"Total pixel count must be positive, got {a_total}")
    if a_target < 0 or a_water < 0:
        raise ValueError("Pixel counts cannot be negative")
    if (a_target + a_water) > a_total * (1.0 + 1e-6):
        raise ValueError(f"Target ({a_target}) + water ({a_water}) cannot exceed total ({a_total})")

    f_naive = a_target / a_total
    f_water = a_water / a_total
    a_nonwater = a_total - a_water

    if a_nonwater <= 0:
        raise ValueError("Non-water pixel area is zero; cannot normalize over terrestrial land.")

    f_corrected = a_target / a_nonwater
    observed_bias = f_naive - f_corrected
    predicted_bias = - (f_water * f_corrected)
    residual = abs(observed_bias - predicted_bias)

    return {
        "a_target": a_target,
        "a_water": a_water,
        "a_nonwater": a_nonwater,
        "a_total": a_total,
        "f_water_pct": f_water * 100.0,
        "f_naive_pct": f_naive * 100.0,
        "f_corrected_pct": f_corrected * 100.0,
        "wpdb_bias_pp": observed_bias * 100.0,
        "wpdb_predicted_pp": predicted_bias * 100.0,
        "residual_pp": residual * 100.0,
    }


def verify_analytical_identity(
    f_water: float,
    f_corrected: float,
    observed_bias: float,
    tolerance: float = 0.01
) -> Tuple[bool, float]:
    """
    Verifies whether an empirical observation satisfies the closed-form WPDB identity:
        | observed_bias - (- f_water * f_corrected) | <= tolerance

    Args:
        f_water: Water surface fraction (0 to 1).
        f_corrected: Non-water normalized terrestrial fraction (0 to 1).
        observed_bias: Observed difference (f_naive - f_corrected).
        tolerance: Maximum acceptable residual (default: 0.01 pp or 0.0001).

    Returns:
        Tuple (is_valid: bool, residual: float)
    """
    predicted_bias = - (f_water * f_corrected)
    residual = abs(observed_bias - predicted_bias)
    return (residual <= tolerance), residual

