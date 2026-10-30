.. _projections:

Projections
***********

The cylindrical and polar stereographic projections are detailed
separately in :ref:`cylindrical plots <cylindrical>` and
:ref:`polar plots <polar>`.


.. include:: examples/example_31.rst

cf-plot looks for auxiliary coordinates of longitude and latitude and
uses them if found. If they aren't present then cf-plot will generate
the grid required using the `projection_x_coordinate` and
`projection_y_coordinate` variables.

For a blockfill plot it uses the latter method and the
supplied bounds.


.. include:: examples/example_32.rst

`cfp.setvars` options affecting the grid plotting for the UKCP grid are:

| grid=True - draw grid
| grid_spacing=1 - grid spacing in degrees
| grid_colour='black' - grid colour
| grid_linestyle='--' - grid line style
| grid_thickness=1.0 - grid thickness

Here we changed the plotted grid with the grid_colour option to
`cfp.setvars`, `xticks` and `yticks` options to `cfp.con`
and make a blockfill plot.


.. include:: examples/example_33.rst


.. include:: examples/example_34.rst

Lambert conformal projections can be cropped.

.. include:: examples/example_35.rst

.. include:: examples/example_36.rst

.. include:: examples/example_37.rst

.. include:: examples/example_38.rst
