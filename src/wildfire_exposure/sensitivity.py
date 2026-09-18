"""Spatial uncertainty and sensitivity analysis for wildfire building exposure (OECD Step 8)."""

from __future__ import annotations

from typing import Sequence
import numpy as np
import rasterio

from .exposure import classify_wildfire_exposure


def sample_with_buffer_sensitivity(
    tile_sources: Sequence[rasterio.io.DatasetReader],
    longitude: np.ndarray,
    latitude: np.ndarray,
    buffer_meters: Sequence[float] = (0.0, 15.0, 30.0),
    degree_per_meter_lat: float = 1.0 / 111320.0,
) -> dict[float, dict[str, int | float]]:
    """Evaluate spatial boundary uncertainty by sampling concentric buffers around building centroids.
    
    In raster burned-area datasets, a fire boundary may clip the edge of a building footprint
    without covering the centroid. Sampling at nominal centroid (0m), 15m (half-pixel),
    and 30m (one 30m Landsat pixel) quantifies spatial boundary sensitivity.
    
    Returns:
        dict mapping buffer_distance -> {
            'exposed_count': int,
            'exposed_percent': float
        }
    """
    longitude = np.asarray(longitude, dtype=np.float64)
    latitude = np.asarray(latitude, dtype=np.float64)
    total_valid = len(longitude)
    if total_valid == 0:
        return {b: {"exposed_count": 0, "exposed_percent": 0.0} for b in buffer_meters}

    results: dict[float, dict[str, int | float]] = {}

    for buf in buffer_meters:
        if buf == 0.0:
            # Nominal centroid sample
            any_burned = np.zeros(total_valid, dtype=bool)
            for src in tile_sources:
                bounds = src.bounds
                in_tile = (
                    (longitude >= bounds.left)
                    & (longitude < bounds.right)
                    & (latitude >= bounds.bottom)
                    & (latitude < bounds.top)
                )
                if not np.any(in_tile):
                    continue
                indices = np.flatnonzero(in_tile & ~any_burned)
                if indices.size == 0:
                    continue
                coords = zip(longitude[indices], latitude[indices])
                sampled = np.asarray(list(src.sample(coords, indexes=1, masked=False))).reshape(-1)
                burned = (sampled == 1.0)
                any_burned[indices[burned]] = True
        else:
            # Sample 4 directional offsets at buffer distance: North, South, East, West
            d_lat = buf * degree_per_meter_lat
            # Approximate lon conversion using median latitude:
            med_lat = np.nanmedian(latitude) if len(latitude) > 0 else 0.0
            cos_lat = np.cos(np.radians(med_lat))
            d_lon = d_lat / max(cos_lat, 0.01)

            offsets = [(0, 0), (0, d_lat), (0, -d_lat), (d_lon, 0), (-d_lon, 0)]
            any_burned = np.zeros(total_valid, dtype=bool)

            for src in tile_sources:
                bounds = src.bounds
                for off_x, off_y in offsets:
                    test_lon = longitude + off_x
                    test_lat = latitude + off_y
                    in_tile = (
                        (test_lon >= bounds.left)
                        & (test_lon < bounds.right)
                        & (test_lat >= bounds.bottom)
                        & (test_lat < bounds.top)
                    )
                    indices = np.flatnonzero(in_tile & ~any_burned)
                    if indices.size == 0:
                        continue
                    coords = zip(test_lon[indices], test_lat[indices])
                    sampled = np.asarray(list(src.sample(coords, indexes=1, masked=False))).reshape(-1)
                    burned = (sampled == 1.0)
                    any_burned[indices[burned]] = True

        cnt = int(any_burned.sum())
        pct = 100.0 * cnt / total_valid if total_valid > 0 else 0.0
        results[buf] = {"exposed_count": cnt, "exposed_percent": pct}

    return results
