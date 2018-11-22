#
# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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
