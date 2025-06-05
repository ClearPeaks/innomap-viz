#!/usr/bin/env python

try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import setup

readme = open("README.md").read()
requirements = open("requirements.txt").read().splitlines()

dev_requires = [
    "pre-commit>=3.8.0",
    "flake8>=3.9.2",
    "flake8-annotations>=2.6.2",
    "isort>=5.9.3",
    "bandit>=1.7.9",
    "pytest>=6.2.4",
    "pytest-mock>=3.6.1",
    "coverage>=5.5",
    "pip-tools>=6.2.0"
]

setup(
    name="clearpeaks-template",  # TODO: Change
    version="1.0.0",
    description="Template description",  # TODO: Change
    long_description=readme,
    long_description_content_type="text/markdown",
    author="template username",  # TODO: Change
    author_email="template email",  # TODO: Change
    url="https://github.com/ClearPeaksSL/python-template",  # TODO: Change
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    setup_requires=["pytest"],
    tests_require=dev_requires,
    extras_require={
        "dev": dev_requires
    },
    zip_safe=False,
    keywords="",
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3"
    ]
)
