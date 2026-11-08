# WPDB Spatial Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Tests: Passing](https://img.shields.io/badge/tests-36%20passed-brightgreen.svg)]()
[![Theory: IEEE CSDE 2026](https://img.shields.io/badge/Theory-IEEE%20CSDE%202026-orange.svg)](https://ieeexplore.ieee.org)

**Riverine Non-Water Spatial Feature Engineering & Dilution Bias Architecture**  
*Developed and maintained by **Md Abu Sayem Sarker** (Data Scientist & GeoAI Researcher).*  
*Core Domains: GeoAI · Remote Sensing · Machine Learning · Software Engineering*  
*Inquiries & Research Feedback: [mdabusayemsarker9@gmail.com](mailto:mdabusayemsarker9@gmail.com) | LinkedIn: [Abu Sayem Sarker](https://www.linkedin.com/in/mdabusayemsarker/) | GitHub: [@sayem088](https://github.com/sayem088)*

---

## 📖 Overview

In river water quality attribution and environmental machine learning, circular Euclidean buffers (e.g., 200m or 500m) drawn around monitoring stations capture large fractions of open water (40% to >65%). Standard GIS tools divide terrestrial land cover pixels by total polygon area, keeping unbuildable aquatic pixels in the denominator. This systematically deflates terrestrial land-use estimates by an average of **~47 percentage points** across urban river reaches (up to **-56.34 pp**).

**WPDB Spatial Engine** eliminates this distortion by normalizing spatial features strictly over non-water land area and verifying the closed-form analytical identity:
$$\Delta f_{\text{built}} = - f_{\text{water}} \cdot f_{\text{built, nw}}$$
$$f_{\text{built, nw}} = \frac{f_{\text{built, naive}}}{1 - f_{\text{water}}}$$

---

## 🚀 3-Tier Scientific GIS Suite

* **Tier 1 — Flow Corridor Extractor (Local Stages B→D):** Performs 1D metric linear referencing, station snapping, 5.0 km upstream reach traversal, and slices corridors into 50 longitudinal 100m bins (300m buffer half-width) with local raster zonal extraction.
* **Tier 2 — Tabular Bias Auditor (Stage D):** Rapid algebraic inversion ($f_{\text{target, nw}} = f_{\text{target, naive}} / [1 - f_{\text{water}}]$) of legacy CSV/Excel tables, tri-color graduated cartography, white-halo labeling, and 300/600 DPI publication plots.
* **Tier 3 — Full Cloud Pipeline (GEE Stages A→D):** End-to-end Google Earth Engine cloud pipeline (JRC skeletonization, station snapping, Sentinel-2 Dynamic World 10m LULC reduceRegions, and Theorem 1 identity verification) with one-click GEE JavaScript/Python script generator.
* **Exact Mathematical Invariance:** Enforces the foundational law $\Delta f_{\text{target}} = - f_{\text{water}} \cdot f_{\text{target, nw}}$, guaranteeing exact $|\varepsilon| = 0.00\text{ pp}$ residual agreement.
* **Publication Ready:** Verified against 11 real-world monitoring stations along the Buriganga and Shitalakhya river networks in Dhaka mega-city.

---

## 📊 Sample Validation Run (Dhaka River Networks, n = 11)

```text
==========================================================
WATER-PIXEL DILUTION BIAS (WPDB) CORRECTION REPORT
==========================================================
Stations Audited:       11
Mean Dilution Bias:     -46.93 pp
Maximum Distortion:     -56.34 pp (Satmasjid Road)
Standard Deviation:     8.74 pp
Max Identity Residual:  0.0000 pp
Theoretical Law Status: VERIFIED (|ε| <= 0.01)
==========================================================
```

---

## 🛠️ Quickstart (Python API)

```python
from wpdb_spatial_engine.core.table_corrector import WPDBTableCorrector

# 1. Load your spatial summary table
corrector = WPDBTableCorrector.from_csv("sample_dhaka_11_stations.csv")

# 2. Run batch correction (auto-detects columns)
corrected_df = corrector.process(
    water_col="water_fraction_pct",
    target_col="naive_built_pct",
    target_name="built",
    is_percentage=True
)

# 3. Print audit report
print(corrector.get_summary_report())

# 4. Save corrected dataset
corrector.save_csv("dhaka_stations_corrected.csv")
```

---

## 📚 Citation

If you use this software in academic research, please cite the underlying theoretical paper:

```bibtex
@inproceedings{sarker2026water,
  author    = {Sarker, Md Abu Sayem and Sakib, Syed Nazmus},
  title     = {Water Pixel Dilution Bias: A Systematic Measurement Error in Riverine Spatial Feature Engineering},
  booktitle = {Proceedings of the 11th IEEE Asia-Pacific Conference on Computer Science and Data Engineering (IEEE CSDE 2026)},
  year      = {2026},
  address   = {Cox's Bazar, Bangladesh},
  publisher = {IEEE}
}
```

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.  
Copyright (c) 2026 **Md Abu Sayem Sarker**.

