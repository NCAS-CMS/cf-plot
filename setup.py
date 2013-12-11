from distutils.core import setup

setup(
    name="cfplot",
    version="1.1",
    author="Andy Heaps",
    author_email="a.j.heaps@reading.ac.uk",
    packages=['cfplot'],
    url="http://climate.ncas.ac.uk/~andy/cfplot_sphinx/_build/html",
    license='LICENSE.txt',
    description="Climate plots in Python",
    long_description=open('README.txt').read(),
    package_data={'cfplot': ['colourmaps/*']}
)
