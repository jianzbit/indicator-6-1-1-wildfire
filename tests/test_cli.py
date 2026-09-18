from pathlib import Path
import pytest
import rasterio
from rasterio.transform import from_origin
import numpy as np
import pandas as pd
from wildfire_exposure.cli import main

def test_cli_run(tmp_path, capsys):
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
    main([
        "run",
        "--iso3", "TEST",
        "--buildings", str(csv_path),
        "--tiles", str(raster_path),
        "--year", "2024",
        "--out", str(out_dir),
        "--sensitivity",
    ])
    captured = capsys.readouterr()
    assert "Pipeline executed successfully for TEST" in captured.out
    assert (out_dir / "TEST_GABAM2024.csv").is_file()
    assert (out_dir / "TEST_GABAM2024_sensitivity.json").is_file()
