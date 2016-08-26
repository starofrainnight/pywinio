#!/usr/bin/env python

from pydgutils_bootstrap import use_pydgutils, download
use_pydgutils()

import os
import os.path
import sys
import shutil
import fnmatch
import glob
import zipfile
import shutil
import pydgutils
import math
from setuptools import setup, find_packages

def download_winio_binary():
    # Download required winio binaries
    winio_url = "http://www.internals.com/utilities/WinIo.zip"
    winio_path = os.path.join(os.curdir, os.path.basename(winio_url))
    if not os.path.exists(winio_path):
        download(winio_url)

    # If existed data directory, we rebuild it
    data_path = os.curdir
    if os.path.exists("WinIO"):
        shutil.rmtree("WinIO")

    # Open the winio zip downloaded_file and unzip to ./data directory.
    winio_zip = zipfile.ZipFile(winio_path)
    winio_zip.extractall(data_path)
    winio_zip.close()

package_name = 'rabird.winio'

# Convert source to v2.x if we are using python 2.x.
our_packages, source_dir = pydgutils.process_packages()
our_requires = pydgutils.process_requirements()

long_description = (
    open("README.rst", "r").read()
    + "\n" +
    open("CHANGES.rst", "r").read()
)

# Prepare winio binary files for setup()
download_winio_binary()

setup(
    name=package_name,
    version="0.1.14",
    author="Hong-She Liang",
    author_email="starofrainnight@gmail.com",
    url="https://github.com/starofrainnight/%s" % package_name,
    description="A wrapper library for WinIO",
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
    ],
    install_requires=our_requires,
    package_dir={"": source_dir},
    packages=our_packages,
    data_files=[("data", glob.glob("WinIO/Binaries/*"))],
    namespace_packages=[package_name.split(".")[0]],
    zip_safe=False,  # Unpack the egg downloaded_file during installation.
)
