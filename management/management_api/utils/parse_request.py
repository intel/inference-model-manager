import falcon
import json
from json import JSONDecodeError

from management_api.utils.errors_handling import MissingParamException
from management_api.utils.logger import get_logger


logger = get_logger(__name__)


def get_body(req):
    # json.loads will be removed when all JSON Schema will be presented
    try:
        body = json.loads(req.stream.read().decode("utf-8"))
    except JSONDecodeError:
        body = req.media
    except IOError as ie:
        logger.error('Request body is not a proper json: {}'.format(ie))
        raise falcon.HTTPBadRequest('Request body is not a proper json: {}'
                                    .format(ie))
    except Exception as e:
        logger.error('Error occurred during decoding request body: {}'
                     .format(e))
        raise falcon.HTTPBadRequest('Error occurred during decoding request '
                                    'body: {}'.format(e))
    return body


def get_params(body, required_keys):
    for required_key in required_keys:
        if required_key not in body:
            raise MissingParamException(required_key)
