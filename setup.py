from __future__ import print_function

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys

from linkhub import __version__

if sys.version_info <= (2, 5):
    error = "ERROR: linkhub requires Python Version 2.6 or above...exiting."
    print(error, file=sys.stderr)
    sys.exit(1)

setup(name = "linkhub",
      version = __version__,
      description = "Linkhub Auth Library",
      long_description = "Linkhub API Authority Library. http://www.linkhub.co.kr",
      author = "Kim Seongjun",
      author_email = "pallet027@gmail.com",
      url = "https://github.com/linkhub-sdk/Linkhub.py",
      download_url = "https://github.com/linkhub-sdk/linkhub.py/archive/"+__version__+".tar.gz",
      packages = ["linkhub"],
      license = "MIT",
      platforms = "Posix; MacOS X; Windows",
      classifiers = ["Development Status :: 5 - Production/Stable",
                     "Intended Audience :: Developers",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                     "Topic :: Internet",
                     "Programming Language :: Python :: 2",
                     "Programming Language :: Python :: 2.6",
                     "Programming Language :: Python :: 2.7",
                     "Programming Language :: Python :: 3",
                     "Programming Language :: Python :: 3.3",
                     "Programming Language :: Python :: 3.4"]
      )