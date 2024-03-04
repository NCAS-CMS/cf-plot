# cf-plot

## Code-light plotting for earth science and aligned research

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
[here, on a dedicated page within the documentation](http://ajheaps.github.io/cf-plot/gallery.html), as illustrated
in this (static) image:

![cf-plot example gallery of plots](docs/media/cf_gallery_image.png)


### Documentation

Found under [the cf-plot homepage](http://ajheaps.github.io/cf-plot) (`http://ajheaps.github.io/cf-plot`).
