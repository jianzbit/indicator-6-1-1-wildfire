"""Five-point geodesic perturbation diagnostic; not a disk/footprint intersection."""
from __future__ import annotations
from typing import Sequence
import numpy as np
import rasterio
from pyproj import Geod
from .exposure import sample_gabam_values_from_sources


def sample_with_buffer_sensitivity(
    tile_sources: Sequence[rasterio.io.DatasetReader], longitude: np.ndarray,
    latitude: np.ndarray, buffer_meters: Sequence[float] = (0.0, 15.0, 30.0),
) -> dict:
    longitude, latitude = np.asarray(longitude, float), np.asarray(latitude, float)
    if longitude.shape != latitude.shape or longitude.ndim != 1:
        raise ValueError('Coordinates must be matching one-dimensional arrays.')
    if any(not np.isfinite(b) or b < 0 for b in buffer_meters):
        raise ValueError('Perturbation distances must be finite and nonnegative.')
    geod = Geod(ellps='WGS84')
    results = {}
    for distance in buffer_meters:
        exposed = np.zeros(len(longitude), dtype=bool)
        all_known = np.ones(len(longitude), dtype=bool)
        samples = [(longitude, latitude)]
        if distance:
            for bearing in (0, 90, 180, 270):
                x, y, _ = geod.fwd(longitude, latitude, np.full(len(longitude), bearing), np.full(len(longitude), distance))
                samples.append((x, y))
        for x, y in samples:
            if len(x):
                values, _, known = sample_gabam_values_from_sources(list(tile_sources), x, y)
                exposed |= known & (values == 1)
                all_known &= known
        classified = exposed | all_known
        n, h, v = len(longitude), int(exposed.sum()), int(classified.sum())
        results[distance] = {
            'exposed_count': h, 'exposed_percent': 100*h/n if n else None,
            'classified_records': v, 'unknown_records': n-v,
            'exposure_lower_percent': 100*h/n if n else None,
            'exposure_upper_percent': 100*(h+n-v)/n if n else None,
            'method': 'centroid plus four geodesic cardinal offsets; not full disk intersection',
        }
    return results
