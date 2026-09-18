# Indicator 6.1.1: Buildings in areas impacted by wildfire

[![CI](https://github.com/Building-Insights-Together/indicator-6.1.1-wildfire-risk/actions/workflows/ci.yml/badge.svg)](https://github.com/Building-Insights-Together/indicator-6.1.1-wildfire-risk/actions)

## Purpose
Estimate national and global building exposure to wildfire-impacted areas using annual burned-area observations (GABAM) and building centroid locations (GHS-OBAT).

## Architecture & Revision (v0.1 -> v0.2)
This revision builds upon Jian's initial investigation and resolves critical quality and analytical findings:

1. **Spatial Tile Catalog Boundary Fix**:
   - GABAM 5° x 5° GeoTIFF tiles encode the **northern** edge of the tile in the latitude prefix of the filename (e.g. `N50E005.tif` spans Latitude `[45.0, 50.0]`, Longitude `[5.0, 10.0]`), rather than the southern edge.
   - Fixed the bounding box calculation in `wildfire_exposure/catalogue.py`, resolving coverage drops where countries like Luxembourg previously reported ~94.6% coverage due to missing `N55E005.tif`. With the fix, valid coordinate tile coverage reaches 100.0%.

2. **NoData & Masked Array Handling**:
   - GABAM v3 rasters use byte values: `0` (unburned background / NoData in unburned areas) and `1` (burned area).
   - In earlier versions, rasterio's masked sampling flagged `0` as masked/nodata, which caused `valid_gabam_pixel_buildings` to equal `exposed_buildings` for all 228 countries (100% burn rate among 'valid' pixels).
   - The extraction pipeline now distinguishes unburned land from nodata/uncovered areas.

3. **Cloud Storage (AWS S3)**:
   - Configured dedicated private analyst S3 bucket: `bit-alpha-data-802892343761-a955a2d204b1-indicator-6-7491703904`.
   - Raw data (GABAM rasters and GHS-OBAT CSV archives) and results (country results, global progress tables) are stored in and synced to S3.

## Structure
- `src/wildfire_exposure/`: Core Python package (catalogue parsing, sampling, exposure classification, S3 integration).
- `notebooks/`: Original exploratory notebook `wildfire_building_exposure_v4.ipynb`.
- `results/tables/`: Consolidated results and country-level exposure tables.
- `tests/`: Automated unit and integration test suite with high line coverage (>95%).

## Quickstart

```bash
uv sync
uv run pytest --cov=src/wildfire_exposure --cov-report=term-missing
```
