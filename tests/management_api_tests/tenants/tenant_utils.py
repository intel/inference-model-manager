from kubernetes.client.rest import ApiException


def does_secret_exist_in_namespace(api_instance, secret_name, secret_namespace):
    try:
        api_instance.read_namespaced_secret(secret_name, secret_namespace)
    except ApiException as apiException:
        if apiException.status == 404:
            return False
    return True


def is_copied_secret_data_matching_original(api_instance, secret_name,
                                            original_secret_namespace,
                                            copied_secret_namespace):
    try:
        original_secret = api_instance.read_namespaced_secret(secret_name,
                                                              original_secret_namespace)
        copied_secret = api_instance.read_namespaced_secret(secret_name, copied_secret_namespace)
    except ApiException as apiException:
        if apiException.status == 404:
            return False
    if original_secret.data == copied_secret.data:
        return True
    return False
