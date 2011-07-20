#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import pysrt
from setuptools import setup, find_packages
README = ''
try:
    f = open('README.rst')
    README = f.read()
    f.close()
except:
    pass

setup(name='pysrt',
      version='.'.join(str(i) for i in pysrt.VERSION),
      author='Jean Boussier',
      author_email='jean.boussier@gmail.com',
      packages=find_packages(),
      description = "SubRip (.srt) subtitle parser and writer",
      long_description=README,
      license = "GPLv3",
      platforms = ["Independent"],
      keywords = "SubRip srt subtitle",
      url = "http://github.com/byroot/pysrt",
      classifiers = [
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Multimedia :: Video",
          "Topic :: Software Development :: Libraries",
          "Topic :: Text Processing :: Markup",
      ],
      )
