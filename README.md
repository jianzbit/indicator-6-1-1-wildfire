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
Curated final tables will go under `results/tables/` and curated final figures under `results/figures/`. Intermediate processing outputs and raw data are excluded from the repository.

## Status
Notebook V4 is organized in this repository. Further curation of final results is pending.
