# WPDB Spatial Engine Documentation 🌊

**WPDB Spatial Engine** is an official QGIS Plugin and open-source scientific software package designed to identify, quantify, and eliminate **Water-Pixel Dilution Bias (WPDB)** in riverine spatial feature engineering and hydrological data science.

* **Step-by-Step User Tutorial:** [docs/tutorial.md](tutorial.md)
* **Author & Lead Architect:** Md Abu Sayem Sarker (Data Scientist & GeoAI Researcher)
* **Core Domains:** GeoAI · Remote Sensing · Machine Learning · Software Engineering
* **Official Repository:** [https://github.com/sayem088/QGIS_Plugin_WPDB_Spatial_Engine](https://github.com/sayem088/QGIS_Plugin_WPDB_Spatial_Engine)
* **Inquiries & Research Feedback:** [mdabusayemsarker9@gmail.com](mailto:mdabusayemsarker9@gmail.com)
* **LinkedIn:** [Abu Sayem Sarker](https://www.linkedin.com/in/mdabusayemsarker/)
* **License:** MIT License (Copyright 2026 Md Abu Sayem Sarker)

---

## The Core Mathematical Law

Conventional circular buffers compute terrestrial land cover fractions over total enclosed polygon area:
$$f_{\text{target, naive}} = \frac{A_{\text{target}}}{A_{\text{total}}} = \frac{A_{\text{target}}}{A_{\text{target}} + A_{\text{other}} + A_{\text{water}}}$$

`WPDB Spatial Engine` isolates terrestrial land cover by excluding unbuildable aquatic pixels from the denominator:
$$f_{\text{target, nw}} = \frac{A_{\text{target}}}{A_{\text{total}} - A_{\text{water}}} = \frac{f_{\text{target, naive}}}{1 - f_{\text{water}}}$$

This yields the exact closed-form measurement error:
$$\Delta f_{\text{target}} = - f_{\text{water}} \cdot f_{\text{target, nw}}$$

---

## 3-Tier Architecture Overview

```mermaid
flowchart TD
    subgraph TIER1["🌊 Tier 1: Local Corridor Extractor (Stages B-D)"]
        direction TB
        L1["Local Vector Centerline + Rasters"] --> P1["5.0 km Upstream Snapping & 50x100m Longitudinal Bins"]
        P1 --> O1["QGIS Map Canvas Polygons + Distance-Resolved CSV"]
    end

    subgraph TIER2["📊 Tier 2: Tabular Bias Auditor (Stage D)"]
        direction TB
        L2["Legacy CSV / Attribute Tables"] --> P2["Closed-Form Inversion & Theorem 1 Verification"]
        P2 --> O2["Tri-Color Map Cartography + 300/600 DPI Publication Plots"]
    end

    subgraph TIER3["☁️ Tier 3: Full Cloud Pipeline (GEE Stages A-D)"]
        direction TB
        L3["GEE Cloud Auth + Study Reach"] --> P3["JRC Centerline + Sentinel-2 Dynamic World 10m reduceRegions"]
        P3 --> O3["Map Canvas Streaming + Standalone GEE Script Generator (.js / .py)"]
    end
```

---

## Empirical Verification in Dhaka Mega-City

Empirical validation across 11 monitoring stations on the Buriganga ($n=7$) and Shitalakhya ($n=4$) river systems confirmed that:
1. Conventional circular buffers deflated built-up density by an average of **$46.93$ percentage points** (ranging from $-27.19$ to $-56.34\text{ pp}$).
2. The closed-form analytical identity predicted observed distortion with **zero residual ($|\varepsilon| \le 0.01\text{ pp}$)** at all 11 stations.
3. At the Hazaribagh tannery cluster, non-water normalization restored true industrial built-up density from $26.5\%$ (misclassified by naive buffers as "Mixed Urban") to **$88.8\%$** ("Industrial Infrastructure").
