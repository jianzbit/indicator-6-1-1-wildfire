# Indicator 6.1.1: Buildings in areas impacted by wildfire

## Purpose
Estimate building exposure to wildfire-impacted areas using burned-area observations and building locations.

## Method
Exposure is based on building points falling on burned GABAM pixels. The current analysis is implemented in notebook version V4.

## Datasets
- GABAM burned-area data
- GHS-OBAT building data

Raw datasets are not stored in GitHub. See [`data/README.md`](data/README.md) for external data documentation.

## Analysis files
- Notebook: [`notebooks/wildfire_building_exposure_v4.ipynb`](notebooks/wildfire_building_exposure_v4.ipynb)
- Rendered HTML: [`notebooks/exports/wildfire_building_exposure_v4.html`](notebooks/exports/wildfire_building_exposure_v4.html)

## Results

The consolidated result is [`results/tables/global_progress_GABAM2024.csv`](results/tables/global_progress_GABAM2024.csv). It contains 228 country/territory result rows and the full 27-column country-level wildfire exposure schema.

Across the included rows, it contains approximately:

- 2,424,602,307 total buildings
- 6,279,518 exposed buildings
- 0.259% weighted exposure overall

Current QA status is qualified: 8 processing attempts were `completed`, 220 were `completed_low_coverage`, 63 were `skipped`, and 1 was `failed`. The consolidated result should not be described as fully validated or complete without further review.

The 228 country-level CSV files are preserved under [`results/tables/country_results/`](results/tables/country_results/), with one result row per country or territory. The processing log is preserved under [`results/qa/processing_log_GABAM2024.csv`](results/qa/processing_log_GABAM2024.csv). No invalid-country output files or checkpoint files were present in the source archive. The large GeoPackage, raw datasets, raster caches, and temporary/intermediate outputs are excluded from GitHub. Curated final figures will go under `results/figures/`.

## Status
Notebook V4 and the consolidated GABAM 2024 result are organized in this repository. Further QA review and final curation remain pending.
