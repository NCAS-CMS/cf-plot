.. _rotated_pole:

Rotated pole plots
******************

.. include:: examples/example_21b.rst


.. include:: examples/example_22.rst

This plot shows some rotated pole data on the native grid.
Notice the way that the longitude lines are warped away from the
centre of the plot. Data over the equatorial regions show little
of this warping.


.. include:: examples/example_23b.rst


In this plot a cylindrical projection plot of rotated pole data is
overlaid with wind vectors.

|   Care is needed when making vector plots as the vectors can be of two forms:
|   a) eastward wind and westward wind are relative to longitude and
       latitude axes
|   b) x-wind and y-wind are relative to the rotated pole axes

Here we have eastward and westward wind so these can be plotted as
normal over a cylindrical projection. For the case of data in
case b) above, the x-wind and y-wind will need to be appropriately
rotated onto a cylindrical grid.


.. include:: examples/example_23a.rst
