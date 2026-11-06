.. _multiple_plots:

Multiple plots
**************



Plots are arranged over rows and columns with the first plot at the
top left and the last plot is the bottom right. Here the margin at the
bottom of the plot is increased with the bottom parameter to ``gopen``
to accomodate a unified colorbar. The colorbars are turned off for
all plots apart from the last one.

.. include:: examples/example_19a.rst


An alternative to wrapping with ``gopen`` and ``gclose`` is supported
through use of the ``gfigure`` context manager which achieves the same
result through an indented block led with the ``with cfp.figure()``
statement. The below shows this in practice to produce the same
result as Example 19a, except using ``gfigure`` instead of ``gopen`` and
``gclose``.

.. include:: examples/example_19d.rst


User specified plot limits are set by first specifying the
``user_position=True`` parameter to gopen and then the plot position to
the ``gpos`` routines. The ``xmin``, ``xmax``, ``ymin``, ``ymax``
paramenters for the plot display area are in normalised coordinates.

Cylidrical projection plots have an additional rider of having a
degree in longitude and latitude being the same size so plots of
this type might not fill the plot area specified as expected.

.. include:: examples/example_19b.rst


The plot position on the page is set manually with the
``user_position=True`` parameter to ``cfp.gopen``
and then passing the required plot size to ``cfp.gpos``.
Two calls to the ``cfp.cbar`` routine place colour bars on the plot.

.. include:: examples/example_19c.rst

