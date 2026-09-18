"""End-to-end pipeline execution for wildfire building exposure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import rasterio

from .catalogue import parse_gabam_tile_name
from .exposure import (
    COUNTRY_RESULT_COLUMNS,
    calculate_percentage,
    classify_wildfire_exposure,
    sample_gabam_values_from_sources,
    validate_country_result,
)
from .s3 import DEFAULT_BUCKET, upload_file_to_s3
from .sensitivity import sample_with_buffer_sensitivity


def run_country_pipeline(
    iso3: str,
    obat_csv_path: Path | str,
    tile_paths: list[Path | str],
    year: int = 2024,
    upload_s3: bool = False,
    s3_bucket: str = DEFAULT_BUCKET,
    out_dir: Path | str = "results/tables",
    run_sensitivity: bool = False,
) -> pd.DataFrame:
    """Run exposure analysis for one country using local data files and optionally push to S3."""
    iso3 = iso3.strip().upper()
    obat_csv_path = Path(obat_csv_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not obat_csv_path.is_file():
        raise FileNotFoundError(f"Building CSV not found: {obat_csv_path}")

    tile_paths = [Path(p) for p in tile_paths]
    for p in tile_paths:
        if not p.is_file():
            raise FileNotFoundError(f"GABAM tile not found: {p}")

    df_buildings = pd.read_csv(obat_csv_path, usecols=["lon", "lat"])
    total_buildings = len(df_buildings)

    valid_mask = (
        df_buildings["lon"].notna()
        & df_buildings["lat"].notna()
        & df_buildings["lon"].between(-180, 180)
        & df_buildings["lat"].between(-90, 90)
    )
    valid_coords = int(valid_mask.sum())
    invalid_coords = total_buildings - valid_coords

    valid_df = df_buildings.loc[valid_mask]

    # Open raster sources
    sources = [rasterio.open(p) for p in tile_paths]
    try:
        sampled_values, tile_covered, valid_pixel = sample_gabam_values_from_sources(
            sources,
            valid_df["lon"].to_numpy(),
            valid_df["lat"].to_numpy(),
        )
        exposed_arr = classify_wildfire_exposure(sampled_values)

        tile_covered_count = int(tile_covered.sum())
        valid_pixel_count = int(valid_pixel.sum())
        exposed_count = int(exposed_arr.sum())

        sensitivity_report = None
        if run_sensitivity and len(valid_df) > 0:
            sensitivity_report = sample_with_buffer_sensitivity(
                sources,
                valid_df["lon"].to_numpy(),
                valid_df["lat"].to_numpy(),
                buffer_meters=(0.0, 15.0, 30.0),
            )
    finally:
        for s in sources:
            s.close()

    result_row = {
        "iso3": iso3,
        "analysis_year": year,
        "gabam_version": "v3",
        "gabam_record_id": 17707433,
        "gabam_archive_md5": "b6c4b70bc95f9c3c30f4dfd5505ef12d",
        "ghs_obat_release": "R2024A",
        "ghs_obat_epoch": "E2020",
        "burned_value_threshold": 0,
        "total_buildings": total_buildings,
        "valid_coordinate_buildings": valid_coords,
        "invalid_coordinate_buildings": invalid_coords,
        "tile_covered_buildings": tile_covered_count,
        "tile_uncovered_valid_coordinate_buildings": valid_coords - tile_covered_count,
        "valid_gabam_pixel_buildings": valid_pixel_count,
        "invalid_or_nodata_gabam_pixel_buildings": tile_covered_count - valid_pixel_count,
        "exposed_buildings": exposed_count,
        "exposed_buildings_percent_total": calculate_percentage(exposed_count, total_buildings),
        "exposed_buildings_percent_valid_coordinates": calculate_percentage(exposed_count, valid_coords),
        "exposed_buildings_percent_valid_gabam_pixels": calculate_percentage(exposed_count, valid_pixel_count),
        "tile_coverage_percent_valid_coordinates": calculate_percentage(tile_covered_count, valid_coords),
        "valid_pixel_coverage_percent_tile_covered": calculate_percentage(valid_pixel_count, tile_covered_count),
        "gabam_tile_count": len(tile_paths),
        "obat_csv_part_count": 1,
        "processed_chunks": 1,
        "partial_test": False,
        "last_completed_part_number": 1,
        "last_completed_chunk_in_part": 1,
    }

    df_result = pd.DataFrame([result_row], columns=COUNTRY_RESULT_COLUMNS)
    validate_country_result(df_result, expected_year=year)

    csv_out = out_dir / f"{iso3}_GABAM{year}.csv"
    df_result.to_csv(csv_out, index=False)

    if sensitivity_report:
        sens_out = out_dir / f"{iso3}_GABAM{year}_sensitivity.json"
        sens_out.write_text(json.dumps(sensitivity_report, indent=2), encoding="utf-8")
        if upload_s3:
            s3_sens_key = f"results/sensitivity/{iso3}_GABAM{year}_sensitivity.json"
            upload_file_to_s3(sens_out, s3_sens_key, bucket=s3_bucket)

    if upload_s3:
        s3_key = f"results/country_results/{iso3}_GABAM{year}.csv"
        upload_file_to_s3(csv_out, s3_key, bucket=s3_bucket)

    return df_result
