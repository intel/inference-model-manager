import pytest
from botocore.exceptions import ClientError
from management_api.upload.multipart_utils import create_upload
from management_api.utils.errors_handling import MinioCallException


@pytest.mark.parametrize("raise_exception, create_multipart_return_value",
                         [(True, ClientError(operation_name="test", error_response={})),
                          (False, "test_file_upload_id")])
def test_create_upload(mocker, raise_exception, create_multipart_return_value):
    bucket = "test"
    key = "test-file"
    create_multipart_mock = mocker.patch('management_api.upload.multipart_utils.minio_client.'
                                         'create_multipart_upload')
    if raise_exception:
        with pytest.raises(MinioCallException):
            create_multipart_mock.side_effect = create_multipart_return_value
            create_upload(bucket=bucket, key=key)
    else:

        create_multipart_mock.return_value = {'UploadId': create_multipart_return_value}
        output = create_upload(bucket=bucket, key=key)
        assert create_multipart_return_value == output
    create_multipart_mock.assert_called_once()
