# BIT-INDICATOR-CARD v1: Indicator 6.1.1 — Buildings in areas impacted by wildfire

```
BIT-INDICATOR-CARD v1
----------------------
Name:                    Indicator 6.1.1 — Buildings in areas impacted by wildfire
Version:                 v0.2
Owner:                   Quinn DuPont (Building Insights Together)
Date:                    2026-09-18

Step 1: Dimension & scope:
  Operationalizes building stock exposure to annual wildfire-affected areas globally. The core spatial unit
  is the individual building centroid (GHS-OBAT R2024A, E2020), evaluated against annual 30 m burned area
  observations (GABAM 2024 v3) and aggregated to national ISO3 boundaries (GAUL 2024 / Esri World Countries).
  Unit of analysis: building centroid; country-year aggregate.

Step 2: Sub-indicators & data sources:
  1. Hazard / Event Extent: GABAM 2024 v3 (Zenodo: 17707433, DOI: 10.5281/zenodo.17707433), 30 m Landsat-derived
     global annual burned area map, tiled in 5° × 5° GeoTIFFs across 80°N to 60°S.
  2. Built-environment Exposure Frame: GHS-OBAT GLOBE R2024A (JRC, epoch E2020), providing representative
     longitude/latitude coordinates, height, area, and volume attributes for ~2.42 billion building records worldwide.
  3. Spatial Boundaries: Esri World Countries GeoJSON / Natural Earth 10m Admin-0 boundaries.
  4. Cloud Dataset Mirror: AWS S3 bucket s3://bit-alpha-data-802892343761-a955a2d204b1-indicator-6-7491703904.

Step 3: Missing data & coverage audit:
  - Coordinate validity: Buildings with missing/invalid lon/lat (|lon|>180 or |lat|>90) are quarantined into
    invalid_coordinate_buildings and excluded from spatial sampling.
  - Spatial missingness / tile coverage: Valid coordinates outside GABAM tile extents are explicitly tracked as
    tile_uncovered_valid_coordinate_buildings. A quality threshold (min 99.0%) is audited.
  - Land vs. Water / Off-extent nodata: GABAM raster byte values (0=unburned land, 1=burned area) are sampled
    without conflating nodata metadata with unburned observations.

Step 4: Multivariate & spatial structure:
  - Pure physical exposure indicator: Evaluates the point-in-raster intersection of building centroids with
    burned-area pixels (burned_value_threshold = 0; value == 1 denotes exposed).
  - Spatial autocorrelation: Wildfire events are intrinsically spatially clustered. Building exposure follows
    clustered fire perimeters in wildland-urban interface (WUI) zones.
  - Granularity vs MAUP: Exposure is computed at point/30m pixel resolution before aggregation to ISO3.

Step 5: Normalization:
  - Exposure is computed as absolute exposed building count, as a percentage of total building stock,
    as a percentage of valid-coordinate buildings, and as a percentage of valid GABAM-covered pixels.

Step 6: Weighting:
  - Equal weighting per building unit in standard counts; volume/floorspace weighting supported via GHS-OBAT attributes.

Step 7: Aggregation:
  - Non-compensatory spatial overlay (direct counting of buildings where GABAM pixel == 1).
  - Exposure metrics: exposed_buildings, exposed_buildings_percent_total, exposed_buildings_percent_valid_coordinates.

Step 8: Uncertainty & sensitivity analysis:
  - Spatial boundary uncertainty: Sensitivity to centroid vs buffer/footprint uncertainty. A building centroid
    may miss a burned pixel that touched the perimeter of a large footprint. Sensitivity buffer analysis (e.g. 15–30 m)
    evaluates boundary classification sensitivity.
  - Annual vs cumulative: Annual snapshot (2024) isolates single-year impact; multi-year cumulative tracks union exposure.

Step 9: Visualization & presentation:
  - Multi-tier outputs:
    1. National summary tables (CSV / Parquet) with full 27-column audit schema.
    2. Interactive HTML Folium/Leaflet choropleths binned into standardized risk exposure brackets [0%, 0.1%, 0.5%, 1%, 2%, 5%, 10%, 25%, 100%].
    3. Distribution summaries and execution logs with duration, coverage quality, and quarantine details.

Step 10: Links & policy relevance:
  - Feeds Pillar 6 (Adaptation & Resilience), directly linked to:
    - Indicator 1.1: Existing Building Stock (baseline denominators).
    - Indicator 6.1.2: Historical Flood Exposure.
    - Indicator 6.2: Building-Level Surrounding Vegetation Cover (WUI fuel load).
    - Sendai Framework Target G / SDG 11.5 / SDG 13.1 climate resilience monitoring.

Provenance: Choices recorded in docs/INDICATOR_CARD.md and Forge institutional memory (indicator:6.1.1).
Reproduction: uv run python -m wildfire_exposure run (input -> output reproducible pipeline).
```
