from distutils.core import setup, Extension
from distutils.command.build import build
import os
import fnmatch
import sys
import imp
import subprocess


def find_package_data_files(directory):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, '*'):
                filename = os.path.join(root, basename)
                yield filename.replace('cfplot/', '', 1)


package_data = [f for f in find_package_data_files('cfplot/colourmaps')]



setup(
    name="cfplot",
    version="1.7.26",
    author="Andy Heaps",
    author_email="a.j.heaps@reading.ac.uk",
    packages=['cfplot'],
    package_dir={'cfplot':'cfplot'},
    package_data={'cfplot': package_data},
    include_package_data=True,
    url="http://climate.ncas.ac.uk/~andy/cfplot_sphinx/_build/html",
    license='LICENSE.txt',
    description="Climate contour and vector plots in Python",
    long_description=open('README.txt').read(),
)
