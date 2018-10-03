import pytest
from botocore.exceptions import ClientError

from management_api.upload.multipart_utils import create_upload, upload_part, complete_upload
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


@pytest.mark.parametrize("raise_exception", [True, False])
def test_upload_part(mocker, raise_exception):
    data = b'part-bytes'
    part_number = 1
    bucket = "test"
    key = "test-file"
    multipart_id = "some-id"
    upload_part_mock = mocker.patch('management_api.upload.multipart_utils.minio_client.'
                                    'upload_part')
    if raise_exception:
        with pytest.raises(MinioCallException):
            upload_part_mock.side_effect = ClientError(operation_name="test", error_response={})
            upload_part(data=data, part_number=part_number, bucket=bucket, key=key,
                        multipart_id=multipart_id)
    else:
        upload_part(data=data, part_number=part_number, bucket=bucket, key=key,
                    multipart_id=multipart_id)
    upload_part_mock.assert_called_once()


@pytest.mark.parametrize("raise_exception", [True, False])
def test_complete_upload(mocker, raise_exception):
    bucket = "test"
    key = "test-file"
    multipart_id = "some-id"
    complete_upload_mock = mocker.patch('management_api.upload.multipart_utils.minio_client.'
                                        'complete_multipart_upload')
    if raise_exception:
        with pytest.raises(MinioCallException):
            complete_upload_mock.side_effect = ClientError(operation_name="test", error_response={})
            complete_upload(bucket=bucket, key=key, multipart_id=multipart_id)
    else:
        complete_upload(bucket=bucket, key=key, multipart_id=multipart_id)

    complete_upload_mock.assert_called_once()
