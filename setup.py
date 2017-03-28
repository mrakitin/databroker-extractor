#!/usr/bin/env python

from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='beamlinex',
    version='20170327.000000',
    description='BeamlineX - tools and utilities for experiments',
    author='Maksim Rakitin',
    url='https://github.com/mrakitin/experiments',
    packages=['beamlinex'],
    install_requires=None,
    entry_points={
        "console_scripts": ['beamlinex = beamlinex.beamlinex:beamlinex_cli']
    },
)
