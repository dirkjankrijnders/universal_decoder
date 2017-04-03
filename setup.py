#!/usr/bin/env python3

from setuptools import setup, find_packages

# Borrowed from: https://github.com/glue-viz/glue/blob/master/setup.py
# Copyright (c) 2013, Glue developers

import os
import subprocess
import sys

from glob import glob
from setuptools import Command

from decconf.buildqt import BuildQt

setup(name='decconf',
      version='1.0',
      description='PythSoft Loconet Decoder configurtion',
      author='Dirkjan Krijnders',
      author_email='dirkjan@krijnders.net',
      url='',
      #packages=['decconf', 'decconf.ui', 'decconf.protocols', 'decconf.interfaces', 'decconf.datamodel', 'decoders', 'entry_points'],
      packages = find_packages(),
      cmdclass={'build_qt': BuildQt},
      install_requires=['appdirs', 'yapsy', 'pyserial', 'Qt.py'],
      entry_points={
            'gui_scripts': [
                  'decconf=decconf.entry_points.decoderconf:main',
                  ],
            'console_scripts': [
                  'bulkLNCVAccess=decconf.entry_points.bulkLNCVaccess:main',
                  ],
            },
)
