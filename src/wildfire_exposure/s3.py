"""S3 storage and sync utilities for indicator 6.1.1 datasets and outputs."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError

DEFAULT_BUCKET = "bit-alpha-data-802892343761-a955a2d204b1-indicator-6-7491703904"


def get_s3_client(region_name: str = "ca-central-1"):
    """Get a boto3 S3 client with configured region."""
    return boto3.client("s3", region_name=region_name)


def upload_file_to_s3(
    local_path: Path | str,
    s3_key: str,
    bucket: str = DEFAULT_BUCKET,
    client: Any = None,
) -> bool:
    """Upload a local file to S3 storage."""
    client = client or get_s3_client()
    local_path = Path(local_path)
    if not local_path.is_file():
        raise FileNotFoundError(f"File not found: {local_path}")
    try:
        client.upload_file(str(local_path), bucket, s3_key)
        return True
    except ClientError as e:
        print(f"Failed to upload {local_path} to s3://{bucket}/{s3_key}: {e}")
        return False


def download_file_from_s3(
    s3_key: str,
    local_path: Path | str,
    bucket: str = DEFAULT_BUCKET,
    client: Any = None,
) -> bool:
    """Download a file from S3 storage to local path."""
    client = client or get_s3_client()
    local_path = Path(local_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        client.download_file(bucket, s3_key, str(local_path))
        return True
    except ClientError as e:
        print(f"Failed to download s3://{bucket}/{s3_key} to {local_path}: {e}")
        return False


def check_s3_key_exists(
    s3_key: str,
    bucket: str = DEFAULT_BUCKET,
    client: Any = None,
) -> bool:
    """Check if an object exists in S3."""
    client = client or get_s3_client()
    try:
        client.head_object(Bucket=bucket, Key=s3_key)
        return True
    except ClientError:
        return False
