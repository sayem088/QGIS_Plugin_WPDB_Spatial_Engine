"""
Spatial buffer and raster masking engine for Water-Pixel Dilution Bias (WPDB).

Author: Md Abu Sayem Sarker
Data Scientist & GeoAI Researcher
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from .formula import calculate_from_pixel_counts


def compute_buffer_metrics(
    water_pixels: int,
    target_pixels: int,
    total_pixels: int
) -> Dict[str, float]:
    """
    Computes exact WPDB spatial metrics from buffer pixel counts.
    """
    return calculate_from_pixel_counts(
        a_target=float(target_pixels),
        a_water=float(water_pixels),
        a_total=float(total_pixels)
    )


def extract_from_raster_arrays(
    water_array: np.ndarray,
    lulc_array: np.ndarray,
    target_val: int = 1,
    water_val: int = 1,
    mask: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """
    Calculates non-water normalized land-use density directly from 2D numpy raster arrays.

    Args:
        water_array: 2D array where water pixels match water_val or > 0.
        lulc_array: 2D array of categorical land cover classes.
        target_val: Pixel value representing target class (e.g. 1 for built-up).
        water_val: Pixel value representing open water.
        mask: Optional boolean 2D mask (e.g. circular buffer footprint, True = inside buffer).

    Returns:
        dict with pixel counts, naive fraction, corrected fraction, and bias.
    """
    if water_array.shape != lulc_array.shape:
        raise ValueError(
            f"Raster shape mismatch: water {water_array.shape} vs lulc {lulc_array.shape}"
        )

    if mask is not None:
        if mask.shape != water_array.shape:
            raise ValueError(f"Mask shape {mask.shape} does not match raster shape {water_array.shape}")
        w_sub = water_array[mask]
        l_sub = lulc_array[mask]
    else:
        w_sub = water_array.ravel()
        l_sub = lulc_array.ravel()

    total_valid = len(w_sub)
    if total_valid == 0:
        raise ValueError("Buffer polygon contains zero valid pixels.")

    # Identify water pixels
    water_mask = (w_sub == water_val) if water_val is not None else (w_sub > 0)
    water_pixels = int(np.sum(water_mask))

    # Identify target terrestrial land cover pixels
    target_mask = (l_sub == target_val)
    target_pixels = int(np.sum(target_mask))

    return compute_buffer_metrics(
        water_pixels=water_pixels,
        target_pixels=target_pixels,
        total_pixels=total_valid
    )


class WPDBSpatialProcessor:
    """
    Spatial engine that intersects station buffer geometries with land-cover
    and water rasters to eliminate dilution bias.
    """

    def __init__(self):
        self.summary_stats: Dict[str, float] = {}

    def process_arrays_batch(
        self,
        station_names: List[str],
        water_array: np.ndarray,
        lulc_array: np.ndarray,
        buffer_masks: List[np.ndarray],
        target_val: int = 1,
        water_val: int = 1,
        target_name: str = "built"
    ) -> pd.DataFrame:
        """
        Processes a batch of station buffers against 2D raster arrays.
        """
        records = []
        for name, mask in zip(station_names, buffer_masks):
            metrics = extract_from_raster_arrays(
                water_array=water_array,
                lulc_array=lulc_array,
                target_val=target_val,
                water_val=water_val,
                mask=mask
            )
            records.append({
                "station_id": name,
                "total_pixels": int(metrics["a_total"]),
                "water_pixels": int(metrics["a_water"]),
                f"{target_name}_pixels": int(metrics["a_target"]),
                "nonwater_pixels": int(metrics["a_nonwater"]),
                "water_fraction_pct": metrics["f_water_pct"],
                f"naive_{target_name}_pct": metrics["f_naive_pct"],
                f"nonwater_{target_name}_pct": metrics["f_corrected_pct"],
                "wpdb_bias_pp": metrics["wpdb_bias_pp"],
                "wpdb_predicted_pp": metrics["wpdb_predicted_pp"],
                "identity_residual_pp": metrics["residual_pp"],
            })

        df = pd.DataFrame(records)
        self._calculate_summary(df)
        return df

    def process_geodataframe(
        self,
        gdf_stations,
        lulc_raster_path: str,
        water_raster_path: str,
        buffer_radius_m: float = 200.0,
        target_class: int = 1,
        water_class: int = 1,
        target_name: str = "built",
        station_id_col: Optional[str] = None
    ):
        """
        Buffers station points, masks rasters using rasterio, and computes non-water stats.
        Requires rasterio and geopandas.
        """
        try:
            import rasterio
            from rasterio.mask import mask as rio_mask
        except ImportError:
            raise ImportError("rasterio is required for file-based spatial raster masking.")

        gdf = gdf_stations.copy()
        id_col = station_id_col or ("station_id" if "station_id" in gdf.columns else gdf.columns[0])

        # Buffer geometries in meters
        buffered_gdf = gdf.copy()
        buffered_gdf["geometry"] = gdf.geometry.buffer(buffer_radius_m)

        records = []
        with rasterio.open(lulc_raster_path) as src_lulc, rasterio.open(water_raster_path) as src_water:
            for _, row in buffered_gdf.iterrows():
                geom = [row.geometry]
                station_name = str(row[id_col])

                try:
                    lulc_img, _ = rio_mask(src_lulc, geom, crop=True)
                    water_img, _ = rio_mask(src_water, geom, crop=True)

                    metrics = extract_from_raster_arrays(
                        water_array=water_img[0],
                        lulc_array=lulc_img[0],
                        target_val=target_class,
                        water_val=water_class,
                        mask=(lulc_img[0] != src_lulc.nodata) if src_lulc.nodata is not None else None
                    )
                    records.append({
                        "station_id": station_name,
                        "total_pixels": int(metrics["a_total"]),
                        "water_pixels": int(metrics["a_water"]),
                        f"{target_name}_pixels": int(metrics["a_target"]),
                        "nonwater_pixels": int(metrics["a_nonwater"]),
                        "water_fraction_pct": metrics["f_water_pct"],
                        f"naive_{target_name}_pct": metrics["f_naive_pct"],
                        f"nonwater_{target_name}_pct": metrics["f_corrected_pct"],
                        "wpdb_bias_pp": metrics["wpdb_bias_pp"],
                        "identity_residual_pp": metrics["residual_pp"],
                    })
                except Exception as e:
                    records.append({
                        "station_id": station_name,
                        "error": str(e)
                    })

        res_df = pd.DataFrame(records)
        self._calculate_summary(res_df)
        return res_df

    def _calculate_summary(self, df: pd.DataFrame) -> None:
        """Calculates network summary metrics."""
        if "wpdb_bias_pp" in df.columns:
            b = df["wpdb_bias_pp"].dropna()
            self.summary_stats["mean_bias"] = float(b.mean())
            self.summary_stats["min_bias"] = float(b.min())
            self.summary_stats["max_bias"] = float(b.max())
            self.summary_stats["std_bias"] = float(b.std())
            self.summary_stats["n_stations"] = int(len(b))

        if "identity_residual_pp" in df.columns:
            r = df["identity_residual_pp"].dropna()
            self.summary_stats["max_residual"] = float(r.max())

