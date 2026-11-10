API reference
*************


API
===


Plotting routines
-----------------

.. autosummary::
   :nosignatures:

   cfplot.con
   cfplot.lineplot
   cfplot.scatter
   cfplot.stipple
   cfplot.stream
   cfplot.traj
   cfplot.vect


Graphics related
----------------

.. autosummary::
   :nosignatures:

   cfplot.gopen
   cfplot.gclose
   cfplot.gpos
   cfplot.gfigure


Configuration related
---------------------

.. autosummary::
   :nosignatures:

   cfplot.axes
   cfplot.axes_plot
   cfplot.cscale
   cfplot.gset
   cfplot.levs
   cfplot.mapset
   cfplot.plotvars
   cfplot.reset
   cfplot.setvars


Colour related
--------------

.. autosummary::
   :nosignatures:

   cfplot.cbar


Utility Routines
----------------

.. autosummary::
   :nosignatures:

   cfplot.add_cyclic
   cfplot.calculate_levels
   cfplot.cf_var_name
   cfplot.cf_var_name_titles
   cfplot.find_dim_names
   cfplot.find_z
   cfplot.fix_floats
   cfplot.generate_titles
   cfplot.ndecs
   cfplot.polar_regular_grid
   cfplot.rgaxes
   cfplot.stipple_points


Validation
----------

.. autosummary::
   :nosignatures:

   cfplot.check_well_formed
   cfplot.orca_check


Deprecated/Obsolete APIs
========================

Deprecations
------------

These functions *are not* intended for user use and will be removed in the next
version. In most cases these have no use in the codebase as of v3.3.0.

.. autosummary::
   :nosignatures:

   regrid

Note the functions ``compare_arrays`` and ``regression_tests`` (version 3.3.0
and earlier) related to testing only so have been moved out of the
functional codebase.


Obsolete Internal API
---------------------

These routines were exposed in the user-facing API at versions 3.3.0 and
below but were marked as not being intended for user use. They have
therefore been removed except for under-the-hood processing at version 3.5.0.
They are listed here for completeness and posterity.

If you made use of any of the functionality provided by these internal-use
routines, and wish to have this in future, please
:ref:`get in touch <ways-to-contact-us>` to let
us know and we may be able to support them again.

* ``_bfill``
* ``_bfill_ugrid``
* ``_cf_data_assign``
* ``_check_data``
* ``_cscale_get_map``
* ``_dim_titles``
* ``_gvals``
* ``_map_title``
* ``_mapaxis``
* ``_plot_map_axes``
* ``_process_color_scales``
* ``_set_map``
* ``_supscr``
* ``_timeaxis``
