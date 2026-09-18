import pytest
from wildfire_exposure.catalogue import parse_gabam_tile_name

def test_parse_gabam_tile_name_hemispheres():
    # Northern and Eastern
    t1 = parse_gabam_tile_name("N50E005.tif")
    assert t1["north"] == 50.0
    assert t1["south"] == 45.0
    assert t1["west"] == 5.0
    assert t1["east"] == 10.0

    # Equator / Prime Meridian
    t2 = parse_gabam_tile_name("N00E000.tif")
    assert t2["north"] == 0.0
    assert t2["south"] == -5.0
    assert t2["west"] == 0.0
    assert t2["east"] == 5.0

    # Southern and Western
    t3 = parse_gabam_tile_name("S10W020.tif")
    assert t3["north"] == -10.0
    assert t3["south"] == -15.0
    assert t3["west"] == -20.0
    assert t3["east"] == -15.0

def test_parse_gabam_tile_name_invalid():
    with pytest.raises(ValueError):
        parse_gabam_tile_name("invalid_tile.tif")
from pathlib import Path
from zipfile import ZipFile
from wildfire_exposure.catalogue import build_gabam_tile_catalogue

def test_build_gabam_tile_catalogue(tmp_path):
    zip_path = tmp_path / "GABAM2024.zip"
    with ZipFile(zip_path, "w") as z:
        z.writestr("ba_tiles-2024-30m-prob_S90G50M11/N50E005.tif", b"fake raster data")
        z.writestr("ba_tiles-2024-30m-prob_S90G50M11/N55E005.tif", b"fake raster data")
        z.writestr("ba_tiles-2024-30m-prob_S90G50M11/gabam2024.vrt", b"fake vrt data")

    cat = build_gabam_tile_catalogue(zip_path)
    assert len(cat) == 2
    assert "tile_name" in cat.columns
    assert "geometry" in cat.columns
    assert cat.iloc[0]["west"] == 5.0

def test_build_gabam_tile_catalogue_errors(tmp_path):
    # Nonexistent file
    with pytest.raises(FileNotFoundError):
        build_gabam_tile_catalogue(tmp_path / "missing.zip")

    # Empty zip
    empty_zip = tmp_path / "empty.zip"
    with ZipFile(empty_zip, "w") as z:
        pass
    with pytest.raises(ValueError, match="No parsable GABAM"):
        build_gabam_tile_catalogue(empty_zip)

    # Duplicate tile zip
    dup_zip = tmp_path / "dup.zip"
    with ZipFile(dup_zip, "w") as z:
        z.writestr("ba_tiles-2024-30m-prob_S90G50M11/N50E005.tif", b"fake")
        z.writestr("ba_tiles-2024-30m-prob_S90G50M11/sub/N50E005.tif", b"fake")
    with pytest.raises(ValueError, match="Duplicate"):
        build_gabam_tile_catalogue(dup_zip)
