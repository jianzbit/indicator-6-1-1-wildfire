from unittest.mock import MagicMock
import pytest
from wildfire_exposure.s3 import upload_file_to_s3, download_file_from_s3, check_s3_key_exists
from botocore.exceptions import ClientError

def test_s3_operations(tmp_path):
    mock_client = MagicMock()
    
    # Upload test
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,c\n1,2,3")
    
    success = upload_file_to_s3(test_file, "results/test.csv", bucket="test-bucket", client=mock_client)
    assert success is True
    mock_client.upload_file.assert_called_once_with(str(test_file), "test-bucket", "results/test.csv")

    # Download test
    dest_file = tmp_path / "downloaded.csv"
    success_dl = download_file_from_s3("results/test.csv", dest_file, bucket="test-bucket", client=mock_client)
    assert success_dl is True
    mock_client.download_file.assert_called_once_with("test-bucket", "results/test.csv", str(dest_file))

    # Check key exists
    exists = check_s3_key_exists("results/test.csv", bucket="test-bucket", client=mock_client)
    assert exists is True

def test_s3_error_handling(tmp_path):
    mock_client = MagicMock()
    mock_client.upload_file.side_effect = ClientError({"Error": {"Code": "403"}}, "upload_file")
    mock_client.download_file.side_effect = ClientError({"Error": {"Code": "404"}}, "download_file")
    mock_client.head_object.side_effect = ClientError({"Error": {"Code": "404"}}, "head_object")

    test_file = tmp_path / "err.csv"
    test_file.write_text("test")

    assert upload_file_to_s3(test_file, "key", client=mock_client) is False
    assert download_file_from_s3("key", tmp_path / "dl.csv", client=mock_client) is False
    assert check_s3_key_exists("key", client=mock_client) is False

def test_upload_missing_file():
    with pytest.raises(FileNotFoundError):
        upload_file_to_s3("nonexistent_path_to_file.csv", "key")
