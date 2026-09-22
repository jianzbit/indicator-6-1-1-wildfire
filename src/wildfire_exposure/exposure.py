"""Core building sampling, wildfire exposure classification, and validation."""

from __future__ import annotations

from contextlib import ExitStack
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd
import pyproj
import rasterio
from rasterio.enums import MaskFlags
from pyproj import CRS, Transformer

BURNED_VALUE_THRESHOLD = 0
EXPECTED_BINARY_GABAM_VALUES = {0, 1}
OBAT_COORDINATE_CRS = CRS.from_epsg(4326)

COUNTRY_RESULT_COLUMNS = [
    "iso3",
    "analysis_year",
    "gabam_version",
    "gabam_record_id",
    "gabam_archive_md5",
    "ghs_obat_release",
    "ghs_obat_epoch",
    "burned_value_threshold",
    "total_buildings",
    "valid_coordinate_buildings",
    "invalid_coordinate_buildings",
    "tile_covered_buildings",
    "tile_uncovered_valid_coordinate_buildings",
    "valid_gabam_pixel_buildings",
    "invalid_or_nodata_gabam_pixel_buildings",
    "exposed_buildings",
    "exposed_buildings_percent_total",
    "exposed_buildings_percent_valid_coordinates",
    "exposed_buildings_percent_valid_gabam_pixels",
    "tile_coverage_percent_valid_coordinates",
    "valid_pixel_coverage_percent_tile_covered",
    "gabam_tile_count",
    "obat_csv_part_count",
    "processed_chunks",
    "partial_test",
    "last_completed_part_number",
    "last_completed_chunk_in_part",
]


def classify_wildfire_exposure(
    values: np.ndarray,
    threshold: float = BURNED_VALUE_THRESHOLD,
) -> np.ndarray:
    """Classify sampled pixel values as burned (exposed) or unburned.
    
    A building is exposed if the sampled GABAM value is finite and > threshold (e.g. 1 > 0).
    """
    values = np.asarray(values, dtype=np.float32)
    return np.isfinite(values) & (values > threshold)


def calculate_percentage(numerator: int | float, denominator: int | float) -> float:
    """Calculate percentage safely, returning np.nan when denominator <= 0."""
    if denominator <= 0 or not np.isfinite(denominator):
        return np.nan
    return float(100.0 * numerator / denominator)


