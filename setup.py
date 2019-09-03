#!/usr/bin/python

from setuptools import setup
import sys

if sys.version_info < (3,):
    raise RuntimeError("libhxl requires Python 3 or higher")

setup(name='ggeocode',
      version="0.1",
      description='Simple Python library for geocoding placenames to countries, using the free GeoNames dataset.',
      author='David Megginson',
      author_email='megginson@un.org',
      install_requires=[],
      packages=['ggeocode'],
)
