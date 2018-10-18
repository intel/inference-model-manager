from management_api.schemas.elements.models import model_name, model_version


model_delete_schema = {
    "type": "object",
    "title": "Model DELETE Schema",
    "required": [
        "modelName",
        "modelVersion",
    ],
    "properties": {
        "modelName": model_name,
        "modelVersion": model_version,
    }
}
