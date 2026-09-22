# Indicator 6.1.1 Methodology & Analysis Guide: Global Building Exposure to Wildfire-Impacted Areas

> Current review (2026-09-21): **conditional implementation research only**. No corrected national release has been regenerated. Legacy global outputs are quarantined; see the [evidence and publication conditions](CONDITIONAL_RESEARCH.md). Earlier descriptions below are historical and do not establish current execution or validation.

## 1. Executive Summary & Purpose

Indicator 6.1.1 measures the number and proportion of building stock exposed to wildfire-impacted areas worldwide. Wildfires cause severe economic disruption, loss of human life, and destruction of the built environment. As climate change accelerates wildfire frequency, intensity, and season length, tracking global building exposure provides a foundational empirical baseline for urban adaptation, spatial planning, building code enforcement, and disaster risk financing.

This indicator is built according to the **OECD/JRC 10-Step Composite Indicator Pipeline** as operationalized by Building Insights Together (BIT).

---

## 2. Theoretical Framework & Conceptual Model (OECD Step 1)

### 2.1 Dimension
Physical exposure of the global building stock to satellite-observed annual burned areas.

### 2.2 Exposure vs. Direct Damage
In alignment with Forge institutional guidance, spatial intersection between building locations and burned area perimeters establishes **exposure**, not confirmed structural destruction. A building within a burned footprint may have burned down, sustained partial heat/ember damage, or survived due to defensive landscaping, fire suppression, or fire-resistant materials. Distinguishing between exposure and observed building destruction requires high-resolution pre- and post-fire aerial imagery (e.g., USGS Carlson et al., 2025). Indicator 6.1.1 establishes the essential first-order global exposure baseline.

### 2.3 Spatial Unit of Analysis
The fundamental spatial unit is the individual building centroid from GHS-OBAT GLOBE R2024A. Country-level aggregates are computed across all internationally recognized ISO3 territories.

---

## 3. Data Sources & Spatial Resolutions (OECD Step 2)

| Dataset | Provider | Native Resolution | Temporal Scope | Description |
|---|---|---|---|---|
| **GABAM 2024 v3** | AIRCAS / Zenodo (17707433) | 30 m | 2024 annual composite | Global annual burned area GeoTIFF tiles (5° × 5°) derived from Landsat time series. |
| **GHS-OBAT R2024A** | EU JRC | Building centroid | Epoch E2020 | Global Open Building Attribute Table covering ~2.42 billion buildings with lon/lat, height, area, volume. |
| **World Boundaries** | Esri / Natural Earth | Vector | 2024 | Global administrative boundaries used for GABAM tile discovery and national dissolve. |
| **Cloud Storage** | AWS S3 | Object store | Continuous | Dedicated private analyst bucket `bit-alpha-data-802892343761-a955a2d204b1-indicator-6-7491703904`. |

---

## 4. Key Analytical & Methodological Issues Addressed (OECD Steps 3–8)

### 4.1 GABAM 5° Spatial Tile Coordinate Convention (Step 3 & 4)
- **Problem**: GABAM tile filenames (e.g., `N50E005.tif`) encode the **northern** latitude boundary of the 5-degree tile, contrary to conventional lower-left/southwest indexing. Prior pipelines assumed the latitude was the southern boundary, creating a 5° northward displacement globally.
- **Resolution**: Bounding box geometry is strictly mapped as `north = latitude`, `south = latitude - 5`, `west = longitude`, `east = longitude + 5`.

### 4.2 GeoTIFF NoData vs. Unburned Land Value Semantics (Step 3 & 5)
- **Problem**: GABAM GeoTIFF metadata flags `nodata: 0`, but `0` also represents unburned land observations in the binary classification (`0` = unburned, `1` = burned). Standard masked array readers masked out all unburned buildings, collapsing valid pixel counts to equal burned counts (artificial 100% burn rate).
- **Resolution**: Point sampling explicitly evaluates unmasked values, validating `0` as unburned and `1` as burned, reserving NoData classification solely for coordinates outside tile bounds or non-finite pixels.

### 4.3 Spatial Uncertainty & Centroid Buffer Sensitivity (Step 8)
- **Problem**: Large commercial and industrial buildings may span dozens to hundreds of meters. A fire that encroached upon the structure footprint might not cover the mathematical centroid.
- **Resolution**: The pipeline supports centroid-in-pixel sampling as the primary baseline, alongside buffer sensitivity analysis to evaluate boundary uncertainty.

---

## 5. Indicator Output Schema

Each country output produces the standard 27-column audit schema:
- `iso3`: ISO 3166-1 alpha-3 territory code.
- `analysis_year`: Calendar year analyzed (default 2024).
- `total_buildings`: Total building records in source frame.
- `valid_coordinate_buildings`: Buildings with valid coordinates in $[-180, 180] \times [-90, 90]$.
- `invalid_coordinate_buildings`: Quarantine count of corrupted coordinates.
- `tile_covered_buildings`: Buildings falling within intersecting GABAM tile bounds.
- `tile_uncovered_valid_coordinate_buildings`: Valid coordinate buildings missing tile coverage.
- `valid_gabam_pixel_buildings`: Buildings with valid raster data ($0$ or $1$).
- `invalid_or_nodata_gabam_pixel_buildings`: Buildings over nodata pixels within tile extents.
- `exposed_buildings`: Buildings where GABAM pixel $> 0$ ($= 1$).
- `exposed_buildings_percent_total`: $100 \times \text{exposed} / \text{total}$.
- `exposed_buildings_percent_valid_coordinates`: $100 \times \text{exposed} / \text{valid\_coordinates}$.
- `exposed_buildings_percent_valid_gabam_pixels`: $100 \times \text{exposed} / \text{valid\_pixels}$.
- `tile_coverage_percent_valid_coordinates`: $100 \times \text{tile\_covered} / \text{valid\_coordinates}$.
- `valid_pixel_coverage_percent_tile_covered`: $100 \times \text{valid\_pixels} / \text{tile\_covered}$.
- Audit metadata: `gabam_version`, `gabam_record_id`, `ghs_obat_release`, `ghs_obat_epoch`, `processed_chunks`.
