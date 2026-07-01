# Changelog

## cf-plot changelog

**Current release: version `3.4.0`, released `2025-04-28`**

*Note*: stated dates of releases correspond to the date a given
version was tagged on GitHub. Up until 2024 some detail may
be missing, with some numbered versions not listed on, or
available from, from the GitHub repository, due to the history
of being developed elsewhere.


-----


### Version `3.5.X`, first released TBC

#### Version `3.5.0`, release TBC

* Modularise the codebase, which has no user-facing implications except
  that functionality is available via sub-modules as well as at the top-level
  e.g. `cfp.con` is available also as `cfp.contour.con`, `cfp.gopen` is also
  `cfp.graphic.graphic.gopen` etc.
  (https://github.com/NCAS-CMS/cf-plot/issues/11)
* Make the internal API obsolete - it is no longer exposed to the user
   (but similar functionality can be added upon request).
* Update the API reference to group and categorise all routines.
* Add missing space between variable name and units in
  colour bar titles (https://github.com/NCAS-CMS/cf-plot/issues/115)
* Update any (documentation) examples which extract a ``Field`` from
  a ``Fieldlist`` of length greater than one to use ``select_by_identity ``
  instead of indexing, for clarity
  (https://github.com/NCAS-CMS/cf-plot/issues/119)
* Add optional animation hooks for external library integration on
  `gopen` (`animation_session_id`, `animation_meta_callback`,
  `animation_frame_callback`) and emit additive animation metadata/frame
  callback payloads from the contour animation path.

### Version `3.4.X`, first released (`3.4.0`) `2025-04-28`

#### Version `3.4.0`, released `2025-04-28`

* Move of codebase home from old repository location of `github.com/ajheaps/cf-plot` to
  `github.com/NCAS-CMS/cf-plot` - the former URL will redirect for the time being
  but cannot be guaranteed to do so in future
* Move of home for documentation: now and going forward hosted permanently at
  `ncas-cms.github.io/cf-plot/` with the previous documentation at root URL
  `ajheaps.github.io/cf-plot/` frozen (no longer updated so do not consult)
* Documentation overhaul including new responsive theme, hierarchical structuring,
   improved navigation, listing of all examples grouped by theme with reorganisation
   of gallery view, updates for informational pages, and more
* New feature: `traj` method can now natively plot *single* trajectories
(i.e. one-dimensional paths, having no trajectory dimension) encoded as
  discrete sampling geometries (https://github.com/NCAS-CMS/cf-plot/issues/84)
* Fix bug whereby `con` contour plot with `verbose=True` would result in
   an `UnboundLocalError` (https://github.com/NCAS-CMS/cf-plot/issues/54)
* Fix bug whereby plots such as with `con` using the 'merc' Mercator projection
    would be cropped to small portion of the y axis
    (https://github.com/NCAS-CMS/cf-plot/issues/65)
* Fix bug whereby the colour bar would be mostly cutoff from the foot of
  the figure for plots such as `con` contour plots when using certain projections
  such as 'ortho', 'merc', and 'lcc' after a call to e.g. `cfp.mapset(proj='ortho')`
  (https://github.com/NCAS-CMS/cf-plot/issues/70)
* Fix bug whereby `con` contour plot in the 'UKCP' projection would
     result in an `IndexError` for `blockfill=True`
     (https://github.com/NCAS-CMS/cf-plot/issues/91) or otherwise an
     `UnboundLocalError` (https://github.com/NCAS-CMS/cf-plot/issues/60)
     or an `AttributeError` (https://github.com/NCAS-CMS/cf-plot/issues/59)
     dependent on other configuration
* Fix bug whereby `con` would result in a blank plot for rotated pole data
  requested for display on its native grid through setting of `cfp.mapset(proj="rotated")`
  (see https://github.com/NCAS-CMS/cf-plot/issues/86)
* Fix bug whereby values at the colour bar extremes in blockfill plots (`con` with
  `blockfill=True`) with `blockfill_fast=None` default would always be shown in white
  (see https://github.com/NCAS-CMS/cf-plot/issues/98)
* Fix bug whereby blockfill plots (`con` with `blockfill=True`) of UGRID data in either polar
  projection (`proj="npstere"` or `proj="spstere"`) could display blacked out areas
  (see https://github.com/NCAS-CMS/cf-plot/issues/99)
* Make consistent the defaults for `feature_zorder` and
   `rotated_grid_thickness` plotting variables as configurable through `setvars`
   (https://github.com/NCAS-CMS/cf-plot/issues/73)
* Set new minimum version of dependency: `'cf-python >= 3.17.0'`
* Set new minimum version of dependency: `'cartopy >= 0.17.0'`
* Removed explicit (listed) dependency to `matplotlib` since this is required already by
  existing dependency Cartopy
* Removed explicit (listed) dependency to `scipy` since this is required already by existing
  dependency cf-python


### Version `3.3.X`, first released (`3.3.0`) `2024-01-15`

#### Version `3.3.0`, released `2024-01-15`

* UGRID support added


### Version `3.2.X`, first released (`3.2.0`) `2023-03-06`

* Rolling bug fix versions


### Version `3.1.X`, first released (`3.1.0`) `2021-04-13`

* UGRID support


### Version `3.0.X`, first released (`3.0.2`) `2019-09-23`

* Port to Python 3 and Mac OSX


### Version `2.4.X`, first released (`2.4.1`) `2019-04-01`

* Trajectories


### Version `2.3.X` first released (`2.3.1`) `2019-03-07`

* Support for the UKCP grid


### Version `2.2.X`, first released (`2.2.18`) `2019-01-30`

* Change from Basemap to Cartopy mapping


### Version `2.1.X`, first released (`2.1.10`) `2017-01-23`

* Rolling set of small additions and bug fixes


### Version `2.0.X`, first released (?) (date unknown)

* Code base changes


### Version `1.9.X`, first released (`1.9.1`) `2016-01-04`

* Rolling update of features


### Version `1.8.X`, first released (`1.8.1`) `2015-12-21`

* Graph plots


### Version `1.7.X`, first released (`1.7.3`) `2015-03-19`

* Rolling update of features


### Version `1.6`, first released (?) (date unknown)

* Rotated pole plots


### Version `1.5`, first released (?) (date unknown)

* Bug/feature fix


### Version `1.4`, first released (?) (date unknown)

* PDF user guide


### Version `1.3.X`, first released (?) (date unknown)

* Bug/feature fix


### Version `1.2`, first released (?) (date unknown)

* Hovmoller plots


### Version `1.1`, first released (?) (date unknown)

* Error handling


### Version `1.0`, first released (?) (date unknown)

* Data interface improvements


### Version `0.9`, first released (?) (date unknown)

* `vect` for vector plotting


### Version `0.8`, first released (?) (date unknown)

* `stipple` for significance plots


### Version `0.7`, first released (?) (date unknown)

* `cscale` for colour scales


### Version `0.6`, first released (?) (date unknown)

* `gopen`, `gclose`, `gpos` opening and closing of output files/plot
  positioning


### Version `0.5`, first released (?) (date unknown)

* latitude-height plots


### Version `0.4`, first released (?) (date unknown)

* `gset`, `axes` for setting plot limits and plotting axes


### Version `0.3`, released `2012-12-10`

* Initial release (first version on GitHub).


-----
