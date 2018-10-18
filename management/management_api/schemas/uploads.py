from management_api.schemas.elements.models import model_name, model_version, upload_id, \
    file_name, parts

multipart_start_schema = {
    "type": "object",
    "title": "Multipart upload start schema",
    "required": [
        "modelName",
        "modelVersion",
        "fileName"
    ],
    "properties": {
        "modelName": model_name,
        "modelVersion": model_version,
        "fileName": file_name
    }
}

multipart_done_schema = {
    "type": "object",
    "title": "Multipart upload done schema",
    "required": [
        "modelName",
        "modelVersion",
        "fileName",
        "uploadId",
        "parts"
    ],
    "properties": {
        "modelName": model_name,
        "modelVersion": model_version,
        "fileName": file_name,
        "uploadId": upload_id,
        "parts": parts
    }
}

multipart_abort_schema = {
    "type": "object",
    "title": "Multipart upload abort schema",
    "required": [
        "modelName",
        "modelVersion",
        "fileName",
        "uploadId"
    ],
    "properties": {
        "modelName": model_name,
        "modelVersion": model_version,
        "fileName": file_name,
        "uploadId": upload_id
    }
}
