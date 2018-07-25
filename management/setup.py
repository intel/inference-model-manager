from setuptools import setup

setup(
    name='management-api',
    version=0.1,
    description="Management API",
    long_description="""Management API""",
    keywords='',
    author_email='',
    packages=['management_api'],
    include_package_data=True,
    zip_safe=False,
    install_requires=["falcon", "kubernetes", "jsonschema", "requests", "boto3", "botocore"],
    entry_points={
        'console_scripts': [
            'management_api = management_api.main:main',
        ]
    },
)
