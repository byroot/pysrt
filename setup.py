#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages


README = ''
try:
    f = open('README.rst')
    README = f.read()
    f.close()
except:
    pass

REQUIRES = ['chardet']

if sys.version_info < (2, 7):
    REQUIRES.append('argparse')

setup(name='pysrt',
      version='1.0.1',
      author='Jean Boussier',
      author_email='jean.boussier@gmail.com',
      packages=['pysrt'],
      description = "SubRip (.srt) subtitle parser and writer",
      long_description=README,
      install_requires=REQUIRES,
      entry_points={'console_scripts': ['srt = pysrt.commands:main']},
      license="GPLv3",
      platforms=["Independent"],
      keywords="SubRip srt subtitle",
      url="https://github.com/byroot/pysrt",
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Multimedia :: Video",
          "Topic :: Software Development :: Libraries",
          "Topic :: Text Processing :: Markup",
      ]
)
