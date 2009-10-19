# -*- coding: utf-8 -*-
from distutils.core import setup

README = ''
try:
    f = open('README')
    README = f.read()
    f.close()
except:
    pass

setup(name='pysrt',
      version='0.1.6',
      author='Jean Boussier',
      author_email='jean.boussier@gmail.com',
      packages=['pysrt'],
      description = "SubRip (.srt) subtitle parser and writer",
      long_description=README,
      license = "GPLv3",
      platforms = ["Independent"],
      keywords = "SubRip srt subtitle",
      url = "http://github.com/byroot/pysrt",
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
