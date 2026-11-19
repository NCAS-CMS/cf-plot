.. _intro:

************
Introduction
************

.. Define external links to use in the docs here

.. _matplotlib:  https://matplotlib.org/
.. _Cartopy:     https://scitools.org.uk/cartopy/docs/latest/
.. _cf-python:   https://ncas-cms.github.io/cf-python/
.. _NCAS-CMS:    https://cms.ncas.ac.uk/index.html
.. _NCAS:        https://ncas.ac.uk/


########
Overview
########

**cf-plot: code-light plotting for earth science and aligned research**
            
cf-plot allows you to produce and customise publication-quality contour, vector,
line and more plots with the power of Python, `matplotlib`_,
`Cartopy`_ and `cf-python`_ in as few lines of code as possible.

.. image:: images/gallery_v360plus.png
   :target: gallery_of_examples.html

It is designed to be a useful visualisation tool for environmental, earth and
aligned sciences, for example to facilitate climate and meteorological research.
cf-plot is developed and maintained by the `NCAS-CMS`_ group, part of `NCAS`_.


###################
Brief Demonstration
###################

In as little as four lines of Python including imports and file reading, using
cf-plot you can for example produce a contour plot showing a 2D subspace of a
netCDF dataset:

.. code-block:: python

   import cf
   import cfplot as cfp
   f = cf.read('<dataset name>.nc')[0]  # picks out a read-in field of the dataset
   cfp.con(f.subspace(time=<chosen time value>))  # creates a contour plot of the field at that time value


################
Examples Gallery
################

A gallery of outputs made with cf-plot, showcasing a range of plotting
possibilities with links to relevant documentation pages and to example code,
can be found on the :ref:`examples page<examples>`, as also linked to the
static image of the gallery at the top of this page.


############
Installation
############

To install cf-plot with its required dependencies, you can use pip:

.. code-block:: bash

   pip install cf-python cf-plot

or you can use conda (or similar package managers such as mamba) as follows
(or equivalent):

.. code-block:: bash

   conda install -c ncas -c conda-forge cf-python cf-plot udunits2

More detail about installation is provided on the
:ref:`installation page<install>` of the documentation.

############
Contributing
############

Everyone is welcome to contribute to cf-plot in the form of bug reports,
documentation, code, design proposals, and more.

Contributing guidelines are available in a
`dedicated document <https://github.com/NCAS-CMS/cf-plot/blob/main/.github/CONTRIBUTING.md>`_
(which is also copied into the documentation :ref:`here<contrib>`).

###############################################
Help: Issues, Questions, Feature Requests, etc.
###############################################

For any queries, see the :ref:`guidance page here<support>`.

