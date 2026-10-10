# cf-plot

## Code-light plotting for earth science and aligned research

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
pip install cf-python cf-plot
```

or you can use `conda` (or similar package managers such
as `mamba`) as follows (or equivalent):

```bash
conda install -c ncas -c conda-forge cf-python cf-plot udunits2
```

More detail about installation is provided on the
[installation page](https://ncas-cms.github.io/cf-plot/installation.html)
(`https://ncas-cms.github.io/cf-plot/installation.html`)
of the documentation.

### Refreshing image-test references

If image tests fail after an environment change, inspect the reference,
generated plot and failure diff before accepting the differences. From the
repository root, generate fresh plots using your testing environment:

```bash
python -m pytest tests/integration/test_contour_plot_examples.py tests/integration/test_advanced_plot_examples.py
```

For a complete refresh, avoid `-k` or `::` selectors: targeted runs preserve
old generated images. The
[reference refresh script](scripts/refresh_image_references.py) previews
updates by default. Select examples by filename suffix (for example,
`gen_fig_16b.png` has ID `16b`):

```bash
python scripts/refresh_image_references.py 4 5 16b
# After visually approving these generated plots:
python scripts/refresh_image_references.py 4 5 16b --write
```

Use `--all` instead of example IDs to preview every available generated
baseline, then `--all --write` only after reviewing all selected plots.
The script validates the selection before writing, replaces existing
references, and removes only their failure-diff images; generated plots
are retained. It does not render or automatically approve plots.

Rerun the image tests afterward to verify the updated references and clear
pytest's recorded failures. Review and commit the reference-image changes;
do not accept a genuine plotting regression merely to make tests pass.

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
