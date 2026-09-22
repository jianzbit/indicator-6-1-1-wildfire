import hashlib
import json
import numpy as np
import pandas as pd
import pytest
import rasterio
from rasterio.transform import from_origin
from wildfire_exposure.exposure import sample_gabam_values_from_sources
from wildfire_exposure.runner import run_country_pipeline
from wildfire_exposure.sensitivity import sample_with_buffer_sensitivity


def raster(path, crs="EPSG:4326", transform=None):
    with rasterio.open(path, "w", driver="GTiff", width=2, height=2,
                       count=1, dtype="uint8", crs=crs,
                       transform=transform or from_origin(0, 2, 1, 1), nodata=0) as dst:
        dst.write(np.array([[1, 0], [0, 1]], dtype="uint8"), 1)


def test_pixel_edges_and_unknowns(tmp_path):
    p = tmp_path / "tile.tif"
    raster(p)
    with rasterio.open(p) as src:
        values, covered, valid = sample_gabam_values_from_sources([src], [0, 0, 2, .5], [2, 0, 1, .5])
        assert covered.tolist() == [True, False, False, True]
        assert valid.tolist() == covered.tolist()
        assert values[0] == 1 and values[3] == 0
        result = sample_with_buffer_sensitivity([src], np.array([10.]), np.array([10.]))
        assert result[0]['unknown_records'] == 1
        assert result[0]['exposure_upper_percent'] == 100


def test_projected_crs_and_missing_crs(tmp_path):
    p = tmp_path / "projected.tif"
    raster(p, "EPSG:3857", from_origin(0, 200000, 100000, 100000))
    with rasterio.open(p) as src:
        values, _, valid = sample_gabam_values_from_sources([src], [.5], [1.5])
        assert valid[0] and values[0] == 1
    raster(p, None)
    with rasterio.open(p) as src, pytest.raises(ValueError, match="CRS"):
        sample_gabam_values_from_sources([src], [.5], [1.5])


def test_manifest_hashes_actual_inputs_and_preserves_unknown(tmp_path):
    p, csv = tmp_path / "tile.tif", tmp_path / "records.csv"
    raster(p)
    pd.DataFrame({'lon': [.5, 10], 'lat': [1.5, 10]}).to_csv(csv, index=False)
    result = run_country_pipeline('LUX', csv, [p], out_dir=tmp_path)
    manifest = json.loads((tmp_path / 'LUX_GABAM2024_manifest.json').read_text())
    assert result.iloc[0]['gabam_archive_md5'] == ''
    for field in ['gabam_version', 'gabam_record_id', 'ghs_obat_release', 'ghs_obat_epoch']:
        assert result.iloc[0][field] == ''
    assert manifest['inputs'][0]['sha256'] == hashlib.sha256(csv.read_bytes()).hexdigest()
    assert manifest['unclassified_records'] == 1
    assert manifest['exposure_lower_percent'] == 50
    assert manifest['exposure_upper_percent'] == 100
    with pytest.raises(ValueError, match='2024'):
        run_country_pipeline('LUX', csv, [p], year=2025, out_dir=tmp_path)


def test_explicit_mask_is_unknown_even_with_binary_values(tmp_path):
    p = tmp_path / 'masked.tif'
    raster(p)
    with rasterio.open(p, 'r+') as dst:
        dst.write_mask(np.array([[0, 255], [255, 255]], dtype='uint8'))
    with rasterio.open(p) as src:
        values, covered, known = sample_gabam_values_from_sources([src], [.5, 1.5], [1.5, 1.5])
    assert covered.tolist() == [True, True]
    assert known.tolist() == [False, True]
    assert np.isnan(values[0]) and values[1] == 0


def test_conflicting_overlap_is_rejected_in_either_order(tmp_path):
    a, b = tmp_path / 'a.tif', tmp_path / 'b.tif'
    raster(a); raster(b)
    with rasterio.open(b, 'r+') as dst:
        dst.write(np.zeros((2, 2), dtype='uint8'), 1)
    with rasterio.open(a) as first, rasterio.open(b) as second:
        for sources in [[first, second], [second, first]]:
            with pytest.raises(ValueError, match='Conflicting'):
                sample_gabam_values_from_sources(sources, [.5], [1.5])
        # Identical overlaps and a known value filling an unknown are allowed.
        values, _, known = sample_gabam_values_from_sources([first, first], [.5], [1.5])
        assert known[0] and values[0] == 1
