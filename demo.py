"""
Interactive Manual Demo for WPDB Spatial Engine.
Run this script to test the correction engine directly in your terminal!

Author: Md Abu Sayem Sarker
"""

import os
import sys

# Ensure plugin package is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wpdb_spatial_engine.core.formula import calculate_wpdb_correction
from wpdb_spatial_engine.core.table_corrector import WPDBTableCorrector

SAMPLE_CSV = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "wpdb_spatial_engine", "sample_data", "sample_dhaka_11_stations.csv"
)


def print_banner():
    print("=" * 65)
    print("🌊 WPDB Spatial Engine: Interactive Test & Verification Suite")
    print("   Developed by: Md Abu Sayem Sarker (Data Scientist & GeoAI Researcher)")
    print("=" * 65)


def run_dhaka_benchmark():
    print("\n[*] Loading Dhaka 11-Station Ground-Truth Benchmark...")
    corrector = WPDBTableCorrector.from_csv(SAMPLE_CSV)
    
    print("[*] Processing non-water normalization...")
    df_res = corrector.process(
        water_col="water_fraction_pct",
        target_col="naive_built_pct",
        target_name="built",
        is_percentage=True
    )

    print("\n--- STATION RESULTS PREVIEW (First 5 Stations) ---")
    cols_to_show = [
        "station_id", "water_fraction_pct", "naive_built_pct",
        "built_corrected_pct", "wpdb_bias_pp", "identity_residual_pp"
    ]
    preview = df_res[cols_to_show].head(5)
    print(preview.to_string(index=False))

    print("\n--- SUMMARY DIAGNOSTIC AUDIT REPORT ---")
    print(corrector.get_summary_report())

    out_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dhaka_corrected_output.csv")
    corrector.save_csv(out_csv)
    print(f"[✓] Corrected dataset exported to:\n    {out_csv}")
    print("    (You can open this file in Excel to inspect all 11 stations!)\n")


def run_interactive_calculator():
    print("\n--- LIVE WPDB SINGLE-STATION CALCULATOR ---")
    try:
        w_input = input("Enter open water percentage (e.g. 62.1 for Hazaribagh): ").strip()
        n_input = input("Enter naive built-up percentage (e.g. 33.66 for Hazaribagh): ").strip()
        
        if not w_input or not n_input:
            print("[!] Inputs cannot be empty.")
            return

        w = float(w_input)
        n = float(n_input)

        res = calculate_wpdb_correction(f_naive=n, f_water=w, is_percentage=True)
        print("\n" + "-" * 45)
        print("CALCULATION RESULTS:")
        print(f"  Input Water Coverage:        {res['f_water']:.2f}%")
        print(f"  Naive (Uncorrected) Built:   {res['f_naive']:.2f}%")
        print(f"  -> TRUE Non-Water Built:     {res['f_corrected']:.2f}%")
        print(f"  -> Dilution Bias (WPDB):     {res['wpdb_bias']:.2f} percentage points")
        print(f"  -> Analytical Prediction:    {res['wpdb_predicted']:.2f} pp")
        print(f"  -> Formula Residual (|ε|):   {res['residual']:.6f} pp")
        print("-" * 45)
        if res['residual'] <= 0.01:
            print("  [✓] Mathematical Law Verified: Exact Zero Residual (|ε| <= 0.01 pp)")
        print("-" * 45 + "\n")
    except Exception as e:
        print(f"[!] Calculation error: {e}")


def main():
    print_banner()
    while True:
        print("Choose an option to try:")
        print("  1. Run automated audit on Dhaka 11-stations benchmark (generates Excel/CSV)")
        print("  2. Live Interactive Calculator (type your own custom numbers)")
        print("  3. Exit")
        choice = input("\nEnter choice [1, 2, or 3]: ").strip()

        if choice == "1":
            run_dhaka_benchmark()
        elif choice == "2":
            run_interactive_calculator()
        elif choice == "3":
            print("\nGoodbye!")
            break
        else:
            print("[!] Invalid choice. Please enter 1, 2, or 3.\n")


if __name__ == "__main__":
    main()

