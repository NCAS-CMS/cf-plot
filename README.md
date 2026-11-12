# cf-plot

## Code-light plotting for earth science and aligned research


| Category      | Click badge for further information... |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Package       | [![PyPI](https://img.shields.io/pypi/v/cf-plot?color=orange&label=PyPI&logo=python&logoColor=white)](https://pypi.org/project/cf-plot/) [![Conda](https://img.shields.io/conda/vn/conda-forge/cf-plot?color=orange&label=Conda)](https://anaconda.org/conda-forge/cf-plot) [![Python versions](https://img.shields.io/pypi/pyversions/cf-plot.svg?color=orange&logo=python&label=Python&logoColor=white)](https://pypi.org/project/cf-plot/) |
| Documentation | [![Documentation](https://img.shields.io/badge/docs-latest-blue)](https://ncas-cms.github.io/cf-plot/) |
| Repository    | [![release](https://img.shields.io/github/v/release/NCAS-CMS/cf-plot?color=green)](https://github.com/NCAS-CMS/cf-plot/releases) [![contributors](https://img.shields.io/github/contributors/NCAS-CMS/cf-plot?color=green)](https://github.com/NCAS-CMS/cf-plot/graphs/contributors) [![commits-since](https://img.shields.io/github/commits-since/NCAS-CMS/cf-plot/latest.svg?color=green)](https://github.com/NCAS-CMS/cf-plot/commits/main) |
| Testing & CI  | [![Tests](https://github.com/NCAS-CMS/cf-plot/actions/workflows/run-tests.yml/badge.svg)](https://github.com/NCAS-CMS/cf-plot/actions/workflows/run-tests.yml) [![Image comparison tests](https://github.com/NCAS-CMS/cf-plot/actions/workflows/run-image-comparison.yml/badge.svg)](https://github.com/NCAS-CMS/cf-plot/actions/workflows/run-image-comparison.yml) [![Linting and formatting](https://github.com/NCAS-CMS/cf-plot/actions/workflows/linting.yml/badge.svg)](https://github.com/NCAS-CMS/cf-plot/actions/workflows/linting.yml) |
| Quality       | [![Status](https://img.shields.io/badge/status-Production%2FStable-F2C94C)](https://pypi.org/project/cf-plot/) |
| Community     | [![Contributing](https://img.shields.io/badge/contributing-guidelines-pink)](https://github.com/NCAS-CMS/cf-plot/blob/main/CONTRIBUTING.md) [![Code of Conduct](https://img.shields.io/badge/code%20of%20conduct-pink.svg)](https://github.com/NCAS-CMS/cf-plot/blob/main/CODE_OF_CONDUCT.md) |
| Licence       | [![MIT Licence](https://img.shields.io/github/license/NCAS-CMS/cf-plot?color=grey)](https://github.com/NCAS-CMS/cf-plot/blob/main/LICENSE.txt) |


### Overview

![cf-plot example gallery of plots](docs/source/images/new_gallery_view.png "Examples Gallery of plots made with the cf-plot library")

**cf-plot allows you to produce and customise publication-quality contour,
vector, line and more plots with the power of Python,
[matplotlib](https://matplotlib.org/),
[Cartopy](https://scitools.org.uk/cartopy/docs/latest/) and
[cf-python](https://ncas-cms.github.io/cf-python/), in as few lines of code
as possible.**

It is designed to be a useful visualisation tool for environmental, earth
and aligned sciences, for example to facilitate climate and meteorological
research. cf-plot is developed and maintained by the
[NCAS-CMS](https://cms.ncas.ac.uk/index.html) group, part of
[NCAS](https://ncas.ac.uk/).


### Brief Demonstration

In as little as four lines of Python including imports and file reading,
using `cf-plot` you can for example produce a contour plot showing a 2D
subspace of a netCDF dataset:

```python
import cf
import cfplot as cfp
f = cf.read('<dataset name>.nc')[0]  # picks out a read-in field of the dataset
cfp.con(f.subspace(time=<chosen time value>))  # creates a contour plot of the field at that time value
```


### Examples Gallery

A gallery of outputs made with cf-plot, showcasing a range of plotting
possibilities with links to relevant documentation pages and to example code,
can be found
[on this dedicated page within the documentation](https://ncas-cms.github.io/cf-plot/gallery_of_examples.html),
as illustrated in the (static) image at the top of this document.


### Documentation

See [the cf-plot homepage](https://ncas-cms.github.io/cf-plot/)
(`https://ncas-cms.github.io/cf-plot`) for the full online documentation.


### Installation

To install cf-plot with its required dependencies, you can use `pip`:

```bash
pip install cf-plot
```

or you can use `conda` (or similar package managers such
as `mamba`) as follows (or equivalent):

```bash
conda install -c conda-forge cf-python cf-plot udunits2
```

More detail about installation is provided on the
[installation page](https://ncas-cms.github.io/cf-plot/installation.html)
(`https://ncas-cms.github.io/cf-plot/installation.html`)
of the documentation.

### Testing

To run the full test suite, call from the repo root:

``` bash
$ pytest tests
```

Note however this calls image comparison testing on plot outputs and exact
image comparison depends on the environment (libraries and versions) used.
So they may fail if your environment differs from that which was used to
generate the reference images. Therefore, to allow like-for-like comparison,
a specific testing conda environment is provided, ``cfplot-test-env.yml``.
With this environment enabled, the image comparison should pass. Note we
recommend use of `mamba` for environment creation/solving, but `conda`
will also work.

```console
$ # Deactivate all other environments present first
$ mamba env create --file cfplot-test-env.yml --name cfplot-test-env
$ conda activate cfplot-test-env
$ pytest tests
```

However you can disable this aspect with the ``--skip-image-comparison``
or equivalently ``-I`` option to the cf-plot test suite run with `pytest`,
so that only the functional tests run. This is advised when you use any
environment other than the above, except where some library version
differs for the purpose of regression testing on that versioning change.

```console
$ pytest tests -I
```

> [!NOTE]
> More comprehensive testing across different environments is under development
> but is not yet available. For now, use the reference environment to test with.


### Contributing

Everyone is welcome to contribute to cf-plot in the form
of bug reports, documentation, code, design proposals, and more.

Contributing guidelines are available in a
[dedicated document](https://github.com/NCAS-CMS/cf-plot/blob/main/.github/CONTRIBUTING.md) which is
copied into the [documentation here](https://ncas-cms.github.io/cf-plot/support.html#contributing-to-cf-plot).


### Help: Issues, Questions, Feature Requests, etc.

For any queries, see the
[guidance page](https://ncas-cms.github.io/cf-plot/support.html)
(`https://ncas-cms.github.io/cf-plot/support.html`).