def sample_gabam_values_from_sources(
    tile_sources: list[rasterio.io.DatasetReader],
    longitude: np.ndarray,
    latitude: np.ndarray,
    additional_nodata_values: set[float] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Sample GABAM raster values for coordinates across multiple tile rasters.
    
    Note on GABAM encoding:
    GABAM GeoTIFF rasters declare nodata: 0 in metadata, but 0 also represents
    unburned pixels on land. Both 0 (unburned) and 1 (burned) are valid data pixels.
    Only out-of-extent or explicitly masked invalid values should be treated as nodata.
    
    Returns:
        values: array of sampled pixel values (float32, np.nan where missing/nodata)
        tile_covered: boolean array indicating whether point lies within any tile's bounding box
        valid_pixel: boolean array indicating whether sampled pixel was valid (0 or 1)
    """
    if not tile_sources:
        raise ValueError("At least one open GABAM raster is required.")

    longitude = np.asarray(longitude, dtype=np.float64)
    latitude = np.asarray(latitude, dtype=np.float64)

    if len(longitude) != len(latitude):
        raise ValueError("Longitude and latitude arrays must have the same length.")

    point_count = len(longitude)
    values = np.full(point_count, np.nan, dtype=np.float32)
    tile_covered = np.zeros(point_count, dtype=bool)
    valid_pixel = np.zeros(point_count, dtype=bool)

    valid_input = (
        np.isfinite(longitude)
        & np.isfinite(latitude)
        & (longitude >= -180)
        & (longitude <= 180)
        & (latitude >= -90)
        & (latitude <= 90)
    )

    if not np.any(valid_input):
        return values, tile_covered, valid_pixel

    sample_x = np.full(point_count, np.nan, dtype=np.float64)
    sample_y = np.full(point_count, np.nan, dtype=np.float64)
    valid_indices = np.flatnonzero(valid_input)

    sample_x[valid_indices] = longitude[valid_indices]
    sample_y[valid_indices] = latitude[valid_indices]

    for source in tile_sources:
        if source.crs is None:
            raise ValueError("GABAM raster must declare a CRS.")
        # Transform each raster independently, then use actual pixel indices.
        # Bounding-box tests mishandle north/south edges and rotated grids.
        x, y = Transformer.from_crs(OBAT_COORDINATE_CRS, source.crs, always_xy=True).transform(
            longitude[valid_indices], latitude[valid_indices])
        finite = np.isfinite(x) & np.isfinite(y)
        indices = valid_indices[finite]
        sample_x[indices], sample_y[indices] = np.asarray(x)[finite], np.asarray(y)[finite]
        rows, cols = rasterio.transform.rowcol(source.transform, sample_x[indices], sample_y[indices])
        in_grid = (np.asarray(rows) >= 0) & (np.asarray(rows) < source.height) & (np.asarray(cols) >= 0) & (np.asarray(cols) < source.width)
        inside = np.zeros(point_count, dtype=bool)
        inside[indices[in_grid]] = True
        tile_covered |= inside

        # Inspect overlaps too: contradictory known observations must not depend
        # on the caller's tile order.
        candidate_indices = np.flatnonzero(inside)
        if candidate_indices.size == 0:
            continue

        coordinates = zip(sample_x[candidate_indices], sample_y[candidate_indices])
        # Ignore nodata=0 only for the declared binary-background convention.
        # An explicit internal/sidecar/alpha mask carries additional information
        # and must remain unknown even when its stored pixel happens to be 0/1.
        flags = source.mask_flag_enums[0]
        explicit_mask = MaskFlags.per_dataset in flags or MaskFlags.alpha in flags
        sampled = list(source.sample(coordinates, indexes=1, masked=explicit_mask))
        numeric_values = np.ma.concatenate(sampled).astype(np.float32).filled(np.nan)

        # In GABAM, both 0 (unburned) and 1 (burned) are valid observations.
        sample_valid = np.isfinite(numeric_values) & np.isin(numeric_values, [0.0, 1.0])

        if additional_nodata_values:
            sample_valid &= ~np.isin(numeric_values, list(additional_nodata_values))

        previous = values[candidate_indices]
        conflicting = sample_valid & np.isfinite(previous) & (previous != numeric_values)
        if conflicting.any():
            raise ValueError("Conflicting valid overlapping GABAM raster samples")

        target_indices = candidate_indices[sample_valid]
        values[target_indices] = numeric_values[sample_valid]
        valid_pixel[target_indices] = True

    return values, tile_covered, valid_pixel


def validate_country_result(result: pd.DataFrame, expected_year: int = 2024) -> None:
    """Validate country exposure result columns and mathematical identities."""
    if len(result) != 1:
        raise ValueError("Country result must contain exactly one row.")

    missing = set(COUNTRY_RESULT_COLUMNS) - set(result.columns)
    if missing:
        raise ValueError(f"Country result is missing columns: {sorted(missing)}")

    row = result.iloc[0]
    if int(row["analysis_year"]) != expected_year:
        raise ValueError(
            f"analysis_year {row['analysis_year']} does not match expected {expected_year}."
        )

    # Count identities
    total = int(row["total_buildings"])
    valid_coords = int(row["valid_coordinate_buildings"])
    invalid_coords = int(row["invalid_coordinate_buildings"])
    if valid_coords + invalid_coords != total:
        raise ValueError("Total buildings != valid_coords + invalid_coords.")

    tile_covered = int(row["tile_covered_buildings"])
    tile_uncovered = int(row["tile_uncovered_valid_coordinate_buildings"])
    if tile_covered + tile_uncovered != valid_coords:
        raise ValueError("Valid coords != tile_covered + tile_uncovered.")

    valid_pixels = int(row["valid_gabam_pixel_buildings"])
    invalid_or_nodata = int(row["invalid_or_nodata_gabam_pixel_buildings"])
    if valid_pixels + invalid_or_nodata != tile_covered:
        raise ValueError("Tile covered != valid_pixels + invalid_or_nodata.")

    exposed = int(row["exposed_buildings"])
    if not (0 <= exposed <= valid_pixels <= tile_covered <= valid_coords <= total):
        raise ValueError("Country result count ordering is invalid.")
