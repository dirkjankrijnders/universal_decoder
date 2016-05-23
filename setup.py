#!/usr/bin/env python3

from setuptools import setup

setup(name='Decoder Configurator',
      version='1.0',
      description='PythSoft Loconet Decoder configurtion',
      author='Dirkjan Krijnders',
      author_email='dirkjan@krijnders.net',
      url='',
      packages=['decconf', 'decconf.ui', 'decconf.protocols', 'decconf.interfaces', 'decconf.datamodel', 'decoders', 'entry_points'],
	  install_requires=['pyside', 'appdirs', 'yapsy', 'pyserial'],
      entry_points={
            'gui_scripts': [
                  'decconf=decconf:main',
                  ],
            },
            'console_scripts': [
                  'bulkLNCVAccess=bulkLNCVaccess:main',
                  ],
            },
     )
