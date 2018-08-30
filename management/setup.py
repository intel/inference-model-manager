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
