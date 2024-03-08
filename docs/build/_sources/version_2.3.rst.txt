.. _version_2.3:
version 2.3 changes
*******************

UKCP grid plotting

0. Added support for the UKCP grid
==================================

Support has been added for the UKCP grid which is an instance of the tranveverse mercator projection.

cfp.mapset(proj='UKCP') will give a transverse mercator projection with the limts of lonmin = -11, 
lonmax = 3, latmin = 49 and latmax = 61.

Some examples of this and other pavailable projections have been added at :ref:`projections<projections>`

New cfp.setvars options affecting the grid plotting for the UKCP grid are:

| grid=True - draw grid
| grid_spacing=1 - grid spacing in degrees
| grid_lons=None - grid longitudes
| gid_lats=None - grid latitudes
| grid_colour='grey' - grid colour
| grid_linestyle='--' - grid line style
| grid_thickness=1.0 - grid thickness

::

    Done



1. Additional projections added - OSGB, EuroPP and TransverseMercator
=====================================================================

OSGB and EuroPP projections have been added.


::

    Done



2. Colourmaps inadvertently removed
===================================

The cf-plot colourmaps directory was inadvertently removed.


::

    Fixed



3. Bug with cyclindrical projection map xlabel and ylabel
=========================================================

A bug with labelling of x and y axes in the cylindrical (PlateCarree) projection
has been fixed.


::

    Fixed


4. Update land, ocean and lake colouring example
================================================

The land, ocean and lake colouring example in :ref:`advanced<advanced>`
was updated to use cartopy code internally in cf-plot


::

    Fixed



5. Bug in blockfill on a map code
=================================

A bug in the blockfill code for maps was fixed.  This bug assumed all blockfill plots were maps which is
incorrect.


::

    Fixed















