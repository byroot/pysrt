# -*- coding: utf-8 -*-
from distutils.core import setup

setup(name='pysrt',
      version='0.1.2',
      author='Jean Boussier',
      author_email='jean.boussier@gmail.com',
      packages=['pysrt'],
      description = "SubRip (.srt) subtitle parser and writer",
      long_description=open('README').read(),
      license = "GPLv3",
      platforms = ["Independent"],
      keywords = "SubRip srt subtitle",
      url = "",
      classifiers = [
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Multimedia :: Video",
          "Topic :: Software Development :: Libraries",
          "Topic :: Text Processing :: Markup",
      ],)
