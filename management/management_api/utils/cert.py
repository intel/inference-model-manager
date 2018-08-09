import falcon
import base64
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from management_api.utils.logger import get_logger
logger = get_logger(__name__)


def validate_cert(cert):
    try:
        pem_data = base64.b64decode(cert)
        x509.load_pem_x509_certificate(pem_data, default_backend())
    except TypeError:
        logger.error('Incorrect certificate data in request body. '
                     'Base64 decoding failure.')
        raise falcon.HTTPBadRequest('Incorrect certificate data in request body'
                                    '. Base64 decoding failure.')
    except ValueError:
        logger.error('Incorrect certificate format')
        raise falcon.HTTPBadRequest('Incorrect certificate format')
    logger.info('Initial certificate validation succeeded')
    return True
