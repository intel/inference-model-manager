import json


def load_schema(path_to_json):
    with open(path_to_json, 'r') as f:
        schema_data = f.read()
    schema = json.loads(schema_data)
    return schema


tenant_post_schema = load_schema('management_api/schemas/tenant_post_schema.json')
tenant_delete_schema = load_schema('management_api/schemas/tenant_delete_schema.json')

endpoint_post_schema = load_schema('management_api/schemas/endpoint_post_schema.json')
endpoint_delete_schema = load_schema('management_api/schemas/endpoint_delete_schema.json')

model_delete_schema = load_schema('management_api/schemas/model_delete_schema.json')
