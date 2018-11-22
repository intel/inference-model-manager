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

import logging


def copy(minio_client, src_bucket, dest_bucket, src_key, dest_key):
    copy_source = f"{src_bucket}/{src_key}"
    try:
        response = minio_client.copy_object(Bucket=dest_bucket, CopySource=copy_source,
                                            Key=dest_key)
    except Exception as e:
        logging.error('An error occurred during minio copy: {}'.format(e))
    return response
