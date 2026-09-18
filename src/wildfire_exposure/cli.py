"""Command-line interface for indicator 6.1.1: wildfire exposure pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .runner import run_country_pipeline
from .s3 import DEFAULT_BUCKET, upload_file_to_s3


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="wildfire_exposure",
        description="BIT Indicator 6.1.1: Buildings in areas impacted by wildfire",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    # Subcommand: run
    run_cmd = sub.add_parser("run", help="run wildfire exposure pipeline for a country")
    run_cmd.add_argument("--iso3", required=True, help="ISO3 country code (e.g. LUX)")
    run_cmd.add_argument("--buildings", required=True, help="Path to GHS-OBAT buildings CSV")
    run_cmd.add_argument("--tiles", nargs="+", required=True, help="Path(s) to GABAM GeoTIFF tiles")
    run_cmd.add_argument("--year", type=int, default=2024, help="Analysis year (default 2024)")
    run_cmd.add_argument("--out", default="results/tables", help="Output directory")
    run_cmd.add_argument("--sensitivity", action="store_true", help="Run spatial buffer sensitivity analysis")
    run_cmd.add_argument("--s3", action="store_true", help="Sync outputs to AWS S3 bucket")
    run_cmd.add_argument("--bucket", default=DEFAULT_BUCKET, help="AWS S3 bucket name")

    args = parser.parse_args(argv)

    if args.command == "run":
        df = run_country_pipeline(
            iso3=args.iso3,
            obat_csv_path=args.buildings,
            tile_paths=args.tiles,
            year=args.year,
            upload_s3=args.s3,
            s3_bucket=args.bucket,
            out_dir=args.out,
            run_sensitivity=args.sensitivity,
        )
        print(f"Pipeline executed successfully for {args.iso3}:")
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
