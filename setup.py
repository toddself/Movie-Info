#!/usr/bin/env python

from distutils.core import setup
from videoxml import __version__

setup(name='movieinfo',
      version=__version__,
      scripts=['videoxml.py'],
      packages=['tmdb'],)