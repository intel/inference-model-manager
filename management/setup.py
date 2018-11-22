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

from setuptools import find_packages, setup

install_requires = []

with open('requirements.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            install_requires.append(line)

setup(
    name='management-api',
    version=0.1,
    description="Management API",
    long_description="""Management API""",
    keywords='',
    author_email='',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    setup_requires=["pytest-runner"],
    tests_require=["pytest==3.7.1", "pytest-mock==1.10.0"],
    entry_points={
        'console_scripts': [
            'management_api = management_api.main:main',
        ]
    },
)
