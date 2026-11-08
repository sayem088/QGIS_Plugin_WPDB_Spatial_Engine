# WPDB Spatial Engine User Guide & Tutorial 🌊

**Plugin Name:** `WPDB Spatial Engine`  
**Version:** `1.0.0`  
**Author & Lead Architect:** Md Abu Sayem Sarker (Data Scientist & GeoAI Researcher)  
**Target Platform:** QGIS 3.22 LTR through 4.2+ (Python 3.9 - 3.12+)  
**Repository:** [sayem088/QGIS_Plugin_WPDB_Spatial_Engine](https://github.com/sayem088/QGIS_Plugin_WPDB_Spatial_Engine)  
**LinkedIn:** [Abu Sayem Sarker](https://www.linkedin.com/in/mdabusayemsarker/)  
**Inquiries & Feedback:** [mdabusayemsarker9@gmail.com](mailto:mdabusayemsarker9@gmail.com)  

---

## 1. Introduction

In river water quality modeling, environmental machine learning, and hydrological data science, researchers routinely extract surrounding land-use density from satellite imagery using circular Euclidean buffers (e.g., $200\,\text{m}$ or $500\,\text{m}$) drawn around monitoring stations.

However, because monitoring stations sit on riverbanks, open water channels occupy **40% to over 65%** of the buffer area. Standard Geographic Information System (GIS) tools retain water pixels in the denominator when calculating land-use percentages ($A_{\text{built}} / A_{\text{total}}$). Because open water is unbuildable, this artificially deflates terrestrial land-use estimates by an average of **~47 percentage points** (reaching over **-56 pp** at industrial reaches).

**WPDB Spatial Engine** provides a 3-tier, mathematically rigorous solution that eliminates this error across local GIS projects and cloud computing environments.

---

## 2. Installation in QGIS

### Option A: Install from Official QGIS Plugin Repository
1. Open QGIS.
2. Go to **Plugins -> Manage and Install Plugins...**
3. In the **All** tab, search for `WPDB Spatial Engine`.
4. Click **Install Plugin**.

### Option B: Install from ZIP File (Direct)
1. Download `wpdb_spatial_engine.zip` from the GitHub Releases or the `dist/` directory.
2. In QGIS, navigate to **Plugins -> Manage and Install Plugins... -> Install from ZIP**.
3. Select `wpdb_spatial_engine.zip` and click **Install Plugin**.
4. The plugin icon (blue-and-red river corridor badge) will appear on your toolbar and under the **Plugins -> WPDB Spatial Engine** menu.

---

## 3. Tier 1: 🌊 River Corridor Extractor (Local Stages B $\rightarrow$ D)

Use this mode when you have local vector layers (stations and river centerline) and raster GeoTIFFs (LULC and Water Mask) in QGIS.

```
[Station Point] ──(Snap)──> [River Centerline] ──(5km Upstream)──> [50 Bins x 100m] ──(Zonal)──> Non-Water Normalization
```

### Step 1: Prepare Your Map Layers
Load four layers into your active QGIS project:
1. **Station Layer:** Point vector layer containing water quality monitoring stations.
2. **River Centerline:** LineString vector layer representing the channel centerline.
3. **Land Cover Raster:** GeoTIFF raster of classified land use (e.g., Sentinel-2 Dynamic World 10m).
4. **Water Mask Raster:** Binary or continuous surface water raster (e.g., JRC Global Surface Water).

### Step 2: Configure Extraction Parameters
Switch to **Tab 1: 🌊 River Corridor Extractor**:
* **Monitoring Stations Layer:** Select your station point layer.
* **River Centerline Layer:** Select the centerline LineString layer.
* **Land Cover Raster:** Select your LULC GeoTIFF.
* **Surface Water Raster:** Select your Water Mask GeoTIFF.
* **Upstream Reach Distance:** Set the traversal length (Default: `5000` meters / $5.0\,\text{km}$).
* **Bin Size:** Set longitudinal slice length (Default: `100` meters = 50 bins).
* **Buffer Width (Each Side):** Set corridor half-width (Default: `300` meters = $600\,\text{m}$ total corridor width).
* **Target LULC Value:** Set integer pixel value for target class (Default: `6` for Built-up).

### Step 3: Execute Corridor Extraction
1. Click **▶ Run Flow-Aware Corridor Extraction**.
2. The engine performs:
   - 1D linear referencing and nearest-vertex station snapping.
   - Upstream distance calculation and $50 \times 100\,\text{m}$ corridor bin polygon slicing.
   - Local zonal pixel counting ($A_{\text{water}}$, $A_{\text{target}}$, $A_{\text{total}}$).
   - Exact non-water normalization ($f_{\text{target, nw}} = f_{\text{target, naive}} / [1 - f_{\text{water}}]$).
3. Click **🗺️ Plot Extracted Corridors on Canvas** to add the $50$-bin corridor polygon layer to your QGIS map canvas.
4. Click **💾 Export Corridor CSV...** to save the distance-resolved longitudinal dataset.

---

## 4. Tier 2: 📊 Tabular Bias Auditor (Stage D)

Use this mode to retrospectively audit and correct pre-extracted CSV or Excel tables from legacy studies, ArcGIS Pro ("Tabulate Area"), or QGIS ("Zonal Statistics").

### Step 1: Select Your Spatial Table
Switch to **Tab 2: 📊 Tabular Bias Auditor**:
* Click **Browse CSV...** and select your tabular dataset.
* *Sample Data:* Try the bundled benchmark at `sample_data/sample_dhaka_11_stations.csv`.

### Step 2: Auto-Map Columns
The plugin auto-detects column names using heuristic pattern matching:
* **Water Fraction Column:** Column representing water surface coverage (e.g., `water_fraction_pct`).
* **Naive Land Cover Column:** Column representing unadjusted terrestrial land use (e.g., `naive_built_pct`).
* **Target Class Label:** Output column name (Default: `built`).
* **Percentage Checkbox:** Check `Values are in Percentages (0 - 100%)` if data is scaled to 100.

### Step 3: Run the Audit
Click **▶ Execute Bias Correction & Audit**.
* The **Results Preview Table** displays:
  - `built_corrected_pct`: True, non-water normalized terrestrial density.
  - `wpdb_bias_pp`: Observed dilution distortion magnitude (always negative).
  - `wpdb_predicted_pp`: Theoretical distortion from the closed-form identity $\Delta f = -f_{\text{water}} \cdot f_{\text{built, nw}}$.
  - `identity_residual_pp`: Exact residual agreement ($|\varepsilon| = 0.00\,\text{pp}$).

### Step 4: Map Cartography & Publication Plots
* **🗺️ Plot on Map Canvas:** Generates a graduated tri-color cartographic layer in QGIS (Red: High Distortion $> 40\,\text{pp}$; Amber: Moderate Distortion $20 - 40\,\text{pp}$; Blue: Low Distortion $< 20\,\text{pp}$) with white halo station labels.
* **📈 View Scientific Plots:** Opens an interactive 2-panel figure dialog displaying:
  - **Panel A:** Dilution Invariance Hyperbola ($\Delta f_{\text{built}}$ vs. $f_{\text{water}}$).
  - **Panel B:** Before vs. After Non-Water Correction Bar Comparison.
  - Export at **300 DPI** or **600 DPI** directly for IEEE / journal publication.

---

## 5. Tier 3: ☁️ Full Cloud Pipeline (GEE Stages A $\rightarrow$ D)

Use this mode for automated, zero-download cloud processing directly on Google Earth Engine satellite collections.

### Step 1: Configure Earth Engine
Switch to **Tab 3: ☁️ Full Cloud Pipeline**:
* **GEE Cloud Project ID:** Enter your Google Cloud Project ID (e.g., `sundarban-489216`).
* Click **🔐 Initialize GEE** to test cloud authentication.

### Step 2: Select Cloud River Reach & Collection
* **River Network Reach:** Select a study river preset (e.g., `Buriganga-Turag River (31.1 km Centerline)` or `Shitalakhya River`).
* **LULC Satellite Collection:** Select `Sentinel-2 Dynamic World (2021-2023 Modal Composite, 10m)`.
* **Target Extraction Class:** Select `Built-up (Class 6)` or another target land use.

### Step 3: Execute Cloud Pipeline
1. Click **🚀 Run End-to-End Cloud Pipeline (Stages A→D)**.
2. Watch the real-time background console log and progress bar:
   - **Stage A:** JRC Global Surface Water occurrence filtering & morphological skeletonization.
   - **Stage B:** Station snapping & upstream 1D graph traversal into 50 bins.
   - **Stage C:** Dynamic World 10m cloud `reduceRegions` pixel aggregation.
   - **Stage D:** Closed-form mathematical inversion and Theorem 1 identity verification.
3. Once completed:
   - Click **🗺️ Load to Canvas** to stream the extracted centerline and 50-bin corridor polygons directly onto your QGIS map canvas.
   - Click **💾 Export GEE CSV...** to save the distance-resolved cloud dataset.

### Step 4: GEE Cloud Script Generator
* Click **📜 View Cloud Script** to open the interactive script viewer.
* Toggle between **GEE JavaScript** (for pasting into `code.earthengine.google.com`) and **GEE Python** (for headless server scripts).
* Click **📋 Copy Script to Clipboard** or **💾 Save Script File...** to export standalone `.js` or `.py` files.

---

## 6. Tier 4: ℹ️ About, Author & Citation

Switch to **Tab 4: ℹ️ About & Citation**:
* **`📋 Copy IEEE Citation (BibTeX)`**: Copies the foundational IEEE CSDE 2026 citation to your clipboard.
* **`📋 Copy JOSS Citation`**: Copies the Journal of Open Source Software citation.
* **`🌐 GitHub Repository`**: Launches the official GitHub repository in your default browser.
* **`💼 LinkedIn Profile`**: Opens the author profile on LinkedIn.

---

## 7. Mathematical Formula Reference

| Quantity | Formula | Description |
| :--- | :--- | :--- |
| **Naive Target Density** | $f_{\text{target, naive}} = \frac{A_{\text{target}}}{A_{\text{total}}}$ | Conventional unadjusted GIS calculation (retains water in denominator). |
| **Non-Water Normalized Density** | $f_{\text{target, nw}} = \frac{f_{\text{target, naive}}}{1 - f_{\text{water}}}$ | True terrestrial land use density along the riverbank corridor. |
| **Water-Pixel Dilution Bias (WPDB)** | $\Delta f_{\text{target}} = f_{\text{target, naive}} - f_{\text{target, nw}}$ | The systematic negative measurement error caused by water dilution. |
| **Theorem 1 Analytical Identity** | $\Delta f_{\text{target}} = - f_{\text{water}} \cdot f_{\text{target, nw}}$ | Closed-form governing law proving WPDB is an exact algebraic consequence. |
| **Identity Residual** | $\varepsilon = \lvert \Delta f_{\text{observed}} - \Delta f_{\text{predicted}} \rvert$ | Guaranteed $\varepsilon = 0.00\,\text{pp}$ across all discrete classified rasters. |

---

## 8. Citation

If you utilize **WPDB Spatial Engine** in academic or applied research, please cite:

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
