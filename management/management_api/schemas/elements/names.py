NAME_REGEX = "^[a-z0-9]([-a-z0-9]*[a-z0-9])?$"

tenant_name = {
    "type": "string",
    "title": "Tenant name",
    "pattern": NAME_REGEX,
    "minLength": 3,
    "maxLength": 63
}

endpoint_name = {
    "type": "string",
    "title": "Endpoint name",
    "pattern": NAME_REGEX,
    "minLength": 3
}

scope_name = {
    "type": "string",
    "title": "Keystone scope name"
}

subject_name = {
    "type": "string",
    "title": "Subject name",
    "pattern": "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\\-]*[a-zA-Z0-9])\\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\\-]*[A-Za-z0-9])$"  # noqa
}
