#!/usr/bin/env python3

from setuptools import setup

setup(name='Decoder configuration',
      version='1.0',
      description='PythSoft Loconet Decoder configurtion',
      author='Dirkjan Krijnders',
      author_email='dirkjan@krijnders.net',
      url='',
      packages=['decconf', 'decconf.ui', 'decconf.datamodel', 'decoders'],
	  install_requires=['pyside', 'appdirs', 'yapsy', 'pyserial'],
     )