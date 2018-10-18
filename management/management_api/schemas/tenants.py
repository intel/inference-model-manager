from management_api.schemas.elements.names import tenant_name, scope_name
from management_api.schemas.elements.resources import quota
from management_api.schemas.elements.verifications import cert


tenant_post_schema = {
    "type": "object",
    "title": "Tenant POST Schema",
    "required": [
        "name",
        "cert",
        "scope",
        "quota"
    ],
    "properties": {
        "name": tenant_name,
        "cert": cert,
        "scope": scope_name,
        "quota": quota
    }
}

tenant_delete_schema = {
    "type": "object",
    "title": "Tenant DELETE Schema",
    "required": [
        "name"
    ],
    "properties": {
        "name": tenant_name
    }
}
