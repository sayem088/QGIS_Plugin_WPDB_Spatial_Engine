---
title: 'WPDB Spatial Engine: A 3-Tier QGIS Plugin and Python Library for Eliminating Water-Pixel Dilution Bias in Riverine Spatial Feature Engineering'
tags:
  - Python
  - QGIS
  - Remote Sensing
  - Environmental Data Science
  - Spatial Stream Networks
  - Hydrology
  - Machine Learning
  - Google Earth Engine
authors:
  - name: Md Abu Sayem Sarker
    affiliation: 1
    email: mdabusayemsarker9@gmail.com
affiliations:
  - name: Data Scientist & GeoAI Researcher, Dhaka, Bangladesh
    index: 1
date: 7 November 2026
bibliography: paper.bib
---

# Summary

In river water quality attribution and hydrological data science, machine learning models rely fundamentally on spatial feature engineering to quantify surrounding anthropogenic stressors from satellite imagery. Standard geospatial workflows construct circular Euclidean buffers (e.g., $200\,\text{m}$ or $500\,\text{m}$ radius) around sampling nodes to summarize land use and land cover (LULC) proportions. However, because water quality monitoring stations are situated along riverbanks, open water channels occupy a large portion (typically $40\%$ to over $65\%$) of the extraction polygon. Standard Geographic Information System (GIS) tools divide terrestrial class areas by total enclosed polygon area, indiscriminately retaining unbuildable aquatic pixels in the normalization denominator. 

This creates a pervasive geometric measurement error formalized as **Water-Pixel Dilution Bias (WPDB)** [@sarker2026water]. Unadjusted circular buffers artificially depress terrestrial land cover estimates by an average of $\sim 47$ percentage points, causing severe misclassification of dense industrial river corridors as low-density greenfields.

`WPDB Spatial Engine` is an open-source Python library and official QGIS plugin engineered to identify, quantify, and eliminate Water-Pixel Dilution Bias across local GIS workflows and cloud computing environments. It implements exact closed-form non-water normalization ($f_{\text{target, nw}} = f_{\text{target, naive}} / [1 - f_{\text{water}}]$) and provides a unified 3-Tier Scientific GIS Suite:
1. **Tier 1 (Local River Corridor Extractor, Stages B $\rightarrow$ D):** Snaps sampling stations to channel centerlines via 1D metric linear referencing, traverses $5.0\,\text{km}$ upstream, and extracts $50$ longitudinal $100\,\text{m}$ bins ($300\,\text{m}$ corridor half-width) across local rasters.
2. **Tier 2 (Tabular Bias Auditor, Stage D):** Retrospectively inverts legacy CSV databases, verifies mathematical identity residuals, renders tri-color graduated cartography, and produces $300/600\,\text{DPI}$ publication-grade audit plots.
3. **Tier 3 (Full Cloud Pipeline, GEE Stages A $\rightarrow$ D):** Asynchronously executes an end-to-end Google Earth Engine pipeline (JRC water skeletonization, Sentinel-2 Dynamic World $10\,\text{m}$ modal composite extraction, and WPDB inversion) with interactive JavaScript and Python code export.

# Statement of Need

A recent systematic review confirmed that multi-radius Euclidean buffering remains the dominant spatial extraction paradigm in river water quality modeling [@gani2023assessing; @nishat2025comparative]. Despite its widespread usage, existing geospatial software suites—including QGIS (Zonal Statistics), ArcGIS Pro (Buffer/Tabulate Area), and Google Earth Engine (`reduceRegion`)—compute land cover fractions strictly relative to the total polygon area. 

When these unadjusted features feed statistical regression or machine learning models, the fitted feature weights reflect channel geometry and water surface area rather than true terrestrial development intensity. Prior to `WPDB Spatial Engine`, researchers had to manually implement custom image-masking scripts, leading to irreproducible workflows and uncorrected legacy datasets.

`WPDB Spatial Engine` directly addresses this gap by providing:
1. **Universal Mathematical Inversion & Auditing:** The ability to retrospectively correct existing published summary tables without requiring terabytes of raw satellite rasters.
2. **Flow-Aware 1D Corridor Extraction:** Directional upstream longitudinal bin segmentation along river networks, replacing flawed circular buffers.
3. **Full Cloud Earth Engine Integration:** Asynchronous GEE execution with automatic code generator for the GEE Web Code Editor.
4. **Rigorous Quality Control:** Automated verification of the analytical identity residual ($|\varepsilon| \le 0.01\,\text{pp}$), guaranteeing zero mathematical deviation within floating-point precision.

# Mathematical Formulation

Conventional spatial buffer tools calculate naive target land cover fraction $f_{\text{target, naive}}$ over total area $A_{\text{total}}$:
\begin{equation}
f_{\text{target, naive}} = \frac{A_{\text{target}}}{A_{\text{total}}} = \frac{A_{\text{target}}}{A_{\text{target}} + A_{\text{other}} + A_{\text{water}}}
\end{equation}

