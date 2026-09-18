# Indicator 6.1.1 – Buildings in areas impacted by wildfire

## Purpose
Estimate annual building exposure to burned areas.

## Methodology
Intersect GHS-OBAT building locations with GABAM 30 m burned-area pixels (approximately 1985–2021). A natural-vegetation or land-cover mask may be applied after method review.

## Input datasets
- GABAM burned-area dataset
- GHS-OBAT building data
- Optional natural-vegetation or land-cover mask

## Processing workflow
Prepare and validate burned-area rasters, align building locations and CRS, identify buildings intersecting burned pixels, and calculate annual counts and percentages.

## Outputs
Building-level exposure records and annual country or area-level exposure counts and percentages. Raw and generated data remain outside GitHub.

## QA/QC
Check CRS, raster validity, temporal coverage, geometry validity, duplicate buildings, country totals, and plausible annual changes.

## Data provenance
Record source, version, access date, processing parameters, and transformations in project metadata.

## Known limitations
GABAM coverage and resolution constrain detection; building data and burned-area timing may not align. The vegetation mask and final exposure rules require confirmation.

## Status
Initial repository setup; analysis implementation pending.
