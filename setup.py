try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup



setup(
    name="cfplot",
    version="1.7.24",
    author="Andy Heaps",
    author_email="a.j.heaps@reading.ac.uk",
    packages=['cfplot'],
    package_dir={'cfplot':'cfplot'},
    package_data={'cfplot': 'colourmaps/*'},
    include_package_data=True,
    url="http://climate.ncas.ac.uk/~andy/cfplot_sphinx/_build/html",
    license='LICENSE.txt',
    description="Climate contour and vector plots in Python",
    long_description=open('README.txt').read(),
    zip_safe=False
)
