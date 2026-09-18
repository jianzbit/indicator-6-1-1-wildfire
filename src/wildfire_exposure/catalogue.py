"""GABAM tile naming, bounds parsing, and spatial catalogue construction."""

from __future__ import annotations

import re
from pathlib import Path
from zipfile import ZipFile

import geopandas as gpd
from shapely.geometry import box

GABAM_TILE_SIZE_DEGREES = 5
GABAM_ARCHIVE_INNER_DIRECTORY = "ba_tiles-2024-30m-prob_S90G50M11"

GABAM_TILE_PATTERN = re.compile(
    r"^(?P<lat_hemisphere>[NS])(?P<latitude>\d{2})"
    r"(?P<lon_hemisphere>[EW])(?P<longitude>\d{3})\.tif$",
    flags=re.IGNORECASE,
)


def parse_gabam_tile_name(tile_name: str) -> dict:
    """Parse GABAM tile name to extract bounding coordinates and geometry.
    
    IMPORTANT: GABAM tiles follow the convention where the latitude in the filename
    represents the NORTHERN edge of the 5-degree tile, and the longitude represents
    the WESTERN edge.
    For example:
      N50E005.tif -> North=50.0, South=45.0, West=5.0, East=10.0
      N00E005.tif -> North=0.0, South=-5.0, West=5.0, East=10.0
      S10E020.tif -> North=-10.0, South=-15.0, West=20.0, East=25.0
    """
    match = GABAM_TILE_PATTERN.fullmatch(Path(tile_name).name)
    if match is None:
        raise ValueError(f"Unsupported GABAM tile name: {tile_name}")

    latitude = int(match.group("latitude"))
    longitude = int(match.group("longitude"))

    if match.group("lat_hemisphere").upper() == "S":
        latitude *= -1
    if match.group("lon_hemisphere").upper() == "W":
        longitude *= -1

    west = float(longitude)
    north = float(latitude)
    east = west + GABAM_TILE_SIZE_DEGREES
    south = north - GABAM_TILE_SIZE_DEGREES

    return {
        "tile_name": Path(tile_name).name,
        "west": west,
        "south": south,
        "east": east,
        "north": north,
        "geometry": box(west, south, east, north),
    }


def build_gabam_tile_catalogue(archive_path: Path) -> gpd.GeoDataFrame:
    """Build a GeoDataFrame catalogue of all GABAM tiles within an archive."""
    archive_path = Path(archive_path)
    if not archive_path.is_file():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    records = []
    with ZipFile(archive_path, "r") as archive:
        for member in archive.infolist():
            if member.is_dir() or not member.filename.lower().endswith(".tif"):
                continue
            if GABAM_ARCHIVE_INNER_DIRECTORY not in member.filename:
                continue

            parsed = parse_gabam_tile_name(member.filename)
            records.append(
                {
                    **parsed,
                    "archive_member": member.filename,
                    "compressed_size_mb": member.compress_size / 1024**2,
                    "uncompressed_size_mb": member.file_size / 1024**2,
                }
            )

    if not records:
        raise ValueError("No parsable GABAM GeoTIFF tiles were found in archive.")

    catalogue = gpd.GeoDataFrame(
        records,
        geometry="geometry",
        crs="EPSG:4326",
    )

    duplicate_names = catalogue["tile_name"].duplicated(keep=False)
    if duplicate_names.any():
        raise ValueError(
            f"Duplicate GABAM tile names were found: {catalogue.loc[duplicate_names, 'tile_name'].tolist()}"
        )

    return catalogue.sort_values("tile_name").reset_index(drop=True)
