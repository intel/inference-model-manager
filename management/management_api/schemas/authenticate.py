from management_api.schemas.elements.verifications import auth_code, refresh_token


authenticate_token_schema = {
    "type": "object",
    "title": "Authenticate token endpoint",
    "oneOf": [{
        "required": [
            "code"
        ]
    },
        {
        "required": [
            "refresh_token"
        ]
    }],
    "properties": {
        "code": auth_code,
        "refresh_token": refresh_token
    }
}