`WPDB Spatial Engine` isolates the buildable terrestrial domain by subtracting open water area from the normalization denominator:
\begin{equation}
f_{\text{target, nw}} = \frac{A_{\text{target}}}{A_{\text{total}} - A_{\text{water}}} = \frac{f_{\text{target, naive}}}{1 - f_{\text{water}}}
\end{equation}
where $f_{\text{water}} \equiv A_{\text{water}} / A_{\text{total}}$ represents the water fraction. 

Subtracting Equation (2) from Equation (1) yields the closed-form algebraic identity governing denominator distortion [@sarker2026water]:
\begin{equation}
\Delta f_{\text{target}} = - f_{\text{water}} \cdot f_{\text{target, nw}}
\end{equation}

Because land cover classes in classified rasters are mutually exclusive and exhaustive, Equation (3) represents a deterministic algebraic law rather than an empirical regression fit. The software verifies this by computing the analytical residual $|\varepsilon| = |\Delta f_{\text{observed}} - \Delta f_{\text{predicted}}|$, confirming exact agreement.

# Software Architecture & Implementation

`WPDB Spatial Engine` is structured into a modular, test-driven architecture:

```
wpdb_spatial_engine/
├── core/
│   ├── formula.py              # Closed-form identity, residual verification, proportions
│   ├── table_corrector.py      # High-throughput CSV and attribute table processor
│   ├── spatial_corrector.py    # 2D raster masking and spatial buffer processor
│   ├── corridor_engine.py      # 1D linear referencing, station snapping & 50 bins
│   ├── gee_worker.py           # Background QThread for asynchronous Earth Engine tasks
│   └── gee_script_generator.py # Standalone GEE JavaScript & Python generator
├── ui/
│   ├── wpdb_dialog.py          # PyQt controller and QGIS canvas layer bindings
│   ├── wpdb_dialog_base.ui     # 4-tab unified scientific GIS interface
│   ├── charts_dialog.py        # Publication plot viewer (300/600 DPI export)
│   └── script_viewer_dialog.py # Interactive GEE JavaScript/Python code viewer
├── sample_data/                # Dhaka 11-station benchmark and GeoJSON centerlines
└── tests/                      # 36 automated unit tests across all components
```

- **Headless Core Engine:** `formula.py`, `table_corrector.py`, `corridor_engine.py`, and `gee_script_generator.py` operate independently of QGIS, relying strictly on NumPy and Pandas for rapid execution ($< 0.1\,\text{s}$ for $1,000$ rows).
- **Asynchronous Cloud Pipeline:** `gee_worker.py` utilizes a background `QThread` with real-time log streaming and progress reporting, preventing QGIS interface lockups during cloud execution.
- **Desktop GUI:** Built with PyQt, featuring 4 dedicated scientific tabs, automated column detection, 1-click cartographic map canvas plotting, and 1-click BibTeX citation copying.

# Empirical Verification & Example Usage

The software includes a benchmark dataset comprising 11 water quality monitoring stations along two major river networks in Dhaka, Bangladesh: the Buriganga River ($n=7$) and Shitalakhya River ($n=4$), cross-referenced against 10-meter Sentinel-2 Dynamic World [@brown2022dynamic] and 30-meter JRC Global Surface Water [@pekel2016high].

Across the 11 stations, conventional circular buffers reported a mean built-up density of only $34.87\%$. Applying `WPDB Spatial Engine` recovered the true terrestrial density of $81.80\%$, revealing a mean dilution bias of $-46.93\,\text{pp}$ (reaching $-56.34\,\text{pp}$ at Satmasjid Road). At Hazaribagh—Dhaka's historic tannery district—a $200\,\text{m}$ buffer misclassified the site as "Mixed Urban" ($26.50\%$ naive built cover), whereas `WPDB Spatial Engine` restored its true industrial designation ($88.80\%$). The software confirmed $|\varepsilon| \le 0.01\,\text{pp}$ across all 11 stations.

## Python API Usage

```python
from wpdb_spatial_engine.core.table_corrector import WPDBTableCorrector
from wpdb_spatial_engine.core.corridor_engine import RiverCenterline, WPDBFlowCorridorPipeline

# 1. Tabular Audit of Legacy Database
corrector = WPDBTableCorrector.from_csv("sample_dhaka_11_stations.csv")
df_corrected = corrector.process(
    water_col="water_fraction_pct",
    target_col="naive_built_pct",
    target_name="built",
    is_percentage=True
)
print(corrector.get_summary_report())

# 2. 1D Flow Corridor Extraction (5km Upstream, 50 Bins)
centerline = RiverCenterline.from_geojson("buriganga_centerline.geojson")
pipeline = WPDBFlowCorridorPipeline(
    centerline=centerline,
    max_upstream_m=5000.0,
    bin_size_m=100.0,
    corridor_width_m=300.0
)
df_bins, df_summary = pipeline.process_stations_dataframe(df_corrected)
print(f"Extracted {len(df_bins)} longitudinal corridor bins successfully.")
```

# Acknowledgements & Foundation

This software implements the mathematical formulations and methodological foundations derived in @sarker2026water.

# References
