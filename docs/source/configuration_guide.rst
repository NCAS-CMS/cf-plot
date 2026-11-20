.. _configguide:

Configuration guide
*******************

What colours can I use?
=======================

cf-plot supports a variety of **colour values**, where a distinct colour choice
is required, and **colour scales**, for mapping data values to a well-defined
and ordered range of colours. See below.


Possible colour values
----------------------

Where a colour **value** can be optionally provided, accepted forms include:

* named matploltib colour values e.g. "blue", "mediumblue" or "midnightblue",
  including shorthand values e.g. "b" (equal to "blue") for common cases;
* case-insensitive hex RGB or RGBA string, e.g. "#ffffff" (white) or
  "7fff00" (chartreuse);
* RGB or RGBA (red, green, blue, alpha) tuple of float values between
  `0.0` and `1.0`;

but see
https://matplotlib.org/stable/users/explain/colors/colors.html#colors-def
for a full range of possibilities. If a colour value is accepted by matplotlib
it will be accepted by cf-plot.

.. TODO document defaults!


Possible colour scales
----------------------

Where a colour **scale** can be optionally provided, cf-plot accepts a
variety of choices outlined in the colour scale guide:
docs/colour_scales.html. Note these include a selection only of colour
scales supported by matplotlib, plus scales supported by NCAR Command Language
and in the language IDL.


What map projections can I use?
===============================

cf-plot supports several mapping projections which can be set. These are:
        "cyl": cylindrical
        "rotated": rotated
        "merc": Mercator
        "robin": Robinson
        "ortho": Orthographic
        "moll": Mollweide
        "lcc": Cropped Lambert Conformal Conic
        "npstere": north pole polar stereographic
        "spstere": south pole polar stereographic
        "UKCP": UKCP
        "OSGB": OSGB
        "EuroPP": EuroPP

The default is "cyl".


What line styling can I use?
============================

cf-plot supports numerous ways to change the appearance of a plotted line.
As well as changing the colour (see above), one can change the linestyle,
thickness, transparency, and more.

.. TODO document defaults!
