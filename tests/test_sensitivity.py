import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from wildfire_exposure.sensitivity import sample_with_buffer_sensitivity

def test_sample_with_buffer_sensitivity(tmp_path):
    raster_path = tmp_path / "N50E005.tif"
    # Create 100x100 raster: north=50.0, west=5.0, res=0.01 deg (~1.1 km)
    transform = from_origin(5.0, 50.0, 0.01, 0.01)
    data = np.zeros((100, 100), dtype=np.uint8)
    # Burn row 10, cols 10 to 20
    data[10, 10:20] = 1

    with rasterio.open(
        raster_path, "w", driver="GTiff", height=100, width=100, count=1,
        dtype=np.uint8, crs="EPSG:4326", transform=transform, nodata=0,
    ) as dst:
        dst.write(data, 1)

    with rasterio.open(raster_path) as src:
        # Centroid exactly on burned pixel (col=15, row=10 -> x=5.15, y=49.9)
        # Centroid just 15m adjacent (row=10.001)
        lons = np.array([5.15, 5.15])
        # pixel row 10 corresponds to y ~ 49.905. 49.905 is inside row 10.
        # Let's test empty case first:
        empty_res = sample_with_buffer_sensitivity([src], np.array([]), np.array([]))
        assert empty_res[0.0]["exposed_count"] == 0

        # Non-empty: pixel (row=10, col=15) is at center (x=5.155, y=49.895)
        res = sample_with_buffer_sensitivity([src], np.array([5.155]), np.array([49.895]))
        assert 0.0 in res
        assert 15.0 in res
        assert 30.0 in res
        assert res[0.0]["exposed_count"] == 1
        assert res[0.0]["exposed_percent"] == 100.0
