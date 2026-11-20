.. _configguide:

Configuration guide
*******************

What colours can I use?
=======================

cf-plot supports a variety of **colour values**, where a distinct colour
choice is required, and **colour scales**, for mapping data values to a
well-defined and ordered range of colours. These are described below.

Possible colour values
----------------------

Where a colour **value** can be optionally provided, accepted forms include:

* Named Matplotlib colour values, e.g. ``"blue"``, ``"mediumblue"`` or
  ``"midnightblue"``, including shorthand values such as ``"b"`` (equivalent
  to ``"blue"``) for common colours;
* Hexadecimal RGB or RGBA strings, e.g. ``"#ffffff"`` (white) or
  ``"#7fff00"`` (chartreuse). These are case-insensitive;
* RGB or RGBA (red, green, blue, alpha) tuples of floating-point values
  between ``0.0`` and ``1.0``.

For a full description of the available options, see the
`Matplotlib documentation page for specifying colours
<https://matplotlib.org/stable/users/explain/colors/colors.html>`_.
If a colour value is accepted by Matplotlib, it will also be accepted by
cf-plot.

.. TODO document defaults!


Possible colour scales
----------------------

Where a colour **scale** can be optionally provided, cf-plot accepts a
variety of choices, outlined in the :doc:`colour_scales` guide.

These include a selection of colour scales supported by Matplotlib, as well
as additional scales originating from the NCAR Command Language (NCL) and
IDL.

What map projections can I use?
===============================

cf-plot supports several map projections, which can be selected using the
``proj`` parameter. The available options are:

* ``"cyl"``: Cylindrical equidistant (default);
* ``"rotated"``: Rotated latitude-longitude;
* ``"merc"``: Mercator;
* ``"robin"``: Robinson;
* ``"ortho"``: Orthographic;
* ``"moll"``: Mollweide;
* ``"lcc"``: Lambert Conformal Conic (cropped);
* ``"npstere"``: North Pole polar stereographic;
* ``"spstere"``: South Pole polar stereographic;
* ``"UKCP"``: UK Climate Projections;
* ``"OSGB"``: British National Grid (Ordnance Survey);
* ``"EuroPP"``: European polar stereographic.

For examples, see the :doc:`projections` page.

What line and marker styling can I use?
=======================================

cf-plot supports numerous ways to customise the appearance of plotted lines
and markers.
In addition to changing the colour (see above), you can adjust properties
such as, for lines:

* **Line style**: the appearance of the line, e.g. solid, dashed or dotted;
* **Line width**: the thickness of the line;
* **Transparency**: the opacity of the line.

For a full description of the available line styles and other styling
options, see the
`Matplotlib documentation for lines and markers
<https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html>`_.

.. TODO document defaults!
