from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import rasterio
from rasterio.transform import from_origin
from wildfire_exposure.exposure import sample_gabam_values_from_sources
from wildfire_exposure.runner import run_country_pipeline

def test_sample_gabam_values(tmp_path):
    raster_path = tmp_path / "N50E005.tif"
    # Create 100x100 synthetic raster from north=50.0, west=5.0 to south=45.0, east=10.0
    transform = from_origin(5.0, 50.0, 0.05, 0.05)
    data = np.zeros((100, 100), dtype=np.uint8)
    # Burn a small patch
    data[10:20, 10:20] = 1

    with rasterio.open(
        raster_path,
        "w",
        driver="GTiff",
        height=100,
        width=100,
        count=1,
        dtype=np.uint8,
        crs="EPSG:4326",
        transform=transform,
        nodata=0,
    ) as dst:
        dst.write(data, 1)

    with rasterio.open(raster_path) as src:
        # Sample inside burned patch (x=5.5, y=49.25)
        # Sample inside unburned (x=6.0, y=48.0)
        # Sample outside bounds (x=4.0, y=48.0)
        lons = np.array([5.75, 6.0, 4.0])
        lats = np.array([49.25, 48.0, 48.0])
        vals, covered, valid = sample_gabam_values_from_sources([src], lons, lats)
        
        assert covered[0] and covered[1] and not covered[2]
        # At index 0, burned value is 1 (valid pixel)
        assert vals[0] == 1.0 and valid[0]
        # At index 1, unburned value is 0 (nodata=0 in raster metadata)
        assert not valid[1] or vals[1] == 0.0

def test_run_country_pipeline(tmp_path):
    raster_path = tmp_path / "N50E005.tif"
    transform = from_origin(5.0, 50.0, 0.05, 0.05)
    data = np.zeros((100, 100), dtype=np.uint8)
    data[10:20, 10:20] = 1
    with rasterio.open(
        raster_path, "w", driver="GTiff", height=100, width=100, count=1,
        dtype=np.uint8, crs="EPSG:4326", transform=transform, nodata=0,
    ) as dst:
        dst.write(data, 1)

    csv_path = tmp_path / "buildings.csv"
    pd.DataFrame({"lon": [5.75, 6.0], "lat": [49.25, 48.0]}).to_csv(csv_path, index=False)

    out_dir = tmp_path / "out"
    res = run_country_pipeline(
        iso3="TEST",
        obat_csv_path=csv_path,
        tile_paths=[raster_path],
        year=2024,
        upload_s3=False,
        out_dir=out_dir,
    )

    assert len(res) == 1
    assert res.iloc[0]["total_buildings"] == 2
    assert res.iloc[0]["tile_covered_buildings"] == 2
    assert res.iloc[0]["exposed_buildings"] == 1
from unittest.mock import patch

def test_runner_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError, match="Building CSV not found"):
        run_country_pipeline("LUX", tmp_path / "missing.csv", [])

    csv_path = tmp_path / "buildings.csv"
    csv_path.write_text("lon,lat\n6.0,49.0")
    with pytest.raises(FileNotFoundError, match="GABAM tile not found"):
        run_country_pipeline("LUX", csv_path, [tmp_path / "missing.tif"])

def test_runner_s3_upload(tmp_path):
    raster_path = tmp_path / "N50E005.tif"
    transform = from_origin(5.0, 50.0, 0.05, 0.05)
    data = np.zeros((100, 100), dtype=np.uint8)
    with rasterio.open(
        raster_path, "w", driver="GTiff", height=100, width=100, count=1,
        dtype=np.uint8, crs="EPSG:4326", transform=transform, nodata=0,
    ) as dst:
        dst.write(data, 1)

    csv_path = tmp_path / "buildings.csv"
    pd.DataFrame({"lon": [6.0], "lat": [48.0]}).to_csv(csv_path, index=False)

    out_dir = tmp_path / "out"
    with patch("wildfire_exposure.runner.upload_file_to_s3") as mock_upload:
        res = run_country_pipeline(
            iso3="TEST",
            obat_csv_path=csv_path,
            tile_paths=[raster_path],
            year=2024,
            upload_s3=True,
            out_dir=out_dir,
        )
        assert len(res) == 1
        assert mock_upload.called
