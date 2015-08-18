#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()
    
import os
import os.path
import sys
import shutil
import logging
import fnmatch
import glob
import zipfile
import shutil
from six.moves import urllib
import math
import rabird.core.distutils
import rabird.core.logging
from setuptools import setup, find_packages
from distutils.command.build import build

def download_file(url):
    """Helper to download large files
    the only arg is a url
    the downloaded_file will also be downloaded_size
    in chunks and print out how much remains
    """
    
    file_name = os.path.basename(url)
    
    print("Download winio zip package from : %s ..." % (url))
    
    try:
        downloaded_file = os.path.join(os.curdir, file_name)
        
        req = urllib.request.urlopen(url)
        total_size = int(req.info().getheader("Content-Length").strip())
        downloaded_size = 0
        block_size = 16 * 1024 # 16k each chunk
        
        print("Total size of winio zip package : %s" % (total_size))
        
        with open(downloaded_file, "wb") as fp:
            while True:
                readed_buffer = req.read(block_size)
                if not readed_buffer:
                    break
                
                downloaded_size += len(readed_buffer)
                
                print("Downloaded : %s%%" % (math.floor((float(downloaded_size) / float(total_size)) * 100)))
                
                fp.write(readed_buffer)
                
    except urllib.error.HTTPError as e:
        print("HTTP Error: %s %s" % (e.code, url))
        return False
    except urllib.error.URLError as e:
        print("URL Error: %s %s" % (e.reason, url))
        return False
    
    return downloaded_file

class custom_build_command(build):
    def run(self):
      
        # Download required winio binaries
        winio_url = "http://www.internals.com/utilities/WinIo.zip"
        winio_path = os.path.join(os.curdir, os.path.basename(winio_url))
        if not os.path.exists(winio_path):
            download_file(winio_url)
            
        # If existed data directory, we rebuild it
        data_path = os.curdir
        if os.path.exists("WinIO"):
            shutil.rmtree("WinIO")
            
        # Open the winio zip downloaded_file and unzip to ./data directory.
        winio_zip = zipfile.ZipFile(winio_path)
        winio_zip.extractall(data_path)
        winio_zip.close()
        
        build.run(self)

package_name = 'rabird.winio'

# Convert source to v2.x if we are using python 2.x.
source_dir = rabird.core.distutils.preprocess_source()

# Exclude the original source package, only accept the preprocessed package!
our_packages = find_packages(where=source_dir)

our_requires = ['pywin32']

long_description=(
     open("README.rst", "r").read()
     + "\n" +
     open("CHANGES.rst", "r").read()
     )

setup(
    name=package_name,
    version="0.0.9",
    author="Hong-She Liang",
    author_email="starofrainnight@gmail.com",
    url="https://github.com/starofrainnight/%s" % package_name,
    description="The wrapper library for winio",
    long_description=long_description,    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",        
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows", 
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",        
        "Framework :: Rabird",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=our_requires,
    package_dir = {"": source_dir},
    packages=our_packages,
    data_files=[("data", glob.glob("WinIO/Binaries/*"))],
    cmdclass= {
        'build': custom_build_command,
    },
    namespace_packages = [package_name.split(".")[0]],
    zip_safe=False, # Unpack the egg downloaded_file during installation.
    )
