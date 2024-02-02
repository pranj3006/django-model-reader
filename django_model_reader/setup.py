from setuptools import setup, find_packages

setup(
    name='django_model_reader',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django',
    ],
)
