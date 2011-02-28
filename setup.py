#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    
from videoxml import __version__

setup(name='MovieInfo',
      version=__version__,
      scripts=['videoxml.py'],
      author='Todd Kennedy',
      author_email='todd.kennedy@gmail.com',
      url='http://robotholocaust.com',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests', '.git']),
      install_requires=["sqlobject",])