model_name = {
    "type": "string",
    "title": "Model name",
    "minLength": 3
}

model_version = {
    "type": "integer",
    "title": "Model version",
    "minimum": 1
}

file_name = {
    "type": "string",
    "title": "Model file name"
}

upload_id = {
    "type": "string",
    "title": "Upload ID to identify whose part is being uploaded"
}

parts = {
    "type": "array",
    "title": "Parts of uploads"
}
