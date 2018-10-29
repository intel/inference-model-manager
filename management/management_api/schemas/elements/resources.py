RESOURCE_REGEX = "^([+]?[0-9.]+)([eEinumkKMGTP]*[+]?[0-9]*)$"

resources_dict = {
    "type": "string",
    "optional": True,
    "pattern": RESOURCE_REGEX
}

resources = {
    "type": "object",
    "title": "Resource quota",
    "properties": {
        "requests.cpu": resources_dict,
        "limits.cpu": resources_dict,
        "requests.memory": resources_dict,
        "limits.memory": resources_dict
    }
}

max_endpoints = {
    "type": "integer",
    "optional": True,
    "title": "maxEndpoints",
    "minimum": 1
}

quota = resources
quota["properties"]["maxEndpoints"] = max_endpoints

replicas = {
    "type": "integer",
    "optional": True,
    "title": "Replicas",
    "minimum": 0
}
