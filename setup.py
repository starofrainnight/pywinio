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
import urllib2
import math
import rabird.core.distutils
import rabird.core.logging
from setuptools import setup, find_packages
from setuptools.command.install import install
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
        
        req = urllib2.urlopen(url)
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
                
    except urllib2.HTTPError, e:
        print "HTTP Error:", e.code, url
        return False
    except urllib2.URLError, e:
        print "URL Error:", e.reason, url
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

from_package = 'src'
to_package = 'rabird'
package_name = 'rabird.winio'

# Convert source to v2.x if we are using python 2.x.
rabird.core.distutils.preprocess_sources_for_compatible(from_package, os.path.realpath(os.curdir))

# Exclude the original source package, only accept the preprocessed package!
our_packages = find_packages(exclude=[from_package, '%s.*' % (from_package)])

our_packages = find_packages()
our_requires = ['pywin32']

setup(
    name=package_name,
    version="0.0.7",
    author="Hong-She Liang",
    author_email="starofrainnight@gmail.com",
    url="",
    zip_safe=False, # Unpack the egg downloaded_file during installation.
    py_modules=[package_name],
    description="%s library" % package_name,
    keywords = "winio",
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries",
    ],
    install_requires=our_requires,
    packages=our_packages,
    data_files=[("data", glob.glob("WinIO/Binaries/*"))],
    cmdclass= {
        'build': custom_build_command,
    },
    namespace_packages = [to_package],
    )
