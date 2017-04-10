""" Setuptools configuration for decconf"""

#!/usr/bin/env python3

from setuptools import setup, find_packages

# Borrowed from: https://github.com/glue-viz/glue/blob/master/setup.py
# Copyright (c) 2013, Glue developers

from decconf.buildqt import BuildQt

setup(name='decconf',
      version='1.0',
      description='PythSoft Loconet Decoder configurtion',
      author='Dirkjan Krijnders',
      author_email='dirkjan@krijnders.net',
      url='',
      packages=find_packages(),
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
     test_suite='nose.collector'
     )
