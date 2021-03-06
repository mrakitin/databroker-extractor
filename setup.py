#!/usr/bin/env python

from setuptools import setup, find_packages

# It's not used at the moment since the dependencies cannot be installed by pip from git+http repos:
with open('requirements.txt') as f:
    required = f.read().splitlines()

# From https://docs.python.org/2/distutils/setupscript.html#installing-package-data:
package_data = {'databroker_extractor': ['config/beamlines.json']}

setup(
    name='databroker-extractor',
    version='20170623.000000',
    description='databroker-extractor - tools and utilities for experiments',
    author='Maksim Rakitin',
    url='https://github.com/mrakitin/databroker-extractor',
    packages=find_packages(),
    package_data=package_data,
    install_requires=None,
    entry_points={
        "console_scripts": ['databroker-extractor = databroker_extractor.extractor:extractor_cli']
    },
)
