import numpy as np
import pandas as pd
import pytest
from wildfire_exposure.exposure import (
    classify_wildfire_exposure,
    calculate_percentage,
    validate_country_result,
    COUNTRY_RESULT_COLUMNS,
)

def test_classify_wildfire_exposure():
    vals = np.array([np.nan, 0.0, 1.0, 2.0, -1.0])
    exposed = classify_wildfire_exposure(vals, threshold=0)
    assert not exposed[0] # nan
    assert not exposed[1] # 0.0
    assert exposed[2]     # 1.0
    assert exposed[3]     # 2.0
    assert not exposed[4] # -1.0

def test_calculate_percentage():
    assert calculate_percentage(5, 10) == 50.0
    assert np.isnan(calculate_percentage(5, 0))
    assert np.isnan(calculate_percentage(5, -1))

def test_validate_country_result():
    row = {
        "iso3": "TEST",
        "analysis_year": 2024,
        "gabam_version": "v3",
        "gabam_record_id": 17707433,
        "gabam_archive_md5": "b6c4b70bc95f9c3c30f4dfd5505ef12d",
        "ghs_obat_release": "R2024A",
        "ghs_obat_epoch": "E2020",
        "burned_value_threshold": 0,
        "total_buildings": 100,
        "valid_coordinate_buildings": 95,
        "invalid_coordinate_buildings": 5,
        "tile_covered_buildings": 90,
        "tile_uncovered_valid_coordinate_buildings": 5,
        "valid_gabam_pixel_buildings": 85,
        "invalid_or_nodata_gabam_pixel_buildings": 5,
        "exposed_buildings": 10,
        "exposed_buildings_percent_total": 10.0,
        "exposed_buildings_percent_valid_coordinates": 10.526,
        "exposed_buildings_percent_valid_gabam_pixels": 11.764,
        "tile_coverage_percent_valid_coordinates": 94.736,
        "valid_pixel_coverage_percent_tile_covered": 94.444,
        "gabam_tile_count": 2,
        "obat_csv_part_count": 1,
        "processed_chunks": 1,
        "partial_test": False,
        "last_completed_part_number": 1,
        "last_completed_chunk_in_part": 1,
    }
    df = pd.DataFrame([row], columns=COUNTRY_RESULT_COLUMNS)
    validate_country_result(df, expected_year=2024)

    # Fail on mismatch
    bad_df = df.copy()
    bad_df["total_buildings"] = 999
    with pytest.raises(ValueError):
        validate_country_result(bad_df, expected_year=2024)

def test_exposure_edge_cases():
    # Longitude/latitude shape mismatch
    with pytest.raises(ValueError, match="same length"):
        from wildfire_exposure.exposure import sample_gabam_values_from_sources
        sample_gabam_values_from_sources([None], np.array([1.0]), np.array([1.0, 2.0]))

    # Empty tile sources
    with pytest.raises(ValueError, match="At least one open GABAM raster"):
        from wildfire_exposure.exposure import sample_gabam_values_from_sources
        sample_gabam_values_from_sources([], np.array([1.0]), np.array([1.0]))

    # All invalid coords
    from wildfire_exposure.exposure import sample_gabam_values_from_sources
    v, c, p = sample_gabam_values_from_sources([None], np.array([np.nan]), np.array([np.nan]))
    assert len(v) == 1 and not c[0] and not p[0]

def test_validate_result_errors():
    row = {
        "iso3": "TEST",
        "analysis_year": 2024,
        "gabam_version": "v3",
        "gabam_record_id": 17707433,
        "gabam_archive_md5": "b6c4b70bc95f9c3c30f4dfd5505ef12d",
        "ghs_obat_release": "R2024A",
        "ghs_obat_epoch": "E2020",
        "burned_value_threshold": 0,
        "total_buildings": 100,
        "valid_coordinate_buildings": 95,
        "invalid_coordinate_buildings": 5,
        "tile_covered_buildings": 90,
        "tile_uncovered_valid_coordinate_buildings": 5,
        "valid_gabam_pixel_buildings": 85,
        "invalid_or_nodata_gabam_pixel_buildings": 5,
        "exposed_buildings": 10,
        "exposed_buildings_percent_total": 10.0,
        "exposed_buildings_percent_valid_coordinates": 10.526,
        "exposed_buildings_percent_valid_gabam_pixels": 11.764,
        "tile_coverage_percent_valid_coordinates": 94.736,
        "valid_pixel_coverage_percent_tile_covered": 94.444,
        "gabam_tile_count": 2,
        "obat_csv_part_count": 1,
        "processed_chunks": 1,
        "partial_test": False,
        "last_completed_part_number": 1,
        "last_completed_chunk_in_part": 1,
    }
    df = pd.DataFrame([row], columns=COUNTRY_RESULT_COLUMNS)

    # Missing column
    df_missing = df.drop(columns=["iso3"])
    with pytest.raises(ValueError, match="missing columns"):
        validate_country_result(df_missing)

    # Wrong year
    with pytest.raises(ValueError, match="analysis_year"):
        validate_country_result(df, expected_year=2023)

    # Empty df
    with pytest.raises(ValueError, match="exactly one row"):
        validate_country_result(pd.DataFrame())

    # tile_covered mismatch
    df_tile_err = df.copy()
    df_tile_err["tile_uncovered_valid_coordinate_buildings"] = 99
    with pytest.raises(ValueError, match="Valid coords"):
        validate_country_result(df_tile_err)

    # pixel mismatch
    df_pix_err = df.copy()
    df_pix_err["invalid_or_nodata_gabam_pixel_buildings"] = 99
    with pytest.raises(ValueError, match="Tile covered"):
        validate_country_result(df_pix_err)

    # exposed > total
    df_exp_err = df.copy()
    df_exp_err["exposed_buildings"] = 1000
    with pytest.raises(ValueError, match="ordering is invalid"):
        validate_country_result(df_exp_err)
