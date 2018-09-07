import falcon
import base64
import binascii
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from management_api.config import ValidityMessage
from management_api.utils.errors_handling import InvalidParamException
from management_api.utils.logger import get_logger
logger = get_logger(__name__)


def validate_cert(cert):
    try:
        pem_data = base64.b64decode(cert, validate=True)
        x509.load_pem_x509_certificate(pem_data, default_backend())
    except binascii.Error:
        raise InvalidParamException("cert", "Error certificate Base64 decoding",
                                    ValidityMessage.CERTIFICATE)
    except ValueError:
        raise InvalidParamException("cert", "Incorrect certificate format",
                                    ValidityMessage.CERTIFICATE)
    logger.info('Initial certificate validation succeeded')
    return True
