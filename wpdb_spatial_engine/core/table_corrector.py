"""
Batch table and CSV processor for Water-Pixel Dilution Bias (WPDB).

Author: Md Abu Sayem Sarker
"""

import os
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
from .formula import calculate_wpdb_correction, calculate_from_pixel_counts


class WPDBTableCorrector:
    """
    Processes tabular spatial datasets (CSV, Excel, DataFrames) to audit and correct
    Water-Pixel Dilution Bias across monitoring stations.
    """

    COMMON_WATER_COLS = [
        "f_water", "water", "water_fraction", "water_pct", "water_fraction_pct",
        "open_water", "water_pixels", "a_water", "water_area"
    ]

    COMMON_TARGET_COLS = [
        "f_built", "built", "built_up", "impervious", "naive_built",
        "naive_built_pct", "f_built_naive", "built_pixels", "a_built",
        "target", "target_fraction", "crops", "vegetation"
    ]

    COMMON_TOTAL_COLS = [
        "total", "total_pixels", "a_total", "buffer_area", "total_area"
    ]

    def __init__(self, df: Optional[pd.DataFrame] = None):
        self.df = df.copy() if df is not None else None
        self.summary_stats: Dict[str, float] = {}

    @classmethod
    def from_csv(cls, file_path: str) -> "WPDBTableCorrector":
        """Loads a table from a CSV file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        df = pd.read_csv(file_path)
        return cls(df)

    def detect_columns(self) -> Dict[str, Optional[str]]:
        """
        Heuristically detects water, target, and total columns in the loaded dataframe.
        """
        if self.df is None or self.df.empty:
            return {"water": None, "target": None, "total": None}

        cols_lower = {col.lower().strip(): col for col in self.df.columns}

        detected_water = None
        for candidate in self.COMMON_WATER_COLS:
            if candidate in cols_lower:
                detected_water = cols_lower[candidate]
                break

        detected_target = None
        for candidate in self.COMMON_TARGET_COLS:
            if candidate in cols_lower:
                detected_target = cols_lower[candidate]
                break

        detected_total = None
        for candidate in self.COMMON_TOTAL_COLS:
            if candidate in cols_lower:
                detected_total = cols_lower[candidate]
                break

        return {
            "water": detected_water,
            "target": detected_target,
            "total": detected_total,
        }

    def process(
        self,
        water_col: Optional[str] = None,
        target_col: Optional[str] = None,
        total_col: Optional[str] = None,
        target_name: str = "built",
        is_percentage: Optional[bool] = None
    ) -> pd.DataFrame:
        """
        Runs the WPDB correction on the dataframe.

        Args:
            water_col: Column containing water fraction or pixel count.
            target_col: Column containing naive target land cover fraction or pixel count.
            total_col: Optional column containing total pixel count (for count-based mode).
            target_name: Label for output columns (e.g. 'built', 'impervious', 'crop').
            is_percentage: True if data is in 0-100%, False if 0-1. If None, auto-detected.

        Returns:
            pd.DataFrame with added correction and audit columns.
        """
        if self.df is None or self.df.empty:
            raise ValueError("No dataframe loaded to process.")

        detected = self.detect_columns()
        water_col = water_col or detected["water"]
        target_col = target_col or detected["target"]
        total_col = total_col or detected["total"]

        if not water_col or water_col not in self.df.columns:
            raise ValueError(f"Water column '{water_col}' not found in table.")
        if not target_col or target_col not in self.df.columns:
            raise ValueError(f"Target column '{target_col}' not found in table.")

        df_out = self.df.copy()

        # Check if raw pixel counts are used
        if total_col and total_col in df_out.columns:
            corrected_list = []
            bias_list = []
            pred_bias_list = []
            residual_list = []
            for _, row in df_out.iterrows():
                res = calculate_from_pixel_counts(
                    a_target=float(row[target_col]),
                    a_water=float(row[water_col]),
                    a_total=float(row[total_col])
                )
                corrected_list.append(res["f_corrected_pct"])
                bias_list.append(res["wpdb_bias_pp"])
                pred_bias_list.append(res["wpdb_predicted_pp"])
                residual_list.append(res["residual_pp"])

            df_out[f"{target_name}_corrected_pct"] = corrected_list
            df_out[f"wpdb_bias_pp"] = bias_list
            df_out[f"wpdb_predicted_pp"] = pred_bias_list
            df_out[f"identity_residual_pp"] = residual_list

        else:
            # Fraction mode
            # Auto-detect percentage if not specified
            sample_water = df_out[water_col].dropna().iloc[0] if not df_out[water_col].dropna().empty else 0.5
            if is_percentage is None:
                is_pct = bool(sample_water > 1.0 or df_out[water_col].max() > 1.0)
            else:
                is_pct = is_percentage

            corrected_list = []
            bias_list = []
            pred_bias_list = []
            residual_list = []

            for _, row in df_out.iterrows():
                try:
                    w = float(row[water_col])
                    n = float(row[target_col])
                    res = calculate_wpdb_correction(f_naive=n, f_water=w, is_percentage=is_pct)
                    corrected_list.append(res["f_corrected"])
                    bias_list.append(res["wpdb_bias"])
                    pred_bias_list.append(res["wpdb_predicted"])
                    residual_list.append(res["residual"])
                except Exception as e:
                    corrected_list.append(float("nan"))
                    bias_list.append(float("nan"))
                    pred_bias_list.append(float("nan"))
                    residual_list.append(float("nan"))

            suffix = "_pct" if is_pct else "_ratio"
            unit = "pp" if is_pct else "diff"

            df_out[f"{target_name}_corrected{suffix}"] = corrected_list
            df_out[f"wpdb_bias_{unit}"] = bias_list
            df_out[f"wpdb_predicted_{unit}"] = pred_bias_list
            df_out[f"identity_residual_{unit}"] = residual_list

        self._calculate_summary(df_out)
        self.df = df_out
        return df_out

    def _calculate_summary(self, df: pd.DataFrame) -> None:
        """Computes summary metrics across processed stations."""
        bias_col = [c for c in df.columns if c.startswith("wpdb_bias_")]
        residual_col = [c for c in df.columns if c.startswith("identity_residual_")]

        if bias_col:
            b = df[bias_col[0]].dropna()
            self.summary_stats["mean_bias"] = float(b.mean())
            self.summary_stats["min_bias"] = float(b.min())
            self.summary_stats["max_bias"] = float(b.max())
            self.summary_stats["std_bias"] = float(b.std())
            self.summary_stats["n_stations"] = int(len(b))

        if residual_col:
            r = df[residual_col[0]].dropna()
            self.summary_stats["max_residual"] = float(r.max())
            self.summary_stats["mean_residual"] = float(r.mean())

    def get_summary_report(self) -> str:
        """Generates a text summary of the audit and correction."""
        if not self.summary_stats:
            return "No correction summary available. Run process() first."

        s = self.summary_stats
        report = (
            f"==========================================================\n"
            f"WATER-PIXEL DILUTION BIAS (WPDB) CORRECTION REPORT\n"
            f"==========================================================\n"
            f"Stations Audited:       {s.get('n_stations', 0)}\n"
            f"Mean Dilution Bias:     {s.get('mean_bias', 0.0):.2f}\n"
            f"Maximum Distortion:     {s.get('min_bias', 0.0):.2f}\n"
            f"Standard Deviation:     {s.get('std_bias', 0.0):.2f}\n"
            f"Max Identity Residual:  {s.get('max_residual', 0.0):.4f}\n"
            f"Theoretical Law Status: {'VERIFIED (|ε| <= 0.01)' if s.get('max_residual', 1.0) <= 0.01 else 'DEVIATION DETECTED'}\n"
            f"==========================================================\n"
        )
        return report

    def save_csv(self, output_path: str) -> None:
        """Saves the corrected dataframe to a CSV file."""
        if self.df is None or self.df.empty:
            raise ValueError("No data to save.")
        self.df.to_csv(output_path, index=False)


def process_csv_file(
    input_csv: str,
    output_csv: str,
    water_col: Optional[str] = None,
    target_col: Optional[str] = None
) -> Tuple[pd.DataFrame, str]:
    """Helper function to run batch correction on a CSV file and output report."""
    corrector = WPDBTableCorrector.from_csv(input_csv)
    corrected_df = corrector.process(water_col=water_col, target_col=target_col)
    corrector.save_csv(output_csv)
    report = corrector.get_summary_report()
    return corrected_df, report

