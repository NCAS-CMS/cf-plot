# cf-plot

## Code-light plotting for earth science and aligned research

### Overview

cf-plot allows you to produce and customise publication-quality contour, vector, line and more plots
with the power of Python, [matplotlib](https://matplotlib.org/),
[Cartopy](https://scitools.org.uk/cartopy/docs/latest/) and
[cf-python](https://ncas-cms.github.io/cf-python/), in as few lines of code as possible.

It is designed to be a useful tool across the various domains in and around environmental and
earth science, including but not limited to climate and meteorological research.


### Brief Demonstration

In as little as four lines of Python including imports, using `cf-plot` you can
for example produce a contour plot showing a 2D subspace of a netCDF dataset:

```python
import cf
import cfplot as cfp
f = cf.read('<dataset name>.nc')[0]  # picks out a read-in field of the dataset
cfp.con(f.subspace(time=<chosen time value>))  # creates a contour plot of the field at that time value
```


### Examples Gallery

A gallery of outputs made with cf-plot, showcasing a range of plotting possibilities with links to relevant
documentation pages and to example code, can be found
[on this dedicated page within the documentation](http://ajheaps.github.io/cf-plot/gallery.html), as illustrated
in this (static) image:

![cf-plot example gallery of plots](docs/media/cf_gallery_image.png)


### Documentation

See [the cf-plot homepage](http://ajheaps.github.io/cf-plot) (`http://ajheaps.github.io/cf-plot`).


### Installation

To install cf-plot with its required dependencies, you can use `pip`:

```bash
pip install cf-python
pip install cf-plot
```

or you can use `conda` (or similar package managers such
as `mamba`) as follows (or equivalent):

```bash
conda install -c ncas -c conda-forge cf-python cf-plot udunits2
conda install -c conda-forge mpich esmpy
```

More detail about installation is provided on the
[installation page](http://ajheaps.github.io/cf-plot/download.html)
(`http://ajheaps.github.io/cf-plot/download.html`)
of the documentation.

### Contributing

Everyone is welcome to contribute to cf-plot, however the NCAS-CMS team reserve
the right to only accept changes which they consider to improve the codebase
and align with future ambitions for the library.

Contributing guidelines will be added to the repository shortly.


### Queries: Issues, Questions, Feature Requests, etc.

See the [queries guidance page](http://ajheaps.github.io/cf-plot/issues.html)
(`http://ajheaps.github.io/cf-plot/issues.html`).
