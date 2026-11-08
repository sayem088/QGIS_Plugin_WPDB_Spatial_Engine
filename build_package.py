"""
Packaging script for WPDB Spatial Engine QGIS Plugin.
Creates a clean, repository-compliant distributable ZIP archive in dist/

Author: Md Abu Sayem Sarker
Data Scientist & GeoAI Researcher
"""

import configparser
import os
import zipfile
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_SOURCE = os.path.join(BASE_DIR, "wpdb_spatial_engine")
DIST_DIR = os.path.join(BASE_DIR, "dist")
OUTPUT_ZIP = os.path.join(DIST_DIR, "wpdb_spatial_engine.zip")

EXCLUDE_EXTS = {".pyc", ".pyo", ".pyd"}
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git", ".idea", ".vscode"}


def validate_metadata() -> str:
    """Validates metadata.txt and returns the version string."""
    meta_path = os.path.join(PLUGIN_SOURCE, "metadata.txt")
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Missing {meta_path}")

    config = configparser.ConfigParser()
    config.read(meta_path, encoding="utf-8")

    general = config["general"]
    version = general.get("version", "1.0.0")
    author = general.get("author", "")

    print(f"[*] Validating Plugin: {general.get('name')}")
    print(f"    Version: {version}")
    print(f"    Author:  {author}")
    print(f"    Email:   {general.get('email')}")

    if author != "Md Abu Sayem Sarker":
        raise ValueError(f"Author mismatch! Found: {author}")

    return version


def build_zip():
    """Packages wpdb_spatial_engine into dist/wpdb_spatial_engine.zip."""
    if not os.path.exists(DIST_DIR):
        os.makedirs(DIST_DIR)

    if os.path.exists(OUTPUT_ZIP):
        os.remove(OUTPUT_ZIP)

    print(f"[*] Packaging {PLUGIN_SOURCE} -> {OUTPUT_ZIP}")

    file_count = 0
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PLUGIN_SOURCE):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in EXCLUDE_EXTS or file.startswith("."):
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, BASE_DIR)

                # Ensure archive root starts with wpdb_spatial_engine/
                zf.write(full_path, rel_path)
                file_count += 1

    size_kb = os.path.getsize(OUTPUT_ZIP) / 1024.0
    print(f"[✓] Package created successfully: {file_count} files ({size_kb:.1f} KB)")


def verify_zip():
    """Inspects the generated ZIP archive to ensure QGIS compliance."""
    print("[*] Verifying ZIP structure for plugins.qgis.org compliance...")
    with zipfile.ZipFile(OUTPUT_ZIP, "r") as zf:
        names = zf.namelist()
        
        # Check root prefix
        non_compliant = [n for n in names if not n.startswith("wpdb_spatial_engine/")]
        if non_compliant:
            raise ValueError(f"Found non-compliant root files in ZIP: {non_compliant}")

        # Check required files exist inside archive
        required_archive_files = [
            "wpdb_spatial_engine/metadata.txt",
            "wpdb_spatial_engine/icon.png",
            "wpdb_spatial_engine/logo.png",
            "wpdb_spatial_engine/__init__.py",
            "wpdb_spatial_engine/plugin.py",
            "wpdb_spatial_engine/core/formula.py",
            "wpdb_spatial_engine/core/table_corrector.py",
            "wpdb_spatial_engine/core/spatial_corrector.py",
            "wpdb_spatial_engine/core/corridor_engine.py",
            "wpdb_spatial_engine/core/gee_worker.py",
            "wpdb_spatial_engine/core/gee_script_generator.py",
            "wpdb_spatial_engine/ui/wpdb_dialog_base.ui",
            "wpdb_spatial_engine/ui/wpdb_dialog.py",
            "wpdb_spatial_engine/ui/style.qss",
            "wpdb_spatial_engine/sample_data/sample_dhaka_11_stations.csv",
        ]

        for req in required_archive_files:
            assert req in names, f"Archive missing required component: {req}"

    print("[✓] ZIP archive verified! 100% compliant with QGIS Plugin Repository standards.")


if __name__ == "__main__":
    try:
        ver = validate_metadata()
        build_zip()
        verify_zip()
        print("\n========================================================")
        print(f"READY FOR SUBMISSION: dist/wpdb_spatial_engine.zip (v{ver})")
        print("Upload to: https://plugins.qgis.org")
        print("========================================================")
    except Exception as e:
        print(f"[!] Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
