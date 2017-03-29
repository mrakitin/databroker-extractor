#!/usr/bin/env python

from setuptools import setup, find_packages

# It's not used at the moment since the dependencies cannot be installed by pip from git++http repos:
with open('requirements.txt') as f:
    required = f.read().splitlines()

# From https://docs.python.org/2/distutils/setupscript.html#installing-package-data:
package_data = {'beamlinex': ['config/beamlines.json']}

setup(
    name='beamlinex',
    version='20170329.000000',
    description='BeamlineX - tools and utilities for experiments',
    author='Maksim Rakitin',
    url='https://github.com/mrakitin/experiments',
    packages=find_packages(),
    package_data=package_data,
    install_requires=None,
    entry_points={
        "console_scripts": ['beamlinex = beamlinex.beamlinex:beamlinex_cli']
    },
)
