from management_api.schemas.elements.models import model_name, model_version
from management_api.schemas.elements.names import endpoint_name, subject_name
from management_api.schemas.elements.resources import replicas, resources


endpoint_post_schema = {
    "type": "object",
    "title": "Endpoint POST Schema",
    "required": [
        "endpointName",
        "modelName",
        "modelVersion",
        "subjectName"
    ],
    "properties": {
        "endpointName": endpoint_name,
        "modelName": model_name,
        "modelVersion": model_version,
        "subjectName": subject_name,
        "replicas": replicas,
        "resources": resources
    }
}

endpoint_delete_schema = {
    "type": "object",
    "title": "Endpoint DELETE Schema",
    "required": [
        "endpointName"
    ],
    "properties": {
        "endpointName": endpoint_name
    }
}

endpoint_patch_schema = {
    "type": "object",
    "title": "Endpoint PATCH Schema",
    "oneOf": [{
        "required": [
            "replicas"
        ]
    },
        {
            "required": [
                "modelName",
                "modelVersion"
            ]
        }
    ],
    "properties": {
        "replicas": replicas,
        "modelName": model_name,
        "modelVersion": model_version
    }
}
