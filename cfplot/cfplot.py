"""
Climate contour/vector plots using cf-python, matplotlib and cartopy.
Andy Heaps NCAS-CMS April 2021
"""
import numpy as np
import subprocess
from scipy import interpolate
import matplotlib
from copy import deepcopy
import os
import sys
import matplotlib.pyplot as plot
from matplotlib.collections import PolyCollection
from distutils.version import StrictVersion
import cartopy
import cartopy.crs as ccrs
import cartopy.util as cartopy_util
import cartopy.feature as cfeature
from scipy.interpolate import griddata
import shapely.geometry as sgeom
import shapely
from matplotlib.collections import PatchCollection

# Check for the minimum cf-python version
cf_version_min = '3.0.0b2'
errstr = '\n\n cf-python > ' + cf_version_min
errstr += '\n needs to be installed to use cf-plot \n\n'
try:
    import cf
    if StrictVersion(cf.__version__) < StrictVersion(cf_version_min):
        raise Warning(errstr)
except ImportError:
    raise Warning(errstr)


# Initiate the pvars class
# This is used for storing plotting variables in cfp.plotvars
class pvars(object):
    def __init__(self, **kwargs):
        '''Initialize a new Pvars instance'''
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def __str__(self):
        '''x.__str__() <==> str(x)'''
        a = None
        v = None
        out = ['%s = %s' % (a, repr(v))]
        for a, v in self.__dict__.items():
            return '\n'.join(out)


# Check for a display and use the Agg backing store if none is present
# This is for batch mode processing
try:
    disp = os.environ["DISPLAY"]
except Exception:
    matplotlib.use('Agg')


# Check for user setting of pre_existing_data_dir pointing to central cartopy setup
# This is used in the cfview simple setup process
try:
    pre_existing_data_dir = os.environ["pre_existing_data_dir"]
    cartopy.config["pre_existing_data_dir"] = pre_existing_data_dir
except:
    pass



# Code to check if the ImageMagick display command is available
def which(program):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    def ext_candidates(fpath):
        yield fpath
        for ext in os.environ.get("PATHEXT", "").split(os.pathsep):
            yield fpath + ext

    for path in os.environ["PATH"].split(os.pathsep):
        exe_file = os.path.join(path, program)
        for candidate in ext_candidates(exe_file):
            if is_exe(candidate):
                return candidate

    return None


# Default colour scales
# cscale1 is a differential data scale - blue to red
cscale1 = ['#0a3278', '#0f4ba5', '#1e6ec8', '#3ca0f0', '#50b4fa', '#82d2ff',
           '#a0f0ff', '#c8faff', '#e6ffff', '#fffadc', '#ffe878', '#ffc03c',
           '#ffa000', '#ff6000', '#ff3200', '#e11400', '#c00000', '#a50000']

# viridis is a continuous data scale - blue, green, yellow
viridis = ['#440154', '#440255', '#440357', '#450558', '#45065a', '#45085b',
           '#46095c', '#460b5e', '#460c5f', '#460e61', '#470f62', '#471163',
           '#471265', '#471466', '#471567', '#471669', '#47186a', '#48196b',
           '#481a6c', '#481c6e', '#481d6f', '#481e70', '#482071', '#482172',
           '#482273', '#482374', '#472575', '#472676', '#472777', '#472878',
           '#472a79', '#472b7a', '#472c7b', '#462d7c', '#462f7c', '#46307d',
           '#46317e', '#45327f', '#45347f', '#453580', '#453681', '#443781',
           '#443982', '#433a83', '#433b83', '#433c84', '#423d84', '#423e85',
           '#424085', '#414186', '#414286', '#404387', '#404487', '#3f4587',
           '#3f4788', '#3e4888', '#3e4989', '#3d4a89', '#3d4b89', '#3d4c89',
           '#3c4d8a', '#3c4e8a', '#3b508a', '#3b518a', '#3a528b', '#3a538b',
           '#39548b', '#39558b', '#38568b', '#38578c', '#37588c', '#37598c',
           '#365a8c', '#365b8c', '#355c8c', '#355d8c', '#345e8d', '#345f8d',
           '#33608d', '#33618d', '#32628d', '#32638d', '#31648d', '#31658d',
           '#31668d', '#30678d', '#30688d', '#2f698d', '#2f6a8d', '#2e6b8e',
           '#2e6c8e', '#2e6d8e', '#2d6e8e', '#2d6f8e', '#2c708e', '#2c718e',
           '#2c728e', '#2b738e', '#2b748e', '#2a758e', '#2a768e', '#2a778e',
           '#29788e', '#29798e', '#287a8e', '#287a8e', '#287b8e', '#277c8e',
           '#277d8e', '#277e8e', '#267f8e', '#26808e', '#26818e', '#25828e',
           '#25838d', '#24848d', '#24858d', '#24868d', '#23878d', '#23888d',
           '#23898d', '#22898d', '#228a8d', '#228b8d', '#218c8d', '#218d8c',
           '#218e8c', '#208f8c', '#20908c', '#20918c', '#1f928c', '#1f938b',
           '#1f948b', '#1f958b', '#1f968b', '#1e978a', '#1e988a', '#1e998a',
           '#1e998a', '#1e9a89', '#1e9b89', '#1e9c89', '#1e9d88', '#1e9e88',
           '#1e9f88', '#1ea087', '#1fa187', '#1fa286', '#1fa386', '#20a485',
           '#20a585', '#21a685', '#21a784', '#22a784', '#23a883', '#23a982',
           '#24aa82', '#25ab81', '#26ac81', '#27ad80', '#28ae7f', '#29af7f',
           '#2ab07e', '#2bb17d', '#2cb17d', '#2eb27c', '#2fb37b', '#30b47a',
           '#32b57a', '#33b679', '#35b778', '#36b877', '#38b976', '#39b976',
           '#3bba75', '#3dbb74', '#3ebc73', '#40bd72', '#42be71', '#44be70',
           '#45bf6f', '#47c06e', '#49c16d', '#4bc26c', '#4dc26b', '#4fc369',
           '#51c468', '#53c567', '#55c666', '#57c665', '#59c764', '#5bc862',
           '#5ec961', '#60c960', '#62ca5f', '#64cb5d', '#67cc5c', '#69cc5b',
           '#6bcd59', '#6dce58', '#70ce56', '#72cf55', '#74d054', '#77d052',
           '#79d151', '#7cd24f', '#7ed24e', '#81d34c', '#83d34b', '#86d449',
           '#88d547', '#8bd546', '#8dd644', '#90d643', '#92d741', '#95d73f',
           '#97d83e', '#9ad83c', '#9dd93a', '#9fd938', '#a2da37', '#a5da35',
           '#a7db33', '#aadb32', '#addc30', '#afdc2e', '#b2dd2c', '#b5dd2b',
           '#b7dd29', '#bade27', '#bdde26', '#bfdf24', '#c2df22', '#c5df21',
           '#c7e01f', '#cae01e', '#cde01d', '#cfe11c', '#d2e11b', '#d4e11a',
           '#d7e219', '#dae218', '#dce218', '#dfe318', '#e1e318', '#e4e318',
           '#e7e419', '#e9e419', '#ece41a', '#eee51b', '#f1e51c', '#f3e51e',
           '#f6e61f', '#f8e621', '#fae622', '#fde724']

# Read in defaults if they exist and overlay
# for contour options of fill, blockfill and lines
global_fill = True
global_lines = True
global_blockfill = False
global_degsym = False
global_viewer = 'display'
defaults_file = os.path.expanduser("~") + '/.cfplot_defaults'
if os.path.exists(defaults_file):
    with open(defaults_file) as file:
        for line in file:
            vals = line.split(' ')
            com, val = vals
            v = False
            if val.strip() == 'True':
                v = True
            if com == 'blockfill':
                global_blockfill = v
            if com == 'lines':
                global_lines = v
            if com == 'fill':
                global_fill = v
            if com == 'degsym':
                global_degsym = v
            if com == 'viewer':
                global_viewer = val.strip()

# plotvars - global plotting variables
plotvars = pvars(lonmin=-180, lonmax=180, latmin=-90, latmax=90, proj='cyl',
                 resolution='110m', plot_type=1, boundinglat=0, lon_0=0,
                 levels=None,
                 levels_min=None, levels_max=None, levels_step=None,
                 norm=None, levels_extend='both', xmin=None,
                 xmax=None, ymin=None, ymax=None, xlog=None, ylog=None,
                 rows=1, columns=1, file=None, orientation='landscape',
                 user_mapset=0, user_gset=0, cscale_flag=0, user_levs=0,
                 user_plot=0, master_plot=None, plot=None, cs=cscale1,
                 cs_user='cscale1', mymap=None, xticks=None, yticks=None,
                 xticklabels=None, yticklabels=None, xstep=None, ystep=None,
                 xlabel=None, ylabel=None, title=None, title_fontsize=15,
                 axis_label_fontsize=11, text_fontsize=11,
                 text_fontweight='normal', axis_label_fontweight='normal',
                 colorbar_fontsize=11, colorbar_fontweight='normal',
                 title_fontweight='normal', continent_thickness=None,
                 continent_color=None, continent_linestyle=None,
                 pos=1, viewer=global_viewer, global_viewer=global_viewer,
                 tspace_year=None, tspace_month=None, tspace_day=None,
                 tspace_hour=None, xtick_label_rotation=0,
                 xtick_label_align='center', ytick_label_rotation=0,
                 ytick_label_align='right', legend_text_size=11,
                 legend_text_weight='normal',
                 cs_uniform=True, master_title=None,
                 master_title_location=[0.5, 0.95], master_title_fontsize=30,
                 master_title_fontweight='normal', dpi=None,
                 plot_xmin=None, plot_xmax=None, plot_ymin=None,
                 plot_ymax=None, land_color=None, ocean_color=None,
                 lake_color=None, twinx=False, twiny=False,
                 rotated_grid_thickness=2.0, rotated_grid_spacing=10,
                 rotated_deg_spacing=0.75, rotated_continents=True,
                 rotated_grid=True, rotated_labels=True,
                 legend_frame=True, legend_frame_edge_color='k',
                 legend_frame_face_color=None, degsym=global_degsym,
                 axis_width=None, grid=True, grid_spacing=1,
                 grid_colour='k', grid_linestyle='--',
                 grid_thickness=1.0, aspect='equal',
                 graph_xmin=None, graph_xmax=None,
                 graph_ymin=None, graph_ymax=None,
                 level_spacing=None, tight=False, gpos_called=False,
                 titles_con_called=False)

# Check for iPython notebook inline
# and set the viewer to None if found
is_inline = 'inline' in matplotlib.get_backend()
if is_inline:
    plotvars.viewer = None

# Check for OSX and if so use matplotlib for for the viewer
# Not all users will have ImageMagick installed / XQuartz running
# Users can still select this with cfp.setvars(viewer='display')
if sys.platform == 'darwin':
    plotvars.global_viewer = 'matplotlib'
    plotvars.viewer = 'matplotlib'


def con(f=None, x=None, y=None, fill=global_fill, lines=global_lines, line_labels=True,
        title=None, colorbar_title=None, colorbar=True,
        colorbar_label_skip=None, ptype=0, negative_linestyle='solid',
        blockfill=global_blockfill, zero_thick=False, colorbar_shrink=None,
        colorbar_orientation=None, colorbar_position=None, xlog=False,
        ylog=False, axes=True, xaxis=True, yaxis=True, xticks=None,
        xticklabels=None, yticks=None, yticklabels=None, xlabel=None,
        ylabel=None, colors='k', swap_axes=False, verbose=None,
        linewidths=None, alpha=1.0, colorbar_text_up_down=False,
        colorbar_fontsize=None, colorbar_fontweight=None,
        colorbar_text_down_up=False, colorbar_drawedges=True,
        colorbar_fraction=None, colorbar_thick=None,
        colorbar_anchor=None, colorbar_labels=None,
        linestyles=None, zorder=1, level_spacing=None,
        ugrid=False, face_lons=False, face_lats=False, face_connectivity=False,
        titles=False, mytest=False, transform_first=None, blockfill_fast=None,
        nlevs=False):
    """
     | con is the interface to contouring in cf-plot. The minimum use is con(f)
     | where f is a 2 dimensional array. If a cf field is passed then an
     | appropriate plot will be produced i.e. a longitude-latitude or
     | latitude-height plot for example. If a 2d numeric array is passed then
     | the optional arrays x and y can be used to describe the x and y data
     | point locations.
     |
     | f - array to contour
     | x - x locations of data in f (optional)
     | y - y locations of data in f (optional)
     | fill=True - colour fill contours
     | lines=True - draw contour lines and labels
     | line_labels=True - label contour lines
     | title=title - title for the plot
     | ptype=0 - plot type - not needed for cf fields.
     |                       0 = no specific plot type,
     |                       1 = longitude-latitude,
     |                       2 = latitude - height,
     |                       3 = longitude - height,
     |                       4 = latitude - time,
     |                       5 = longitude - time
     |                       6 = rotated pole
     | negative_linestyle='solid' - set to one of 'solid', 'dashed'
     | zero_thick=False - add a thick zero contour line. Set to 3 for example.
     | blockfill=False - set to True for a blockfill plot
     | colorbar_title=colbar_title - title for the colour bar
     | colorbar=True - add a colour bar if a filled contour plot
     | colorbar_label_skip=None - skip colour bar labels. Set to 2 to skip
     |                            every other label.
     | colorbar_orientation=None - options are 'horizontal' and 'vertical'
     |                      The default for most plots is horizontal but
     |                      for polar stereographic plots this is vertical.
     | colorbar_shrink=None - value to shrink the colorbar by.  If the colorbar
     |                        exceeds the plot area then values of 1.0, 0.55
     |                        or 0.5m may help it better fit the plot area.
     | colorbar_position=None - position of colorbar
     |                          [xmin, ymin, x_extent,y_extent] in normalised
     |                          coordinates. Use when a common colorbar
     |                          is required for a set of plots. A typical set
     |                          of values would be [0.1, 0.05, 0.8, 0.02]
     | colorbar_fontsize=None - text size for colorbar labels and title
     | colorbar_fontweight=None - font weight for colorbar labels and title
     | colorbar_text_up_down=False - if True horizontal colour bar labels alternate
     |                             above (start) and below the colour bar
     | colorbar_text_down_up=False - if True horizontal colour bar labels alternate
     |                             below (start) and above the colour bar
     | colorbar_drawedges=True - draw internal divisions in the colorbar
     | colorbar_fraction=None - space for the colorbar - default = 0.21, in normalised
     |                       coordinates
     | colorbar_thick=None - thickness of the colorbar - default = 0.015, in normalised
     |                       coordinates
     | colorbar_anchor=None - default=0.5 - anchor point of colorbar within the fraction space.
     |                        0.0 = close to plot, 1.0 = further away
     | colorbar_labels=None - labels to use for colorbar.  The default is to use the contour
     |                        levels as labels
     | colorbar_text_up_down=False - on a horizontal colorbar alternate the
     |                               labels top and bottom starting in the up position
     | colorbar_text_down_up=False - on a horizontal colorbar alternate the
     |                               labels bottom and top starting in the bottom position
     | colorbar_drawedges=True - draw internal delimeter lines in the colorbar
     | colors='k' - contour line colors - takes one or many values.
     | xlog=False - logarithmic x axis
     | ylog=False - logarithmic y axis
     | axes=True - plot x and y axes
     | xaxis=True - plot xaxis
     | yaxis=True - plot y axis
     | xticks=None - xtick positions
     | xticklabels=None - xtick labels
     | yticks=None - y tick positions
     | yticklabels=None - ytick labels
     | xlabel=None - label for x axis
     | ylabel=None - label for y axis
     | swap_axes=False - swap plotted axes - only valid for X, Y, Z vs T plots
     | verbose=None - change to 1 to get a verbose listing of what con
     |                is doing
     | linewidths=None - contour linewidths.  Either a single number for all
     |                   lines or array of widths
     | linestyles=None - takes 'solid', 'dashed', 'dashdot' or 'dotted'
     | alpha=1.0 - transparency setting.  The default is no transparency.
     | zorder=1 - order of drawing
     | level_spacing=None - Default of 'linear' level spacing.  Also takes 'log', 'loglike',
     |                      'outlier' and 'inspect'
     | ugrid=False - flag for contouring ugrid data
     | face_lons=None - longitude points for face vertices
     | face_lats=None - latitude points for face verticies
     | face_connectivity=None - connectivity for face verticies
     | titles=False - set to True to have a dimensions title
     | transform_first=None - Cartopy should transform the points before calling the contouring algorithm, 
     |                         which can have a significant impact on speed (it is much faster to transform
     |                         points than it is to transform patches) If this is unset and the number of points
     |                         in the x direction is > 400 then it is set to True.
     | blockfill_fast=None - Use pcolormesh blockfill.  This is possibly less reliable that the usual code but is 
     |                       faster for higher resolution datasets
     | nlevs=False - Let Matplotlib work out the levels for the contour plot

     :Returns:
      None

    """

    # Turn off divide warning in contour routine which is a numpy issue
    old_settings = np.seterr(all='ignore')
    np.seterr(divide='ignore')

    # Set potential user axis labels
    user_xlabel = xlabel
    user_ylabel = ylabel

    # Set blockfill to True if blockfill_fast is not None
    if blockfill_fast is not None:
        blockfill=True
         
    # Extract data for faces if a UGRID blockplot
    blockfill_ugrid = False
    if face_lons and face_lats and face_connectivity:
        blockfill_ugrid = True
        fill = False
        ugrid = True
        if isinstance(f, cf.Field):
            field = f.array
        else:
            field = f
        field_orig = deepcopy(field)
        if isinstance(face_lons, cf.Field):
            face_lons_array = face_lons.array
        else:
            face_lons_array = face_lons

        if isinstance(face_lats, cf.Field):
            face_lats_array = face_lats.array
        else:
            face_lats_array = face_lats

        if isinstance(face_connectivity, cf.Field):
            face_connectivity_array = face_connectivity.array
        else:
            face_connectivity_array = face_connectivity

    # Call gpos(1) if not already called
    if plotvars.rows > 1 or plotvars.columns > 1:
        if plotvars.gpos_called is False:
            gpos(1)

    # Extract required data for contouring
    # If a cf-python field
    if isinstance(f, cf.Field):

        # Check data is 2D
        ndims = np.squeeze(f.data).ndim
        ugrid = False
        if ndims == 1:
            ugrid = True      
        if ndims > 2:
            errstr = "\n\ncfp.con error need a 1 or 2 dimensional field to contour\n"
            errstr += "received " + str(np.squeeze(f.data).ndim) + " dimensions\n\n"
            errstr += str(f)
            raise TypeError(errstr)

        # Extract data
        if verbose:
            print('con - calling cf_data_assign')

        #if not ugrid_blockfill:
        field, x, y, ptype, colorbar_title, xlabel, ylabel, xpole, ypole =\
            cf_data_assign(f, colorbar_title, verbose=verbose)

        if user_xlabel is not None:
            xlabel = user_xlabel
        if user_ylabel is not None:
            ylabel = user_ylabel
    elif isinstance(f, cf.FieldList):
        raise TypeError("\n\ncfp.con - cannot contour a field list\n\n")
    else:
        if verbose:
            print('con - using user assigned data')
        field = f  # field data passed in as f
        if x is None:
            x = np.arange(np.shape(field)[1])
        if y is None:
            y = np.arange(np.shape(field)[0])

        check_data(field, x, y)
        xlabel = ''
        ylabel = ''

    # Set contour line styles
    matplotlib.rcParams['contour.negative_linestyle'] = negative_linestyle

    # Set contour lines off on block plots
    if blockfill:
        fill = False
        field_orig = deepcopy(field)
        x_orig = deepcopy(x)
        y_orig = deepcopy(y)

        # Check number of colours and levels match if user has modified the
        # number of colours
        if plotvars.cscale_flag == 2:
            ncols = np.size(plotvars.cs)
            nintervals = np.size(plotvars.levels) - 1
            if plotvars.levels_extend == 'min':
                nintervals += 1
            if plotvars.levels_extend == 'max':
                nintervals += 1
            if plotvars.levels_extend == 'both':
                nintervals += 2
            if ncols != nintervals:
                errstr = "\n\ncfp.con - blockfill error \n"
                errstr += "need to match number of colours and contour intervals\n"
                errstr += "Don't forget to take account of the colorbar "
                errstr += "extensions\n\n"
                raise TypeError(errstr)

    # Turn off colorbar if fill is turned off
    if not fill and not blockfill and not blockfill_ugrid:
        colorbar = False

    # Revert to default colour scale if cscale_flag flag is set
    if plotvars.cscale_flag == 0:
        plotvars.cs = cscale1

    # Set the orientation of the colorbar
    if plotvars.plot_type == 1:
        if plotvars.proj == 'npstere' or plotvars.proj == 'spstere':
            if colorbar_orientation is None:
                colorbar_orientation = 'vertical'
    if colorbar_orientation is None:
        colorbar_orientation = 'horizontal'

    # Store original map resolution
    resolution_orig = plotvars.resolution

    # Set size of color bar if not specified
    if colorbar_shrink is None:
        colorbar_shrink = 1.0
        if plotvars.proj == 'npstere' or plotvars.proj == 'spstere':
            colorbar_shrink = 0.8


    # Set plot type if user specified
    if (ptype is not None):
        plotvars.plot_type = ptype

    # Get contour levels if none are defined
    spacing = 'linear'
    if plotvars.level_spacing is not None:
        spacing = plotvars.level_spacing
    if level_spacing is not None: 
        spacing = level_spacing

    if plotvars.levels is None:
        clevs, mult, fmult = calculate_levels(field=field,
                                              level_spacing=spacing,
                                              verbose=verbose)
    else:
        clevs = plotvars.levels
        mult = 0
        fmult = 1

    # Set the colour scale if nothing is defined
    includes_zero = False
    if plotvars.cscale_flag == 0:
        col_zero = 0
        for cval in clevs:
            if includes_zero is False:
                col_zero = col_zero + 1
            if cval == 0:
                includes_zero = True

        if includes_zero:
            cs_below = col_zero
            cs_above = np.size(clevs) - col_zero + 1
            if plotvars.levels_extend == 'max' or plotvars.levels_extend == 'neither':
                cs_below = cs_below - 1
            if plotvars.levels_extend == 'min' or plotvars.levels_extend == 'neither':
                cs_above = cs_above - 1
            uniform = True
            if plotvars.cs_uniform is False:
                uniform = False
            cscale('scale1', below=cs_below, above=cs_above, uniform=uniform)
        else:
            ncols = np.size(clevs)+1
            if plotvars.levels_extend == 'min' or plotvars.levels_extend == 'max':
                ncols = ncols-1
            if plotvars.levels_extend == 'neither':
                ncols = ncols-2
            cscale('viridis', ncols=ncols)

        plotvars.cscale_flag = 0

    # User selected colour map but no mods so fit to levels
    if plotvars.cscale_flag == 1:
        ncols = np.size(clevs)+1
        if plotvars.levels_extend == 'min' or plotvars.levels_extend == 'max':
            ncols = ncols-1
        if plotvars.levels_extend == 'neither':
            ncols = ncols-2
        cscale(plotvars.cs_user, ncols=ncols)
        plotvars.cscale_flag = 1

    # Set colorbar labels
    # Set a sensible label spacing if the user hasn't already done so
    if colorbar_label_skip is None:
        if colorbar_orientation == 'horizontal':
            nchars = 0
            for lev in clevs:
                nchars = nchars + len(str(lev))
            colorbar_label_skip = int(nchars / 80 + 1)
            if plotvars.columns > 1:
                colorbar_label_skip = int(nchars * (plotvars.columns) / 80)
        else:
            colorbar_label_skip = 1

    if colorbar_label_skip > 1:
        if includes_zero:
            # include zero in the colorbar labels
            zero_pos = [i for i, mylev in enumerate(clevs) if mylev == 0][0]
            cbar_labels = clevs[zero_pos]
            i = zero_pos + colorbar_label_skip
            while i <= len(clevs) - 1:
                cbar_labels = np.append(cbar_labels, clevs[i])
                i = i + colorbar_label_skip
            i = zero_pos - colorbar_label_skip
            if i >= 0:
                while i >= 0:
                    cbar_labels = np.append(clevs[i], cbar_labels)
                    i = i - colorbar_label_skip
        else:
            cbar_labels = clevs[0]
            i = int(colorbar_label_skip)
            while i <= len(clevs) - 1:
                cbar_labels = np.append(cbar_labels, clevs[i])
                i = i + colorbar_label_skip

    else:
        cbar_labels = clevs

    if colorbar_label_skip is None:
        colorbar_label_skip = 1

    # Make a list of strings of the colorbar levels for later labelling
    clabels = []
    for i in cbar_labels:
        clabels.append(str(i))
        if colorbar_label_skip > 1:
            for skip in np.arange(colorbar_label_skip - 1):
                clabels.append('')

    if colorbar_labels is not None:
        cbar_labels = colorbar_labels
    else:
        cbar_labels = clabels

    # Turn off line_labels if the field is all the same
    # Matplotlib 3.2.2 throws an error if there are no line labels
    if np.nanmin(field) == np.nanmax(field):
        line_labels = False

    # Add mult to colorbar_title if used
    if (colorbar_title is None):
        colorbar_title = ''
    if (mult != 0):
        colorbar_title = colorbar_title + ' *10$^{' + str(mult) + '}$'

    # Catch null title
    if title is None:
        title = ''
    if plotvars.title is not None:
        title = plotvars.title

    # Set plot variables
    title_fontsize = plotvars.title_fontsize
    text_fontsize = plotvars.text_fontsize
    if colorbar_fontsize is None:
        colorbar_fontsize = plotvars.colorbar_fontsize
    if colorbar_fontweight is None:
        colorbar_fontweight = plotvars.colorbar_fontweight
    continent_thickness = plotvars.continent_thickness
    continent_color = plotvars.continent_color
    continent_linestyle = plotvars.continent_linestyle
    land_color = plotvars.land_color
    ocean_color = plotvars.ocean_color
    lake_color = plotvars.lake_color
    title_fontweight = plotvars.title_fontweight
    if continent_thickness is None:
        continent_thickness = 1.5
    if continent_color is None:
        continent_color = 'k'
    if continent_linestyle is None:
        continent_linestyle = 'solid'
    cb_orient = colorbar_orientation

    # Retrieve any user defined axis labels
    if xlabel == '' and plotvars.xlabel is not None:
        xlabel = plotvars.xlabel
    if ylabel == '' and plotvars.ylabel is not None:
        ylabel = plotvars.ylabel
    if xticks is None and plotvars.xticks is not None:
        xticks = plotvars.xticks
        if plotvars.xticklabels is not None:
            xticklabels = plotvars.xticklabels
        else:
            xticklabels = list(map(str, xticks))
    if yticks is None and plotvars.yticks is not None:
        yticks = plotvars.yticks
        if plotvars.yticklabels is not None:
            yticklabels = plotvars.yticklabels
        else:
            yticklabels = list(map(str, yticks))

    # Calculate a set of dimension titles if requested
    if titles: 
        plotvars.titles_con_called = True
        title_dims = generate_titles(f)
        if not colorbar:
            title_dims = colorbar_title + '\n' + title_dims


    # Check if data is well formed
    # i.e. dimensions have only recognizable X, Y, Z, T or a subset
    well_formed = False
    if isinstance(f, cf.Field):
        well_formed = check_well_formed(f)
        
        
        
    #level_opts = {'levels': clevs}
    if nlevs is not False:
        clevs = nlevs
        plotvars.levels_extend = 'neither'
        if plotvars.cscale_flag == 0:
            if np.min(field) < 0 and np.max(field) > 0:
                cscale('scale1', ncols=nlevs)
            else:
                cscale('viridis', ncols=nlevs)
            plotvars.cscale_flag = 0
        else:
            cscale(plotvars.cs_user, ncols=nlevs)
  
        

    ##################
    # Map contour plot
    ##################
    if ptype == 1:
        if verbose:
            print('con - making a map plot')


        # Open a new plot if necessary
        if plotvars.user_plot == 0:
            gopen(user_plot=0)

        # Set up mapping
        lonrange = np.nanmax(x) - np.nanmin(x)
        latrange = np.nanmax(y) - np.nanmin(y)
        # Reset mapping
        if plotvars.user_mapset == 0:
            plotvars.lonmin = -180
            plotvars.lonmax = 180
            plotvars.latmin = -90
            plotvars.latmax = 90


        if (lonrange > 350 and latrange > 170) or plotvars.user_mapset == 1:
            set_map()
        else:
            mapset(lonmin=np.nanmin(x), lonmax=np.nanmax(x),
                   latmin=np.nanmin(y), latmax=np.nanmax(y),
                   user_mapset=0, resolution=resolution_orig)
            set_map()




        mymap = plotvars.mymap
        user_mapset = plotvars.user_mapset

        lonrange = np.nanmax(x) - np.nanmin(x)
        





        if not blockfill_ugrid:
            if not ugrid:
                if lonrange > 350 and np.ndim(y) == 1:
                    # Add cyclic information if missing.
                    if lonrange < 360:
                        # field, x = cartopy_util.add_cyclic_point(field, x)
                        # Call add_cyclic_point it spacing is regular
                        x_regular = True
                        xspacing = x[1] - x[0]
                        for ix in np.arange(len(x) - 1):
                            if x[ix+1] - x[ix] != xspacing:
                                x_regular = False
                        if x_regular:
                            field, x = add_cyclic(field, x)
                            
                        lonrange = np.nanmax(x) - np.nanmin(x)

                        # cartopy line drawing fix
                        if x[-1] - x[0] == 360.0:
                            x[-1] = x[-1] + 0.001

                    # Shift grid if needed
                    if plotvars.lonmin < np.nanmin(x):
                        # Cartopy feature at version 0.20.0 
                        # -360 to 0 creates strange contours
                        vers = cartopy.__version__.split('.')
                        val = int(vers[0] +vers[1])
                        if val < 20:
                            x = x - 360
                    if plotvars.lonmin > np.nanmax(x):
                        x = x + 360
            else:
                # Get the ugrid data within the map coordinates
                # Matplotlib tricontour cannot plot missing data so we need to split 
                # the missing data into a separate field to deal with this

                field_modified = deepcopy(field)
                pts_nan = np.where(np.isnan(field_modified))
                field_modified[pts_nan] = -1e30

                field_ugrid, lons_ugrid, lats_ugrid = ugrid_window(field_modified, x, y)
                #pts_real  = np.where(np.isfinite(field_ugrid))
                pts_real = np.where(field_ugrid > -1e29)
                pts_nan = np.where(field_ugrid < -1e29)


                field_ugrid_nan = []
                lons_ugrid_nan = []
                lats_ugrid_nan = []
                if np.size(pts_nan) > 0:
                    field_ugrid_nan = deepcopy(field_ugrid)
                    lons_ugrid_nan = deepcopy(lons_ugrid)
                    lats_ugrid_nan = deepcopy(lats_ugrid)
                    field_ugrid_nan[:] = 0
                    field_ugrid_nan[pts_nan] = 1


                field_ugrid_real = deepcopy(field_ugrid[pts_real])
                lons_ugrid_real = deepcopy(lons_ugrid[pts_real])
                lats_ugrid_real = deepcopy(lats_ugrid[pts_real])


        if not ugrid:
            # Flip latitudes and field if latitudes are in descending order
            if np.ndim(y) == 1:
                if y[0] > y[-1]:
                    y = y[::-1]
                    field = np.flipud(field)

        # Plotting a sub-area of the grid produces stray contour labels
        # in polar plots. Subsample the latitudes to remove this problem

        if plotvars.proj == 'npstere' and np.ndim(y) == 1:
            if not blockfill_ugrid:
                if ugrid:
                    pts = np.where(lats_ugrid > plotvars.boundinglat - 5)
                    pts = np.array(pts).flatten()
                    lons_ugrid_real = lons_ugrid_real[pts]
                    lats_ugrid_real = lats_ugrid_real[pts]
                    field_ugrid_real = field_ugrid_real[pts]
                else:
                    myypos = find_pos_in_array(vals=y, val=plotvars.boundinglat)
                    if myypos != -1:
                        y = y[myypos:]
                        field = field[myypos:, :]

        if plotvars.proj == 'spstere' and np.ndim(y) == 1:
            if not blockfill_ugrid:
                if ugrid:
                    pts = np.where(lats_ugrid_real < plotvars.boundinglat + 5)
                    lons_ugrid_real = lons_ugrid_real[pts]
                    lats_ugrid_real = lats_ugrid_real[pts]
                    field_ugrid_real = field_ugrid_real[pts]
                else:
                    myypos = find_pos_in_array(vals=y, val=plotvars.boundinglat, above=True)
                    if myypos != -1:
                        y = y[0:myypos + 1]
                        field = field[0:myypos + 1, :]


        # Set the longitudes and latitudes
        lons, lats = x, y

        # Set the plot limits
        if lonrange > 350:
            gset(
                xmin=plotvars.lonmin,
                xmax=plotvars.lonmax,
                ymin=plotvars.latmin,
                ymax=plotvars.latmax,
                user_gset=0)
        else:
            if user_mapset == 1:
                gset(xmin=plotvars.lonmin,
                     xmax=plotvars.lonmax,
                     ymin=plotvars.latmin,
                     ymax=plotvars.latmax,
                     user_gset=0)
            else:
                gset(xmin=np.nanmin(lons),
                     xmax=np.nanmax(lons),
                     ymin=np.nanmin(lats),
                     ymax=np.nanmax(lats),
                     user_gset=0)




        # Filled contours
        if fill:
            if verbose:
                print('con - adding filled contours')
            # Get colour scale for use in contouring
            # If colour bar extensions are enabled then the colour map goes
            # from 1 to ncols-2.  The colours for the colour bar extensions
            # are then changed on the colorbar and plot after the plot is made
            colmap = cscale_get_map()

            cmap = matplotlib.colors.ListedColormap(colmap)
            if (plotvars.levels_extend ==
                    'min' or plotvars.levels_extend == 'both'):
                cmap.set_under(plotvars.cs[0])
            if (plotvars.levels_extend ==
                    'max' or plotvars.levels_extend == 'both'):
                cmap.set_over(plotvars.cs[-1])

            # For fast map contours add transform_first=True to contourf command
            # and make lons and lats 2D
            if transform_first is None and np.ndim(lons) == 1 and np.ndim(lats) == 1:
                if np.size(lons) >= 400:
                    transform_first = True
                    
            # Fast map contours are also needed when clevs is a integer
            if type(clevs) == int and plotvars.plot_type == 1 and plotvars.proj == 'cyl':
                transform_first=True
            
            
            
            if transform_first:
                if np.ndim(lons) == 1 and np.ndim(lats) == 1:
                    lons, lats = np.meshgrid(lons, lats)
                    
                    
            
            # Filled colour contours
            if not ugrid:               
                plotvars.image = mymap.contourf(lons, lats, field * fmult, clevs,
                               extend=plotvars.levels_extend,
                               cmap=cmap, norm=plotvars.norm,
                               alpha=alpha, transform=ccrs.PlateCarree(),
                               zorder=zorder, transform_first=transform_first)
                
            else:
                if np.size(field_ugrid_real) > 0: 
                    plotvars.image = mymap.tricontourf(lons_ugrid_real, lats_ugrid_real, field_ugrid_real * fmult,
                                      clevs, extend=plotvars.levels_extend,
                                      cmap=cmap, norm=plotvars.norm,
                                      alpha=alpha, transform=ccrs.PlateCarree(),
                                      zorder=zorder)

        # Block fill
        if blockfill:
            if verbose:
                print('con - adding blockfill')
            if isinstance(f, cf.Field):

                if f.ref('grid_mapping_name:transverse_mercator', default=False):
                    # Special case for transverse mercator
                    bfill(f=f, clevs=clevs, lonlat=False, alpha=alpha, fast=blockfill_fast,zorder=zorder)

                else:

                    if f.coord('X').has_bounds() and f.coord('Y').has_bounds():
                        xpts = np.squeeze(f.coord('X').bounds.array[:, 0])
                        ypts = np.squeeze(f.coord('Y').bounds.array[:, 0])
                        # Add last longitude point
                        xpts = np.append(xpts, f.coord('X').bounds.array[-1, 1])
                        # Add last latitude point
                        ypts = np.append(ypts, f.coord('Y').bounds.array[-1, 1])

                        bfill(f=field_orig * fmult, x=xpts, y=ypts, clevs=clevs,
                              lonlat=True, bound=1, alpha=alpha, fast=blockfill_fast, zorder=zorder)
                    else:
                        bfill(f=field_orig * fmult, x=x_orig, y=y_orig, clevs=clevs,
                              lonlat=True, bound=0, alpha=alpha, fast=blockfill_fast, zorder=zorder)

            else:
                bfill(f=field_orig * fmult, x=x_orig, y=y_orig, clevs=clevs,
                      lonlat=True, bound=0, alpha=alpha, fast=blockfill_fast, zorder=zorder)

        # Block fill for ugrid
        if blockfill_ugrid:
            if verbose:
                print('con - adding blockfill for UGRID')
            bfill_ugrid(f=field_orig * fmult, face_lons=face_lons_array, 
                       face_lats=face_lats_array, 
                       face_connectivity=face_connectivity_array, clevs=clevs,
                       alpha=alpha, fast=blockfill_fast, zorder=zorder)

        # Contour lines and labels
        if lines:
            if verbose:
                print('con - adding contour lines and labels')

            if not ugrid:
                cs = mymap.contour(lons, lats, field * fmult, clevs, colors=colors,
                                   linewidths=linewidths, linestyles=linestyles, alpha=alpha,
                                   transform=ccrs.PlateCarree(), zorder=zorder)
            else:

                cs = mymap.tricontour(lons_ugrid_real, lats_ugrid_real, field_ugrid_real * fmult,
                                      clevs, colors=colors,
                                      linewidths=linewidths, linestyles=linestyles, alpha=alpha,
                                      transform=ccrs.PlateCarree(), zorder=zorder)

            if line_labels and type(clevs) == list:
                nd = ndecs(clevs)
                fmt = '%d'
                if nd != 0:
                    fmt = '%1.' + str(nd) + 'f'
                plotvars.plot.clabel(cs, levels=clevs, fmt=fmt, zorder=zorder, colors=colors,
                                     fontsize=text_fontsize)


            # Thick zero contour line
            if zero_thick:
                cs = mymap.contour(lons, lats, field * fmult, [-1e-32, 0],
                                   colors=colors, linewidths=zero_thick,
                                   linestyles=linestyles, alpha=alpha,
                                   transform=ccrs.PlateCarree(), zorder=zorder)



        # Add a ugrid mask if there is one
        if ugrid and not blockfill_ugrid:
            if np.size(field_ugrid_nan) > 0:
                cmap_white = matplotlib.colors.ListedColormap([1.0, 1.0, 1.0])
                mymap.tricontourf(lons_ugrid_nan, lats_ugrid_nan, field_ugrid_nan , [0.5, 1.5],
                                  extend='neither',
                                  cmap=cmap_white, norm=plotvars.norm,
                                  alpha=alpha, transform=ccrs.PlateCarree(),
                                  zorder=zorder)

        # Axes
        plot_map_axes(axes=axes, xaxis=xaxis, yaxis=yaxis,
                      xticks=xticks, xticklabels=xticklabels,
                      yticks=yticks, yticklabels=yticklabels,
                      user_xlabel=user_xlabel, user_ylabel=user_ylabel,
                      verbose=verbose)

        # Coastlines and features
        feature = cfeature.NaturalEarthFeature(name='land',
                                               category='physical',
                                               scale=plotvars.resolution,
                                               facecolor='none')
        mymap.add_feature(feature,
                          edgecolor=continent_color,
                          linewidth=continent_thickness,
                          linestyle=continent_linestyle,
                          zorder=zorder)

        if ocean_color is not None:
            mymap.add_feature(cfeature.OCEAN, edgecolor='face', facecolor=ocean_color,
                              zorder=999)
        if land_color is not None:
            mymap.add_feature(cfeature.LAND, edgecolor='face', facecolor=land_color,
                              zorder=999)
        if lake_color is not None:
            mymap.add_feature(cfeature.LAKES, edgecolor='face', facecolor=lake_color,
                              zorder=999)

        # Title
        if title != '':
            map_title(title)

        # Titles for dimensions
        if titles:
            dim_titles(title_dims, dims=True)

        # Color bar
        if colorbar:
            cbar(labels=cbar_labels, orientation=cb_orient, position=colorbar_position,
                 shrink=colorbar_shrink, title=colorbar_title, fontsize=colorbar_fontsize,
                 fontweight=colorbar_fontweight, text_up_down=colorbar_text_up_down,
                 text_down_up=colorbar_text_down_up, drawedges=colorbar_drawedges,
                 fraction=colorbar_fraction, thick=colorbar_thick,
                 anchor=colorbar_anchor, levs=clevs, verbose=verbose)


        # Reset plot limits if not a user plot
        if plotvars.user_gset == 0:
            gset()

    ################################################
    # Latitude, longitude or time vs Z contour plots
    ################################################
    if ptype == 2 or ptype == 3 or ptype == 7:

        if verbose:
            if ptype == 2:
                print('con - making a latitude-pressure plot')
            if ptype == 3:
                print('con - making a longitude-pressure plot')
            if ptype == 7:
                print('con - making a time-pressure plot')

        # Work out which way is up
        positive = None
        myz = find_z(f)
        
        
        if isinstance(f, cf.Field) and well_formed:
            if hasattr(f.construct(myz), 'positive'):
                positive = f.construct(myz).positive
            else:
                errstr = "\ncf-plot - data error \n"
                errstr += "data needs a vertical coordinate direction"
                errstr += " as required in CF data conventions"
                errstr += "\nMaking a contour plot assuming positive is down\n\n"
                errstr += "If this is incorrect the data needs to be modified to \n"
                errstr += "include a correct value for the direction attribute\n"
                errstr += "such as in f.coord(\'Z\').positive=\'down\'"
                errstr += "\n\n"
                print(errstr)
                positive = 'down'
        else:
            positive = 'down'
            if 'theta' in ylabel.split(' '):
                positive = 'up'
            if 'height' in ylabel.split(' '):
                positive = 'up'

        if plotvars.user_plot == 0:
            gopen(user_plot=0)

        # Use gset parameter of ylog if user has set this
        if plotvars.ylog is True or plotvars.ylog == 1:
            ylog = True

        # Set plot limits
        user_gset = plotvars.user_gset
        if user_gset == 0:
            # Program selected data plot limits
            xmin = np.nanmin(x)
            if xmin < -80 and xmin >= -90:
                xmin = -90
            xmax = np.nanmax(x)
            if xmax > 80 and xmax <= 90:
                xmax = 90

            if positive == 'down':
                ymin = np.nanmax(y)
                ymax = np.nanmin(y)
                if ymax < 10:
                    ymax = 0
            else:
                ymin = np.nanmin(y)
                ymax = np.nanmax(y)

        else:
            # Use user specified plot limits
            xmin = plotvars.xmin
            xmax = plotvars.xmax
            ymin = plotvars.ymin
            ymax = plotvars.ymax

        ystep = 100
        myrange = abs(ymax - ymin)

        if myrange < 1:
            ystep = abs(ymax - ymin)/10.
        if abs(ymax - ymin) > 1:
            ystep = 1
        if abs(ymax - ymin) > 10:
            ystep = 10
        if abs(ymax - ymin) > 100:
            ystep = 100
        if abs(ymax - ymin) > 1000:
            ystep = 200
        if abs(ymax - ymin) > 2000:
            ystep = 500
        if abs(ymax - ymin) > 5000:
            ystep = 1000
        if abs(ymax - ymin) > 15000:
            ystep = 5000

        # Work out ticks and tick labels
        if ylog is False or ylog == 0:
            heightticks = gvals(dmin=min(ymin, ymax),
                                dmax=max(ymin, ymax),
                                mystep=ystep, mod=False)[0]

            if myrange < 1 and myrange > 0.1:
                heightticks = np.arange(10)/10.0

        else:
            heightticks = []
            for tick in 1000, 100, 10, 1:
                if tick >= min(ymin, ymax) and tick <= max(ymin, ymax):
                    heightticks.append(tick)
        heightlabels = heightticks

        if axes:
            if xaxis:
                if xticks is not None:
                    if xticklabels is None:
                        xticklabels = xticks
            else:
                xticks = [100000000]
                xticklabels = xticks
                xlabel = ''

            if yaxis:
                if yticks is not None:
                    heightticks = yticks
                    heightlabels = yticks
                    if yticklabels is not None:
                        heightlabels = yticklabels
            else:
                heightticks = [100000000]
                ylabel = ''

        else:
            xticks = [100000000]
            xticklabels = xticks
            heightticks = [100000000]
            heightlabels = heightticks
            xlabel = ''
            ylabel = ''

        if yticks is None:
            yticks = heightticks
            yticklabels = heightlabels

        # Time - height contour plot
        if ptype == 7:
            if isinstance(f, cf.Field):
                if plotvars.user_gset == 0:
                    tmin = f.construct('T').dtarray[0]
                    tmax = f.construct('T').dtarray[-1]
                else:
                    # Use user set values if present
                    tmin = plotvars.xmin
                    tmax = plotvars.xmax

                    ref_time = f.construct('T').units
                    ref_calendar = f.construct('T').calendar
                    time_units = cf.Units(ref_time, ref_calendar)
                    t = cf.Data(cf.dt(tmin), units=time_units)
                    xmin = t.array
                    t = cf.Data(cf.dt(tmax), units=time_units)
                    xmax = t.array

        if xticks is None and xaxis:
            if ptype == 2:
                xticks, xticklabels = mapaxis(min=xmin, max=xmax, type=2)  # lat-pressure
            if ptype == 3:
                xticks, xticklabels = mapaxis(min=xmin, max=xmax, type=1)  # lon-pressure

            if ptype == 7:
                # time-pressure
                if isinstance(f, cf.Field):

                    # Change plotvars.xmin and plotvars.xmax from a date string
                    # to a number
                    ref_time = f.construct('T').units
                    ref_calendar = f.construct('T').calendar
                    time_units = cf.Units(ref_time, ref_calendar)

                    t = cf.Data(cf.dt(tmin), units=time_units)
                    xmin = t.array
                    t = cf.Data(cf.dt(tmax), units=time_units)
                    xmax = t.array

                    taxis = cf.Data(
                        [cf.dt(tmin), cf.dt(tmax)], units=time_units)
                    time_ticks, time_labels, tlabel = timeaxis(taxis)

                    # Use user supplied labels if present
                    if user_xlabel is None:
                        xlabel = tlabel
                    if xticks is None:
                        xticks = time_ticks
                    if xticklabels is None:
                        xticklabels = time_labels

                else:
                    errstr = '\nNot a CF field\nPlease use ptype=0 and '
                    errstr = errstr + 'specify axis labels manually\n'
                    raise Warning(errstr)

        # Set plot limits
        if ylog is False or ylog == 0:
            gset(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                 user_gset=user_gset)
        else:
            if ymax == 0:
                ymax = 1  # Avoid zero in a log plot
            gset(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                 ylog=True, user_gset=user_gset)

        # Label axes
        axes_plot(xticks=xticks, xticklabels=xticklabels, yticks=heightticks,
                  yticklabels=heightlabels, xlabel=xlabel, ylabel=ylabel)

        # Get colour scale for use in contouring
        # If colour bar extensions are enabled then the colour map goes
        # from 1 to ncols-2.  The colours for the colour bar extensions are
        # then changed on the colorbar and plot after the plot is made
        colmap = cscale_get_map()

        # Filled contours
        if fill:
            colmap = cscale_get_map()
            cmap = matplotlib.colors.ListedColormap(colmap)
            if (plotvars.levels_extend ==
                    'min' or plotvars.levels_extend == 'both'):
                cmap.set_under(plotvars.cs[0])
            if (plotvars.levels_extend ==
                    'max' or plotvars.levels_extend == 'both'):
                cmap.set_over(plotvars.cs[-1])

            plotvars.image = plotvars.plot.contourf(x, y, field * fmult, clevs,
                                   extend=plotvars.levels_extend,
                                   cmap=cmap,
                                   norm=plotvars.norm, alpha=alpha,
                                   zorder=zorder)

        # Block fill
        if blockfill:
            if isinstance(f, cf.Field):

                hasbounds = True

                if ptype == 2:
                    if f.coord('Y').has_bounds() and f.coord('Z').has_bounds():
                        xpts = np.squeeze(f.coord('Y').bounds.array)[:, 0]
                        xpts = np.append(xpts, f.coord('Y').bounds.array[-1, 1])
                        ypts = np.squeeze(f.coord('Z').bounds.array)[:, 0]
                        ypts = np.append(ypts, f.coord('Z').bounds.array[-1, 1])
                    else:
                        hasbounds = False

                if ptype == 3:
                    if f.coord('X').has_bounds() and f.coord('Z').has_bounds():
                        xpts = np.squeeze(f.coord('X').bounds.array)[:, 0]
                        xpts = np.append(xpts, f.coord('X').bounds.array[-1, 1])
                        ypts = np.squeeAllTrop_UpStrat_Eq_Total_AllWN_Timeseries_2ze(f.coord('Z').bounds.array)[:, 0]
                        ypts = np.append(xpts, f.coord('Z').bounds.array[-1, 1])
                    else:
                        hasbounds = False

                if ptype == 7:
                    if f.coord('T').has_bounds() and f.coord('Z').has_bounds():
                        xpts = np.squeeze(f.coord('T').bounds.array)[:, 0]
                        xpts = np.append(xpts, f.coord('T').bounds.array[-1, 1])
                        ypts = np.squeeze(f.coord('Z').bounds.array)[:, 0]
                        ypts = np.append(xpts, f.coord('Z').bounds.array[-1, 1])
                    else:
                        hasbounds = False

                if hasbounds:
                    bfill(f=field_orig * fmult, x=xpts, y=ypts, clevs=clevs,
                          lonlat=False, bound=1, alpha=alpha, fast=blockfill_fast, zorder=zorder)
                else:
                    bfill(f=field_orig * fmult, x=x_orig, y=y_orig, clevs=clevs,
                          lonlat=False, bound=0, alpha=alpha, fast=blockfill_fast, zorder=zorder)

            else:
                bfill(f=field_orig * fmult, x=x_orig, y=y_orig, clevs=clevs,
                      lonlat=False, bound=0, alpha=alpha, fast=blockfill_fast, zorder=zorder)

        # Contour lines and labels
        if lines:
            cs = plotvars.plot.contour(
                x, y, field * fmult, clevs, colors=colors,
                linewidths=linewidths, linestyles=linestyles, zorder=zorder)
            if line_labels and type(clevs) == list:
                nd = ndecs(clevs)
                fmt = '%d'
                if nd != 0:
                    fmt = '%1.' + str(nd) + 'f'
                plotvars.plot.clabel(cs,fmt=fmt,colors=colors, zorder=zorder,
                                     fontsize=text_fontsize)

                # Thick zero contour line
                if zero_thick:
                    cs = plotvars.plot.contour(x, y, field * fmult,
                                               [-1e-32, 0], colors=colors,
                                               linewidths=zero_thick,
                                               linestyles=linestyles, alpha=alpha,
                                               zorder=zorder)

        # Titles for dimensions
        if titles:
            dim_titles(title_dims, dims=True)
        
        # Color bar
        if colorbar:
            cbar(labels=cbar_labels,
                 orientation=cb_orient,
                 position=colorbar_position,
                 shrink=colorbar_shrink,
                 title=colorbar_title,
                 fontsize=colorbar_fontsize,
                 fontweight=colorbar_fontweight,
                 text_up_down=colorbar_text_up_down,
                 text_down_up=colorbar_text_down_up,
                 drawedges=colorbar_drawedges,
                 fraction=colorbar_fraction,
                 thick=colorbar_thick,
                 levs=clevs,
                 anchor=colorbar_anchor,
                 verbose=verbose)

        # Title
        plotvars.plot.set_title(title, y=1.03, fontsize=title_fontsize,
                                fontweight=title_fontweight)

        # Reset plot limits to those supplied by the user
        if user_gset == 1 and ptype == 7:
            gset(xmin=tmin, xmax=tmax, ymin=ymin, ymax=ymax,
                 user_gset=user_gset)

        # reset plot limits if not a user plot
        if plotvars.user_gset == 0:
            gset()

    ########################
    # Hovmuller contour plot
    ########################
    if (ptype == 4 or ptype == 5):
        if verbose:
            print('con - making a Hovmuller plot')
        yplotlabel = 'Time'
        if ptype == 4:
            xplotlabel = 'Longitude'
        if ptype == 5:
            xplotlabel = 'Latitude'
        user_gset = plotvars.user_gset

        # Time strings set to None initially
        tmin = None
        tmax = None

        # Set plot limits
        if all(val is not None for val in [
               plotvars.xmin, plotvars.xmax, plotvars.ymin, plotvars.ymax]):
            # Store time strings for later use
            tmin = plotvars.ymin
            tmax = plotvars.ymax

            # Check data has CF attributes needed
            check_units = check_units = True
            check_calendar = True
            check_Units_reftime = True
            if hasattr(f.construct('T'), 'units') is False:
                check_units = False
            if hasattr(f.construct('T'), 'calendar') is False:
                check_calendar = False
            if hasattr(f.construct('T'), 'Units'):
                if not hasattr(f.construct('T').Units, 'reftime'):
                    check_Units_reftime = False
            else:
                check_Units_reftime = False
            if False in [check_units, check_calendar, check_Units_reftime]:
                print('\nThe required CF time information to make the plot')
                print('is not available please fix the following before')
                print('trying to plot again')
                if check_units is False:
                    print('Time axis missing: units')
                if check_calendar is False:
                    print('Time axis missing: calendar')
                if check_Units_reftime is False:
                    print('Time axis missing: Units.reftime')
                return

            # Change from date string in ymin and ymax to date as a float

            ref_time = f.construct('T').units
            ref_calendar = f.construct('T').calendar

            time_units = cf.Units(ref_time, ref_calendar)
            t = cf.Data(cf.dt(plotvars.ymin), units=time_units)
            ymin = t.array
            t = cf.Data(cf.dt(plotvars.ymax), units=time_units)
            ymax = t.array
            xmin = plotvars.xmin
            xmax = plotvars.xmax
        else:
            xmin = np.nanmin(x)
            xmax = np.nanmax(x)
            ymin = np.nanmin(y)
            ymax = np.nanmax(y)

        # Extract axis labels
        if len(f.constructs('T')) > 1:
            errstr = "\n\nTime axis error - only one time axis allowed\n "
            errstr += "Please list time axes with print(f.constructs())\n"
            errstr += "and remove the ones not needed for a hovmuller plot \n"
            errstr += "with f.del_construct('unwanted_time_axis')\n"
            errstr += "before trying to plot again\n\n\n\n"
            raise TypeError(errstr)

        time_ticks, time_labels, ylabel = timeaxis(f.construct('T'))

        if ptype == 4:
            lonlatticks, lonlatlabels = mapaxis(min=xmin, max=xmax, type=1)
        if ptype == 5:
            lonlatticks, lonlatlabels = mapaxis(min=xmin, max=xmax, type=2)

        if axes:
            if xaxis:
                if xticks is not None:
                    lonlatticks = xticks
                    lonlatlabels = xticks
                    if xticklabels is not None:
                        lonlatlabels = xticklabels
            else:
                lonlatticks = [100000000]
                xlabel = ''

            if yaxis:
                if yticks is not None:
                    timeticks = yticks
                    timelabels = yticks
                    if yticklabels is not None:
                        timelabels = yticklabels
            else:
                timeticks = [100000000]
                ylabel = ''

        else:
            timeticks = [100000000]
            xplotlabel = ''
            yplotlabel = ''

        if user_xlabel is not None:
            xplotlabel = user_xlabel
        if user_ylabel is not None:
            yplotlabel = user_ylabel

        # Use the automatically generated labels if none are supplied
        if ylabel is None:
            yplotlabel = 'time'
        if np.size(time_ticks) > 0:
            timeticks = time_ticks
        if np.size(time_labels) > 0:
            timelabels = time_labels

        # Swap axes if requested
        if swap_axes:
            x, y = y, x
            field = np.flipud(np.rot90(field))
            xmin, ymin = ymin, xmin
            xmax, ymax = ymax, xmax
            xplotlabel, yplotlabel = yplotlabel, xplotlabel
            lonlatticks, timeticks = timeticks, lonlatticks
            lonlatlabels, timelabels = timelabels, lonlatlabels

        # Set plot limits
        if plotvars.user_plot == 0:
            gopen(user_plot=0)
        gset(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, user_gset=user_gset)

        # Revert to time strings if set
        if all(val is not None for val in [tmin, tmax]):
            plotvars.ymin = tmin
            plotvars.ymax = tmax

        # Set and label axes
        axes_plot(xticks=lonlatticks, xticklabels=lonlatlabels,
                  yticks=timeticks, yticklabels=timelabels,
                  xlabel=xplotlabel, ylabel=yplotlabel)

        # Get colour scale for use in contouring
        # If colour bar extensions are enabled then the colour map goes
        # from 1 to ncols-2.  The colours for the colour bar extensions are
        # then changed on the colorbar and plot after the plot is made
        colmap = cscale_get_map()

        # Filled contours
        if fill:
            colmap = cscale_get_map()
            cmap = matplotlib.colors.ListedColormap(colmap)
            if (plotvars.levels_extend ==
                    'min' or plotvars.levels_extend == 'both'):
                cmap.set_under(plotvars.cs[0])
            if (plotvars.levels_extend ==
                    'max' or plotvars.levels_extend == 'both'):
                cmap.set_over(plotvars.cs[-1])

            plotvars.image = plotvars.plot.contourf(x, y, field * fmult, clevs,
                                   extend=plotvars.levels_extend,
                                   cmap=cmap,
                                   norm=plotvars.norm, alpha=alpha,
                                   zorder=zorder)

        # Block fill
        if blockfill:
            if isinstance(f, cf.Field):
                if f.coord('X').has_bounds():
                    if ptype == 4:
                        xpts = np.squeeze(f.coord('X').bounds.array)[:, 0]
                        xpts = np.append(xpts, f.coord('X').bounds.array[-1, 1])
                    if ptype == 5:
                        xpts = np.squeeze(f.coord('Y').bounds.array)[:, 0]
                        xpts = np.append(xpts, f.coord('Y').bounds.array[-1, 1])
                    ypts = np.squeeze(f.coord('T').bounds.array)[:, 0]
                    ypts = np.append(ypts, f.coord('T').bounds.array[-1, 1])
                    if swap_axes:
                        xpts, ypts = ypts, xpts
                        field_orig = np.flipud(np.rot90(field_orig))

                    bfill(f=field_orig * fmult, x=xpts, y=ypts, clevs=clevs,
                          lonlat=False, bound=1, alpha=alpha, fast=blockfill_fast, zorder=zorder)
                else:
                    if swap_axes:
                        x_orig, y_orig = y_orig, x_orig
                        field_orig = np.flipud(np.rot90(field_orig))
                    bfill(f=field_orig * fmult, x=x_orig, y=y_orig, clevs=clevs,
                          lonlat=False, bound=0, alpha=alpha, fast=blockfill_fast, zorder=zorder)

            else:
                if swap_axes:
                    x_orig, y_orig = y_orig, x_orig
                    field_orig = np.flipud(np.rot90(field_orig))
                bfill(f=field_orig * fmult, x=x_orig, y=y_orig, clevs=clevs,
                      lonlat=False, bound=0, alpha=alpha, fast=blockfill_fast, zorder=zorder)

        # Contour lines and labels
        if lines:
            cs = plotvars.plot.contour(x, y, field * fmult, clevs, colors=colors,
                                       linewidths=linewidths, linestyles=linestyles, alpha=alpha)
            if line_labels and type(clevs) == list:
                nd = ndecs(clevs)
                fmt = '%d'
                if nd != 0:
                    fmt = '%1.' + str(nd) + 'f'
                plotvars.plot.clabel(cs, fmt=fmt, colors=colors, zorder=zorder,
                                     fontsize=text_fontsize)

                # Thick zero contour line
                if zero_thick:
                    cs = plotvars.plot.contour(x, y, field * fmult,
                                               [-1e-32, 0], colors=colors,
                                               linewidths=zero_thick,
                                               linestyles=linestyles, alpha=alpha,
                                               zorder=zorder)
        # Titles for dimensions
        if titles:
            dim_titles(title_dims, dims=True)

        # Color bar
        if colorbar:
            cbar(labels=cbar_labels,
                 orientation=cb_orient,
                 position=colorbar_position,
                 shrink=colorbar_shrink,
                 title=colorbar_title,
                 fontsize=colorbar_fontsize,
                 fontweight=colorbar_fontweight,
                 text_up_down=colorbar_text_up_down,
                 text_down_up=colorbar_text_down_up,
                 drawedges=colorbar_drawedges,
                 fraction=colorbar_fraction,
                 thick=colorbar_thick,
                 levs=clevs,
                 anchor=colorbar_anchor,
                 verbose=verbose)

        # Title
        plotvars.plot.set_title(
            title,
            y=1.03,
            fontsize=title_fontsize,
            fontweight=title_fontweight)

        # reset plot limits if not a user plot
        if user_gset == 0:
            gset()

    ###########################
    # Rotated pole contour plot
    ###########################
    if ptype == 6:

        # Extract x and y grid points
        if plotvars.proj == 'cyl':
            xpts = x
            ypts = y
        else:
            xpts = np.arange(np.size(x))
            ypts = np.arange(np.size(y))

        if verbose:
            print('con - making a rotated pole plot')
        user_gset = plotvars.user_gset
        if plotvars.user_plot == 0:
            gopen(user_plot=0)

        # Set plot limits
        if plotvars.proj == 'rotated':
            plotargs = {}
            gset(xmin=0, xmax=np.size(xpts) - 1,
                 ymin=0, ymax=np.size(ypts) - 1,
                 user_gset=user_gset)
            plot = plotvars.plot

        # Set plot limits
        if plotvars.proj == 'UKCP':
            plot = plotvars.plot
            plotargs = {}

        if plotvars.proj == 'cyl':
            rotated_pole = f.ref('grid_mapping_name:rotated_latitude_longitude')
            xpole = rotated_pole['grid_north_pole_longitude']
            ypole = rotated_pole['grid_north_pole_latitude']

            transform = ccrs.RotatedPole(pole_latitude=ypole,
                                         pole_longitude=xpole)
            plotargs = {'transform': transform}
            if plotvars.user_mapset == 1:
                set_map()
            else:
                if np.ndim(xpts) == 1:
                    lonpts, latpts = np.meshgrid(xpts, ypts)
                else:
                    lonpts = xpts
                    latpts = ypts

                points = ccrs.PlateCarree().transform_points(transform, lonpts.flatten(),
                                                             latpts.flatten())
                lons = np.array(points)[:, 0]
                lats = np.array(points)[:, 1]

                mapset(lonmin=np.min(lons), lonmax=np.max(lons),
                       latmin=np.min(lats), latmax=np.max(lats),
                       user_mapset=0, resolution=resolution_orig)
                set_map()

            plotargs = {'transform': transform}
            plot = plotvars.mymap

        # Get colour scale for use in contouring
        # If colour bar extensions are enabled then the colour map goes
        # from 1 to ncols-2.  The colours for the colour bar extensions are
        # then changed on the colorbar and plot after the plot is made
        colmap = cscale_get_map()

        # Filled contours
        if fill:
            colmap = cscale_get_map()
            cmap = matplotlib.colors.ListedColormap(colmap)
            if (plotvars.levels_extend ==
                    'min' or plotvars.levels_extend == 'both'):
                cmap.set_under(plotvars.cs[0])
            if (plotvars.levels_extend ==
                    'max' or plotvars.levels_extend == 'both'):
                cmap.set_over(plotvars.cs[-1])

            plot.contourf(xpts, ypts, field * fmult, clevs,
                          extend=plotvars.levels_extend,
                          cmap=cmap,
                          norm=plotvars.norm, alpha=alpha,
                          zorder=zorder, **plotargs)

        # Block fill
        if blockfill:
            bfill(f=field_orig * fmult,
                  x=xpts,
                  y=ypts,
                  clevs=clevs,
                  lonlat=False,
                  bound=0,
                  alpha=alpha, fast=blockfill_fast,
                  zorder=zorder)

        # Contour lines and labels
        if lines:
            cs = plot.contour(xpts, ypts, field * fmult, clevs, colors=colors,
                              linewidths=linewidths, linestyles=linestyles,
                              zorder=zorder, **plotargs)
            if line_labels and type(clevs) == list:
                nd = ndecs(clevs)
                fmt = '%d'
                if nd != 0:
                    fmt = '%1.' + str(nd) + 'f'
                plot.clabel(cs, fmt=fmt, colors=colors, zorder=zorder,
                            fontsize=text_fontsize)

            # Thick zero contour line
            if zero_thick:
                cs = plot.contour(xpts, ypts, field * fmult,
                                  [-1e-32, 0], colors=colors,
                                  linewidths=zero_thick,
                                  linestyles=linestyles, alpha=alpha,
                                  zorder=zorder, **plotargs)

        # Titles for dimensions
        if titles:
            dim_titles(title_dims, dims=True)

        # Color bar
        if colorbar:
            cbar(labels=cbar_labels,
                 orientation=cb_orient,
                 position=colorbar_position,
                 shrink=colorbar_shrink,
                 title=colorbar_title,
                 fontsize=colorbar_fontsize,
                 fontweight=colorbar_fontweight,
                 text_up_down=colorbar_text_up_down,
                 text_down_up=colorbar_text_down_up,
                 drawedges=colorbar_drawedges,
                 fraction=colorbar_fraction,
                 thick=colorbar_thick,
                 levs=clevs,
                 anchor=colorbar_anchor,
                 verbose=verbose)

        # Rotated grid axes
        if axes:
            if plotvars.proj == 'cyl':
                plot_map_axes(axes=axes, xaxis=xaxis, yaxis=yaxis,
                              xticks=xticks, xticklabels=xticklabels,
                              yticks=yticks, yticklabels=yticklabels,
                              user_xlabel=user_xlabel, user_ylabel=user_ylabel,
                              verbose=verbose)
            else:
                rgaxes(xpole=xpole, ypole=ypole, xvec=x, yvec=y,
                       xticks=xticks, xticklabels=xticklabels,
                       yticks=yticks, yticklabels=yticklabels,
                       axes=axes, xaxis=xaxis, yaxis=yaxis,
                       xlabel=xlabel, ylabel=ylabel)
                

        if plotvars.proj == 'rotated' or plotvars.proj == 'UKCP':
            # Remove Matplotlib default axis labels
            axes_plot(xticks=[100000000], xticklabels=[''],
                      yticks=[100000000], yticklabels=[''],
                      xlabel='', ylabel='')

        # Add title and coastlines for cylindrical projection
        if plotvars.proj == 'cyl':
            # Coastlines
            feature = cfeature.NaturalEarthFeature(
                          name='land', category='physical',
                          scale=plotvars.resolution,
                          facecolor='none')
            plotvars.mymap.add_feature(feature, edgecolor=continent_color,
                                       linewidth=continent_thickness,
                                       linestyle=continent_linestyle,
                                       zorder=zorder)

            # Title
            if title != '':
                map_title(title)

        # Add title for native grid
        if plotvars.proj == 'rotated':
            # Title
            plotvars.plot.set_title(title, y=1.03,
                                    fontsize=title_fontsize,
                                    fontweight=title_fontweight)

        # reset plot limits if not a user plot
        if plotvars.user_gset == 0:
            gset()

    #############
    # Other plots
    #############
    if ptype == 0:
        if verbose:
            print('con - making an other plot')
        if plotvars.user_plot == 0:
            gopen(user_plot=0)
        user_gset = plotvars.user_gset

        # Set axis labels to None
        xplotlabel = None
        yplotlabel = None

        cf_field = False
        if f is not None:
            if isinstance(f, cf.Field):
                cf_field = True
                f = f.squeeze()

        # Work out axes if none are supplied
        if any(val is None for val in [
               plotvars.xmin, plotvars.xmax, plotvars.ymin, plotvars.ymax]):
            xmin = np.nanmin(x)
            xmax = np.nanmax(x)
            ymin = np.nanmin(y)
            ymax = np.nanmax(y)
        else:
            xmin = plotvars.xmin
            xmax = plotvars.xmax
            ymin = plotvars.ymin
            ymax = plotvars.ymax
            
            
        # Change from date string to a number if strings are passed
        time_xstr = False
        time_ystr = False

        try:
            float(xmin)
        except Exception:
            time_xstr = True
        try:
            float(ymin)
        except Exception:
            time_ystr = True

        xaxisticks = None
        yaxisticks = None
        xtimeaxis = False
        ytimeaxis = False


        if cf_field and f.has_construct('T'):
            if np.size(f.construct('T').array) > 1:

                taxis = f.construct('T')

                data_axes = f.get_data_axes()
                count = 1
                for d in data_axes:
                    i = f.constructs.domain_axis_identity(d)
                    try:
                        c = f.coordinate([i])
                        if np.size(c.array) > 1:
                            test_for_time_axis = False
                            sn = getattr(c, 'standard_name', 'NoName')
                            an = c.get_property('axis', 'NoName')
                            if (sn == 'time' or an == 'T'):
                                test_for_time_axis = True

                            if count == 1:
                                if test_for_time_axis:
                                    ytimeaxis = True
                            elif count == 2:
                                if test_for_time_axis:
                                    xtimeaxis = True
                            count += 1
                    except ValueError:
                        print("no sensible coordinates for this axis")

                if time_xstr or time_ystr:
                    ref_time = f.construct('T').units
                    ref_calendar = f.construct('T').calendar
                    time_units = cf.Units(ref_time, ref_calendar)

                    if time_xstr:
                        t = cf.Data(cf.dt(xmin), units=time_units)
                        xmin = t.array
                        t = cf.Data(cf.dt(xmax), units=time_units)
                        xmax = t.array
                        taxis = cf.Data([xmin, xmax], units=time_units)
                        taxis.calendar = ref_calendar

                    if time_ystr:
                        t = cf.Data(cf.dt(ymin), units=time_units)
                        ymin = t.array
                        t = cf.Data(cf.dt(ymax), units=time_units)
                        ymax = t.array
                        taxis = cf.Data([ymin, ymax], units=time_units)
                        taxis.calendar = ref_calendar

                if xtimeaxis:
                    xaxisticks, xaxislabels, xplotlabel = timeaxis(taxis)
                if ytimeaxis:
                    yaxisticks, yaxislabels, yplotlabel = timeaxis(taxis)
                
        
        if cf_field:
            coords = list(f.coords())
            mycoords = []
            for coord in coords:
                if np.size(f.coord(coord).array) > 1:
                    mycoords.append(coord)
            mycoords.reverse()
            
            for icoord in np.arange(len(mycoords)):
            
                myaxisticks = None
                myaxislabels = None
                mylabel = None
               
                if f.coord(mycoords[icoord]).X:
                    myaxisticks, myaxislabels = mapaxis(np.min(f.coord('X').array), np.max(f.coord('X').array), type=1)
                    mylabel = 'longitude'
                
                if f.coord(mycoords[icoord]).Y:
                    myaxisticks, myaxislabels = mapaxis(np.min(f.coord('Y').array), np.max(f.coord('Y').array), type=2)
                    mylabel = 'latitude'
                    
                if myaxisticks is not None:
                    if icoord == 0:
                        xaxisticks, xaxislabels, xlabel = myaxisticks, myaxislabels, mylabel
                    if icoord == 1:
                        yaxisticks, yaxislabels, ylabel = myaxisticks, myaxislabels, mylabel                   
                    
                    

                
                
                
        if xaxisticks is None:
            xaxisticks = gvals(dmin=xmin, dmax=xmax, mod=False)[0]
            xaxislabels = xaxisticks

        if yaxisticks is None:
            yaxisticks = gvals(dmin=ymax, dmax=ymin, mod=False)[0]
            yaxislabels = yaxisticks

        if user_xlabel is not None:
            xplotlabel = user_xlabel
        else:
            if xplotlabel is None:
                xplotlabel = xlabel
        if user_ylabel is not None:
            yplotlabel = user_ylabel
        else:
            if yplotlabel is None:
                yplotlabel = ylabel

        # Draw axes
        if axes:
            if xaxis:
                if xticks is not None:
                    xaxisticks = xticks
                    xaxislabels = xticks
                    if xticklabels is not None:
                        xaxislabels = xticklabels
            else:
                xaxisticks = [100000000]
                xlabel = ''

            if yaxis:
                if yticks is not None:
                    yaxisticks = yticks
                    yaxislabels = yticks
                    if yticklabels is not None:
                        yaxislabels = yticklabels
            else:
                yaxisticks = [100000000]
                ylabel = ''

        else:
            xaxisticks = [100000000]
            yaxisticks = [100000000]
            xlabel = ''
            ylabel = ''

        # Swap axes if requested
        if swap_axes:
            x, y = y, x
            field = np.flipud(np.rot90(field))
            xmin, ymin = ymin, xmin
            xmax, ymax = ymax, xmax
            xplotlabel, yplotlabel = yplotlabel, xplotlabel
            xaxisticks, yaxisticks = yaxisticks, xaxisticks
            xaxislabels, yaxislabels = yaxislabels, xaxislabels

        # Set plot limits and set default plot labels
        gset(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, user_gset=user_gset)

        # Draw axes
        axes_plot(xticks=xaxisticks, xticklabels=xaxislabels,
                  yticks=yaxisticks, yticklabels=yaxislabels,
                  xlabel=xplotlabel, ylabel=yplotlabel)

        # Get colour scale for use in contouring
        # If colour bar extensions are enabled then the colour map goes
        # then from 1 to ncols-2.  The colours for the colour bar extensions
        # are changed on the colorbar and plot after the plot is made
        colmap = cscale_get_map()

        # Filled contours
        if fill:
            colmap = cscale_get_map()
            cmap = matplotlib.colors.ListedColormap(colmap)
            if (plotvars.levels_extend ==
                    'min' or plotvars.levels_extend == 'both'):
                cmap.set_under(plotvars.cs[0])
            if (plotvars.levels_extend ==
                    'max' or plotvars.levels_extend == 'both'):
                cmap.set_over(plotvars.cs[-1])

            plotvars.image = plotvars.plot.contourf(x, y, field * fmult, clevs,
                                   extend=plotvars.levels_extend,
                                   cmap=cmap,
                                   norm=plotvars.norm, alpha=alpha,
                                   zorder=zorder)

        # Block fill
        if blockfill:
            bfill(f=field_orig * fmult, x=x_orig, y=y_orig, clevs=clevs,
                  lonlat=False, bound=0, alpha=alpha, fast=blockfill_fast, zorder=zorder)

        # Contour lines and labels
        if lines:
            cs = plotvars.plot.contour(x, y, field * fmult, clevs, colors=colors,
                                       linewidths=linewidths, linestyles=linestyles,
                                       zorder=zorder)
            if line_labels and type(clevs) == list:
                nd = ndecs(clevs)
                fmt = '%d'
                if nd != 0:
                    fmt = '%1.' + str(nd) + 'f'
                plotvars.plot.clabel(cs, fmt=fmt, colors=colors, zorder=zorder,
                                     fontsize=text_fontsize)

            # Thick zero contour line
            if zero_thick:
                cs = plotvars.plot.contour(x, y, field * fmult, [-1e-32, 0],
                                           colors=colors,
                                           linewidths=zero_thick,
                                           linestyles=linestyles, alpha=alpha,
                                           zorder=zorder)

        # Titles for dimensions
        if titles:
            dim_titles(title_dims, dims=True)

        # Color bar
        if colorbar:
            cbar(labels=cbar_labels,
                 orientation=cb_orient,
                 position=colorbar_position,
                 shrink=colorbar_shrink,
                 title=colorbar_title,
                 fontsize=colorbar_fontsize,
                 fontweight=colorbar_fontweight,
                 text_up_down=colorbar_text_up_down,
                 text_down_up=colorbar_text_down_up,
                 drawedges=colorbar_drawedges,
                 fraction=colorbar_fraction,
                 thick=colorbar_thick,
                 levs=clevs,
                 anchor=colorbar_anchor,
                 verbose=verbose)

        # Title
        plotvars.plot.set_title(
            title,
            y=1.03,
            fontsize=title_fontsize,
            fontweight=title_fontweight)

        # reset plot limits if not a user plot
        if plotvars.user_gset == 0:
            gset()

    ############################
    # Set axis width if required
    ############################
    if plotvars.axis_width is not None:
        for axis in ['top', 'bottom', 'left', 'right']:
            plotvars.plot.spines[axis].set_linewidth(plotvars.axis_width)

    ################################
    # Add a master title if reqested
    ################################
    if plotvars.master_title is not None:
        location = plotvars.master_title_location
        plotvars.master_plot.text(location[0], location[1],
                                  plotvars.master_title,
                                  horizontalalignment='center',
                                  fontweight=plotvars.master_title_fontweight,
                                  fontsize=plotvars.master_title_fontsize)

    # Reset map resolution
    if plotvars.user_mapset == 0:
        mapset()
        mapset(resolution=resolution_orig)

    ##################
    # Save or view plot
    ##################

    if plotvars.user_plot == 0:
        if verbose:
            print('con - saving or viewing plot')

        np.seterr(**old_settings)  # reset to default numpy error settings

        gclose()


def mapset(lonmin=None, lonmax=None, latmin=None, latmax=None, proj='cyl',
           boundinglat=0, lon_0=0, lat_0=40, resolution='110m', user_mapset=1,
           aspect=None):
    """
     | mapset sets the mapping parameters.
     |
     | lonmin=lonmin - minimum longitude
     | lonmax=lonmax - maximum longitude
     | latmin=latmin - minimum latitude
     | latmax=latmax - maximum latitude
     | proj=proj - 'cyl' for cylindrical projection. 'npstere' or 'spstere'
     |      for northern hemisphere or southern hemisphere polar stereographic.
     |      ortho, merc, moll, robin and lcc are abreviations for orthographic,
     |      mercator, mollweide, robinson and lambert conformal projections
     |      'rotated' for contour plots on the native rotated grid.
     |
     | boundinglat=boundinglat - edge of the viewable latitudes in a
     |      stereographic plot
     | lon_0=0 - longitude centre of desired map domain in polar
     |           stereographic and orthogrphic plots
     | lat_0=40 - latitude centre of desired map domain in orthogrphic plots
     | resolution='110m' - the map resolution - can be one of '110m',
     | '50m' or '10m'.  '50m' means 1:50,000,000 and not 50 metre.
     | user_mapset=user_mapset - variable to indicate whether a user call
     |      to mapset has been made.
     |
     | The default map plotting projection is the cyclindrical equidistant
     | projection from -180 to 180 in longitude and -90 to 90 in latitude.
     | To change the map view in this projection to over the United Kingdom,
     | for example, you would use
     | mapset(lonmin=-6, lonmax=3, latmin=50, latmax=60)
     | or
     | mapset(-6, 3, 50, 60)
     |
     | The limits are -360 to 720 in longitude so to look at the equatorial
     | Pacific you could use
     | mapset(lonmin=90, lonmax=300, latmin=-30, latmax=30)
     | or
     | mapset(lonmin=-270, lonmax=-60, latmin=-30, latmax=30)
     |
     | The default setting for the cylindrical projection is for 1 degree of
     | longitude to have the same size as one degree of latitude.  When plotting
     | a smaller map setting aspect='auto' turns this off and the map fills the
     | plot area. Setting aspect to a number a circle will be stretched such that
     | the height is num times the width. aspect=1 is the same as aspect='equal'.
     |
     | The proj parameter accepts 'npstere' and 'spstere' for northern
     | hemisphere or southern hemisphere polar stereographic projections.
     | In addition to these the boundinglat parameter sets the edge of the
     | viewable latitudes and lon_0 sets the centre of desired map domain.
     |
     |
     |
     | Map settings are persistent until a new call to mapset is made. To
     | reset to the default map settings use mapset().

     :Returns:
      None
    """

    # Set the continent resolution
    plotvars.resolution = resolution

    if all(val is None for val in [
           lonmin, lonmax, latmin, latmax, aspect]) and proj == 'cyl':
        plotvars.lonmin = -180
        plotvars.lonmax = 180
        plotvars.latmin = -90
        plotvars.latmax = 90
        plotvars.proj = 'cyl'
        plotvars.user_mapset = 0
        plotvars.aspect = 'equal'

        plotvars.plot_xmin = None
        plotvars.plot_xmax = None
        plotvars.plot_ymin = None
        plotvars.plot_ymax = None

        return

    # Set the aspect ratio
    if aspect is None:
        aspect = 'equal'
    plotvars.aspect = aspect

    if lonmin is None:
        lonmin = -180
    if lonmax is None:
        lonmax = 180
    if latmin is None:
        latmin = -90
        if proj == 'merc':
            latmin = -80
    if latmax is None:
        latmax = 90
        if proj == 'merc':
            latmax = 80

    if proj == 'moll':
        lonmin = lon_0 - 180
        lonmax = lon_0 + 180

    plotvars.lonmin = lonmin
    plotvars.lonmax = lonmax
    plotvars.latmin = latmin
    plotvars.latmax = latmax
    plotvars.proj = proj
    plotvars.boundinglat = boundinglat
    plotvars.lon_0 = lon_0
    plotvars.lat_0 = lat_0
    plotvars.user_mapset = user_mapset


def levs(min=None, max=None, step=None, manual=None, extend='both'):
    """
     | The levs command manually sets the contour levels.

     | min=min - minimum level
     | max=max - maximum level
     | step=step - step between levels
     | manual= manual - set levels manually
     | extend='neither', 'both', 'min', or 'max' - colour bar limit extensions

     | Use the levs command when a predefined set of levels is required. The
     | min, max and step parameters can be used to define a set of  levels.
     | These can take integer or floating point numbers. If just the step is
     | defined then cf-plot will internally try to define a reasonable set
     | of levels.


     | If colour filled contours are plotted then the default is to extend
     | the minimum and maximum contours coloured for out of range values
     | - extend='both'.

     | Once a user call is made to levs the levels are persistent.
     | i.e. the next plot will use the same set of levels.
     | Use levs() to reset to undefined levels.

     :Returns:
      None

    """

    if all(val is None for val in [min, max, step, manual]):
        plotvars.levels = None
        plotvars.levels_min = None
        plotvars.levels_max = None
        plotvars.levels_step = None
        plotvars.levels_extend = 'both'
        plotvars.norm = None
        plotvars.user_levs = 0
        return

    if manual is not None:
        plotvars.levels = np.array(manual)
        plotvars.levels_min = None
        plotvars.levels_max = None
        plotvars.levels_step = None
        # Set the normalization object as we are using potentially unevenly
        # spaced levels
        ncolors = np.size(plotvars.levels)
        if extend == 'both' or extend == 'max':
            ncolors = ncolors - 1
        plotvars.norm = matplotlib.colors.BoundaryNorm(
            boundaries=plotvars.levels, ncolors=ncolors)
        plotvars.user_levs = 1
    else:
        if all(val is not None for val in [min, max, step]):
            plotvars.levels_min = min
            plotvars.levels_max = max
            plotvars.levels_step = step
            plotvars.norm = None
            if all(isinstance(item, int) for item in [min, max, step]):
                lstep = step * 1e-10
                levs = (np.arange(min, max + lstep, step, dtype=np.float64))
                levs = ((levs * 1e10).astype(np.int64)).astype(np.float64)
                levs = (levs / 1e10).astype(np.int)
                plotvars.levels = levs
            else:
                lstep = step * 1e-10
                levs = np.arange(min, max + lstep, step, dtype=np.float64)
                levs = (levs * 1e10).astype(np.int64).astype(np.float64)
                levs = levs / 1e10
                plotvars.levels = levs
            plotvars.user_levs = 1

            # Check for spurious decimal places due to numeric representation
            # and fix if found
            for pt in np.arange(np.size(plotvars.levels)):
                ndecs = str(plotvars.levels[pt])[::-1].find('.')
                if ndecs > 7:
                    plotvars.levels[pt] = round(plotvars.levels[pt], 7)

    # If step only is set then reset user_levs to zero
    if step is not None and all(val is None for val in [min, max]):
        plotvars.user_levs = 0
        plotvars.levels = None
        plotvars.levels_step = step

    # Check extend has a proper value
    if extend not in ['neither', 'min', 'max', 'both']:
        errstr = "\n\n extend must be one of 'neither', 'min', 'max', 'both'\n"
        raise TypeError(errstr)
    plotvars.levels_extend = extend


def mapaxis(min=None, max=None, type=None):
    """
     | mapaxis is used to work out a sensible set of longitude and latitude
     | tick marks and labels.  This is an internal routine and is not used
     | by the user.

     | min=None - minimum axis value
     | max=None - maximum axis value
     | type=None - 1 = longitude, 2 = latitude

     :Returns:
      longtitude/latitude ticks and longitude/latitude tick labels
     |
     |
     |
     |
     |
     |
     |
    """

    degsym = ''
    if plotvars.degsym:
        degsym = r'$\degree$'
    if type == 1:
        lonmin = min
        lonmax = max
        lonrange = lonmax - lonmin
        lonstep = 60
        if lonrange <= 180:
            lonstep = 30
        if lonrange <= 90:
            lonstep = 10
        if lonrange <= 30:
            lonstep = 5
        if lonrange <= 10:
            lonstep = 2
        if lonrange <= 5:
            lonstep = 1

        lons = np.arange(-720, 720 + lonstep, lonstep)
        lonticks = []
        for lon in lons:
            if lon >= lonmin and lon <= lonmax:
                lonticks.append(lon)

        lonlabels = []
        for lon in lonticks:
            lon2 = np.mod(lon + 180, 360) - 180
            if lon2 < 0 and lon2 > -180:
                if lon != 180:
                    lonlabels.append(str(abs(lon2)) + degsym + 'W')

            if lon2 > 0 and lon2 <= 180:
                lonlabels.append(str(lon2) + degsym + 'E')
            if lon2 == 0:
                lonlabels.append('0' + degsym)

            if lon == 180 or lon == -180:
                lonlabels.append('180' + degsym)

        return(lonticks, lonlabels)

    if type == 2:
        latmin = min
        latmax = max
        latrange = latmax - latmin
        latstep = 30
        if latrange <= 90:
            latstep = 10
        if latrange <= 30:
            latstep = 5
        if latrange <= 10:
            latstep = 2
        if latrange <= 5:
            latstep = 1

        lats = np.arange(-90, 90 + latstep, latstep)
        latticks = []
        for lat in lats:
            if lat >= latmin and lat <= latmax:
                latticks.append(lat)

        latlabels = []
        for lat in latticks:
            if lat < 0:
                latlabels.append(str(abs(lat)) + degsym + 'S')
            if lat > 0:
                latlabels.append(str(lat) + degsym + 'N')
            if lat == 0:
                latlabels.append('0' + degsym)

        return(latticks, latlabels)


def timeaxis(dtimes=None):
    """
     | timeaxis is used to work out a sensible set of time labels and tick
     | marks given a time span  This is an internal routine and is not used
     | by the user.

     | dtimes=None - data times as a CF variable

     :Returns:
      time ticks and labels
     |
     |
     |
     |
     |
     |
     |
    """

    time_units = dtimes.Units

    time_ticks = []
    time_labels = []
    axis_label = 'Time'

    yearmin = min(dtimes.year.array)
    yearmax = max(dtimes.year.array)
    tmin = min(dtimes.dtarray)
    tmax = max(dtimes.dtarray)
    if hasattr(dtimes, 'calendar'):
        calendar = dtimes.calendar
    else:
        calendar = 'standard'

    if plotvars.user_gset != 0:
        if isinstance(plotvars.xmin, str):
            t = cf.Data(cf.dt(plotvars.xmin), units=time_units, calendar=calendar)
            yearmin = int(t.year)
            t = cf.Data(cf.dt(plotvars.xmax), units=time_units, calendar=calendar)
            yearmax = int(t.year)
            tmin = cf.dt(plotvars.xmin, units=time_units, calendar=calendar)
            tmax = cf.dt(plotvars.xmax, units=time_units, calendar=calendar)
        if isinstance(plotvars.ymin, str):
            t = cf.Data(cf.dt(plotvars.ymin), units=time_units, calendar=calendar)
            yearmin = int(t.year)
            t = cf.Data(cf.dt(plotvars.ymax), units=time_units, calendar=calendar)
            yearmax = int(t.year)
            tmin = cf.dt(plotvars.ymin, calendar=calendar)
            tmax = cf.dt(plotvars.ymax, calendar=calendar)

    # Years
    span = yearmax - yearmin
    if span > 4 and span < 3000:
        axis_label = 'Time (year)'
        tvals = []
        if span <= 15:
            step = 1
        if span > 15:
            step = 2
        if span > 30:
            step = 5
        if span > 60:
            step = 10
        if span > 160:
            step = 20
        if span > 300:
            step = 50
        if span > 600:
            step = 100
        if span > 1300:
            step = 200

        if plotvars.tspace_year is not None:
            step = plotvars.tspace_year

        years = np.arange(yearmax / step + 2) * step
        tvals = years[np.where((years >= yearmin) & (years <= yearmax))]

        # Catch tvals if not properly defined and use gvals to generate some
        # year tick marks
        if np.size(tvals) < 2:
            tvals = gvals(dmin=yearmin, dmax=yearmax)[0]

        for year in tvals:
            time_ticks.append(np.min(
                (cf.Data(cf.dt(str(int(year)) + '-01-01 00:00:00'),
                 units=time_units, calendar=calendar).array)))
            time_labels.append(str(int(year)))

    # Months
    if yearmax - yearmin <= 4:

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug',  'Sep', 'Oct', 'Nov', 'Dec']

        # Check number of labels with 1 month steps
        tsteps = 0
        for year in np.arange(yearmax - yearmin + 1) + yearmin:
            for month in np.arange(12):
                mytime = cf.dt(str(year) + '-' +
                               str(month + 1) + '-01 00:00:00', calendar=calendar)
                if mytime >= tmin and mytime <= tmax:
                    tsteps = tsteps + 1

        if tsteps < 17:
            mvals = np.arange(12)
        if tsteps >= 17:
            mvals = np.arange(4) * 3

        for year in np.arange(yearmax - yearmin + 1) + yearmin:
            for month in mvals:
                mytime = cf.dt(str(year) + '-' +
                               str(month + 1) + '-01 00:00:00', calendar=calendar)
                if mytime >= tmin and mytime <= tmax:
                    time_ticks.append(
                        np.min((cf.Data(mytime, units=time_units, calendar=calendar).array)))
                    time_labels.append(
                        str(months[month]) + ' ' + str(int(year)))

    # Days and hours
    if np.size(time_ticks) <= 2:
        myday = cf.dt(int(tmin.year), int(tmin.month), int(tmin.day), calendar=calendar)
        not_found = 0
        hour_counter = 0
        span = 0
        while not_found <= 48:
            mydate = cf.Data(myday, dtimes.Units) + \
                cf.Data(hour_counter, 'hour')
            if mydate >= tmin and mydate <= tmax:
                span = span + 1
            else:
                not_found = not_found + 1

            hour_counter = hour_counter + 1

        step = 1
        if span > 13:
            step = 1
        if span > 13:
            step = 4
        if span > 25:
            step = 6
        if span > 100:
            step = 12
        if span > 200:
            step = 24
        if span > 400:
            step = 48
        if span > 800:
            step = 96
        if plotvars.tspace_hour is not None:
            step = plotvars.tspace_hour
        if plotvars.tspace_day is not None:
            step = plotvars.tspace_day * 24

        not_found = 0
        hour_counter = 0
        axis_label = 'Time (hour)'
        if span >= 24:
            axis_label = 'Time'
        time_ticks = []
        time_labels = []

        while not_found <= 48:
            mytime = cf.Data(myday, dtimes.Units) + cf.Data(hour_counter, 'hour')
            if mytime >= tmin and mytime <= tmax:
                time_ticks.append(np.min(mytime.array))
                label = str(mytime.year) + '-' + str(mytime.month) + '-' + str(mytime.day)
                if (hour_counter/24 != int(hour_counter/24)):
                    label += ' ' + str(mytime.hour) + ':00:00'
                time_labels.append(label)
            else:
                not_found = not_found + 1

            hour_counter = hour_counter + step

    return(time_ticks, time_labels, axis_label)


def ndecs(data=None):
    """
    | ndecs finds the number of decimal places in an array.  Needed to make the
    | colour bar match the contour line labelling.

    | data=data - input array of values

    :Returns:
    |  maximum number of necimal places
    |
    |
    |
    |
    |
    |
    |
    |
    """

    maxdecs = 0

    for i in range(len(data)):
        number = data[i]
        a = str(number).split('.')
        if np.size(a) == 2:
            number_decs = len(a[1])
            if number_decs > maxdecs:
                maxdecs = number_decs

    return maxdecs


def axes(xticks=None, xticklabels=None, yticks=None, yticklabels=None,
         xstep=None, ystep=None, xlabel=None, ylabel=None, title=None):
    """
     | axes is a function to set axes plotting parameters. The xstep and ystep
     | parameters are used to label the axes starting at the left hand side and
     | bottom of the plot respectively. For tighter control over labelling use
     | xticks, yticks to specify the tick positions and xticklabels,
     | yticklabels to specify the associated labels.

     | xstep=xstep - x axis step
     | ystep=ystep - y axis step
     | xlabel=xlabel - label for the x-axis
     | ylabel=ylabel - label for the y-axis
     | xticks=xticks - values for x ticks
     | xticklabels=xticklabels - labels for x tick marks
     | yticks=yticks - values for y ticks
     | yticklabels=yticklabels - labels for y tick marks
     | title=None - set title
     |
     | Use axes() to reset all the axes plotting attributes to the default.

     :Returns:
      None
    """

    if all(val is None for val in [
           xticks, yticks, xticklabels, yticklabels, xstep, ystep, xlabel,
           ylabel, title]):
        plotvars.xticks = None
        plotvars.yticks = None
        plotvars.xticklabels = None
        plotvars.yticklabels = None
        plotvars.xstep = None
        plotvars.ystep = None
        plotvars.xlabel = None
        plotvars.ylabel = None
        plotvars.title = None
        return

    plotvars.xticks = xticks
    plotvars.yticks = yticks
    plotvars.xticklabels = xticklabels
    plotvars.yticklabels = yticklabels
    plotvars.xstep = xstep
    plotvars.ystep = ystep
    plotvars.xlabel = xlabel
    plotvars.ylabel = ylabel
    plotvars.title = title


def axes_plot(xticks=None, xticklabels=None, yticks=None, yticklabels=None,
              xlabel=None, ylabel=None, title=None):
    """
     | axes_plot is a system function to specify axes plotting parameters.
     | Use xticks, yticks to specify the tick positions and xticklabels,
     | yticklabels to specify the associated labels.
     |
     | xticks=xticks - values for x ticks
     | xticklabels=xticklabels - labels for x tick marks
     | yticks=yticks - values for y ticks
     | yticklabels=yticklabels - labels for y tick marks
     | xlabel=xlabel - label for the x-axis
     | ylabel=ylabel - label for the y-axis
     | title=None - set title
     |

     :Returns:
      None
    """

    if plotvars.title is not None:
        title = plotvars.title
    title_fontsize = plotvars.title_fontsize
    text_fontsize = plotvars.text_fontsize
    axis_label_fontsize = plotvars.axis_label_fontsize
    if title_fontsize is None:
        title_fontsize = 15
    if text_fontsize is None:
        text_fontsize = 11
    if axis_label_fontsize is None:
        axis_label_fontsize = 11
    axis_label_fontweight = plotvars.axis_label_fontweight
    title_fontweight = plotvars.title_fontweight

    if (plotvars.plot_type == 1 or plotvars.plot_type == 6) and plotvars.proj == 'cyl':
        plot = plotvars.mymap
        lon_mid = plotvars.lonmin + (plotvars.lonmax - plotvars.lonmin) / 2.0
        plotargs = {'crs': ccrs.PlateCarree()}
    else:
        plot = plotvars.plot
        plotargs = {}

    if xlabel is not None:
        plotvars.plot.set_xlabel(xlabel, fontsize=axis_label_fontsize,
                                 fontweight=axis_label_fontweight)
    if ylabel is not None:
        plotvars.plot.set_ylabel(ylabel, fontsize=axis_label_fontsize,
                                 fontweight=axis_label_fontweight)

    xticklen = (plotvars.lonmax - plotvars.lonmin)*0.007
    yticklen = (plotvars.latmax-plotvars.latmin)*0.014

    # set the plot
    if (plotvars.plot_type == 1 or plotvars.plot_type == 6):
        this_plot = plotvars.mymap
    else:
        this_plot = plotvars.plot

    if plotvars.plot_type == 6 and (plotvars.proj == 'rotated' or plotvars.proj == 'UKCP'):
        this_plot = plotvars.plot

    # get the plot bounds
    l, b, w, h = this_plot.get_position().bounds

    lonrange = plotvars.lonmax - plotvars.lonmin
    lon_mid = plotvars.lonmin + (plotvars.lonmax - plotvars.lonmin) / 2.0

    # Set the ticks and tick labels
    if xticks is not None:
        # fudge min and max longitude tick positions or the labels wrap
        xticks_new = xticks
        if lonrange >= 360:
            xticks_new[0] = xticks_new[0] + 0.01
            xticks_new[-1] = xticks_new[-1] - 0.01

        plot.set_xticks(xticks_new, **plotargs)
        plot.set_xticklabels(xticklabels,
                             rotation=plotvars.xtick_label_rotation,
                             horizontalalignment=plotvars.xtick_label_align)

        # Plot a corresponding tick on the top of the plot - cartopy feature?
        proj = ccrs.PlateCarree(central_longitude=lon_mid)
        if plotvars.plot_type == 1:
            for xval in xticks_new:
                xpt, ypt = proj.transform_point(xval, plotvars.latmax, ccrs.PlateCarree())
                ypt2 = ypt + yticklen
                plot.plot([xpt, xpt], [ypt, ypt2], color='k', linewidth=0.8, clip_on=False)

    if yticks is not None:
        plot.set_yticks(yticks, **plotargs)
        plot.set_yticklabels(yticklabels,
                             rotation=plotvars.ytick_label_rotation,
                             horizontalalignment=plotvars.ytick_label_align)

        # Plot a corresponding tick on the right of the plot - cartopy feature?
        if plotvars.plot_type == 1:
            proj = ccrs.PlateCarree(central_longitude=lon_mid)
            for ytick in yticks:
                xpt, ypt = proj.transform_point(plotvars.lonmax-0.001, ytick, ccrs.PlateCarree())
                xpt2 = xpt + xticklen
                plot.plot([xpt, xpt2], [ypt, ypt], color='k', linewidth=0.8, clip_on=False)

    # Set font size and weight
    for label in plot.xaxis.get_ticklabels():
        label.set_fontsize(axis_label_fontsize)
        label.set_fontweight(axis_label_fontweight)
    for label in plot.yaxis.get_ticklabels():
        label.set_fontsize(axis_label_fontsize)
        label.set_fontweight(axis_label_fontweight)

    # Title
    if title is not None:
        plot.set_title(title, y=1.03, fontsize=title_fontsize, fontweight=title_fontweight)


def gset(xmin=None, xmax=None, ymin=None, ymax=None,
         xlog=False, ylog=False, user_gset=1, twinx=None, twiny=None):
    """
     | Set plot limits for all non longitude-latitide plots.
     | xmin, xmax, ymin, ymax are all needed to set the plot limits.
     | Set xlog/ylog to True or 1 to get a log axis.
     |
     | xmin=None - x minimum
     | xmax=None - x maximum
     | ymin=None - y minimum
     | ymax=None - y maximum
     | xlog=False - log x
     | ylog=False - log y
     | twinx=None - set to True to make a twin y axis plot
     | twiny=None - set to True to make a twin x axis plot
     |
     | Once a user call is made to gset the plot limits are persistent.
     | i.e. the next plot will use the same set of plot limits.
     | Use gset() to reset to undefined plot limits i.e. the full range
     | of the data.
     |
     | To set date axes use date strings i.e.
     | cfp.gset(xmin = '1970-1-1', xmax = '1999-12-31', ymin = 285,
     |          ymax = 295)
     |
     | Note the correct date format is 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'
     | anything else will give unexpected results.

     :Returns:
      None

     |
     |
     |
     |

    """

    plotvars.user_gset = user_gset

    if all(val is None for val in [xmin, xmax, ymin, ymax]):
        plotvars.xmin = None
        plotvars.xmax = None
        plotvars.ymin = None
        plotvars.ymax = None
        plotvars.xlog = False
        plotvars.ylog = False
        plotvars.twinx = False
        plotvars.twiny = False
        plotvars.user_gset = 0
        return

    bcount = 0
    for val in [xmin, xmax, ymin, ymax]:
        if val is None:
            bcount = bcount + 1

    if bcount != 0 and bcount != 4:
        errstr = 'gset error\n'
        errstr += 'xmin, xmax, ymin, ymax all need to be passed to gset\n'
        errstr += 'to set the plot limits\n'
        raise Warning(errstr)

    plotvars.xmin = xmin
    plotvars.xmax = xmax
    plotvars.ymin = ymin
    plotvars.ymax = ymax
    plotvars.xlog = xlog
    plotvars.ylog = ylog

    # Check if any axes are time strings
    time_xstr = False
    time_ystr = False
    try:
        float(xmin)
    except Exception:
        time_xstr = True
    try:
        float(ymin)
    except Exception:
        time_ystr = True

    # Set plot limits
    if plotvars.plot is not None and twinx is None and twiny is None:
        if not time_xstr and not time_ystr:
            plotvars.plot.axis(
                [plotvars.xmin, plotvars.xmax, plotvars.ymin, plotvars.ymax])

        if plotvars.xlog:
            plotvars.plot.set_xscale('log')
        if plotvars.ylog:
            plotvars.plot.set_yscale('log')

    # Set twinx or twiny if requested
    if twinx is not None:
        plotvars.twinx = twinx
    if twiny is not None:
        plotvars.twiny = twiny


def gopen(rows=1, columns=1, user_plot=1, file='cfplot.png',
          orientation='landscape', figsize=[11.7, 8.3],
          left=None, right=None, top=None, bottom=None, wspace=None,
          hspace=None, dpi=None, user_position=False):
    """
     | gopen is used to open a graphic file.
     |
     | rows=1 - number of plot rows on the page
     | columns=1 - number of plot columns on the page
     | user_plot=1 - internal plot variable - do not use.
     | file='cfplot.png' - default file name
     | orientation='landscape' - orientation - also takes 'portrait'
     | figsize=[11.7, 8.3]  - figure size in inches
     | left=None - left margin in normalised coordinates - default=0.12
     | right=None - right margin in normalised coordinates - default=0.92
     | top=None - top margin in normalised coordinates - default=0.08
     | bottom=None - bottom margin in normalised coordinates - default=0.08
     | wspace=None - width reserved for blank space between subplots - default=0.2
     | hspace=None - height reserved for white space between subplots - default=0.2
     | dpi=None - resolution in dots per inch
     | user_position=False - set to True to supply plot position via gpos
     |               xmin, xmax, ymin, ymax values


     :Returns:
      None

     |
     |
     |
     |
     |

    """

    # Set values in globals
    plotvars.rows = rows
    plotvars.columns = columns
    if file != 'cfplot.png':
        plotvars.file = file
    plotvars.orientation = orientation
    plotvars.user_plot = user_plot
    plotvars.gpos_called = False

    # Set user defined plot area to None
    plotvars.plot_xmin = None
    plotvars.plot_xmax = None
    plotvars.plot_ymin = None
    plotvars.plot_ymax = None

    if left is None:
        left = 0.12
    if right is None:
        right = 0.92
    if top is None:
        top = 0.95
    if bottom is None:
        bottom = 0.08
        if rows >= 3:
            bottom = 0.1
    if wspace is None:
        wspace = 0.2
    if hspace is None:
        hspace = 0.2
        if rows >= 3:
            hspace = 0.5

    if orientation != 'landscape':
        if orientation != 'portrait':
            errstr = 'gopen error\n'
            errstr += 'orientation incorrectly set\n'
            errstr += 'input value was ' + orientation + '\n'
            errstr += 'Valid options are portrait or landscape\n'
            raise Warning(errstr)

    # Set master plot size
    if orientation == 'landscape':
        plotvars.master_plot = plot.figure(figsize=(figsize[0], figsize[1]))
    else:
        plotvars.master_plot = plot.figure(figsize=(figsize[1], figsize[0]))

    # Set margins
    plotvars.master_plot.subplots_adjust(
        left=left,
        right=right,
        top=top,
        bottom=bottom,
        wspace=wspace,
        hspace=hspace)

    # Set initial subplot
    if user_position is False and rows == 1 and columns == 1:
        gpos(pos=1)

    # Change tick length for plots > 2x2
    if (columns > 2 or rows > 2):
        matplotlib.rcParams['xtick.major.size'] = 2
        matplotlib.rcParams['ytick.major.size'] = 2

    # Set image resolution
    if dpi is not None:
        plotvars.dpi = dpi


def gclose(view=True):
    """
     | gclose saves a graphics file.  The default is to view the file as well
     | - use view = False to turn this off.

     | view = True - view graphics file

     :Returns:
      None

     |
     |
     |
     |
     |
     |
     |
     |
     |

    """

    # Reset the user_plot variable to off
    plotvars.user_plot = 0

    # Test for python or ipython
    interactive = False
    try:
        __IPYTHON__
        interactive = True
    except NameError:
        interactive = False

    if matplotlib.is_interactive():
        interactive = True

    # Remove whitespace if requested
    saveargs = {}
    if plotvars.tight:
        saveargs = {'bbox_inches': 'tight'}

    file = plotvars.file
    if file is not None:
        # Save a file
        type = 1
        if file[-3:] == '.ps':
            type = 1
        if file[-4:] == '.eps':
            type = 1
        if file[-4:] == '.png':
            type = 1
        if file[-4:] == '.pdf':
            type = 1
        if type is None:
            file = file + '.png'
        plotvars.master_plot.savefig(
            file, orientation=plotvars.orientation, dpi=plotvars.dpi, **saveargs)
        plot.close()
    else:
        if plotvars.viewer == 'display' and interactive is False:
            # Use Imagemagick display command if this exists
            disp = which('display')
            if disp is not None:
                tfile = 'cfplot.png'
                plotvars.master_plot.savefig(
                    tfile, orientation=plotvars.orientation, dpi=plotvars.dpi, **saveargs)
                matplotlib.pyplot.ioff()
                subprocess.Popen([disp, tfile])
            else:
                plotvars.viewer = 'matplotlib'
        if plotvars.viewer == 'matplotlib' or interactive:
            # Use Matplotlib viewer
            matplotlib.pyplot.ion()
            plot.show()

    # Reset plotting
    plotvars.plot = None
    plotvars.twinx = None
    plotvars.twiny = None
    plotvars.plot_xmin = None
    plotvars.plot_xmax = None
    plotvars.plot_ymin = None
    plotvars.plot_ymax = None
    plotvars.graph_xmin = None
    plotvars.graph_xmax = None
    plotvars.graph_ymin = None
    plotvars.graph_ymax = None
    plotvars.gpos_called = False
    plotvars.mymap = None
    plotvars.titles_con_called = False


def gpos(pos=1, xmin=None, xmax=None, ymin=None, ymax=None):
    """
     | Set plot position. Plots start at top left and increase by one each plot
     | to the right. When the end of the row has been reached then the next
     | plot will be the leftmost plot on the next row down.

     | pos=pos - plot position
     |
     | The following four parameters are used to get full user control
     | over the plot position.  In addition to these cfp.gopen
     | must have the user_position=True parameter set.
     | xmin=None xmin in normalised coordinates
     | xmax=None xmax in normalised coordinates
     | ymin=None ymin in normalised coordinates
     | ymax=None ymax in normalised coordinates
     |
     |

     :Returns:
      None

     |
     |
     |
     |
     |
     |
     |
     |

    """

    # Reset mymap
    plotvars.mymap = None

    # Check inputs are okay
    if pos < 1 or pos > plotvars.rows * plotvars.columns:
        errstr = 'pos error - pos out of range:\n range = 1 - '
        errstr = errstr + str(plotvars.rows * plotvars.columns)
        errstr = errstr + '\n input pos was ' + str(pos)
        errstr = errstr + '\n'
        raise Warning(errstr)


    user_pos = False
    if all(val is not None for val in [xmin, xmax, ymin, ymax]):
        user_pos = True
        plotvars.plot_xmin = xmin
        plotvars.plot_xmax = xmax
        plotvars.plot_ymin = ymin
        plotvars.plot_ymax = ymax

    # Reset any accumulated muliple graph limits
    plotvars.graph_xmin = None
    plotvars.graph_xmax = None
    plotvars.graph_ymin = None
    plotvars.graph_ymax = None

    # Set gpos_called
    plotvars.gpos_called = True

    # Reset titles_con_called
    plotvars.titles_con_called = False

    if user_pos is False:
        plotvars.plot = plotvars.master_plot.add_subplot(
            plotvars.rows, plotvars.columns, pos)
    else:
        delta_x = plotvars.plot_xmax - plotvars.plot_xmin
        delta_y = plotvars.plot_ymax - plotvars.plot_ymin

        plotvars.plot = plotvars.master_plot.add_axes([plotvars.plot_xmin,
                                                       plotvars.plot_ymin,
                                                       delta_x, delta_y])


    plotvars.plot.tick_params(which='both', direction='out', right=True, top=True)

    # Set position in global variables
    plotvars.pos = pos

    # Reset contour levels if they are not defined by the user
    if plotvars.user_levs == 0:
        if plotvars.levels_step is None:
            levs()
        else:
            levs(step=plotvars.levels_step)


def pcon(mb=None, km=None, h=7.0, p0=1000):
    """
     | pcon is a function for converting pressure to height in kilometers and
     | vice-versa. This function uses the equation P=P0exp(-z/H) to translate
     | between pressure and height. In pcon the surface pressure P0 is set to
     | 1000.0mb and the scale height H is set to 7.0. The value of H can vary
     | from 6.0 in the polar regions to 8.5 in the tropics as well as
     | seasonally. The value of P0 could also be said to be 1013.25mb rather
     | than 1000.0mb.

     | As this relationship is approximate:
     | (i) Only use this for making the axis labels on y axis pressure plots
     | (ii) Put the converted axis on the right hand side to indicate that
     |      this isn't the primary unit of measure

     | print cfp.pcon(mb=[1000, 300, 100, 30, 10, 3, 1, 0.3])
     | [0. 8.42780963 16.11809565 24.54590528 32.2361913
     |  40.66400093 48.35428695, 56.78209658]

     | mb=None - input pressure
     | km=None - input height
     | h=7.0 - default value for h
     | p0=1000 - default value for p0

     :Returns:
      | pressure(mb) if height(km) input,
      | height(km) if pressure(mb) input
     """

    if all(val is None for val in [mb, km]) == 2:
        errstr = 'pcon error - pcon must have mb or km input\n'
        raise Warning(errstr)

    if mb is not None:
        return h * (np.log(p0) - np.log(mb))
    if km is not None:
        return np.exp(-1.0 * (np.array(km) / h - np.log(p0)))


def supscr(text=None):
    """
     | supscr - add superscript text formatting for ** and ^
     | This is an internal routine used in titles and colour bars
     | and not used by the user.
     | text=None - input text

     :Returns:
      Formatted text
     |
     |
     |
     |
     |
     |
     |
    """

    if text is None:
        errstr = '\n supscr error - supscr must have text input\n'
        raise Warning(errstr)

    tform = ''

    sup = 0
    for i in text:
        if (i == '^'):
            sup = 2
        if (i == '*'):
            sup = sup + 1

        if (sup == 0):
            tform = tform + i
        if (sup == 1):
            if (i not in '*'):
                tform = tform + '*' + i
                sup = 0
        if (sup == 3):
            if i in '-0123456789':
                tform = tform + i
            else:
                tform = tform + '}$' + i
                sup = 0
        if (sup == 2):
            tform = tform + '$^{'
            sup = 3

    if (sup == 3):
        tform = tform + '}$'

    tform = tform.replace('m2', 'm$^{2}$')
    tform = tform.replace('m3', 'm$^{3}$')
    tform = tform.replace('m-2', 'm$^{-2}$')
    tform = tform.replace('m-3', 'm$^{-3}$')
    tform = tform.replace('s-1', 's$^{-1}$')
    tform = tform.replace('s-2', 's$^{-2}$')

    return tform


def gvals(dmin=None, dmax=None, mystep=None, mod=True):
    """
     | gvals - work out a sensible set of values between two limits
     | This is an internal routine used for contour levels and axis
     | labelling and is not generally used by the user.

     | dmin = None - minimum
     | dmax = None - maximum
     | mystep = None - use this step
     | mod = True - modify data to make use of a multipler
     |
     |
     |
     |
     |
     |
    """

    # Copies of inputs as these might be changed
    dmin1 = deepcopy(dmin)
    dmax1 = deepcopy(dmax)

    # Swap values if dmin1 > dmax1 
    if dmax1 < dmin1:
        dmin1, dmax1 = dmax1, dmin1

    # Data range
    data_range = dmax1 - dmin1

    # field multiplier
    mult = 0
    vals = None

    # Return some values if dmin1 = dmax1
    if dmin1 == dmax1:
        vals = np.array([dmin1 - 1, dmin1, dmin1 + 1])
        mult = 0
        return vals, mult

    # Modify if requested or if out of range 0.001 to 2000000
    if data_range < 0.001:
        while dmax1 <= 3:
            dmin1 = dmin1 * 10.0
            dmax1 = dmax1 * 10.0
            data_range = dmax1 - dmin1
            mult = mult - 1

    if data_range > 2000000:
        while dmax1 > 10:
            dmin1 = dmin1 / 10.0
            dmax1 = dmax1 / 10.0
            data_range = dmax1 - dmin1
            mult = mult + 1


    if data_range >= 0.001 and data_range <= 2000000:
        
        # Calculate an appropriate step
        step = None
        test_steps = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1,
                      0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000,
                      20000, 50000, 100000]

        if mystep is not None:
            step = mystep
        else:
            for val in test_steps:
                nvals = data_range / val

                if val < 1:
                    if nvals > 8:
                        step = val
                else:
                    if nvals > 11:
                        step = val

        # Return an error if no step found
        if step is None:
            errstr = '\n\n cfp.gvals - no valid step values found \n\n'
            errstr += 'cfp.gvals(' + str(dmin1) + ',' + str(dmax1) + ')\n\n'
            raise Warning(errstr)

        # values  < 0.0
        vals = None
        vals1 = None
        if dmin1 < 0.0:
            vals1 = (np.arange(-dmin1 / step) * -step)[::-1] - step

        # values  >= 0.0
        vals2 = None
        if dmax1 >= 0.0:
            vals2 = np.arange(dmax1 / step + 1) * step

        if vals1 is not None and vals2 is None:
            vals = vals1
        if vals2 is not None and vals1 is None:
            vals = vals2
        if vals1 is not None and vals2 is not None:
            vals = np.concatenate((vals1, vals2))

        # Round off decimal numbers so that
        # (np.arange(4) * -0.1)[3] = -0.30000000000000004 gives -0.3 as expected
        if step < 1:
            vals = vals.round(6)

        # Change values to integers for values >= 1
        if step >= 1:
            vals = vals.astype(int)

        pts = np.where(np.logical_and(vals >= dmin1, vals <= dmax1))
        if np.min(pts) > -1:
            vals = vals[pts]

        if mod is False:
            vals = vals * 10**mult
            mult = 0
            
    # Catch if no values have been defined    
    if vals is None:
        vals = np.array([dmin, dmax])


    return(vals, mult)


def cf_data_assign(f=None, colorbar_title=None, verbose=None, rotated_vect=False):
    """
     | Check cf input data is okay and return data for contour plot.
     | This is an internal routine not used by the user.
     | f=None - input cf field
     | colorbar_title=None - input colour bar title
     | rotated vect=False - return 1D x and y for rotated plot vectors
     | verbose=None - set to 1 to get a verbose idea of what the
     |          cf_data_assign is doing

     :Returns:
      | f - data for contouring
      | x - x coordinates of data (optional)
      | y - y coordinates of data (optional)
      | ptype - plot type
      | colorbar_title - colour bar title
      | xlabel - x label for plot
      | ylabel - y label for plot
      |
      |
      |
      |
      |
    """

    # Check input data has the correct number of dimensions
    # Take into account rotated pole fields having extra dimensions
    ndim = len(f.domain_axes().filter_by_size(cf.gt(1)))
    if f.ref('grid_mapping_name:rotated_latitude_longitude', default=False) is False:
        if (ndim > 2 or ndim < 1):
            print('')
            if (ndim > 2):
                errstr = 'cf_data_assign error - data has too many dimensions'
            if (ndim < 1):
                errstr = 'cf_data_assign error - data has too few dimensions'
            errstr += '\n cf-plot requires one or two dimensional data\n'
            for mydim in list(f.dimension_coordinates()):
                sn = getattr(f.construct(mydim), 'standard_name', False)
                ln = getattr(f.construct(mydim), 'long_name', False)
                if sn:
                    errstr = errstr + \
                        str(mydim) + ',' + str(sn) + ',' + \
                        str(f.construct(mydim).size) + '\n'
                else:
                    if ln:
                        errstr = errstr + \
                            str(mydim) + ',' + str(ln) + ',' + \
                            str(f.construct(mydim).size) + '\n'
            raise Warning(errstr)

    # Set up data arrays and variables
    lons = None
    lats = None
    height = None
    time = None
    xlabel = ''
    ylabel = ''
    has_lons = False
    has_lats = False
    has_height = False
    has_time = False
    xpole = None
    ypole = None
    ptype = None
    field = None
    x = None
    y = None
    
    
    # Check for multiple Z coordinates
    myz = find_z(f)

    # Extract coordinate data if a matching CF standard_name or axis is found
    for mycoord in f.coords():
        c = f.coord(mycoord)
        if c.X:
            if verbose:
                print(vs + 'lons -', mydim)
            lons = np.squeeze(f.construct(mycoord).array)
            if np.size(lons) > 1:
                has_lons = True
            
        if c.Y:
            if verbose:
                print(vs + 'lats -', mydim)
            lats = np.squeeze(f.construct(mycoord).array)
            if np.size(lats) > 1:
                has_lats = True
            
        if c.Z:
            if verbose:
                print(vs + 'height -', mydim)
            height = np.squeeze(f.construct(mycoord).array)
            if np.size(height) > 1:
                has_height = True
            
        if c.T:
            if verbose:
                print(vs + 'time -', mydim)
            time = np.squeeze(f.construct(mycoord).array)
            if np.size(time) > 1:
                has_time = True
                    

    # assign field data
    field = np.squeeze(f.array)

    # Change Boolean data to integer
    if str(f.dtype) == 'bool':
        warnstr = '\n\n\n Warning - boolean data found - converting to integers\n\n\n'
        print(warnstr)
        g = deepcopy(f)
        g.dtype = int
        field = np.squeeze(g.array)

    # Check what plot type is required.
    # 0=simple contour plot, 1=map plot, 2=latitude-height plot,
    # 3=longitude-time plot, 4=latitude-time plot.
    if has_lons and has_lats:
        ptype = 1
        x = lons
        y = lats

    if has_lats and has_height:
        ptype = 2
        x = lats
        y = height
        
        xname = cf_var_name(field=f, dim='Y')
        xunits = str(getattr(f.construct('Y'), 'Units', ''))
        if xunits == 'degrees_north':
            xunits = 'degrees'
        if xunits != '':
            xlabel = xname + ' (' + xunits + ')'
        else:
            xlabel = xname
            
        yname = cf_var_name(field=f, dim=myz)
        yunits = str(getattr(f.construct(myz), 'Units', ''))
        if yunits != '':
            ylabel = yname + ' (' + yunits + ')'
        else:
            ylabel = yname 
                         
    if has_lons and has_height:
        ptype = 3
        x = lons
        y = height
        
        xname = cf_var_name(field=f, dim='X')
        xunits = str(getattr(f.construct('X'), 'Units', ''))
        if xunits == 'degrees_east':
            xunits = 'degrees'
        if xunits != '':
            xlabel = xname + ' (' + xunits + ')'
        else:
            xlabel = xname
            
        yname = cf_var_name(field=f, dim=myz)
        yunits = str(getattr(f.construct(myz), 'Units', ''))
        if yunits != '':
            ylabel = yname + ' (' + yunits + ')'
        else:
            ylabel = yname 
        
    if has_lons and has_time:
        ptype = 4
        x = lons
        y = time
        
        xname = cf_var_name(field=f, dim='X')
        xunits = str(getattr(f.construct('X'), 'Units', ''))
        if xunits == 'degrees_east':
            xunits = 'degrees'
        if xunits != '':
            xlabel = xname + ' (' + xunits + ')'
        else:
            xlabel = xname
            
        yname = cf_var_name(field=f, dim='T')
        yunits = str(getattr(f.construct('T'), 'Units', ''))
        if yunits != '':
            ylabel = yname + ' (' + yunits + ')'
        else:
            ylabel = yname 

    if has_lats and has_time:
        ptype = 5
        x = lats
        y = time
        
        xname = cf_var_name(field=f, dim='Y')
        xunits = str(getattr(f.construct('Y'), 'Units', ''))
        if xunits == 'degrees_north':
            xunits = 'degrees'
        if xunits != '':
            xlabel = xname + ' (' + xunits + ')'
        else:
            xlabel = xname
            
        yname = cf_var_name(field=f, dim='T')
        yunits = str(getattr(f.construct('T'), 'Units', ''))
        if yunits != '':
            ylabel = yname + ' (' + yunits + ')'
        else:
            ylabel = yname 

    # time height plot
    if has_height and has_time:
        ptype = 7
        x = time
        y = height
        
        xname = cf_var_name(field=f, dim='T')
        xunits = str(getattr(f.construct('T'), 'Units', ''))
        if xunits != '':
            xlabel = xname + ' (' + xunits + ')'
        else:
            xlabel = xname
            
        yname = cf_var_name(field=f, dim='Z')
        yunits = str(getattr(f.construct('Z'), 'Units', ''))
        if yunits != '':
            ylabel = yname + ' (' + yunits + ')'
        else:
            ylabel = yname 

        # Rotate array to get it as time vs height
        field = np.rot90(field)
        field = np.flipud(field)

    # Rotated pole
    if f.ref('grid_mapping_name:rotated_latitude_longitude', default=False):
        ptype = 6

        rotated_pole = f.ref('grid_mapping_name:rotated_latitude_longitude')
        xpole = rotated_pole['grid_north_pole_longitude']
        ypole = rotated_pole['grid_north_pole_latitude']

        # Extract grid x and y coordinates
        for mydim in list(f.dimension_coordinates()):
            name = cf_var_name(field=f, dim=mydim)

            if name in ['grid_longitude', 'longitude', 'x']:
                x = np.squeeze(f.construct(mydim).array)
                xunits = str(getattr(f.construct(mydim), 'units', ''))
                xlabel = cf_var_name(field=f, dim=mydim)

            if name in ['grid_latitude', 'latitude', 'y']:
                y = np.squeeze(f.construct(mydim).array)
                # Flip y and data if reversed
                if y[0] > y[-1]:
                    y = y[::-1]
                    field = np.flipud(field)
                yunits = str(getattr(f.construct(mydim), 'Units', ''))
                ylabel = cf_var_name(field=f, dim=mydim) + yunits


    # Extract auxiliary lons and lats if they exist
    if ptype == 1 or ptype is None:
        if plotvars.proj != 'rotated' and not rotated_vect:
            aux_lons = False
            aux_lats = False
            for mydim in list(f.auxiliary_coordinates()):
                name = cf_var_name(field=f, dim=mydim)
                if name in ['longitude']:
                    xpts = np.squeeze(f.construct(mydim).array)
                    aux_lons = True
                if name in ['latitude']:
                    ypts = np.squeeze(f.construct(mydim).array)
                    aux_lats = True

            if aux_lons and aux_lats:
                x = xpts
                y = ypts
                ptype = 1


    # UKCP grid
    if f.ref('grid_mapping_name:transverse_mercator', default=False):
        ptype = 1
        field = np.squeeze(f.array)

        # Find the auxiliary lons and lats if provided
        has_lons = False
        has_lats = False
        for mydim in list(f.auxiliary_coordinates()):
            name = cf_var_name(field=f, dim=mydim)
            if name in ['longitude']:
                x = np.squeeze(f.construct(mydim).array)
                has_lons = True
            if name in ['latitude']:
                y = np.squeeze(f.construct(mydim).array)
                has_lats = True

        # Calculate lons and lats if no auxiliary data for these
        if not has_lons or not has_lats:
            xpts = f.construct('X').array
            ypts = f.construct('Y').array
            field = np.squeeze(f.array)

            ref = f.ref('grid_mapping_name:transverse_mercator')
            false_easting = ref['false_easting']
            false_northing = ref['false_northing']
            central_longitude = ref['longitude_of_central_meridian']
            central_latitude = ref['latitude_of_projection_origin']
            scale_factor = ref['scale_factor_at_central_meridian']

            # Set the transform
            transform = ccrs.TransverseMercator(false_easting=false_easting,
                                                false_northing=false_northing,
                                                central_longitude=central_longitude,
                                                central_latitude=central_latitude,
                                                scale_factor=scale_factor)

            # Calculate the longitude and latitude points
            xvals, yvals = np.meshgrid(xpts, ypts)
            points = ccrs.PlateCarree().transform_points(transform, xvals, yvals)
            x = np.array(points)[:, :, 0]
            y = np.array(points)[:, :, 1]


    # None of the above
    if ptype is None:
        ptype = 0

        data_axes = f.get_data_axes()
        count = 1
        for d in data_axes:
            try:
                c = f.coordinate(filter_by_axis  = [d])
                if np.size(c.array) > 1:
                    if count == 1:
                        
                        y = c
                        mycoord = 'dimensioncoordinate'+str(d[-1])
                        yunits = str(getattr(f.coord(mycoord), 'Units', ''))
                        if yunits != '':
                            yunits = '(' + yunits + ')'
                        ylabel = cf_var_name(field=f, dim=mycoord) + yunits                         
                    elif count == 2:
                        x = c
                        mycoord = 'dimensioncoordinate'+str(d[-1])
                        xunits = str(getattr(f.coord(mycoord), 'units', ''))
                        if xunits != '':
                            xunits = '(' + xunits + ')'
                        xlabel = cf_var_name(field=f, dim=mycoord) + xunits
                    count += 1
            except ValueError:
                errstr = "\n\ncf_data_assign - cannot find data to return\n\n" 
                errstr += str(f.constructs.domain_axis_identity(d)) + "\n\n"
                raise Warning(errstr)



    # Assign colorbar_title
    if (colorbar_title is None):
        colorbar_title = 'No Name'
        if hasattr(f, 'id'):
            colorbar_title = f.id
        nc = f.nc_get_variable(None)
        if nc:
            colorbar_title = f.nc_get_variable()
        if hasattr(f, 'short_name'):
            colorbar_title = f.short_name
        if hasattr(f, 'long_name'):
            colorbar_title = f.long_name
        if hasattr(f, 'standard_name'):
            colorbar_title = f.standard_name

        if hasattr(f, 'Units'):
            if str(f.Units) == '':
                colorbar_title = colorbar_title + ''
            else:
                colorbar_title = colorbar_title + \
                    '(' + supscr(str(f.Units)) + ')'

        
    # Return data
    return(field, x, y, ptype, colorbar_title, xlabel, ylabel, xpole, ypole)


def check_data(field=None, x=None, y=None):
    """
     | check_data - check user input contour data is correct.
     | This is an internal routine and is not used by the user.
     |
     | field=None - field
     | x=None - x points for field
     | y=None - y points for field
     |
     |
     |
     |
     |
     |
    """

    # Input error trapping
    args = True
    errstr = '\n'
    if np.size(field) == 1:
        if field is None:
            errstr = errstr + 'con error - a field for contouring must be '
            errstr += 'passed with the f= flag\n'
            args = False
    if np.size(x) == 1:
        if x is None:
            x = np.arange(np.shape(field)[1])
    if np.size(y) == 1:
        if y is None:
            y = np.arange(np.shape(field)[0])
    if not args:
        raise Warning(errstr)

    # Check input dimensions look okay.
    # All inputs 2D
    if np.ndim(field) == 2 and np.ndim(x) == 2 and np.ndim(y) == 2:
        xpts = np.shape(field)[1]
        ypts = np.shape(field)[0]
        if xpts != np.shape(x)[1] or xpts != np.shape(y)[1]:
            args = False
        if ypts != np.shape(x)[0] or ypts != np.shape(y)[0]:
            args = False
        if args:
            return

    # Field x and y all 1D
    if np.ndim(field) == 1 and np.ndim(x) == 1 and np.ndim(y) == 1:
        if np.size(x) != np.size(field):
            args = False
        if np.size(y) != np.size(field):
            args = False
        if args:
            return

    # Field 2D, x and y 1D
    if np.ndim(field) != 2:
        args = False
    if np.ndim(x) != 1:
        args = False
    if np.ndim(y) != 1:
        args = False
    if np.ndim(field) == 2:
        if np.size(x) != np.shape(field)[1]:
            args = False
        if np.size(y) != np.shape(field)[0]:
            args = False

    if args is False:
        errstr = errstr + 'Input arguments incorrectly shaped:\n'
        errstr = errstr + 'x has shape:' + str(np.shape(x)) + '\n'
        errstr = errstr + 'y has shape:' + str(np.shape(y)) + '\n'
        errstr = errstr + 'field has shape' + str(np.shape(field)) + '\n\n'
        errstr = errstr + 'Expected x=xpts, y=ypts, field=(ypts,xpts)\n'
        errstr = errstr + 'x=npts, y=npts, field=npts\n'
        errstr = errstr + \
            'or x=[ypts, xpts], y=[ypts, xpts], field=[ypts, xpts]\n'
        raise Warning(errstr)


def cscale(scale=None, ncols=None, white=None, below=None,
           above=None, reverse=False, uniform=False):
    """
    | cscale - choose and manipulate colour maps.  Around 200 colour scales are
    |          available - see the gallery section for more details.
    |
    | scale=None - name of colour map
    | ncols=None - number of colours for colour map
    | white=None - change these colours to be white
    | below=None - change the number of colours below the mid point of
    |               the colour scale to be this
    | above=None - change the number of colours above the mid point of
    |               the colour scale to be this
    | reverse=False - reverse the colour scale
    | uniform=False - produce a uniform colour scale.
    |                 For example: if below=3 and above=10 are specified
    |                 then initially below=10 and above=10 are used.  The
    |                 colour scale is then cropped to use scale colours
    |                 6 to 19.  This produces a more uniform intensity colour
    |                 scale than one where all the blues are compressed into
    |                 3 colours.
    |
    |
    | Personal colour maps are available by saving the map as red green blue
    | to a file with a set of values on each line.
    |
    |
    | Use cscale() To reset to the default settings.
    |
    :Returns:
        None

    |
    |
    |
    |
    """

    # If no map requested reset to default
    if scale is None:
        scale = 'scale1'
        plotvars.cscale_flag = 0
        return
    else:
        plotvars.cs_user = scale
        plotvars.cscale_flag = 1
        vals = [ncols, white, below, above]
        if any(val is not None for val in vals):
            plotvars.cscale_flag = 2
        if reverse is not False or uniform is not False:
            plotvars.cscale_flag = 2

    if scale == 'scale1' or scale == '':
        if scale == 'scale1':
            myscale = cscale1
        if scale == 'viridis':
            myscale = viridis
        # convert cscale1 or viridis from hex to rgb
        r = []
        g = []
        b = []
        for myhex in myscale:
            myhex = myhex.lstrip('#')
            mylen = len(myhex)
            rgb = tuple(int(myhex[i:i + mylen // 3], 16)
                        for i in range(0, mylen, mylen // 3))
            r.append(rgb[0])
            g.append(rgb[1])
            b.append(rgb[2])
    else:
        package_path = os.path.dirname(__file__)
        file = os.path.join(package_path, 'colourmaps/' + scale + '.rgb')
        if os.path.isfile(file) is False:
            if os.path.isfile(scale) is False:
                errstr = '\ncscale error - colour scale not found:\n'
                errstr = errstr + 'File ' + file + ' not found\n'
                errstr = errstr + 'File ' + scale + ' not found\n'
                raise Warning(errstr)
            else:
                file = scale

        # Read in rgb values and convert to hex
        f = open(file, 'r')
        lines = f.read()
        lines = lines.splitlines()
        r = []
        g = []
        b = []
        for line in lines:
            vals = line.split()
            r.append(int(vals[0]))
            g.append(int(vals[1]))
            b.append(int(vals[2]))

    # Reverse the colour scale if requested
    if reverse:
        r = r[::-1]
        g = g[::-1]
        b = b[::-1]

    # Interpolate to a new number of colours if requested
    if ncols is not None:
        x = np.arange(np.size(r))
        xnew = np.linspace(0, np.size(r) - 1, num=ncols, endpoint=True)
        f_red = interpolate.interp1d(x, r)
        f_green = interpolate.interp1d(x, g)
        f_blue = interpolate.interp1d(x, b)
        r = f_red(xnew)
        g = f_green(xnew)
        b = f_blue(xnew)

    # Change the number of colours below and above the mid-point if requested
    if below is not None or above is not None:

        # Mid-point of colour scale
        npoints = np.size(r) // 2

        # Below mid point x locations
        x_below = []
        lower = 0
        if below == 1:
            x_below = 0
        if below is not None:
            lower = below
        if below is None:
            lower = npoints
        if below is not None and uniform:
            lower = max(above, below)
        if (lower > 1):
            x_below = ((npoints - 1) / float(lower - 1)) * np.arange(lower)

        # Above mid point x locations
        x_above = []
        upper = 0
        if above == 1:
            x_above = npoints * 2 - 1
        if above is not None:
            upper = above
        if above is None:
            upper = npoints
        if above is not None and uniform:
            upper = max(above, below)
        if (upper > 1):
            x_above = ((npoints - 1) / float(upper - 1)) * \
                np.arange(upper) + npoints

        # Append new colour positions
        xnew = np.append(x_below, x_above)

        # Interpolate to new colour scale
        xpts = np.arange(np.size(r))
        f_red = interpolate.interp1d(xpts, r)
        f_green = interpolate.interp1d(xpts, g)
        f_blue = interpolate.interp1d(xpts, b)
        r = f_red(xnew)
        g = f_green(xnew)
        b = f_blue(xnew)

        # Reset colours if uniform is set
        if uniform:
            mid_pt = max(below, above)
            r = r[mid_pt - below:mid_pt + above]
            g = g[mid_pt - below:mid_pt + above]
            b = b[mid_pt - below:mid_pt + above]

    # Convert to hex
    hexarr = []
    for col in np.arange(np.size(r)):
        hexarr.append('#%02x%02x%02x' % (int(r[col]), int(g[col]), int(b[col])))

    # White requested colour positions
    if white is not None:
        if np.size(white) == 1:
            hexarr[white] = '#ffffff'
        else:
            for col in white:
                hexarr[col] = '#ffffff'

    # Set colour scale
    plotvars.cs = hexarr


def cscale_get_map():
    """
    | cscale_get_map - return colour map for use in contour plots.
    |                   This depends on the colour bar extensions
    | This is an internal routine and is not used by the user.
    |
    |
    :Returns:
         colour map
    |
    |
    |
    |
    |
    """
    cscale_ncols = np.size(plotvars.cs)
    if (plotvars.levels_extend == 'both'):
        colmap = plotvars.cs[1:cscale_ncols - 1]
    if (plotvars.levels_extend == 'min'):
        colmap = plotvars.cs[1:]
    if (plotvars.levels_extend == 'max'):
        colmap = plotvars.cs[:cscale_ncols - 1]
    if (plotvars.levels_extend == 'neither'):
        colmap = plotvars.cs
    return (colmap)


def bfill(f=None, x=None, y=None, clevs=False, lonlat=None, bound=False,
          alpha=1.0, single_fill_color=None, white=True, zorder=4, fast=None):
    """
     | bfill - block fill a field with colour rectangles
     | This is an internal routine and is not generally used by the user.
     |
     | f=None - field
     | x=None - x points for field
     | y=None - y points for field
     | clevs=None - levels for filling
     | lonlat=None - longitude and latitude data
     | bound=False - x and y are cf data boundaries
     | alpha=alpha - transparency setting 0 to 1
     | white=True - colour unplotted areas white
     | single_fill_color=None - colour for a blockfill between two levels
     |                        - makes maplotlib named colours or
     |                        - hexadecimal notation - '#d3d3d3' for grey
     | zorder=4 - plotting order
     | fast=None - use fast plotting with pcolormesh which is useful for larger datasets
     |
      :Returns:
        None
     |
     |
     |
     |
    """

    



    # Set lonlat if not specified
    lonlat = False
    if plotvars.plot_type == 1:
        lonlat = True

    # If single_fill_color is defined then turn off whiting out the background.
    if single_fill_color is not None:
        white = False

    # Set the default map coordinates for the data to be PlateCarree
    plotargs = {}
    if lonlat:
        plotargs = {'transform': ccrs.PlateCarree()}

    if isinstance(f, cf.Field):

        if f.ref('grid_mapping_name:transverse_mercator', default=False):
            lonlat = True

            # Case of transverse mercator of which UKCP is an example
            ref = f.ref('grid_mapping_name:transverse_mercator')
            false_easting = ref['false_easting']
            false_northing = ref['false_northing']
            central_longitude = ref['longitude_of_central_meridian']
            central_latitude = ref['latitude_of_projection_origin']
            scale_factor = ref['scale_factor_at_central_meridian']

            transform = ccrs.TransverseMercator(false_easting=false_easting,
                                                false_northing=false_northing,
                                                central_longitude=central_longitude,
                                                central_latitude=central_latitude,
                                                scale_factor=scale_factor)

            # Extract the axes and data
            xpts = np.append(f.dim('X').bounds.array[:, 0], f.dim('X').bounds.array[-1, 1])
            ypts = np.append(f.dim('Y').bounds.array[:, 0], f.dim('Y').bounds.array[-1, 1])
            field = np.squeeze(f.array)
            plotargs = {'transform': transform}

    else:
        # Assign f to field as this may be modified in lat-lon plots
        field = f

        if bound:
            xpts = x
            ypts = y
        else:
            # Find x box boundaries
            xpts = x[0] - (x[1] - x[0]) / 2.0
            for ix in np.arange(np.size(x) - 1):
                xpts = np.append(xpts, x[ix] + (x[ix + 1] - x[ix]) / 2.0)
            xpts = np.append(xpts, x[ix + 1] + (x[ix + 1] - x[ix]) / 2.0)

            # Find y box boundaries
            ypts = y[0] - (y[1] - y[0]) / 2.0
            for iy in np.arange(np.size(y) - 1):
                ypts = np.append(ypts, y[iy] + (y[iy + 1] - y[iy]) / 2.0)
            ypts = np.append(ypts, y[iy + 1] + (y[iy + 1] - y[iy]) / 2.0)

        # Shift lon grid if needed
        if lonlat:
            # Extract upper bound and original rhs of box longitude bounding points
            upper_bound = ypts[-1]

            # Reduce xpts and ypts by 1 or shifting of grid fails
            # The last points are the right / upper bounds for the last data box
            xpts = xpts[0:-1]
            ypts = ypts[0:-1]

            if plotvars.lonmin < np.nanmin(xpts):
                xpts = xpts - 360
            if plotvars.lonmin > np.nanmax(xpts):
                xpts = xpts + 360

            # Add cyclic information if missing.
            lonrange = np.nanmax(xpts) - np.nanmin(xpts)
            if lonrange < 360:
                # field, xpts = cartopy_util.add_cyclic_point(field, xpts)
                field, xpts = add_cyclic(field, xpts)

            right_bound = xpts[-1] + (xpts[-1] - xpts[-2])

            # Add end x and y end points
            xpts = np.append(xpts, right_bound)
            ypts = np.append(ypts, upper_bound)

    levels = np.array(deepcopy(clevs)).astype('float')
    

    # Polar stereographic
    # Set points past plotting limb to be plotvars.boundinglat
    # Also set any lats past the pole to be the pole
    if plotvars.proj == 'npstere':
        pts = np.where(ypts < plotvars.boundinglat)
        if np.size(pts) > 0:
            ypts[pts] = plotvars.boundinglat
        pts = np.where(ypts > 90.0)
        if np.size(pts) > 0:
            ypts[pts] = 90.0

    if plotvars.proj == 'spstere':
        pts = np.where(ypts > plotvars.boundinglat)
        if np.size(pts) > 0:
            ypts[pts] = plotvars.boundinglat
        pts = np.where(ypts < -90.0)
        if np.size(pts) > 0:
            ypts[pts] = -90.0

    # Generate a Matplotlib colour map
    if single_fill_color is None:
        cols = plotvars.cs
    else:
        cols = single_fill_color

    cmap = matplotlib.colors.ListedColormap(cols)


    levels_orig = deepcopy(levels)

    if single_fill_color is None:
        if plotvars.levels_extend == 'both' or plotvars.levels_extend == 'min':
            levels = np.insert(levels, 0, -1e30)
        if plotvars.levels_extend == 'both' or plotvars.levels_extend == 'max':
            levels = np.append(levels, 1e30)

        if plotvars.levels_extend == 'both' or plotvars.levels_extend == 'min':
            cmap.set_under(plotvars.cs[0])
            cols = cols[1:]
        if plotvars.levels_extend == 'both' or plotvars.levels_extend == 'max':
            cmap.set_over(plotvars.cs[-1])
            cols = cols[:-1]



    # Colour array for storing the cell colour.  Start with -1 as the default
    # as the colours run from 0 to np.size(levels)-1
    colarr = np.zeros([np.shape(field)[0], np.shape(field)[1]])-1
    for i in np.arange(np.size(levels)-1):
        lev = levels[i]
        pts = np.where(np.logical_and(field > lev, field <= levels[i+1]))
        colarr[pts] = int(i)

    # Change points that are masked back to -1
    if isinstance(field, np.ma.MaskedArray):
        pts = np.ma.where(field.mask)
        if np.size(pts) > 0:
            colarr[pts] = -1

    norm = matplotlib.colors.BoundaryNorm(levels, cmap.N)

    if fast:
        if type(clevs) == int:
            norm = False
                      
        if lonlat:
            for offset in [0, 360.0]:
                if type(clevs) == int:
                    plotvars.image = plotvars.mymap.pcolormesh(xpts+offset, ypts, field, transform=ccrs.PlateCarree(), cmap=cmap)
                else:
                    plotvars.image = plotvars.mymap.pcolormesh(xpts+offset, ypts, field, transform=ccrs.PlateCarree(), cmap=cmap, norm=norm)                    
        else:
            if type(clevs) == int:
                plotvars.image = plotvars.plot.pcolormesh(xpts, ypts, field, cmap=cmap)
            else:
                plotvars.image = plotvars.plot.pcolormesh(xpts, ypts, field, cmap=cmap, norm=norm)        
    
    else:
    
        if plotvars.plot_type == 1 and plotvars.proj != 'cyl':

            for i in np.arange(np.size(levels)-1):
                allverts = []
                xy_stack = np.column_stack(np.where(colarr == i))

                for pt in np.arange(np.shape(xy_stack)[0]):
                    ix = xy_stack[pt][1]
                    iy = xy_stack[pt][0]
                    lons = [xpts[ix], xpts[ix+1], xpts[ix+1], xpts[ix], xpts[ix]]
                    lats = [ypts[iy], ypts[iy], ypts[iy+1], ypts[iy+1], ypts[iy]]

                    txpts, typts = lons, lats
                    verts = [
                        (txpts[0], typts[0]),
                        (txpts[1], typts[1]),
                        (txpts[2], typts[2]),
                        (txpts[3], typts[3]),
                        (txpts[4], typts[4]),
                        ]

                    allverts.append(verts)

                # Make the collection and add it to the plot.
                if single_fill_color is None:
                    color = plotvars.cs[i]
                else:
                    color = single_fill_color
                coll = PolyCollection(allverts, facecolor=color, edgecolors=color, alpha=alpha,
                                      zorder=zorder, **plotargs)

                if lonlat:
                    plotvars.mymap.add_collection(coll)
                else:
                    plotvars.plot.add_collection(coll)
        else:
            for i in np.arange(np.size(levels)-1):

                allverts = []
                xy_stack = np.column_stack(np.where(colarr == i))
                for pt in np.arange(np.shape(xy_stack)[0]):
                    ix = xy_stack[pt][1]
                    iy = xy_stack[pt][0]
                    verts = [
                        (xpts[ix], ypts[iy]),
                        (xpts[ix+1], ypts[iy]),
                        (xpts[ix+1], ypts[iy+1]),
                        (xpts[ix], ypts[iy+1]),
                        (xpts[ix], ypts[iy]),
                        ]

                    allverts.append(verts)

                # Make the collection and add it to the plot.
                if single_fill_color is None:
                    color = plotvars.cs[i]
                else:
                    color = single_fill_color

                coll = PolyCollection(allverts, facecolor=color, edgecolors=color,
                                      alpha=alpha, zorder=zorder, **plotargs)




                if lonlat:
                    plotvars.mymap.add_collection(coll)
                else:
                    plotvars.plot.add_collection(coll)

        # Add white for undefined areas
        if white:
            allverts = []
            xy_stack = np.column_stack(np.where(colarr == -1))
            for pt in np.arange(np.shape(xy_stack)[0]):
                ix = xy_stack[pt][1]
                iy = xy_stack[pt][0]

                verts = [
                    (xpts[ix], ypts[iy]),
                    (xpts[ix+1], ypts[iy]),
                    (xpts[ix+1], ypts[iy+1]),
                    (xpts[ix], ypts[iy+1]),
                    (xpts[ix], ypts[iy]),
                    ]

                allverts.append(verts)

            # Make the collection and add it to the plot.
            color = plotvars.cs[i]
            coll = PolyCollection(allverts, facecolor='#ffffff', edgecolors='#ffffff',
                                  alpha=alpha, zorder=zorder, **plotargs)

            if lonlat:
                plotvars.mymap.add_collection(coll)
            else:
                plotvars.plot.add_collection(coll)


def regrid(f=None, x=None, y=None, xnew=None, ynew=None):
    """
     | regrid - bilinear interpolation of a grid to new grid locations
     |
     |
     |     f=None - original field
     |     x=None - original field x values
     |     y=None - original field y values
     |     xnew=None - new x points
     |     ynew=None - new y points
     |
     :Returns:
        field values at requested locations
     |
     |
    """

    # Copy input arrays
    regrid_f = deepcopy(f)
    regrid_x = deepcopy(x)
    regrid_y = deepcopy(y)
    fieldout = []

    # Reverse xpts and field if necessary
    if regrid_x[0] > regrid_x[-1]:
        regrid_x = regrid_x[::-1]
        regrid_f = np.fliplr(regrid_f)

    # Reverse ypts and field if necessary
    if regrid_y[0] > regrid_y[-1]:
        regrid_y = regrid_y[::-1]
        regrid_f = np.flipud(regrid_f)

    # Iterate over the new grid to get the new grid values.
    for i in np.arange(np.size(xnew)):

        xval = xnew[i]
        yval = ynew[i]

        # Find position of new grid point in the x and y arrays
        myxpos = find_pos_in_array(vals=regrid_x, val=xval)
        myypos = find_pos_in_array(vals=regrid_y, val=yval)

        myxpos2 = myxpos + 1
        myypos2 = myypos + 1

        if (myxpos2 != myxpos):
            alpha = (xnew[i] - regrid_x[myxpos]) / \
                (regrid_x[myxpos2] - regrid_x[myxpos])
        else:
            alpha = (xnew[i] - regrid_x[myxpos]) / 1E-30

        newval1 = (regrid_f[myypos, myxpos] - regrid_f[myypos, myxpos2])
        newval1 = newval1 * alpha
        newval1 = regrid_f[myypos, myxpos] - newval1

        newval2 = (regrid_f[myypos2, myxpos] - regrid_f[myypos2, myxpos2])
        newval2 = newval2 * alpha
        newval2 = regrid_f[myypos2, myxpos] - newval2

        if (myypos2 != myypos):
            alpha2 = (ynew[i] - regrid_y[myypos])
            alpha2 = alpha2 / (regrid_y[myypos2] - regrid_y[myypos])
        else:
            alpha2 = (ynew[i] - regrid_y[myypos]) / 1E-30

        newval3 = newval1 - (newval1 - newval2) * alpha2

        fieldout = np.append(fieldout, newval3)

    return fieldout


def stipple(f=None, x=None, y=None, min=None, max=None,
            size=80, color='k', pts=50, marker='.', edgecolors='k',
            alpha=1.0, ylog=False, zorder=1):
    """
     | stipple - put markers on a plot to indicate value of interest
     |
     | f=None - cf field or field
     | x=None - x points for field
     | y=None - y points for field
     | min=None - minimum threshold for stipple
     | max=None - maximum threshold for stipple
     | size=80 - default size for stipples
     | color='k' - default colour for stipples
     | pts=50 - number of points in the x direction
     | marker='.' - default marker for stipples
     | edegecolors='k' - outline colour
     | alpha=1.0 - transparency setting - default is off
     | ylog=False - set to True if a log pressure stipple plot
     |              is required
     | zorder=2 - plotting order
     |
     |
     :Returns:
        None
     |
     |
    """

    if plotvars.plot_type not in [1, 2, 3]:
        errstr = '\n stipple error - only X-Y, X-Z and Y-Z \n'
        errstr = errstr + 'stipple supported at the present time\n'
        errstr = errstr + 'Please raise a feature request if you see this error.\n'
        raise Warning(errstr)

    # Extract required data for contouring
    # If a cf-python field
    if isinstance(f, cf.Field):
        colorbar_title = ''
        field, xpts, ypts, ptype, colorbar_title, xlabel, ylabel, xpole, \
            ypole = cf_data_assign(f, colorbar_title)
    elif isinstance(f, cf.FieldList):
        raise TypeError("Can't plot a field list")
    else:
        field = f  # field data passed in as f
        check_data(field, x, y)
        xpts = x
        ypts = y

    if plotvars.plot_type == 1:
        # Cylindrical projection
        # Add cyclic information if missing.
        lonrange = np.nanmax(xpts) - np.nanmin(xpts)
        if lonrange < 360:
            # field, xpts = cartopy_util.add_cyclic_point(field, xpts)
            field, xpts = add_cyclic(field, xpts)

        if plotvars.proj == 'cyl':
            # Calculate interpolation points
            xnew, ynew = stipple_points(xmin=np.nanmin(xpts),
                                        xmax=np.nanmax(xpts),
                                        ymin=np.nanmin(ypts),
                                        ymax=np.nanmax(ypts),
                                        pts=pts, stype=2)

            # Calculate points in map space
            xnew_map = xnew
            ynew_map = ynew

        if plotvars.proj == 'npstere' or plotvars.proj == 'spstere':
            # Calculate interpolation points
            xnew, ynew, xnew_map, ynew_map = polar_regular_grid()
            # Convert longitudes to be 0 to 360
            # negative longitudes are incorrectly regridded in polar stereographic projection
            xnew = np.mod(xnew + 360.0, 360.0)

    if plotvars.plot_type >= 2 and plotvars.plot_type <= 3:

        # Flip data if a lat-height plot and lats start at the north pole
        if plotvars.plot_type == 2:
            if xpts[0] > xpts[-1]:
                xpts = xpts[::-1]
                field = np.fliplr(field)

        # Calculate interpolation points
        ymin = np.nanmin(ypts)
        ymax = np.nanmax(ypts)
        if ylog:
            ymin = np.log10(ymin)
            ymax = np.log10(ymax)

        xnew, ynew = stipple_points(xmin=np.nanmin(xpts),
                                    xmax=np.nanmax(xpts),
                                    ymin=ymin,
                                    ymax=ymax,
                                    pts=pts, stype=2)

        if ylog:
            ynew = 10**ynew

    # Get values at the new points
    vals = regrid(f=field, x=xpts, y=ypts, xnew=xnew, ynew=ynew)

    # Work out which of the points are valid
    valid_points = np.array([], dtype='int64')
    for i in np.arange(np.size(vals)):
        if vals[i] >= min and vals[i] <= max:
            valid_points = np.append(valid_points, i)

    if plotvars.plot_type == 1:
        proj = ccrs.PlateCarree()

        if np.size(valid_points) > 0:
            plotvars.mymap.scatter(xnew[valid_points], ynew[valid_points],
                                   s=size, c=color, marker=marker,
                                   edgecolors=edgecolors,
                                   alpha=alpha, transform=proj, zorder=zorder)

    if plotvars.plot_type >= 2 and plotvars.plot_type <= 3:
        plotvars.plot.scatter(xnew[valid_points], ynew[valid_points],
                              s=size, c=color, marker=marker,
                              edgecolors=edgecolors,
                              alpha=alpha, zorder=zorder)


def stipple_points(xmin=None, xmax=None, ymin=None,
                   ymax=None, pts=None, stype=None):
    """
     | stipple_points - calculate interpolation points
     |
     | xmin=None - plot x minimum
     | ymax=None - plot x maximum
     | ymin=None - plot y minimum
     | ymax=None - plot x maximum
     | pts=None -  number of points in the x and y directions
     |             one number gives the same in both directions
     |
     | stype=None - type of grid.  1=regular, 2=offset
     |
     |
     |
     :Returns:
        stipple locations in x and y
     |
     |
    """

    # Work out number of points in x and y directions
    if np.size(pts) == 1:
        pts_x = pts
        pts_y = pts
    if np.size(pts) == 2:
        pts_x = pts[0]
        pts_y = pts[1]

    # Create regularly spaced points
    xstep = (xmax - xmin) / float(pts_x)
    x1 = [xmin + xstep / 4]
    while (np.nanmax(x1) + xstep) < xmax - xstep / 10:
        x1 = np.append(x1, np.nanmax(x1) + xstep)

    x2 = [xmin + xstep * 3 / 4]
    while (np.nanmax(x2) + xstep) < xmax - xstep / 10:
        x2 = np.append(x2, np.nanmax(x2) + xstep)

    ystep = (ymax - ymin) / float(pts_y)
    y1 = [ymin + ystep / 2]
    while (np.nanmax(y1) + ystep) < ymax - ystep / 10:
        y1 = np.append(y1, np.nanmax(y1) + ystep)

    # Create interpolation points
    xnew = []
    ynew = []
    iy = 0

    for y in y1:
        iy = iy + 1
        if stype == 1:
            xnew = np.append(xnew, x1)
            y2 = np.zeros(np.size(x1))
            y2.fill(y)
            ynew = np.append(ynew, y2)

        if stype == 2:
            if iy % 2 == 0:
                xnew = np.append(xnew, x1)
                y2 = np.zeros(np.size(x1))
                y2.fill(y)
                ynew = np.append(ynew, y2)
            if iy % 2 == 1:
                xnew = np.append(xnew, x2)
                y2 = np.zeros(np.size(x2))
                y2.fill(y)
                ynew = np.append(ynew, y2)

    return xnew, ynew


def find_pos_in_array(vals=None, val=None, above=False):
    """
     | find_pos_in_array - find the position of a point in an array
     |
     | vals - array values
     | val - value to find position of
     |
     |
     |
     |
     |
     |
     :Returns:
       position in array
     |
     |
     |
    """

    pos = -1
    if above is False:
        for myval in vals:
            if val > myval:
                pos = pos + 1

    if above:
        for myval in vals:
            if val >= myval:
                pos = pos + 1

        if np.size(vals) - 1 > pos:
            pos = pos + 1

    return pos


def vect(u=None, v=None, x=None, y=None, scale=None, stride=None, pts=None,
         key_length=None, key_label=None, ptype=None, title=None, magmin=None,
         width=0.02, headwidth=3, headlength=5, headaxislength=4.5,
         pivot='middle', key_location=[0.95, -0.06], key_show=True, axes=True,
         xaxis=True, yaxis=True, xticks=None, xticklabels=None, yticks=None,
         yticklabels=None, xlabel=None, ylabel=None, ylog=False, color='k',
         zorder=3, titles=None, alpha=1.0):
    """
     | vect - plot vectors
     |
     | u=None - u wind
     | v=None - v wind
     | x=None - x locations of u and v
     | y=None - y locations of u and v
     | scale=None - data units per arrow length unit.  A smaller values gives
     |              a larger vector. Generally takes one value but in the case
     |              of two supplied values the second vector scaling applies to
     |              the v field.
     | stride=None - plot vector every stride points. Can take two values one
     |               for x and one for y.
     | pts=None - use bilinear interpolation to interpolate vectors onto a new
     |            grid - takes one or two values.
     |            If one value is passed then this is used for both the x and
     |            y axes.
     | magmin=None - don't plot any vects with less than this magnitude.
     | key_length=None - length of the key.  Generally takes one value but in
     |                   the case of two supplied values the second vector
     |                   scaling applies to the v field.
     | key_label=None - label for the key. Generally takes one value but in the
     |                  case of two supplied values the second vector scaling
     |                  applies to the v field.
     | key_location=[0.9, -0.06] - location of the vector key relative to the
     |                             plot in normalised coordinates.
     | key_show=True - draw the key.  Set to False if not required.
     | ptype=0 - plot type - not needed for cf fields.
     |                       0 = no specific plot type,
     |                       1 = longitude-latitude,
     |                       2 = latitude - height,
     |                       3 = longitude - height,
     |                       4 = latitude - time,
     |                       5 = longitude - time
     |                       6 = rotated pole
     |
     | title=None - plot title
     | width=0.005 - shaft width in arrow units; default is 0.005 times the
     |               width of the plot
     | headwidth=3 - head width as multiple of shaft width, default is 3
     | headlength=5 - head length as multiple of shaft width, default is 5
     | headaxislength=4.5 - head length at shaft intersection, default is 4.5
     | pivot='middle' - the part of the arrow that is at the grid point; the
     |                  arrow rotates about this point
                        takes 'tail', 'middle', 'tip'
     | axes=True - plot x and y axes
     | xaxis=True - plot xaxis
     | yaxis=True - plot y axis
     | xticks=None - xtick positions
     | xticklabels=None - xtick labels
     | yticks=None - y tick positions
     | yticklabels=None - ytick labels
     | xlabel=None - label for x axis
     | ylabel=None - label for y axis
     | ylog=False - log y axis
     | color='k' - colour for the vectors - default is black.
     | zorder=3 - plotting order
     | titles=None - generate dimension and cell_methods titles for plot
     | alpha=1.0 - transparency setting.  The default is no transparency.
     |
     :Returns:
      None
     |
     |
     |
    """

    # If the vector color is white set the quicker key colour to black
    # so that it can be seen
    qkey_color = color
    if qkey_color == 'w' or qkey_color == 'white':
        qkey_color = 'k'

    colorbar_title = ''
    text_fontsize = plotvars.text_fontsize
    continent_thickness = plotvars.continent_thickness
    continent_color = plotvars.continent_color
    if text_fontsize is None:
        text_fontsize = 11
    if continent_thickness is None:
        continent_thickness = 1.5
    if continent_color is None:
        continent_color = 'k'
    # ylog=plotvars.ylog
    title_fontsize = plotvars.title_fontsize
    title_fontweight = plotvars.title_fontweight
    if title_fontsize is None:
        title_fontsize = 15
    resolution_orig = plotvars.resolution

    # Set potential user axis labels
    user_xlabel = xlabel
    user_ylabel = ylabel

    rotated_vect = False
    if isinstance(u, cf.Field):
        if u.ref('grid_mapping_name:rotated_latitude_longitude', default=False):
            rotated_vect = True

    # Extract required data
    # If a cf-python field
    if isinstance(u, cf.Field):

        # Check data is 2D
        ndims = np.squeeze(u.data).ndim
        if ndims != 2:
            errstr = "\n\ncfp.vect error need a 2 dimensonal u field to make vectors\n"
            errstr += "received " + str(np.squeeze(u.data).ndim)
            if ndims == 1:
                errstr += " dimension\n\n"
            else:
                errstr += " dimensions\n\n"
            raise TypeError(errstr)

        u_data, u_x, u_y, ptype, colorbar_title, xlabel, ylabel, xpole, \
            ypole = cf_data_assign(u, colorbar_title, rotated_vect=rotated_vect)
    elif isinstance(u, cf.FieldList):
        raise TypeError("Can't plot a field list")
    else:
        # field=f #field data passed in as f
        check_data(u, x, y)
        u_data = deepcopy(u)
        u_x = deepcopy(x)
        u_y = deepcopy(y)
        xlabel = ''
        ylabel = ''

    if isinstance(v, cf.Field):

        # Check data is 2D
        ndims = np.squeeze(v.data).ndim
        if ndims != 2:
            errstr = "\n\ncfp.vect error need a 2 dimensonal v field to make vectors\n"
            errstr += "received " + str(np.squeeze(v.data).ndim)
            if ndims == 1:
                errstr += " dimension\n\n"
            else:
                errstr += " dimensions\n\n"
            raise TypeError(errstr)

        v_data, v_x, v_y, ptype, colorbar_title, xlabel, ylabel, xpole, \
            ypole = cf_data_assign(v, colorbar_title, rotated_vect=rotated_vect)
    elif isinstance(v, cf.FieldList):
        raise TypeError("Can't plot a field list")
    else:
        # field=f #field data passed in as f
        check_data(v, x, y)
        v_data = deepcopy(v)
        v_x = deepcopy(x)
        xlabel = ''
        ylabel = ''

    # If a minimum magnitude is specified mask these data points
    if magmin is not None:
        mag = np.sqrt(u_data**2 + v_data**2)
        invalid = np.where(mag <= magmin)
        if np.size(invalid) > 0:
            u_data[invalid] = np.nan
            v_data[invalid] = np.nan

    # Reset xlabel and ylabel values with user defined labels in specified
    if user_xlabel is not None:
        xlabel = user_xlabel
    if user_ylabel is not None:
        ylabel = user_ylabel

    # Retrieve any user defined axis labels
    if xlabel == '' and plotvars.xlabel is not None:
        xlabel = plotvars.xlabel
    if ylabel == '' and plotvars.ylabel is not None:
        ylabel = plotvars.ylabel
    if xticks is None and plotvars.xticks is not None:
        xticks = plotvars.xticks
        if plotvars.xticklabels is not None:
            xticklabels = plotvars.xticklabels
        else:
            xticklabels = list(map(str, xticks))
    if yticks is None and plotvars.yticks is not None:
        yticks = plotvars.yticks
        if plotvars.yticklabels is not None:
            yticklabels = plotvars.yticklabels
        else:
            yticklabels = list(map(str, yticks))

    if scale is None:
        scale = np.nanmax(u_data) / 4.0

    if key_length is None:
        key_length = scale

    # Calculate a set of dimension titles if requested
    if titles: 
        title_dims = generate_titles(u)
        title_dims = 'u\n' + title_dims
        title_dims2 = generate_titles(v)
        title_dims2 = 'v\n' + title_dims2


    # Open a new plot if necessary
    if plotvars.user_plot == 0:
        gopen(user_plot=0)

    # Call gpos(1) if not already called
    if plotvars.rows > 1 or plotvars.columns > 1:
        if plotvars.gpos_called is False:
            gpos(1)

    # Set plot type if user specified
    if (ptype is not None):
        plotvars.plot_type = ptype

    lonrange = np.nanmax(u_x) - np.nanmin(u_x)
    latrange = np.nanmax(u_y) - np.nanmin(u_y)

    if plotvars.plot_type == 1:
        # Set up mapping
        if (lonrange > 350 and latrange > 170) or plotvars.user_mapset == 1:
            set_map()
        else:
            mapset(lonmin=np.nanmin(u_x), lonmax=np.nanmax(u_x),
                   latmin=np.nanmin(u_y), latmax=np.nanmax(u_y),
                   user_mapset=0, resolution=resolution_orig)
            set_map()

        mymap = plotvars.mymap

        # u_data, u_x = cartopy_util.add_cyclic_point(u_data, u_x)
        u_data, u_x = add_cyclic(u_data, u_x)
        # v_data, v_x = cartopy_util.add_cyclic_point(v_data, v_x)
        v_data, v_x = add_cyclic(v_data, v_x)

    # stride data points to reduce vector density
    if stride is not None:
        if np.size(stride) == 1:
            xstride = stride
            ystride = stride
        if np.size(stride) == 2:
            xstride = stride[0]
            ystride = stride[1]

        u_x = u_x[0::xstride]
        u_y = u_y[0::ystride]
        u_data = u_data[0::ystride, 0::xstride]
        v_data = v_data[0::ystride, 0::xstride]

    # Map vectors
    if plotvars.plot_type == 1:
        lonmax = plotvars.lonmax
        proj = ccrs.PlateCarree()

        # Fix for high latitude vectors as described at https://github.com/SciTools/cartopy/issues/1179
        if plotvars.proj != 'cyl':
            u_src_crs = u_data / np.cos(u_y[:, np.newaxis] / 180 * np.pi)
            v_src_crs = v_data
            magnitude = np.ma.sqrt(u_data**2 + v_data**2)
            magn_src_crs = np.ma.sqrt(u_src_crs**2 + v_src_crs**2)

            u_data = u_src_crs * magnitude / magn_src_crs
            v_data = v_src_crs * magnitude / magn_src_crs



        if pts is None:
            quiv = plotvars.mymap.quiver(u_x, u_y, u_data, v_data, scale=scale,
                                         pivot=pivot, units='inches',
                                         width=width, headwidth=headwidth,
                                         headlength=headlength,
                                         headaxislength=headaxislength,
                                         color=color, transform=proj,
                                         alpha=alpha, zorder=zorder)
        else:
            if plotvars.proj == 'cyl':
                # **cartopy 0.16 fix for longitide points in cylindrical projection
                # when regridding to a number of points
                # Make points within the plotting region
                for pt in np.arange(np.size(u_x)):
                    if u_x[pt] > lonmax:
                        u_x[pt] = u_x[pt]-360

            quiv = plotvars.mymap.quiver(u_x, u_y, u_data, v_data, scale=scale,
                                         pivot=pivot, units='inches',
                                         width=width, headwidth=headwidth,
                                         headlength=headlength,
                                         headaxislength=headaxislength,
                                         color=color,
                                         regrid_shape=pts, transform=proj,
                                         alpha=alpha, zorder=zorder)

        # Make key_label if none exists
        if key_label is None:
            key_label = str(key_length)
        if isinstance(u, cf.Field):
            key_label = supscr(key_label + u.units)
        if key_show:
            plotvars.mymap.quiverkey(quiv, key_location[0],
                                     key_location[1],
                                     key_length,
                                     key_label, labelpos='W',
                                     color=qkey_color,
                                     fontproperties={'size': str(plotvars.axis_label_fontsize)},
                                     coordinates='axes')

        # axes
        plot_map_axes(axes=axes, xaxis=xaxis, yaxis=yaxis,
                      xticks=xticks, xticklabels=xticklabels,
                      yticks=yticks, yticklabels=yticklabels,
                      user_xlabel=user_xlabel, user_ylabel=user_ylabel,
                      verbose=False)

        # Coastlines
        continent_thickness = plotvars.continent_thickness
        continent_color = plotvars.continent_color
        continent_linestyle = plotvars.continent_linestyle
        if continent_thickness is None:
            continent_thickness = 1.5
        if continent_color is None:
            continent_color = 'k'
        if continent_linestyle is None:
            continent_linestyle = 'solid'

        feature = cfeature.NaturalEarthFeature(name='land', category='physical',
                                               scale=plotvars.resolution,
                                               facecolor='none')
        mymap.add_feature(feature, edgecolor=continent_color,
                          linewidth=continent_thickness,
                          linestyle=continent_linestyle)

        # Title
        if title is not None:
            map_title(title)

        # Titles for dimensions
        if titles:
            if plotvars.titles_con_called is False:
                dim_titles(title_dims, title2=title_dims2, dims=True)
            else:
                dim_titles(title2=title_dims, title3=title_dims2, dims=True)


    if plotvars.plot_type == 6:
        if u.ref('grid_mapping_name:rotated_latitude_longitude', False):
            proj = ccrs.PlateCarree()

            # Set up mapping
            if (lonrange > 350 and latrange > 170) or plotvars.user_mapset == 1:
                set_map()

            else:
                mapset(lonmin=np.nanmin(u_x), lonmax=np.nanmax(u_x),
                       latmin=np.nanmin(u_y), latmax=np.nanmax(u_y),
                       user_mapset=0, resolution=resolution_orig)
                set_map()

            quiv = plotvars.mymap.quiver(u_x, u_y, u_data, v_data, scale=scale*10, transform=proj,
                                         pivot=pivot, units='inches',
                                         width=width, headwidth=headwidth,
                                         headlength=headlength,
                                         headaxislength=headaxislength,
                                         color=color, alpha=alpha, zorder=zorder)

            # Make key_label if none exists
            if key_label is None:
                key_label = str(key_length)
            if isinstance(u, cf.Field):
                key_label = supscr(key_label + u.units)

            if key_show:
                plotvars.mymap.quiverkey(quiv, key_location[0],
                                         key_location[1],
                                         key_length,
                                         key_label, labelpos='W',
                                         color=qkey_color,
                                         fontproperties={'size': str(plotvars.axis_label_fontsize)},
                                         coordinates='axes')

            # Axes on the native grid
            if plotvars.plot == 'rotated':
                rgaxes(xpole=xpole, ypole=ypole, xvec=x, yvec=y,
                       xticks=xticks, xticklabels=xticklabels,
                       yticks=yticks, yticklabels=yticklabels,
                       axes=axes, xaxis=xaxis, yaxis=yaxis,
                       xlabel=xlabel, ylabel=ylabel)

            if plotvars.plot == 'cyl':
                plot_map_axes(axes=axes, xaxis=xaxis, yaxis=yaxis,
                              xticks=xticks, xticklabels=xticklabels,
                              yticks=yticks, yticklabels=yticklabels,
                              user_xlabel=user_xlabel, user_ylabel=user_ylabel,
                              verbose=False)

            # Title
            if title is not None:
                map_title(title)


            # Titles for dimensions
            if titles:
                dim_titles(title_dims, titles2=dim_titles2, dims=True)



    ######################################
    # Latitude or longitude vs height plot
    ######################################
    if plotvars.plot_type == 2 or plotvars.plot_type == 3:

        user_gset = plotvars.user_gset
        if user_gset == 0:
            # Program selected data plot limits
            xmin = np.nanmin(u_x)
            xmax = np.nanmax(u_x)
            if plotvars.plot_type == 2:
                if xmin < -80 and xmin >= -90:
                    xmin = -90
                if xmax > 80 and xmax <= 90:
                    xmax = 90
            ymin = np.nanmin(u_y)
            if ymin <= 10:
                ymin = 0
            ymax = np.nanmax(u_y)
        else:
            # User specified plot limits
            xmin = plotvars.xmin
            xmax = plotvars.xmax
            if plotvars.ymin < plotvars.ymax:
                ymin = plotvars.ymin
                ymax = plotvars.ymax
            else:
                ymin = plotvars.ymax
                ymax = plotvars.ymin

        ystep = None
        if (ymax == 1000):
            ystep = 100
        if (ymax == 100000):
            ystep = 10000

        ytype = 0  # pressure or similar y axis
        if 'theta' in ylabel.split(' '):
            ytype = 1
        if 'height' in ylabel.split(' '):
            ytype = 1
            ystep = 100
            if (ymax - ymin) > 5000:
                ystep = 500.0
            if (ymax - ymin) > 10000:
                ystep = 1000.0
            if (ymax - ymin) > 50000:
                ystep = 10000.0

        # Set plot limits and draw axes
        if ylog != 1:
            if ytype == 1:
                gset(
                    xmin=xmin,
                    xmax=xmax,
                    ymin=ymin,
                    ymax=ymax,
                    user_gset=user_gset)
            else:
                gset(
                    xmin=xmin,
                    xmax=xmax,
                    ymin=ymax,
                    ymax=ymin,
                    user_gset=user_gset)

            # Set default x-axis labels
            lltype = 1
            if plotvars.plot_type == 2:
                lltype = 2
            llticks, lllabels = mapaxis(min=xmin, max=xmax, type=lltype)

            heightticks = gvals(
                dmin=ymin,
                dmax=ymax,
                mystep=ystep,
                mod=False)[0]
            heightlabels = heightticks

            if axes:
                if xaxis:
                    if xticks is not None:
                        llticks = xticks
                        lllabels = xticks
                        if xticklabels is not None:
                            lllabels = xticklabels
                else:
                    llticks = [100000000]
                    xlabel = ''

                if yaxis:
                    if yticks is not None:
                        heightticks = yticks
                        heightlabels = yticks
                        if yticklabels is not None:
                            heightlabels = yticklabels
                else:
                    heightticks = [100000000]
                    ylabel = ''

            else:
                llticks = [100000000]
                heightticks = [100000000]
                xlabel = ''
                ylabel = ''

            axes_plot(xticks=llticks, xticklabels=lllabels,
                      yticks=heightticks, yticklabels=heightlabels,
                      xlabel=xlabel, ylabel=ylabel)

        # Log y axis
        if ylog:
            if ymin == 0:
                ymin = 1  # reset zero mb/height input to a small value
            gset(xmin=xmin,
                 xmax=xmax,
                 ymin=ymax,
                 ymax=ymin,
                 ylog=1,
                 user_gset=user_gset)
            llticks, lllabels = mapaxis(min=xmin,
                                        max=xmax,
                                        type=plotvars.plot_type)

            if axes:
                if xaxis:
                    if xticks is not None:
                        llticks = xticks
                        lllabels = xticks
                        if xticklabels is not None:
                            lllabels = xticklabels
                else:
                    llticks = [100000000]
                    xlabel = ''

                if yaxis:
                    if yticks is not None:
                        heightticks = yticks
                        heightlabels = yticks
                        if yticklabels is not None:
                            heightlabels = yticklabels
                else:
                    heightticks = [100000000]
                    ylabel = ''

                if yticks is None:
                    axes_plot(
                        xticks=llticks,
                        xticklabels=lllabels,
                        xlabel=xlabel,
                        ylabel=ylabel)
                else:
                    axes_plot(xticks=llticks, xticklabels=lllabels,
                              yticks=heightticks, yticklabels=heightlabels,
                              xlabel=xlabel, ylabel=ylabel)

        # Regrid the data if requested
        if pts is not None:

            xnew, ynew = stipple_points(xmin=np.min(u_x), xmax=np.max(u_x),
                                        ymin=np.min(u_y), ymax=np.max(u_y),
                                        pts=pts, stype=1)

            if ytype == 0:
                # Make y interpolation in log space as we have a pressure coordinate
                u_vals = regrid(f=u_data, x=u_x, y=np.log10(u_y), xnew=xnew, ynew=np.log10(ynew))
                v_vals = regrid(f=v_data, x=u_x, y=np.log10(u_y), xnew=xnew, ynew=np.log10(ynew))
            else:
                u_vals = regrid(f=u_data, x=u_x, y=u_y, xnew=xnew, ynew=ynew)
                v_vals = regrid(f=v_data, x=u_x, y=u_y, xnew=xnew, ynew=ynew)

            u_x = xnew
            u_y = ynew
            u_data = u_vals
            v_data = v_vals

        # set scale and key lengths
        if np.size(scale) == 1:
            scale_u = scale
            scale_v = scale
        else:
            scale_u = scale[0]
            scale_v = scale[1]

        if np.size(key_length) == 2:
            key_length_u = key_length[0]
            key_length_v = key_length[1]
            # scale v data
            v_data = v_data * scale_u / scale_v
        else:
            key_length_u = key_length

        # Plot the vectors
        quiv = plotvars.plot.quiver(u_x, u_y, u_data, v_data, pivot=pivot,
                                    units='inches', scale=scale_u,
                                    width=width, headwidth=headwidth,
                                    headlength=headlength,
                                    headaxislength=headaxislength,
                                    color=color, alpha=alpha, zorder=zorder)

        # Plot single key
        if np.size(scale) == 1:
            # Single scale vector
            if key_label is None:
                key_label_u = str(key_length_u)
                if isinstance(u, cf.Field):
                    key_label_u = supscr(key_label_u + ' (' + u.units + ')')
            else:
                key_label_u = key_label[0]
            if key_show:
                plotvars.plot.quiverkey(quiv, key_location[0],
                                        key_location[1],
                                        key_length_u, key_label_u,
                                        labelpos='W',
                                        color=qkey_color,
                                        fontproperties={'size': str(plotvars.axis_label_fontsize)})

        # Plot two keys
        if np.size(scale) == 2:
            # translate from normalised units to plot units
            xpos = key_location[0] * \
                (plotvars.xmax - plotvars.xmin) + plotvars.xmin
            ypos = key_location[1] * \
                (plotvars.ymax - plotvars.ymin) + plotvars.ymin

            # horizontal and vertical spacings for offsetting vector reference
            # text
            xoffset = 0.01 * abs(plotvars.xmax - plotvars.xmin)
            yoffset = 0.01 * abs(plotvars.ymax - plotvars.ymin)

            # Assign key labels if necessary
            if key_label is None:
                key_label_u = str(key_length_u)
                key_label_v = str(key_length_v)
                if isinstance(u, cf.Field):
                    key_label_u = supscr(key_label_u + ' (' + u.units + ')')
                if isinstance(v, cf.Field):
                    key_label_v = supscr(key_label_v + ' (' + v.units + ')')
            else:
                key_label_u = supscr(key_label[0])
                key_label_v = supscr(key_label[1])

            # Plot reference vectors and keys
            if key_show:
                plotvars.plot.quiver(xpos, ypos, key_length[0], 0,
                                     pivot='tail', units='inches',
                                     scale=scale[0],
                                     headaxislength=headaxislength,
                                     width=width, headwidth=headwidth,
                                     headlength=headlength,
                                     clip_on=False,
                                     color=qkey_color)

                plotvars.plot.quiver(xpos, ypos, 0, key_length[1],
                                     pivot='tail', units='inches',
                                     scale=scale[1],
                                     headaxislength=headaxislength,
                                     width=width, headwidth=headwidth,
                                     headlength=headlength,
                                     clip_on=False,
                                     color=qkey_color)

                plotvars.plot.text(xpos,
                                   ypos + yoffset,
                                   key_label_u,
                                   horizontalalignment='left',
                                   verticalalignment='top')
                plotvars.plot.text(xpos - xoffset,
                                   ypos,
                                   key_label_v,
                                   horizontalalignment='right',
                                   verticalalignment='bottom')

        if title is not None:
            plotvars.plot.set_title(title,
                                    y=1.03,
                                    fontsize=plotvars.title_fontsize,
                                    fontweight=title_fontweight)

            # Titles for dimensions
            if titles:
                dim_titles(title_dims, titles2=dim_titles2, dims=True)


    ##########
    # Save plot
    ##########
    if plotvars.user_plot == 0:
        gset()
        cscale()
        gclose()

    if plotvars.user_mapset == 0:
        mapset()
        mapset(resolution=resolution_orig)


def set_map():
    """
     | set_map - set map and write into plotvars.mymap
     |
     | No inputs
     | This is an internal routine and not used by the user
     |
     |
     |
     |
     |
     :Returns:
      None
     |
     |
     |
    """


    # Return if mymap is already set
    if plotvars.mymap is not None:
        return



    # Set up mapping
    extent = True
    lon_mid = plotvars.lonmin + (plotvars.lonmax - plotvars.lonmin) / 2.0
    lonmin = plotvars.lonmin
    lonmax = plotvars.lonmax
    latmin = plotvars.latmin
    latmax = plotvars.latmax

    if plotvars.proj == 'cyl':
        proj = ccrs.PlateCarree(central_longitude=lon_mid)

        # Cartopy line plotting and identical left == right fix

        if lonmax - lonmin == 360.0:
            lonmax = lonmax + 0.01

    if plotvars.proj == 'merc':
        min_latitude = -80.0
        if plotvars.lonmin > min_latitude:
            min_latitude = plotvars.lonmin
        max_latitude = 84.0
        if plotvars.lonmax < max_latitude:
            max_latitude = plotvars.lonmax
        proj = ccrs.Mercator(central_longitude=plotvars.lon_0,
                             min_latitude=min_latitude,
                             max_latitude=max_latitude)

    if plotvars.proj == 'npstere':
        proj = ccrs.NorthPolarStereo(central_longitude=plotvars.lon_0)
        # **cartopy 0.16 fix
        # Here we add in 0.01 to the longitude extent as this helps with plotting
        # lines and line labels
        lonmin = plotvars.lon_0-180
        lonmax = plotvars.lon_0+180.01
        latmin = plotvars.boundinglat
        latmax = 90

    if plotvars.proj == 'spstere':
        proj = ccrs.SouthPolarStereo(central_longitude=plotvars.lon_0)
        # **cartopy 0.16 fix
        # Here we add in 0.01 to the longitude extent as this helps with plotting
        # lines and line labels
        lonmin = plotvars.lon_0-180
        lonmax = plotvars.lonmax+180.01
        latmin = -90
        latmax = plotvars.boundinglat

    if plotvars.proj == 'ortho':
        proj = ccrs.Orthographic(central_longitude=plotvars.lon_0,
                                 central_latitude=plotvars.lat_0)
        lonmin = plotvars.lon_0-180.0
        lonmax = plotvars.lon_0+180.01
        extent = False

    if plotvars.proj == 'moll':
        proj = ccrs.Mollweide(central_longitude=plotvars.lon_0)
        lonmin = plotvars.lon_0-180.0
        lonmax = plotvars.lon_0+180.01
        extent = False

    if plotvars.proj == 'robin':
        proj = ccrs.Robinson(central_longitude=plotvars.lon_0)

    if plotvars.proj == 'lcc':
        latmin = plotvars.latmin
        latmax = plotvars.latmax
        lonmin = plotvars.lonmin
        lonmax = plotvars.lonmax
        lon_0 = lonmin+(lonmax-lonmin)/2.0
        lat_0 = latmin+(latmax-latmin)/2.0
        cutoff = -40
        if lat_0 <= 0:
            cutoff = 40

        standard_parallels = [33, 45]
        if latmin <= 0 and latmax <= 0:
            standard_parallels = [-45, -33]
        proj = ccrs.LambertConformal(central_longitude=lon_0,
                                     central_latitude=lat_0,
                                     cutoff=cutoff, standard_parallels=standard_parallels)

    if plotvars.proj == 'rotated':
        proj = ccrs.PlateCarree(central_longitude=lon_mid)

    if plotvars.proj == 'OSGB':
        proj = ccrs.OSGB()

    if plotvars.proj == 'EuroPP':
        proj = ccrs.EuroPP()

    if plotvars.proj == 'UKCP':
        # Special case of TransverseMercator for UKCP
        proj = ccrs.TransverseMercator()

    if plotvars.proj == 'TransverseMercator':
        proj = ccrs.TransverseMercator()
        lonmin = plotvars.lon_0-180.0
        lonmax = plotvars.lon_0+180.01
        extent = False


    if plotvars.proj == 'LambertCylindrical':
        proj = ccrs.LambertCylindrical()
        lonmin = plotvars.lonmin
        lonmax = plotvars.lonmax
        latmin = plotvars.latmin
        latmax = plotvars.latmax
        extent = True



    # Add a plot containing the projection
    if plotvars.plot_xmin:
        delta_x = plotvars.plot_xmax - plotvars.plot_xmin
        delta_y = plotvars.plot_ymax - plotvars.plot_ymin
        mymap = plotvars.master_plot.add_axes([plotvars.plot_xmin,
                                              plotvars.plot_ymin,
                                              delta_x, delta_y],
                                              projection=proj)
    else:
        mymap = plotvars.master_plot.add_subplot(plotvars.rows,
                                                 plotvars.columns,
                                                 plotvars.pos,
                                                 projection=proj)

    # Set map extent
    set_extent = True
    if plotvars.proj in ['OSGB', 'EuroPP', 'UKCP', 'robin', 'lcc']:
        set_extent = False

    if extent and set_extent:
        mymap.set_extent([lonmin, lonmax, latmin, latmax], crs=ccrs.PlateCarree())

    # Set the scaling for PlateCarree
    if plotvars.proj == 'cyl':
        mymap.set_aspect(plotvars.aspect)

    if plotvars.proj == 'lcc':
        # Special case of lcc
        mymap.set_extent([lonmin, lonmax, latmin, latmax], crs=ccrs.PlateCarree())

    if plotvars.proj == 'UKCP':
        # Special case of TransverseMercator for UKCP
        mymap.set_extent([-11, 3, 49, 61], crs=ccrs.PlateCarree())

    if plotvars.proj == 'EuroPP':
        # EuroPP somehow needs some limits setting.
        mymap.set_extent([-12, 25, 30, 75], crs=ccrs.PlateCarree())

    # Remove any plotvars.plot axes leaving just the plotvars.mymap axes
    plotvars.plot.set_frame_on(False)
    plotvars.plot.set_xticks([])
    plotvars.plot.set_yticks([])

    # Store map
    plotvars.mymap = mymap


def polar_regular_grid(pts=50):
    """
     | polar_regular_grid - return a regular grid over a polar
     |                      stereographic area
     |
     | pts=50 - number  of grid points in the x and y directions
     |
     |
     |
     |
     |
     |
     :Returns:
      lons, lats of grid in degrees
      x, y locations of lons and lats
     |
     |
     |
    """

    boundinglat = plotvars.boundinglat
    lon_0 = plotvars.lon_0

    if plotvars.proj == 'npstere':
        thisproj = ccrs.NorthPolarStereo(central_longitude=lon_0)
    else:
        thisproj = ccrs.SouthPolarStereo(central_longitude=lon_0)

    # Find min and max of plotting region in device coordinates
    lons = np.array([lon_0-90, lon_0, lon_0+90, lon_0+180])
    lats = np.array([boundinglat, boundinglat, boundinglat, boundinglat])
    extent = thisproj.transform_points(ccrs.PlateCarree(), lons, lats)

    xmin = np.min(extent[:, 0])
    xmax = np.max(extent[:, 0])
    ymin = np.min(extent[:, 1])
    ymax = np.max(extent[:, 1])

    # Make up a stipple of points for cover the pole
    points_device = stipple_points(
        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, pts=pts, stype=2)

    xnew = np.array(points_device)[0, :]
    ynew = np.array(points_device)[1, :]

    points_polar = ccrs.PlateCarree().transform_points(thisproj, xnew, ynew)

    lons = np.array(points_polar)[:, 0]
    lats = np.array(points_polar)[:, 1]

    if plotvars.proj == 'npstere':
        valid = np.where(lats >= boundinglat)
    else:
        valid = np.where(lats <= boundinglat)

    return lons[valid], lats[valid], xnew[valid], ynew[valid]


def cf_var_name(field=None, dim=None):
    """
     | cf_var_name - return the name from a supplied dimension
     |               in the following order
     |               ncvar
     |               short_name
     |               long_name
     |               standard_name
     |
     | field=None - field
     | dim=None - dimension required - 'dim0', 'dim1' etc.
     |
     |
     |
     |
     |
     :Returns:
      name
     |
     |
     |
    """

    # Check for multiple Z coordinates
    # Adjust dim if necessary
    if dim == 'Z':
        z_count = 0
        z_names =[]
        for mycoord in list(field.coords()):
            if field.coord(mycoord).Z:
                z_count += 1
                z_names.append(mycoord)
                            
        if z_count > 1:
            dim = z_names[-1]
            
            
    id = getattr(field.construct(dim), 'id', False)
    ncvar = field.construct(dim).nc_get_variable(False)
    short_name = getattr(field.construct(dim), 'short_name', False)
    long_name = getattr(field.construct(dim), 'long_name', False)
    standard_name = getattr(field.construct(dim), 'standard_name', False)

    name = 'No Name'
    if id:
        name = id
    if ncvar:
        name = ncvar
    if short_name:
        name = short_name
    if long_name:
        name = long_name
    if standard_name:
        name = standard_name

    return name


def cf_var_name_titles(field=None, dim=None):
    """
     | cf_var_name - return the name from a supplied dimension
     |               in the following preference order:
     |               standard_name
     |               long_name
     |               short_name
     |               ncvar
     |
     | field=None - field
     | dim=None - dimension required - 'dim0', 'dim1' etc.
     |
     :Returns:
      name
    """

    name = None
    units = None
    if field.has_construct(dim):

        id = getattr(field.construct(dim), 'id', False)
        ncvar = field.construct(dim).nc_get_variable(False)
        short_name = getattr(field.construct(dim), 'short_name', False)
        long_name = getattr(field.construct(dim), 'long_name', False)
        standard_name = getattr(field.construct(dim), 'standard_name', False)

        #name = 'No Name'
        if id:
            name = id
        if ncvar:
            name = ncvar
        if short_name:
            name = short_name
        if long_name:
            name = long_name
        if standard_name:
            name = standard_name

        units = getattr(field.construct(dim), 'units', '')
        if len(units) > 0:
            units = '(' + units + ')'
    return name, units


def process_color_scales():
    """
     | Process colour scales to generate images of them for the web
     | documentation and the rst code for inclusion in the
     | colour_scale.rst file.
     |
     |
     | No inputs
     | This is an internal routine and not used by the user
     |
     |
     |
     |
     |
     :Returns:
      None
     |
     |
     |
    """

    # Define scale categories
    uniform = ['viridis', 'magma', 'inferno', 'plasma', 'parula', 'gray']

    ncl_large = ['amwg256', 'BkBlAqGrYeOrReViWh200', 'BlAqGrYeOrRe',
                 'BlAqGrYeOrReVi200', 'BlGrYeOrReVi200', 'BlRe', 'BlueRed',
                 'BlueRedGray', 'BlueWhiteOrangeRed', 'BlueYellowRed',
                 'BlWhRe', 'cmp_b2r', 'cmp_haxby', 'detail', 'extrema',
                 'GrayWhiteGray', 'GreenYellow', 'helix', 'helix1',
                 'hotres', 'matlab_hot', 'matlab_hsv', 'matlab_jet',
                 'matlab_lines', 'ncl_default', 'ncview_default',
                 'OceanLakeLandSnow', 'rainbow', 'rainbow_white_gray',
                 'rainbow_white', 'rainbow_gray', 'tbr_240_300',
                 'tbr_stdev_0_30', 'tbr_var_0_500', 'tbrAvg1', 'tbrStd1',
                 'tbrVar1', 'thelix', 'ViBlGrWhYeOrRe', 'wh_bl_gr_ye_re',
                 'WhBlGrYeRe', 'WhBlReWh', 'WhiteBlue',
                 'WhiteBlueGreenYellowRed', 'WhiteGreen',
                 'WhiteYellowOrangeRed', 'WhViBlGrYeOrRe', 'WhViBlGrYeOrReWh',
                 'wxpEnIR', '3gauss', '3saw', 'BrBG']

    ncl_meteoswiss = ['hotcold_18lev', 'hotcolr_19lev', 'mch_default',
                      'perc2_9lev', 'percent_11lev', 'precip2_15lev',
                      'precip2_17lev', 'precip3_16lev', 'precip4_11lev',
                      'precip4_diff_19lev', 'precip_11lev',
                      'precip_diff_12lev', 'precip_diff_1lev',
                      'rh_19lev', 'spread_15lev']

    ncl_color_blindness = ['StepSeq25', 'posneg_2', 'posneg_1',
                           'BlueDarkOrange18', 'BlueDarkRed18',
                           'GreenMagenta16', 'BlueGreen14', 'BrownBlue12',
                           'Cat12']

    ncl_small = ['amwg', 'amwg_blueyellowred', 'BlueDarkRed18',
                 'BlueDarkOrange18', 'BlueGreen14', 'BrownBlue12', 'Cat12',
                 'cmp_flux', 'cosam12', 'cosam', 'GHRSST_anomaly',
                 'GreenMagenta16', 'hotcold_18lev', 'hotcolr_19lev',
                 'mch_default', 'nrl_sirkes', 'nrl_sirkes_nowhite',
                 'perc2_9lev', 'percent_11lev', 'posneg_2', 'prcp_1', 'prcp_2',
                 'prcp_3', 'precip_11lev', 'precip_diff_12lev',
                 'precip_diff_1lev', 'precip2_15lev', 'precip2_17lev',
                 'precip3_16lev', 'precip4_11lev', 'precip4_diff_19lev',
                 'radar', 'radar_1', 'rh_19lev', 'seaice_1', 'seaice_2',
                 'so4_21', 'spread_15lev', 'StepSeq25', 'sunshine_9lev',
                 'sunshine_diff_12lev', 'temp_19lev', 'temp_diff_18lev',
                 'temp_diff_1lev', 'topo_15lev', 'wgne15', 'wind_17lev']

    orography = ['os250kmetres', 'wiki_1_0_2', 'wiki_1_0_3',
                 'wiki_2_0', 'wiki_2_0_reduced', 'arctic']

    idl_guide = []
    for i in np.arange(1, 45):
        idl_guide.append('scale' + str(i))

    for category in ['uniform', 'ncl_meteoswiss', 'ncl_small', 'ncl_large',
                     'ncl_color_blindness', 'orography', 'idl_guide']:
        if category == 'uniform':
            scales = uniform
            div = '================== ====='
            chars = 10
            title = 'Perceptually uniform colour maps for use with continuous '
            title += 'data'
            print(title)
            print('----------------------------------------------')
            print('')
            print(div)
            print('Name               Scale')
            print(div)

        if category == 'ncl_meteoswiss':
            scales = ncl_meteoswiss
            div = '================== ====='
            chars = 19
            print('NCAR Command Language - MeteoSwiss colour maps')
            print('----------------------------------------------')
            print('')
            print(div)
            print('Name               Scale')
            print(div)
        if category == 'ncl_small':
            scales = ncl_small
            div = '=================== ====='
            chars = 20
            print('NCAR Command Language - small color maps (<50 colours)')
            print('------------------------------------------------------')
            print('')
            print(div)
            print('Name                Scale')
            print(div)
        if category == 'ncl_large':
            scales = ncl_large
            div = '======================= ====='
            chars = 24
            print('NCAR Command Language - large colour maps (>50 colours)')
            print('-------------------------------------------------------')
            print('')
            print(div)
            print('Name                    Scale')
            print(div)
        if category == 'ncl_color_blindness':
            scales = ncl_color_blindness
            div = '================ ====='
            chars = 17
            title = 'NCAR Command Language - Enhanced to help with colour'
            title += 'blindness'
            print(title)
            title = '-----------------------------------------------------'
            title += '---------'
            print(title)
            print('')
            print(div)
            print('Name             Scale')
            print(div)
            chars = 17
        if category == 'orography':
            scales = orography
            div = '================ ====='
            chars = 17
            print('Orography/bathymetry colour scales')
            print('----------------------------------')
            print('')
            print(div)
            print('Name             Scale')
            print(div)
            chars = 17
        if category == 'idl_guide':
            scales = idl_guide
            div = '======= ====='
            chars = 8
            print('IDL guide scales')
            print('----------------')
            print('')
            print(div)
            print('Name    Scale')
            print(div)
            chars = 8

        for scale in scales:
            # Make image of scale
            fig = plot.figure(figsize=(8, 0.5))
            ax1 = fig.add_axes([0.05, 0.1, 0.9, 0.2])
            cscale(scale)
            cmap = matplotlib.colors.ListedColormap(plotvars.cs)
            cb1 = matplotlib.colorbar.ColorbarBase(
                ax1, cmap=cmap, orientation='horizontal', ticks=None)
            cb1.set_ticks([0.0, 1.0])
            cb1.set_ticklabels(['', ''])
            file = '/home/andy/cf-docs/cfplot_sphinx/images/'
            file += 'colour_scales/' + scale + '.png'
            plot.savefig(file)
            plot.close()

            # Use convert to trim the png file to remove white space
            subprocess.call(["convert", "-trim", file, file])

            name_pad = scale
            while len(name_pad) < chars:
                name_pad = name_pad + ' '
            fn = name_pad + '.. image:: images/colour_scales/' + scale + '.png'
            print(fn)

        print(div)
        print('')
        print('')


def reset():
    """
     | reset all plotting variables
     |
     |
     |
     |
     |
     |
     |
     :Returns:
      name
     |
     |
     |
    """
    axes()
    cscale()
    levs()
    gset()
    mapset()
    setvars()


def setvars(file=None, title_fontsize=None, text_fontsize=None,
            colorbar_fontsize=None, colorbar_fontweight=None,
            axis_label_fontsize=None, title_fontweight=None,
            text_fontweight=None, axis_label_fontweight=None, fontweight=None,
            continent_thickness=None, continent_color=None,
            continent_linestyle=None, viewer=None,
            tspace_year=None, tspace_month=None, tspace_day=None,
            tspace_hour=None, xtick_label_rotation=None,
            xtick_label_align=None, ytick_label_rotation=None,
            ytick_label_align=None, legend_text_weight=None,
            legend_text_size=None, cs_uniform=None,
            master_title=None, master_title_location=None,
            master_title_fontsize=None, master_title_fontweight=None,
            dpi=None, land_color=None, ocean_color=None,
            lake_color=None,
            rotated_grid_spacing=None, rotated_deg_spacing=None,
            rotated_continents=None, rotated_grid=None,
            rotated_labels=None, rotated_grid_thickness=None,
            legend_frame=None,
            legend_frame_edge_color=None, legend_frame_face_color=None,
            degsym=None, axis_width=None, grid=None,
            grid_spacing=None,
            grid_colour=None, grid_linestyle=None, grid_thickness=None,
            tight=None, level_spacing=None):
    """
     | setvars - set plotting variables and their defaults
     |
     | file=None - output file name
     | title_fontsize=None - title fontsize, default=15
     | title_fontweight='normal' - title fontweight
     | text_fontsize='normal' - text font size, default=11
     | text_fontweight='normal' - text font weight
     | axis_label_fontsize=None - axis label fontsize, default=11
     | axis_label_fontweight='normal' - axis font weight
     | legend_text_size='11' - legend text size
     | legend_text_weight='normal' - legend text weight
     | colorbar_fontsize='11' - colorbar text size
     | colorbar_fontweight='normal' - colorbar font weight
     | legend_text_weight='normal' - legend text weight
     | master_title_fontsize=30 - master title font size
     | master_title_fontweight='normal' - master title font weight
     | continent_thickness=1.5 - default=1.5
     | continent_color='k' - default='k' (black)
     | continent_linestyle='solid' - default='k' (black)
     | viewer='display' - use ImageMagick display program
     |                    'matplotlib' to use image widget to view the picture
     | tspace_year=None - time axis spacing in years
     | tspace_month=None - time axis spacing in months
     | tspace_day=None - time axis spacing in days
     | tspace_hour=None - time axis spacing in hours
     | xtick_label_rotation=0 - rotation of xtick labels
     | xtick_label_align='center' - alignment of xtick labels
     | ytick_label_rotation=0 - rotation of ytick labels
     | ytick_label_align='right' - alignment of ytick labels

     | cs_uniform=True - make a uniform differential colour scale
     | master_title=None - master title text
     | master_title_location=[0.5,0.95] - master title location
     | dpi=None - dots per inch setting
     | land_color=None - land colour
     | ocean_color=None - ocean colour
     | lake_color=None - lake colour
     | rotated_grid_spacing=10 - rotated grid spacing in degrees
     | rotated_deg_spacing=0.75 - rotated grid spacing between graticule dots
     | rotated_deg_tkickness=1.0 - rotated grid thickness for longitude and latitude lines
     | rotated_continents=True - draw rotated continents
     | rotated_grid=True - draw rotated grid
     | rotated_labels=True - draw rotated grid labels
     | legend_frame=True - draw a frame around a lineplot legend
     | legend_frame_edge_color='k' - color for the legend frame
     | legend_frame_face_color=None - color for the legend background
     | degsym=True - add degree symbol to longitude and latitude axis labels
     | axis_width=None - width of line for the axes
     | grid=True - draw grid
     | grid_spacing=1 - grid spacing in degrees
     | grid_colour='k' - grid colour
     | grid_linestyle='--' - grid line style
     | grid_thickness=1.0 - grid thickness
     | tight=False - remove whitespace around the plot
     | level_spacing=None - default contour level spacing - takes 'linear', 'log', 'loglike', 
     |                      'outlier' and 'inspect'
     |
     | Use setvars() to reset to the defaults
     |
     |
     |
     :Returns:
      name
     |
     |
     |
    """

    vals = [file, title_fontsize, text_fontsize, axis_label_fontsize,
            continent_thickness, title_fontweight, text_fontweight,
            axis_label_fontweight, fontweight,  continent_color,
            continent_linestyle, tspace_year,
            tspace_month, tspace_day, tspace_hour, xtick_label_rotation,
            xtick_label_align, ytick_label_rotation, ytick_label_align,
            legend_text_size, legend_text_weight, cs_uniform,
            master_title, master_title_location,
            master_title_fontsize, master_title_fontweight, dpi,
            land_color, ocean_color, lake_color, rotated_grid_spacing,
            rotated_deg_spacing, rotated_continents, rotated_grid,
            rotated_grid_thickness,
            rotated_labels, colorbar_fontsize, colorbar_fontweight,
            legend_frame, legend_frame_edge_color, legend_frame_face_color,
            degsym, axis_width, grid, grid_spacing,
            grid_colour, grid_linestyle, grid_thickness, tight, level_spacing]
    if all(val is None for val in vals):
        plotvars.file = None
        plotvars.title_fontsize = 15
        plotvars.text_fontsize = 11
        plotvars.colorbar_fontsize = 11
        plotvars.axis_label_fontsize = 11
        plotvars.title_fontweight = 'normal'
        plotvars.text_fontweight = 'normal'
        plotvars.colorbar_fontweight = 'normal'
        plotvars.axis_label_fontweight = 'normal'
        plotvars.fontweight = 'normal'
        plotvars.continent_thickness = None
        plotvars.continent_color = None
        plotvars.continent_linestyle = None
        plotvars.tspace_year = None
        plotvars.tspace_month = None
        plotvars.tspace_day = None
        plotvars.tspace_hour = None
        plotvars.xtick_label_rotation = 0
        plotvars.xtick_label_align = 'center'
        plotvars.ytick_label_rotation = 0
        plotvars.ytick_label_align = 'right'
        plotvars.legend_text_size = 11
        plotvars.legend_text_weight = 'normal'
        plotvars.cs_uniform = True
        plotvars.viewer = plotvars.global_viewer
        plotvars.master_title = None
        plotvars.master_title_location = [0.5, 0.95]
        plotvars.master_title_fontsize = 30
        plotvars.master_title_fontweight = 'normal'
        plotvars.dpi = None
        plotvars.land_color = None
        plotvars.ocean_color = None
        plotvars.lake_color = None
        plotvars.rotated_grid_spacing = 10
        plotvars.rotated_deg_spacing = 0.75
        plotvars.rotated_grid_thickness = 1.0
        plotvars.rotated_continents = True
        plotvars.rotated_grid = True
        plotvars.rotated_labels = True
        plotvars.legend_frame = True
        plotvars.legend_frame_edge_color = 'k'
        plotvars.legend_frame_face_color = None
        plotvars.degsym = False
        plotvars.axis_width = None
        plotvars.grid = True
        plotvars.grid_spacing = 1
        plotvars.grid_colour = 'k'
        plotvars.grid_linestyle = '--'
        plotvars.grid_thickness = 1.0
        matplotlib.pyplot.ioff()
        plotvars.tight = False
        plotvars.level_spacing = None

    if file is not None:
        plotvars.file = file
    if title_fontsize is not None:
        plotvars.title_fontsize = title_fontsize
    if axis_label_fontsize is not None:
        plotvars.axis_label_fontsize = axis_label_fontsize
    if continent_thickness is not None:
        plotvars.continent_thickness = continent_thickness
    if continent_color is not None:
        plotvars.continent_color = continent_color
    if continent_linestyle is not None:
        plotvars.continent_linestyle = continent_linestyle
    if text_fontsize is not None:
        plotvars.text_fontsize = colorbar_fontsize
    if colorbar_fontsize is not None:
        plotvars.colorbar_fontsize = colorbar_fontsize
    if text_fontweight is not None:
        plotvars.text_fontweight = text_fontweight
    if axis_label_fontweight is not None:
        plotvars.axis_label_fontweight = axis_label_fontweight
    if colorbar_fontweight is not None:
        plotvars.colorbar_fontweight = colorbar_fontweight
    if title_fontweight is not None:
        plotvars.title_fontweight = title_fontweight
    if viewer is not None:
        plotvars.viewer = viewer
    if tspace_year is not None:
        plotvars.tspace_year = tspace_year
    if tspace_month is not None:
        plotvars.tspace_month = tspace_month
    if tspace_day is not None:
        plotvars.tspace_day = tspace_day
    if tspace_hour is not None:
        plotvars.tspace_hour = tspace_hour
    if xtick_label_rotation is not None:
        plotvars.xtick_label_rotation = xtick_label_rotation
    if xtick_label_align is not None:
        plotvars.xtick_label_align = xtick_label_align
    if ytick_label_rotation is not None:
        plotvars.ytick_label_rotation = ytick_label_rotation
    if ytick_label_align is not None:
        plotvars.ytick_label_align = ytick_label_align
    if legend_text_size is not None:
        plotvars.legend_text_size = legend_text_size
    if legend_text_weight is not None:
        plotvars.legend_text_weight = legend_text_weight
    if cs_uniform is not None:
        plotvars.cs_uniform = cs_uniform
    if master_title is not None:
        plotvars.master_title = master_title
    if master_title_location is not None:
        plotvars.master_title_location = master_title_location
    if master_title_fontsize is not None:
        plotvars.master_title_fontsize = master_title_fontsize
    if master_title_fontweight is not None:
        plotvars.master_title_fontweight = master_title_fontweight
    if dpi is not None:
        plotvars.dpi = dpi
    if land_color is not None:
        plotvars.land_color = land_color
    if ocean_color is not None:
        plotvars.ocean_color = ocean_color
    if lake_color is not None:
        plotvars.lake_color = lake_color
    if rotated_grid_spacing is not None:
        plotvars.rotated_grid_spacing = rotated_grid_spacing
    if rotated_deg_spacing is not None:
        plotvars.rotated_deg_spacing = rotated_deg_spacing
    if rotated_grid_thickness is not None:
        plotvars.rotated_grid_thickness = rotated_grid_thickness
    if rotated_continents is not None:
        plotvars.rotated_continents = rotated_continents
    if rotated_grid is not None:
        plotvars.rotated_grid = rotated_grid
    if rotated_labels is not None:
        plotvars.rotated_labels = rotated_labels
    if legend_frame is not None:
        plotvars.legend_frame = legend_frame
    if legend_frame_edge_color is not None:
        plotvars.legend_frame_edge_color = legend_frame_edge_color
    if legend_frame_face_color is not None:
        plotvars.legend_frame_face_color = legend_frame_face_color
    if degsym is not None:
        plotvars.degsym = degsym
    if axis_width is not None:
        plotvars.axis_width = axis_width
    if grid is not None:
        plotvars.grid = grid
    if grid_spacing is not None:
        plotvars.grid_spacing = grid_spacing
    if grid_colour is not None:
        plotvars.grid_colour = grid_colour
    if grid_linestyle is not None:
        plotvars.grid_linestyle = grid_linestyle
    if grid_thickness is not None:
        plotvars.grid_thickness = grid_thickness
    if tight is not None:
        plotvars.tight = tight
    if level_spacing is not None:
        plotvars.level_spacing = level_spacing

def vloc(xvec=None, yvec=None, lons=None, lats=None):
    """
     | vloc is used to locate the positions of a set of points in a vector
     |
     |
     |
     | xvec=None - data longitudes
     | yvec=None - data latitudes
     | lons=None - required longitude positions
     | lats=None - required latitude positions

     :Returns:
      locations of user points in the longitude and latitude points
     |
     |
     |
     |
     |
     |
     |
    """

    # Check input parameters
    if any(val is None for val in [xvec, yvec, lons, lats]):
        errstr = '\nvloc error\n'
        errstr += 'xvec, yvec, lons, lats all need to be passed to vloc to\n'
        errstr += 'generate a set of location points\n'
        raise Warning(errstr)

    xarr = np.zeros(np.size(lons))
    yarr = np.zeros(np.size(lats))

    # Convert longitudes to -180 to 180.
    for i in np.arange(np.size(xvec)):
        xvec[i] = ((xvec[i] + 180) % 360) - 180
    for i in np.arange(np.size(lons)):
        lons[i] = ((lons[i] + 180) % 360) - 180

    # Centre around 180 degrees longitude if needed.
    if (max(xvec) > 150):
        for i in np.arange(np.size(xvec)):
            xvec[i] = (xvec[i] + 360.0) % 360.0
        pts = np.where(xvec < 0.0)
        xvec[pts] = xvec[pts] + 360.0
        for i in np.arange(np.size(lons)):
            lons[i] = (lons[i] + 360.0) % 360.0
        pts = np.where(lons < 0.0)
        lons[pts] = lons[pts] + 360.0

    # Find position in array
    for i in np.arange(np.size(lons)):

        if ((lons[i] < min(xvec)) or (lons[i] > max(xvec))):
            xpt = -1
        else:
            xpts = np.where(lons[i] >= xvec)
            xpt = np.nanmax(xpts)

        if ((lats[i] < min(yvec)) or (lats[i] > max(yvec))):
            ypt = -1
        else:
            ypts = np.where(lats[i] >= yvec)
            ypt = np.nanmax(ypts)

        if (xpt >= 0):
            xarr[i] = xpt + (lons[i] - xvec[xpt]) / (xvec[xpt + 1] - xvec[xpt])
        else:
            xarr[i] = None

        if (ypt >= 0) and ypt <= np.size(yvec) - 2:
            yarr[i] = ypt + (lats[i] - yvec[ypt]) / (yvec[ypt + 1] - yvec[ypt])
        else:
            yarr[i] = None

    return (xarr, yarr)


def rgaxes(xpole=None, ypole=None, xvec=None, yvec=None,
           xticks=None, xticklabels=None, yticks=None, yticklabels=None,
           axes=None, xaxis=None, yaxis=None, xlabel=None, ylabel=None):
    """
     | rgaxes - label rotated grid plots
     |
     | xpole=None - location of xpole in degrees
     | ypole=None - location of ypole in degrees
     | xvec=None - location of x grid points
     | yvec=None - location of y grid points
     |
     | axes=True - plot x and y axes
     | xaxis=True - plot xaxis
     | yaxis=True - plot y axis
     | xticks=None - xtick positions
     | xticklabels=None - xtick labels
     | yticks=None - y tick positions
     | yticklabels=None - ytick labels
     | xlabel=None - label for x axis
     | ylabel=None - label for y axis
     |
     :Returns:
      name
     |
     |
     |
     |
     |
     |
    """

    spacing = plotvars.rotated_grid_spacing
    degspacing = plotvars.rotated_deg_spacing
    continents = plotvars.rotated_continents
    grid = plotvars.rotated_grid
    labels = plotvars.rotated_labels
    grid_thickness = plotvars.rotated_grid_thickness

    # Invert y array if going from north to south
    # Otherwise this gives nans for all output
    yvec_orig = yvec
    if (yvec[0] > yvec[np.size(yvec) - 1]):
        yvec = yvec[::-1]

    gset(xmin=0, xmax=np.size(xvec) - 1,
         ymin=0, ymax=np.size(yvec) - 1, user_gset=0)

    # Set continent thickness and color if not already set
    if plotvars.continent_thickness is None:
        continent_thickness = 1.5
    if plotvars.continent_color is None:
        continent_color = 'k'

    # Draw continents
    if continents:

        import cartopy.io.shapereader as shpreader
        import shapefile
        shpfilename = shpreader.natural_earth(resolution=plotvars.resolution,
                                              category='physical',
                                              name='coastline')
        reader = shapefile.Reader(shpfilename)
        shapes = [s.points for s in reader.shapes()]
        for shape in shapes:
            lons, lats = list(zip(*shape))
            lons = np.array(lons)
            lats = np.array(lats)

            rotated_transform = ccrs.RotatedPole(pole_latitude=ypole, pole_longitude=xpole)
            points = rotated_transform.transform_points(ccrs.PlateCarree(), lons, lats)
            xout = np.array(points)[:, 0]
            yout = np.array(points)[:, 1]

            xpts, ypts = vloc(lons=xout, lats=yout, xvec=xvec, yvec=yvec)
            plotvars.plot.plot(xpts, ypts, linewidth=continent_thickness,
                               color=continent_color)

    if xticks is None:
        lons = -180 + np.arange(360 / spacing + 1) * spacing
    else:
        lons = xticks
    if yticks is None:
        lats = -90 + np.arange(180 / spacing + 1) * spacing
    else:
        lats = yticks

    # Work out how far from plot to plot the longitude and latitude labels
    xlim = plotvars.plot.get_xlim()
    spacing_x = (xlim[1] - xlim[0]) / 20
    ylim = plotvars.plot.get_ylim()
    spacing_y = (ylim[1] - ylim[0]) / 20
    spacing = min(spacing_x, spacing_y)

    # Draw lines along a longitude
    if axes:
        if xaxis:
            for val in np.arange(np.size(lons)):
                ipts = 179.0 / degspacing
                lona = np.zeros(int(ipts)) + lons[val]
                lata = -90 + np.arange(ipts - 1) * degspacing

                rotated_transform = ccrs.RotatedPole(pole_latitude=ypole, pole_longitude=xpole)
                points = rotated_transform.transform_points(ccrs.PlateCarree(), lona, lata)
                xout = np.array(points)[:, 0]
                yout = np.array(points)[:, 1]

                xpts, ypts = vloc(lons=xout, lats=yout, xvec=xvec, yvec=yvec)
                if grid:
                    plotvars.plot.plot(xpts, ypts, ':', linewidth=grid_thickness,
                                       color='k')

                if labels:
                    # Make a label unless the axis is all Nans
                    if (np.size(ypts[5:]) > np.sum(np.isnan(ypts[5:]))):
                        ymin = np.nanmin(ypts[5:])
                        loc = np.where(ypts == ymin)[0]
                        if np.size(loc) > 1:
                            loc = loc[1]

                        if loc > 0:
                            if np.isfinite(xpts[loc]):
                                line = matplotlib.lines.Line2D(
                                       [xpts[loc], xpts[loc]], [0, -spacing/2], color='k')
                                plotvars.plot.add_line(line)
                                line.set_clip_on(False)
                                fw = plotvars.text_fontweight
                                if xticklabels is None:
                                    xticklabel = mapaxis(lons[val], lons[val], type=1)[1][0]
                                else:
                                    xticklabel = xticks[val]

                                plotvars.plot.text(xpts[loc], -spacing,
                                                   xticklabel,
                                                   horizontalalignment='center',
                                                   verticalalignment='top',
                                                   fontsize=plotvars.text_fontsize,
                                                   fontweight=fw)

    # Draw lines along a latitude
    if axes:
        if yaxis:
            for val in np.arange(np.size(lats)):
                ipts = 359.0 / degspacing
                lata = np.zeros(int(ipts)) + lats[val]
                lona = -180.0 + np.arange(ipts - 1) * degspacing

                rotated_transform = ccrs.RotatedPole(pole_latitude=ypole, pole_longitude=xpole)
                points = rotated_transform.transform_points(ccrs.PlateCarree(), lona, lata)
                xout = np.array(points)[:, 0]
                yout = np.array(points)[:, 1]
                xpts, ypts = vloc(lons=xout, lats=yout, xvec=xvec, yvec=yvec)

                if grid:
                    plotvars.plot.plot(xpts, ypts, ':', linewidth=grid_thickness,
                                       color='k')

                if labels:
                    # Make a label unless the axis is all Nans
                    if (np.size(xpts[5:]) > np.sum(np.isnan(xpts[5:]))):
                        xmin = np.nanmin(xpts[5:])
                        loc = np.where(xpts == xmin)[0]
                        if np.size(loc) == 1:
                            if loc > 0:
                                if np.isfinite(ypts[loc]):
                                    line = matplotlib.lines.Line2D(
                                           [0, -spacing/2], [ypts[loc], ypts[loc]], color='k')
                                    plotvars.plot.add_line(line)
                                    line.set_clip_on(False)
                                    fw = plotvars.text_fontweight
                                    if yticklabels is None:
                                        yticklabel = mapaxis(lats[val], lats[val], type=2)[1][0]
                                    else:
                                        yticklabel = yticks[val]

                                    plotvars.plot.text(-spacing, ypts[loc],
                                                       yticklabel,
                                                       horizontalalignment='right',
                                                       verticalalignment='center',
                                                       fontsize=plotvars.text_fontsize,
                                                       fontweight=fw)

    # Reset yvec
    yvec = yvec_orig


def lineplot(f=None, x=None, y=None, fill=True, lines=True, line_labels=True,
             title=None, ptype=0, linestyle='-', linewidth=1.0, color=None,
             xlog=False, ylog=False, verbose=None, swap_xy=False,
             marker=None, markersize=5.0, markeredgecolor='k',
             markeredgewidth=0.5, label=None,
             legend_location='upper right', xunits=None, yunits=None,
             xlabel=None, ylabel=None, xticks=None, yticks=None,
             xticklabels=None, yticklabels=None, xname=None, yname=None,
             axes=True, xaxis=True, yaxis=True, titles=False, zorder=None):
    """
    | lineplot is the interface to line plotting in cf-plot.
    | The minimum use is lineplot(f) where f is a CF field.
    | If x and y are passed then an appropriate plot is made allowing
    | x vs data and y vs data plots.

    | When making a labelled line plot:
    | always have a label for each line
    | always put the legend location as an option to the last call to lineplot
    |
    | f - CF data used to make a line plot
    | x - x locations of data in y
    | y - y locations of data in x
    | linestyle='-' - line style
    | color=None - line color.  Defaults to Matplotlib colour scheme unless specified
    | linewidth=1.0 - line width
    | marker=None - marker for points along the line
    | markersize=5.0 - size of the marker
    | markeredgecolor = 'k' - colour of edge around the marker
    | markeredgewidth = 0.5 - width of edge around the marker
    | xlog=False - log x-axis
    | ylog=False - log y-axis
    | label=None - line label - label for line
    | legend_location='upper right' - default location of legend
    |                 Other options are {'best': 0, 'center': 10, 'center left': 6,
    |                                    'center right': 7, 'lower center': 8,
    |                                    'lower left': 3, 'lower right': 4, 'right': 5,
    |                                    'upper center': 9, 'upper left': 2, 'upper right': 1}
    | titles=False - set to True to have a dimensions title
    | verbose=None - change to 1 to get a verbose listing of what lineplot
    |                is doing
    | zorder=None - plotting order
    |
    | The following parameters override any CF data defaults:
    | title=None - plot title
    | xunits=None - x units
    | yunits=None - y units
    | xlabel=None - x name
    | ylabel=None - y name
    | xname=None - depreciated keyword
    | yname=None - depreciated keyword
    | xticks=None - x ticks
    | xticklabels=None - x tick labels
    | yticks=None - y ticks
    | yticklabels - y tick labels
    | axes=True - plot x and y axes
    | xaxis=True - plot xaxis
    | yaxis=True - plot y axis
    |
    |
    | When making a multiple line plot:
    | a) set the axis limits with gset before plotting the lines
    | b) the last call to lineplot is the one that any of the above
    |    axis overrides should be placed in.
    |
    |
    """
    if verbose:
        print('lineplot - making a line plot')

    # Catch depreciated keywords
    if xname is not None or yname is not None:
        print('\nlineplot error')
        print('xname and yname are now depreciated keywords')
        print('Please use xlabel and ylabel\n')
        return

    ##################
    # Open a new plot is necessary
    ##################
    if plotvars.user_plot == 0:
        gopen(user_plot=0)

    # Call gpos(1) if not already called
    if plotvars.rows > 1 or plotvars.columns > 1:
        if plotvars.gpos_called is False:
            gpos(1)

    ##################
    # Extract required data
    # If a cf-python field
    ##################
    cf_field = False
    if f is not None:
        if isinstance(f, cf.Field):
            cf_field = True

            # Check data is 1D
            ndims = np.squeeze(f.data).ndim
            if ndims != 1:
                errstr = "\n\ncfp.lineplot error need a 1 dimensonal field to make a line\n"
                errstr += "received " + str(np.squeeze(f.data).ndim) + " dimensions\n\n"
                raise TypeError(errstr)

            if x is not None:
                if isinstance(x, cf.Field):
                    errstr = "\n\ncfp.lineplot error - two or more cf-fields passed for plotting.\n"
                    errstr += "To plot two cf-fields open a graphics plot with cfp.gopen(), \n"
                    errstr += "plot the two fields separately with cfp.lineplot and then close\n"
                    errstr += "the graphics plot with cfp.gclose()\n\n"
                    raise TypeError(errstr)

        elif isinstance(f, cf.FieldList):
            errstr = "\n\ncfp.lineplot - cannot plot a field list\n\n"
            raise TypeError(errstr)



    plot_xlabel = ''
    plot_ylabel = ''
    xlabel_units = ''
    ylabel_units = ''

    if cf_field:
        # Extract data
        if verbose:
            print('lineplot - CF field, extracting data')

        has_count = 0
        for mydim in list(f.dimension_coordinates()):
            if np.size(np.squeeze(f.construct(mydim).array)) > 1:
                has_count = has_count + 1
                x = np.squeeze(f.construct(mydim).array)

                # x label
                xlabel_units = str(getattr(f.construct(mydim), 'Units', ''))
                plot_xlabel = cf_var_name(field=f, dim=mydim) + ' ('
                plot_xlabel += xlabel_units + ')'
                y = np.squeeze(f.array)

                # y label
                if hasattr(f, 'id'):
                    plot_ylabel = f.id
                nc = f.nc_get_variable(False)
                if nc:
                    plot_ylabel = f.nc_get_variable()
                if hasattr(f, 'short_name'):
                    plot_ylabel = f.short_name
                if hasattr(f, 'long_name'):
                    plot_ylabel = f.long_name
                if hasattr(f, 'standard_name'):
                    plot_ylabel = f.standard_name

                if hasattr(f, 'Units'):
                    ylabel_units = str(f.Units)
                else:
                    ylabel_units = ''
                plot_ylabel += ' (' + ylabel_units + ')'

        if has_count != 1:
            errstr = '\n lineplot error - passed field is not suitable '
            errstr += 'for plotting as a line\n'
            for mydim in list(f.dimension_coordinates()):
                sn = getattr(f.construct(mydim), 'standard_name', False)
                ln = getattr(f.construct(mydim), 'long_name', False)
                if sn:
                    errstr = errstr + \
                        str(mydim) + ',' + str(sn) + ',' + \
                        str(f.construct(mydim).size) + '\n'
                else:
                    if ln:
                        errstr = errstr + \
                            str(mydim) + ',' + str(ln) + ',' + \
                            str(f.construct(mydim).size) + '\n'
            raise Warning(errstr)
    else:
        if verbose:
            print('lineplot - not a CF field, using passed data')
        errstr = ''
        if x is None or y is None:
            errstr = 'lineplot error- must define both x and y'
        if f is not None:
            errstr += 'lineplot error- must define just x and y to make '
            errstr += 'a lineplot'
        if errstr != '':
            raise Warning('\n' + errstr + '\n')

    # Z on y-axis
    ztype = None
    if xlabel_units in ['mb', 'mbar', 'millibar', 'decibar',
                        'atmosphere', 'atm', 'pascal', 'Pa', 'hPa']:
        ztype = 1
    if xlabel_units in ['meter', 'metre', 'm', 'kilometer', 'kilometre', 'km']:
        ztype = 2
        
        
    myz = find_z(f)
    if cf_field and f.has_construct(myz):
        z_coord = f.construct(myz)
        if len(z_coord.array) > 1:
            zlabel = ''
            if hasattr(z_coord, 'long_name'):
                zlabel = z_coord.long_name
            if hasattr(z_coord, 'standard_name'):
                zlabel = z_coord.standard_name
            if zlabel == 'atmosphere_hybrid_height_coordinate':
                ztype = 2

    if ztype is not None:
        x, y = y, x
        plot_xlabel, plot_ylabel = plot_ylabel, plot_xlabel

    # Set data values
    if verbose:
        print('lineplot - setting data values')
    xpts = np.squeeze(x)
    ypts = np.squeeze(y)
    minx = np.min(x)
    miny = np.min(y)
    maxx = np.max(x)
    maxy = np.max(y)

    # Use accumulated plot limits if making a multiple line plot
    if plotvars.graph_xmin is None:
        plotvars.graph_xmin = minx
    else:
        if minx < plotvars.graph_xmin:
            plotvars.graph_xmin = minx

    if plotvars.graph_xmax is None:
        plotvars.graph_xmax = maxx
    else:
        if maxx > plotvars.graph_xmax:
            plotvars.graph_xmax = maxx

    if plotvars.graph_ymin is None:
        plotvars.graph_ymin = miny
    else:
        if miny < plotvars.graph_ymin:
            plotvars.graph_ymin = miny

    if plotvars.graph_ymax is None:
        plotvars.graph_ymax = maxy
    else:
        if maxy > plotvars.graph_ymax:
            plotvars.graph_ymax = maxy

    # Reset plot limits based on accumulated plot limits
    minx = plotvars.graph_xmin
    maxx = plotvars.graph_xmax
    miny = plotvars.graph_ymin
    maxy = plotvars.graph_ymax

    if cf_field and f.has_construct('T'):
        taxis = f.construct('T')

    if ztype == 1:
        miny = np.max(y)
        maxy = np.min(y)

    if ztype == 2:
        if cf_field and f.has_construct('Z'):
            if f.construct('Z').positive == 'down':
                miny = np.max(y)
                maxy = np.min(y)

    # Use user set values if present
    time_xstr = False
    time_ystr = False
    if plotvars.xmin is not None:
        minx = plotvars.xmin
        miny = plotvars.ymin
        maxx = plotvars.xmax
        maxy = plotvars.ymax

        # Change from date string to a number if strings are passed
        try:
            float(minx)
        except Exception:
            time_xstr = True
        try:
            float(miny)
        except Exception:
            time_ystr = True

        if cf_field and f.has_construct('T'):
            taxis = f.construct('T')
            if time_xstr or time_ystr:
                ref_time = f.construct('T').units
                ref_calendar = f.construct('T').calendar
                time_units = cf.Units(ref_time, ref_calendar)

                if time_xstr:
                    t = cf.Data(cf.dt(minx), units=time_units)
                    minx = t.array
                    t = cf.Data(cf.dt(maxx), units=time_units)
                    maxx = t.array
                    taxis = cf.Data([cf.dt(plotvars.xmin),
                                    cf.dt(plotvars.xmax)], units=time_units)

                if time_ystr:
                    t = cf.Data(cf.dt(miny), units=time_units)
                    miny = t.array
                    t = cf.Data(cf.dt(maxy), units=time_units)
                    maxy = t.array
                    taxis = cf.Data([cf.dt(plotvars.ymin),
                                     cf.dt(plotvars.ymax)], units=time_units)

    # Set x and y labelling
    # Retrieve any user defined axis labels
    if plot_xlabel == '' and plotvars.xlabel is not None:
        plot_xlabel = plotvars.xlabel
    if plot_ylabel == '' and plotvars.ylabel is not None:
        plot_ylabel = plotvars.ylabel
    if xticks is None and plotvars.xticks is not None:
        xticks = plotvars.xticks
        if plotvars.xticklabels is not None:
            xticklabels = plotvars.xticklabels
        else:
            xticklabels = list(map(str, xticks))
    if yticks is None and plotvars.yticks is not None:
        yticks = plotvars.yticks
        if plotvars.yticklabels is not None:
            yticklabels = plotvars.yticklabels
        else:
            yticklabels = list(map(str, yticks))

    mod = False
    ymult = 0

    if xticks is None:
        if plot_xlabel[0:3].lower() == 'lon':
            xticks, xticklabels = mapaxis(minx, maxx, type=1)
        if plot_xlabel[0:3].lower() == 'lat':
            xticks, xticklabels = mapaxis(minx, maxx, type=2)
    if cf_field:
        if xticks is None:
            if f.has_construct('T'):
                if np.size(f.construct('T').array) > 1:
                    xticks, xticklabels, plot_xlabel = timeaxis(taxis)
    if xticks is None:
        xticks, ymult = gvals(dmin=minx, dmax=maxx, mod=mod)

        # Fix long floating point numbers if necessary
        fix_floats(xticks)
        xticklabels = xticks
    else:
        if xticklabels is None:
            xticklabels = []
            for val in xticks:
                xticklabels.append('{}'.format(val))

    if yticks is None:
        if abs(maxy - miny) > 1:
            if miny < maxy:
                yticks, ymult = gvals(dmin=miny, dmax=maxy, mod=mod)
            if maxy < miny:
                yticks, ymult = gvals(dmin=maxy, dmax=miny, mod=mod)

        else:
            yticks, ymult = gvals(dmin=miny, dmax=maxy, mod=mod)

            # Fix long floating point numbers if necessary
            fix_floats(yticks)

    if yticklabels is None:
        yticklabels = []

        for val in yticks:
            yticklabels.append(str(round(val, 9)))

    if xlabel is not None:
        plot_xlabel = xlabel
        if xunits is not None:
            plot_xlabel += '('+xunits+')'

    if ylabel is not None:
        plot_ylabel = ylabel
        if yunits is not None:
            plot_ylabel += '('+yunits+')'

    if swap_xy:
        if verbose:
            print('lineplot - swapping x and y')

        xpts, ypts = ypts, xpts
        minx, miny = miny, minx
        maxx, maxy = maxy, maxx
        plot_xlabel, plot_ylabel = plot_ylabel, plot_xlabel
        xticks, yticks = yticks, xticks
        xticklabels, yticklabels = yticklabels, xticklabels

    if plotvars.user_gset == 1:
        if time_xstr is False and time_ystr is False:
            minx = plotvars.xmin
            maxx = plotvars.xmax
            miny = plotvars.ymin
            maxy = plotvars.ymax

    if axes:
        if xaxis is not True:
            xticks = [100000000]
            xticklabels = xticks
            plot_xlabel = ''

        if yaxis is not True:
            yticks = [100000000]
            yticklabels = yticks
            plot_ylabel = ''

    else:
        xticks = [100000000]
        xticklabels = xticks
        yticks = [100000000]
        yticklabels = yticks
        plot_xlabel = ''
        plot_ylabel = ''



    # Generate titles if requested
    if titles: 
        title_dims = generate_titles(f)



    # Make graph
    if verbose:
        print('lineplot - making graph')

    xlabelalignment = plotvars.xtick_label_align
    ylabelalignment = plotvars.ytick_label_align

    if lines is False:
        linewidth = 0.0

    colorarg = {}
    if color is not None:
        colorarg = {'color': color}

    graph = plotvars.plot

    if plotvars.twinx:
        graph = graph.twinx()
        ylabelalignment = 'left'

    if plotvars.twiny:
        graph = graph.twiny()

    # Reset y limits if minx = maxy
    if plotvars.xmin is None:
        if miny == maxy:
            miny = miny - 1.0
            maxy = maxy + 1.0

    graph.axis([minx, maxx, miny, maxy])
    graph.tick_params(direction='out', which='both', right=True, top=True)
    graph.set_xlabel(plot_xlabel, fontsize=plotvars.axis_label_fontsize,
                     fontweight=plotvars.axis_label_fontweight)
    graph.set_ylabel(plot_ylabel, fontsize=plotvars.axis_label_fontsize,
                     fontweight=plotvars.axis_label_fontweight)

    if plotvars.xlog or xlog:
        graph.set_xscale('log')
    if plotvars.ylog or ylog:
        graph.set_yscale('log')

    if xticks is not None:
        graph.set_xticks(xticks)
        graph.set_xticklabels(xticklabels,
                              rotation=plotvars.xtick_label_rotation,
                              horizontalalignment=xlabelalignment,
                              fontsize=plotvars.axis_label_fontsize,
                              fontweight=plotvars.axis_label_fontweight)
    if yticks is not None:
        graph.set_yticks(yticks)
        graph.set_yticklabels(yticklabels,
                              rotation=plotvars.ytick_label_rotation,
                              horizontalalignment=ylabelalignment,
                              fontsize=plotvars.axis_label_fontsize,
                              fontweight=plotvars.axis_label_fontweight)

    graph.plot(xpts, ypts, **colorarg, linestyle=linestyle,
               linewidth=linewidth, marker=marker,
               markersize=markersize,
               markeredgecolor=markeredgecolor,
               markeredgewidth=markeredgewidth,
               label=label, zorder=zorder)

    # Set axis width if required
    if plotvars.axis_width is not None:
        for axis in ['top', 'bottom', 'left', 'right']:
            plotvars.plot.spines[axis].set_linewidth(plotvars.axis_width)

    # Add a legend if needed
    if label is not None:
        legend_properties = {
            'size': plotvars.legend_text_size,
            'weight': plotvars.legend_text_weight}
        graph.legend(loc=legend_location, prop=legend_properties,
                     frameon=plotvars.legend_frame,
                     edgecolor=plotvars.legend_frame_edge_color,
                     facecolor=plotvars.legend_frame_face_color)

    # Set title
    if title is not None:
        graph.set_title(title, fontsize=plotvars.title_fontsize,
                        fontweight=plotvars.title_fontweight)

    # Titles for dimensions
    if titles:
        plotvars.plot = graph
        plotvars.plot_type = 0
        dim_titles(title_dims, dims=True)


    ##################
    # Save or view plot
    ##################
    if plotvars.user_plot == 0:
        if verbose:
            print('Saving or viewing plot')
        gclose()


def regression_tests():
    """
    | Test for cf-plot regressions
    | Run through some standard levs, gvals, lon and lat labelling
    | Make all the gallery plots and use Imagemaick to display them
    | alongside a reference plot
    |
    |
    |
    |
    |
    """

    print('==================')
    print('Regression testing')
    print('==================')
    print('')

    print('------------------')
    print('Testing for levels')
    print('------------------')
    ref_answer = [-35, -30, -25, -20, -15, -10, -5, 0, 5,
                  10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65]
    compare_arrays(ref=ref_answer, levs_test=True, min=-35, max=65, step=5)

    ref_answer = [-6., -4.8, -3.6, -2.4, -1.2, 0., 1.2, 2.4, 3.6, 4.8, 6.]
    compare_arrays(ref=ref_answer, levs_test=True, min=-6, max=6, step=1.2)

    ref_answer = [50000, 51000, 52000, 53000, 54000, 55000, 56000, 57000,
                  58000, 59000, 60000]
    compare_arrays(ref=ref_answer, levs_test=True, min=50000, max=60000, step=1000)

    ref_answer = [-7000, -6500, -6000, -5500, -5000, -4500, -4000, -3500,
                  -3000, -2500, -2000, -1500, -1000, -500]
    compare_arrays(
        ref=ref_answer,
        levs_test=True,
        min=-7000,
        max=-300,
        step=500)

    print('')
    print('-----------------')
    print('Testing for gvals')
    print('-----------------')
    ref_answer = [281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293]
    compare_arrays(ref=ref_answer, min=280.50619506835938,
                   max=293.48431396484375, mult=0, gvals_test=True)

    ref_answer = [0.356,  0.385,  0.414,  0.443,  0.472,  0.501,  0.53,  0.559,
                  0.588,  0.617,  0.646,  0.675]
    compare_arrays(ref=ref_answer, min=0.356, max=0.675, mult=0,
                   gvals_test=True)

    ref_answer = [-45, -40, -35, -30, -25, -20, -15, -10, -5, 0, 5, 10, 15,
                  20, 25, 30, 35, 40, 45, 50]
    compare_arrays(ref=ref_answer, min=-49.510975, max=53.206604, mult=0,
                   gvals_test=True)

    ref_answer = [47000, 48000, 49000, 50000, 51000, 52000, 53000, 54000,
                  55000, 56000, 57000, 58000, 59000, 60000, 61000, 62000,
                  63000, 64000]
    compare_arrays(ref=ref_answer, min=46956, max=64538, mult=0,
                   gvals_test=True)

    ref_answer = [-1., -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0., 0.1]
    compare_arrays(ref=ref_answer, min=-1.0, max=0.1, mult=0,
                   gvals_test=True)

    print('')
    print('----------------------------------------')
    print('Testing for longitude/latitude labelling')
    print('----------------------------------------')
    ref_answer = ([-180, -120, -60, 0, 60, 120, 180],
                  ['180', '120W', '60W', '0', '60E', '120E', '180'])
    compare_arrays(ref=ref_answer, min=-180, max=180, type=1,
                   mapaxis_test=True)

    ref_answer = ([150, 180, 210, 240, 270],
                  ['150E', '180', '150W', '120W', '90W'])
    compare_arrays(ref=ref_answer, min=135, max=280, type=1,
                   mapaxis_test=True)

    ref_answer = ([0, 10, 20, 30, 40, 50, 60, 70, 80, 90], ['0', '10E', '20E',
                  '30E', '40E', '50E', '60E', '70E', '80E', '90E'])
    compare_arrays(ref=ref_answer, min=0, max=90, type=1, mapaxis_test=True)

    ref_answer = ([-90, -60, -30, 0, 30, 60, 90],
                  ['90S', '60S', '30S', '0', '30N', '60N', '90N'])
    compare_arrays(ref=ref_answer, min=-90, max=90, type=2, mapaxis_test=True)

    ref_answer = ([0, 5, 10, 15, 20, 25, 30],
                  ['0', '5N', '10N', '15N', '20N', '25N', '30N'])
    compare_arrays(ref=ref_answer, min=0, max=30, type=2, mapaxis_test=True)

    print('')
    print('-----------------')
    print('Testing for plots')
    print('-----------------')

    # Run through gallery examples and compare to reference plots

    # example1
    reset()
    setvars(file='fig1.png')
    f = cf.read('/opt/graphics/cfplot_data/tas_A1.nc')[0]
    con(f.subspace(time=15))
    compare_images(1)

    # example2
    reset()
    setvars(file='fig2.png')
    f = cf.read('/opt/graphics/cfplot_data/tas_A1.nc')[0]
    con(f.subspace(time=15), blockfill=True, lines=False)
    compare_images(2)

    # example3
    reset()
    setvars(file='fig3.png')
    f = cf.read('/opt/graphics/cfplot_data/tas_A1.nc')[0]
    mapset(lonmin=-15, lonmax=3, latmin=48, latmax=60)
    levs(min=265, max=285, step=1)
    con(f.subspace(time=15))
    compare_images(3)

    # example4
    reset()
    setvars(file='fig4.png')
    f = cf.read('/opt/graphics/cfplot_data/ggap.nc')[1]
    mapset(proj='npstere')
    con(f.subspace(pressure=500))
    compare_images(4)

    # example5
    reset()
    setvars(file='fig5.png')
    f = cf.read('/opt/graphics/cfplot_data/ggap.nc')[1]
    mapset(proj='spstere', boundinglat=-30, lon_0=180)
    con(f.subspace(pressure=500))
    compare_images(5)

    # example6
    reset()
    setvars(file='fig6.png')
    f = cf.read('/opt/graphics/cfplot_data/ggap.nc')[3]
    con(f.subspace(longitude=0))
    compare_images(6)

    # example7
    reset()
    setvars(file='fig7.png')
    f = cf.read('/opt/graphics/cfplot_data/ggap.nc')[1]
    con(f.collapse('mean', 'longitude'))
    compare_images(7)

    # example8
    reset()
    setvars(file='fig8.png')
    f = cf.read('/opt/graphics/cfplot_data/ggap.nc')[1]
    con(f.collapse('mean', 'longitude'), ylog=1)
    compare_images(8)

    # example9
    reset()
    setvars(file='fig9.png')
    f = cf.read('/opt/graphics/cfplot_data/ggap.nc')[0]
    con(f.collapse('mean', 'latitude'))
    compare_images(9)

    # example10
    reset()
    setvars(file='fig10.png')
    f = cf.read('/opt/graphics/cfplot_data/tas_A1.nc')[0]
    cscale('plasma')
    con(f.subspace(longitude=0), lines=0)
    compare_images(10)

    # example11
    reset()
    setvars(file='fig11.png')
    f = cf.read('/opt/graphics/cfplot_data/tas_A1.nc')[0]
    gset(-30, 30, '1960-1-1', '1980-1-1')
    levs(min=280, max=305, step=1)
    cscale('plasma')
    con(f.subspace(longitude=0), lines=0)
    compare_images(11)

    # example12
    reset()
    setvars(file='fig12.png')
    f = cf.read('/opt/graphics/cfplot_data/tas_A1.nc')[0]
    cscale('plasma')
    con(f.subspace(latitude=0), lines=0)
    compare_images(12)

    # example13
    reset()
    setvars(file='fig13.png')
    f = cf.read('/opt/graphics/cfplot_data/ggap.nc')
    u = f[1].subspace(pressure=500)
    v = f[3].subspace(pressure=500)
    vect(u=u, v=v, key_length=10, scale=100, stride=5)
    compare_images(13)

    # example14
    reset()
    setvars(file='fig14.png')
    f = cf.read('/opt/graphics/cfplot_data/ggap.nc')
    u = f[1].subspace(pressure=500)
    v = f[3].subspace(pressure=500)
    t = f[0].subspace(pressure=500)

    gopen()
    mapset(lonmin=10, lonmax=120, latmin=-30, latmax=30)
    levs(min=254, max=270, step=1)
    con(t)
    vect(u=u, v=v, key_length=10, scale=50, stride=2)
    gclose()
    compare_images(14)

    # example15
    reset()
    setvars(file='fig15.png')
    u = cf.read('/opt/graphics/cfplot_data/ggap.nc')[1]
    v = cf.read('/opt/graphics/cfplot_data/ggap.nc')[3]
    u = u.subspace(Z=500)
    v = v.subspace(Z=500)

    mapset(proj='npstere')
    vect(u=u, v=v, key_length=10, scale=100, pts=40,
         title='Polar plot with regular point distribution')
    compare_images(15)

    # example16
    reset()
    setvars(file='fig16.png')
    c = cf.read('/opt/graphics/cfplot_data/vaAMIPlcd_DJF.nc')[0]
    c = c.subspace(Y=cf.wi(-60, 60))
    c = c.subspace(X=cf.wi(80, 160))
    c = c.collapse('T: mean X: mean')

    g = cf.read('/opt/graphics/cfplot_data/wapAMIPlcd_DJF.nc')[0]
    g = g.subspace(Y=cf.wi(-60, 60))
    g = g.subspace(X=cf.wi(80, 160))
    g = g.collapse('T: mean X: mean')

    vect(u=c, v=-g, key_length=[5, 0.05],
         scale=[20, 0.2], title='DJF', key_location=[0.95, -0.05])
    compare_images(16)

    # example17
    reset()
    setvars(file='fig17.png')
    f = cf.read('/opt/graphics/cfplot_data/tas_A1.nc')[0]
    g = f.subspace(time=15)
    gopen()
    cscale('magma')
    con(g)
    stipple(f=g, min=220, max=260, size=100, color='#00ff00')
    stipple(f=g, min=300, max=330, size=50, color='#0000ff', marker='s')
    gclose()
    compare_images(17)

    # example18
    reset()
    setvars(file='fig18.png')
    f = cf.read('/opt/graphics/cfplot_data/tas_A1.nc')[0]
    g = f.subspace(time=15)
    gopen()
    cscale('magma')
    mapset(proj='npstere')
    con(g)
    stipple(f=g, min=265, max=295, size=100, color='#00ff00')
    gclose()
    compare_images(18)

    # example19
    reset()
    setvars(file='fig19.png')
    f = cf.read('/opt/graphics/cfplot_data/ggap.nc')[1]
    gopen(rows=2, columns=2, bottom=0.2)
    gpos(1)
    con(f.subspace(pressure=500), colorbar=None)
    gpos(2)
    mapset(proj='moll')
    con(f.subspace(pressure=500), colorbar=None)
    gpos(3)
    mapset(proj='npstere', boundinglat=30, lon_0=180)
    con(f.subspace(pressure=500), colorbar=None)
    gpos(4)
    mapset(proj='spstere', boundinglat=-30, lon_0=180)
    con(f.subspace(pressure=500), colorbar_position=[
        0.1, 0.1, 0.8, 0.02], colorbar_orientation='horizontal')
    gclose()
    compare_images(19)

    # example20
    reset()
    setvars(file='fig20.png')
    f = cf.read('/opt/graphics/cfplot_data/Geostropic_Adjustment.nc')[0]
    con(f.subspace[9])
    compare_images(20)

    # example21
    reset()
    setvars(file='fig21.png')
    f = cf.read('/opt/graphics/cfplot_data/Geostropic_Adjustment.nc')[0]
    con(f.subspace[9], title='test data',
        xticks=np.arange(5) * 100000 + 100000,
        yticks=np.arange(7) * 2000 + 2000,
        xlabel='x-axis', ylabel='z-axis')
    compare_images(21)

    # example22
    reset()
    setvars(file='fig22.png')
    f = cf.read_field('/opt/graphics/cfplot_data/rgp.nc')
    cscale('gray')
    con(f)
    compare_images(22)

    # example23
    reset()
    setvars(file='fig23.png')
    f = cf.read_field('/opt/graphics/cfplot_data/rgp.nc')
    data = f.array
    xvec = f.construct('dim1').array
    yvec = f.construct('dim0').array
    xpole = 160
    ypole = 30

    gopen()
    cscale('plasma')
    xpts = np.arange(np.size(xvec))
    ypts = np.arange(np.size(yvec))
    gset(xmin=0, xmax=np.size(xvec) - 1, ymin=0, ymax=np.size(yvec) - 1)
    levs(min=980, max=1035, step=2.5)
    con(data, xpts, ypts[::-1])
    rgaxes(xpole=xpole, ypole=ypole, xvec=xvec, yvec=yvec)
    gclose()
    compare_images(23)

    # example24
    reset()
    setvars(file='fig24.png')
    from matplotlib.mlab import griddata

    # Arrays for data
    lons = []
    lats = []
    pressure = []
    temp = []

    # Read data
    f = open('/opt/graphics/cfplot_data/synop_data.txt')
    lines = f.readlines()
    for line in lines:
        mysplit = line.split()
        lons = np.append(lons, float(mysplit[1]))
        lats = np.append(lats, float(mysplit[2]))
        pressure = np.append(pressure, float(mysplit[3]))
        temp = np.append(temp, float(mysplit[4]))

    # Linearly interpolate data to a regular grid
    lons_new = np.arange(140) * 0.1 - 11.0
    lats_new = np.arange(140) * 0.1 + 49.0
    temp_new = griddata(lons, lats, temp, lons_new, lats_new, interp='linear')

    cscale('parula')
    con(x=lons_new, y=lats_new, f=temp_new, ptype=1)
    compare_images(24)

    # example25
    reset()
    setvars(file='fig25.png')
    gopen()
    con(x=lons_new, y=lats_new, f=temp_new, ptype=1)
    for i in np.arange(len(lines)):
        plotvars.plot.text(float(lons[i]), float(lats[i]), str(temp[i]),
                           horizontalalignment='center',
                           verticalalignment='center')

    gclose()
    compare_images(25)

    # example26
    reset()
    setvars(file='fig26.png')
    from netCDF4 import Dataset as ncfile
    from matplotlib.mlab import griddata

    # Get an Orca grid and flatten the arrays
    nc = ncfile('/opt/graphics/cfplot_data/orca2.nc')
    lons = np.array(nc.variables['longitude'])
    lats = np.array(nc.variables['latitude'])
    temp = np.array(nc.variables['sst'])
    lons = lons.flatten()
    lats = lats.flatten()
    temp = temp.flatten()

    # Add wrap around at both longitude limits
    pts = np.squeeze(np.where(lons < -150))
    lons = np.append(lons, lons[pts] + 360)
    lats = np.append(lats, lats[pts])
    temp = np.append(temp, temp[pts])

    pts = np.squeeze(np.where(lons > 150))
    lons = np.append(lons, lons[pts] - 360)
    lats = np.append(lats, lats[pts])
    temp = np.append(temp, temp[pts])

    lons_new = np.arange(181 * 8) * 0.25 - 180.0
    lats_new = np.arange(91 * 8) * 0.25 - 90.0
    temp_new = griddata(lons, lats, temp, lons_new, lats_new, interp='linear')

    con(x=lons_new, y=lats_new, f=temp_new, ptype=1)
    compare_images(26)

    # example27
    reset()
    setvars(file='fig27.png')
    f = cf.read('/opt/graphics/cfplot_data/ggap.nc')[1]
    g = f.collapse('X: mean')
    lineplot(g.subspace(pressure=100), marker='o', color='blue',
             title='Zonal mean zonal wind at 100mb')
    compare_images(27)

    # example28
    reset()
    setvars(file='fig28.png')
    f = cf.read('/opt/graphics/cfplot_data/ggap.nc')[1]
    g = f.collapse('X: mean')
    xticks = [-90, -75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75, 90]
    xticklabels = ['90S', '75S', '60S', '45S', '30S', '15S', '0', '15N',
                   '30N', '45N', '60N', '75N', '90N']
    xpts = [-30, 30, 30, -30, -30]
    ypts = [-8, -8, 5, 5, -8]

    gset(xmin=-90, xmax=90, ymin=-10, ymax=50)
    gopen()
    lineplot(g.subspace(pressure=100), marker='o', color='blue',
             title='Zonal mean zonal wind', label='100mb')
    lineplot(g.subspace(pressure=200), marker='D', color='red',
             label='200mb', xticks=xticks, xticklabels=xticklabels,
             legend_location='upper right')
    plotvars.plot.plot(xpts, ypts, linewidth=3.0, color='green')
    plotvars.plot.text(35, -2, 'Region of interest',
                       horizontalalignment='left')
    gclose()
    compare_images(28)

    # example29
    reset()
    setvars(file='fig29.png')
    f = cf.read('/opt/graphics/cfplot_data/tas_A1.nc')[0]
    temp = f.subspace(time=cf.wi(cf.dt('1900-01-01'), cf.dt('1980-01-01')))
    temp_annual = temp.collapse('T: mean', group=cf.Y())
    temp_annual_global = temp_annual.collapse('area: mean', weights='area')
    temp_annual_global.Units -= 273.15
    lineplot(
        temp_annual_global,
        title='Global average annual temperature',
        color='blue')
    compare_images(29)


def compare_images(example=None):
    """
    | Compare images and return an error string if they don't match
    |
    |
    |
    |
    |
    |
    |
    """
    import hashlib
    disp = which('display')
    conv = which('convert')
    comp = which('compare')
    file = 'fig' + str(example) + '.png'
    file_new = '/home/andy/cfplot.src/cfplot/' + file
    file_ref = '/home/andy/regression/' + file

    # Check md5 checksums are the same and display files if not
    if hashlib.md5(open(file_new, 'rb').read()).hexdigest() != hashlib.md5(
            open(file_ref, 'rb').read()).hexdigest():
        print('***Failed example ' + str(example) + '**')
        error_image = '/home/andy/cfplot.src/cfplot/' + 'error_' + file
        diff_image = '/home/andy/cfplot.src/cfplot/' + 'difference_' + file
        p = subprocess.Popen([comp, file_new, file_ref, diff_image])
        (output, err) = p.communicate()
        p.wait()
        p = subprocess.Popen([conv, "+append", file_new,
                             file_ref, error_image])
        (output, err) = p.communicate()
        p.wait()
        subprocess.Popen([disp, diff_image])

    else:
        print('Passed example ' + str(example))


def compare_arrays(ref=None, levs_test=None, gvals_test=None,
                   mapaxis_test=None, min=None, max=None, step=None,
                   mult=None, type=None):
    """
    | Compare arrays and return an error string if they don't match
    |
    |
    |
    |
    |
    |
    |
    """

    anom = 0
    if levs_test:
        levs(min, max, step)
        if np.size(ref) != np.size(plotvars.levels):
            anom = 1
        else:
            for val in np.arange(np.size(ref)):
                if abs(ref[val] - plotvars.levels[val]) >= 1e-6:
                    anom = 1

        if anom == 1:
            print('***levs failure***')
            print('min, max, step are', min, max, step)
            print('generated levels are:')
            print(plotvars.levels)
            print('expected levels:')
            print(ref)
        else:
            pass_str = 'Passed cfp.levs(min=' + str(min) + ', max='
            pass_str += str(max) + ', step=' + str(step) + ')'
            print(pass_str)

    anom = 0
    if gvals_test:
        vals, testmult = gvals(min, max)
        if np.size(ref) != np.size(vals):
            anom = 1
        else:
            for val in np.arange(np.size(ref)):
                if abs(ref[val] - vals[val]) >= 1e-6:
                    anom = 1
        if mult != testmult:
            anom = 1

        if anom == 1:
            print('***gvals failure***')
            print('cfp.gvals(' + str(min) + ', ' + str(max) + ')')
            print('')
            print('generated values are:', vals)
            print('with a  multiplier of ', testmult)
            print('')
            print('expected values:', ref)
            print('with a  multiplier of ', mult)
        else:
            pass_str = 'Passed cfp.gvals(' + str(min) + ', ' + str(max) + ')'
            print(pass_str)

    anom = 0
    if mapaxis_test:
        ref_ticks = ref[0]
        ref_labels = ref[1]
        test_ticks, test_labels = mapaxis(min=min, max=max, type=type)
        if np.size(test_ticks) != np.size(ref_ticks):
            anom = 1
        else:
            for val in np.arange(np.size(ref_ticks)):
                if abs(ref_ticks[val] - test_ticks[val]) >= 1e-6:
                    anom = 1
                if ref_labels[val] != test_labels[val]:
                    anom = 1

        if anom == 1:
            print('***mapaxis failure***')
            print('')
            print('cfp.mapaxis(min=' + str(min) + ', max=' + str(max))
            print(', type=' + str(type) + ')')
            print('generated values are:', test_ticks)
            print('with labels:', test_labels)
            print('')
            print('expected ticks:', ref_ticks)
            print('with labels:', ref_labels)
        else:
            pass_str = 'Passed cfp.mapaxis(min=' + str(min) + ', max='
            pass_str += str(max) + ', type=' + str(type) + ')'
            print(pass_str)


def traj(f=None, title=None, ptype=0, linestyle='-', linewidth=1.0, linecolor='b',
         marker='o', markevery=1, markersize=5.0, markerfacecolor='r',
         markeredgecolor='g', markeredgewidth=1.0, latmax=None, latmin=None,
         axes=True, xaxis=True, yaxis=True,
         verbose=None, legend=False, legend_lines=False,
         xlabel=None, ylabel=None, xticks=None, yticks=None,
         xticklabels=None, yticklabels=None, colorbar=None,
         colorbar_position=None, colorbar_orientation='horizontal',
         colorbar_title=None, colorbar_text_up_down=False,
         colorbar_text_down_up=False, colorbar_drawedges=True,
         colorbar_fraction=None, colorbar_thick=None,
         colorbar_anchor=None, colorbar_shrink=None,
         colorbar_labels=None,
         vector=False, head_width=0.4, head_length=1.0,
         fc='k', ec='k', zorder=None):
    """
    | traj is the interface to trajectory plotting in cf-plot.
    | The minimum use is traj(f) where f is a CF field.
    |
    | f - CF data used to make a line plot
    | linestyle='-' - line style
    | linecolor='b' - line colour
    | linewidth=1.0 - line width
    | marker='o' - marker for points along the line
    | markersize=30 - size of the marker
    | markerfacecolor='b' - colour of the marker face
    | markeredgecolor='g' - colour of the marker edge
    | legend=False - plot different colour markers based on a set of user levels
    | zorder=None - order for plotting
    | verbose=None - Set to True to get a verbose listing of what traj is doing
    |
    | The following parameters override any CF data defaults:
    | title=None - plot title
    | axes=True - plot x and y axes
    | xaxis=True - plot xaxis
    | yaxis=True - plot y axis
    | xlabel=None - x name
    | ylabel=None - y name
    | xticks=None - x ticks
    | xticklabels=None - x tick labels
    | yticks=None - y ticks
    | yticklabels=None - y tick labels
    | colorbar=None - plot a colorbar
    | colorbar_position=None - position of colorbar
    |                          [xmin, ymin, x_extent,y_extent] in normalised
    |                          coordinates. Use when a common colorbar
    |                          is required for a set of plots. A typical set
    |                          of values would be [0.1, 0.05, 0.8, 0.02]
    | colorbar_orientation=None - orientation of the colorbar
    | colorbar_title=None - title for the colorbar
    | colorbar_text_up_down=False - if True horizontal colour bar labels alternate
    |                             above (start) and below the colour bar
    | colorbar_text_down_up=False - if True horizontal colour bar labels alternate
    |                             below (start) and above the colour bar
    | colorbar_drawedges=True - draw internal divisions in the colorbar
    | colorbar_fraction=None - space for the colorbar - default = 0.21, in normalised
    |                       coordinates
    | colorbar_thick=None - thickness of the colorbar - default = 0.015, in normalised
    |                       coordinates
    | colorbar_anchor=None - default=0.5 - anchor point of colorbar within the fraction space.
    |                        0.0 = close to plot, 1.0 = further away
    | colorbar_shrink=None - value to shrink the colorbar by.  If the colorbar
    |                        exceeds the plot area then values of 1.0, 0.55
    |                        or 0.5m ay help it better fit the plot area.
    | colorbar_labels=None - labels for the colorbar.  Default is to use the levels defined
    |                        using cfp.levs
    | Vector options
    | vector=False - Draw vectors
    | head_width=2.0 - vector head width
    | head_length=2.0 - vector head length
    | fc='k' - vector face colour
    | ec='k' - vector edge colour


    """
    if verbose:
        print('traj - making a trajectory plot')

    if isinstance(f, cf.FieldList):
        errstr = "\n\ncfp.traj - cannot make a trajectory plot from a field list "
        errstr += "- need to pass a field\n\n"
        raise TypeError(errstr)

    # Read in data
    # Find the auxiliary lons and lats if provided
    has_lons = False
    has_lats = False
    for mydim in list(f.auxiliary_coordinates()):
        name = cf_var_name(field=f, dim=mydim)
        if name in ['longitude']:
            lons = np.squeeze(f.construct(mydim).array)
            has_lons = True
        if name in ['latitude']:
            lats = np.squeeze(f.construct(mydim).array)
            has_lats = True

    data = f.array

    # Raise an error if lons and lats not found in the input data
    if not has_lons or not has_lats:
        message = '\n\n\ntraj error\n'
        if not has_lons:
            message += 'missing longitudes in the field auxiliary data\n'
        if not has_lats:
            message += 'missing latitudes in the field auxiliary data\n'
        message += '\n\n\n'
        raise TypeError(message)

    if latmax is not None:
        pts = np.where(lats >= latmax)
        if np.size(pts) > 0:
            lons[pts] = np.nan
            lats[pts] = np.nan

    if latmin is not None:
        pts = np.where(lats <= latmin)
        if np.size(pts) > 0:
            lons[pts] = np.nan
            lats[pts] = np.nan

    # Set potential user axis labels
    user_xlabel = xlabel
    user_ylabel = ylabel

    user_xlabel = ''
    user_ylabel = ''

    # Set plotting parameters
    continent_thickness = 1.5
    continent_color = 'k'
    continent_linestyle = '-'
    if plotvars.continent_thickness is not None:
        continent_thickness = plotvars.continent_thickness
    if plotvars.continent_color is not None:
        continent_color = plotvars.continent_color
    if plotvars.continent_linestyle is not None:
        continent_linestyle = plotvars.continent_linestyle
    land_color = plotvars.land_color
    ocean_color = plotvars.ocean_color
    lake_color = plotvars.lake_color

    ##################
    # Open a new plot is necessary
    ##################
    if plotvars.user_plot == 0:
        gopen(user_plot=0)

    # Call gpos(1) if not already called
    if plotvars.rows > 1 or plotvars.columns > 1:
        if plotvars.gpos_called is False:
            gpos(1)

    # Set up mapping
    if plotvars.user_mapset == 0:
        plotvars.lonmin = -180
        plotvars.lonmax = 180
        plotvars.latmin = -90
        plotvars.latmax = 90

    set_map()
    mymap = plotvars.mymap

    # Set the plot limits
    gset(xmin=plotvars.lonmin, xmax=plotvars.lonmax,
         ymin=plotvars.latmin, ymax=plotvars.latmax, user_gset=0)

    # Make lons and lats 2d if they are 1d
    ndim = np.ndim(lons)
    if ndim == 1:
        lons = lons.reshape(1, -1)
        lats = lats.reshape(1, -1)

    ntracks = np.shape(lons)[0]
    if ndim == 1:
        ntracks = 1

    if legend or legend_lines:
        # Check levels are not None
        levs = plotvars.levels
        if plotvars.levels is not None:
            if verbose:
                print('traj - plotting different colour markers based on a user set of levels')
            levs = plotvars.levels

        else:
            # Automatic levels
            if verbose:
                print('traj - generating automatic legend levels')
            dmin = np.nanmin(data)
            dmax = np.nanmax(data)
            levs, mult = gvals(dmin=dmin, dmax=dmax, mod=False)

        # Add extend options to the levels if set
        if plotvars.levels_extend == 'min' or plotvars.levels_extend == 'both':
            levs = np.append(-1e-30, levs)
        if plotvars.levels_extend == 'max' or plotvars.levels_extend == 'both':
            levs = np.append(levs, 1e30)

        # Set the default colour scale
        if plotvars.cscale_flag == 0:
            cscale('viridis', ncols=np.size(levs) + 1)
            plotvars.cscale_flag = 0

        # User selected colour map but no mods so fit to levels
        if plotvars.cscale_flag == 1:
            cscale(plotvars.cs_user, ncols=np.size(levs) + 1)
            plotvars.cscale_flag = 1

    ##################################
    # Line, symbol and vector plotting
    ##################################
    for track in np.arange(ntracks):
        xpts = lons[track, :]
        ypts = lats[track, :]
        data2 = data[track, :]

        xpts_orig = deepcopy(xpts)
        xpts = np.mod(xpts + 180, 360) - 180

        # Check if xpts are only within the remapped longitudes above
        if np.min(xpts) < -170 or np.max(xpts) > 170:
            xpts = xpts_orig

            for ix in np.arange(np.size(xpts)-1):
                diff = xpts[ix+1] - xpts[ix]
                if diff >= 60:
                    xpts[ix+1] = xpts[ix+1] - 360.0
                if diff <= -60:
                    xpts[ix+1] = xpts[ix+1] + 360.0

        # Plot lines and markers
        plot_linewidth = linewidth
        plot_markersize = markersize
        if legend:
            plot_markersize = 0.0

        if plot_linewidth > 0.0 or plot_markersize > 0.0:
            if verbose and track == 0 and linewidth > 0.0:
                print('plotting lines')
            if verbose and track == 0 and markersize > 0.0:
                print('plotting markers')

            if legend_lines is False:
                mymap.plot(xpts, ypts, color=linecolor,
                           linewidth=plot_linewidth, linestyle=linestyle,
                           marker=marker, markevery=markevery, markersize=plot_markersize,
                           markerfacecolor=markerfacecolor, markeredgecolor=markeredgecolor,
                           markeredgewidth=markeredgewidth,
                           zorder=zorder, clip_on=True, transform=ccrs.PlateCarree())
            else:
                line_xpts = xpts.compressed()
                line_ypts = ypts.compressed()
                line_data = data2.compressed()

                for i in np.arange(np.size(line_xpts)-1):
                    val = (line_data[i] + line_data[i+1])/2.0

                    col = plotvars.cs[np.max(np.where(val > plotvars.levels))]
                    mymap.plot(line_xpts[i:i+2], line_ypts[i:i+2], color=col,
                               linewidth=plot_linewidth, linestyle=linestyle,
                               zorder=zorder, clip_on=True, transform=ccrs.PlateCarree())

        # Plot vectors
        if vector:
            if verbose and track == 0:
                print('plotting vectors')
            if zorder is None:
                plot_zorder = 101
            else:
                plot_zorder = zorder
            if plotvars.proj == 'cyl':
                if isinstance(xpts, np.ma.MaskedArray):
                    pts = np.ma.MaskedArray.count(xpts)
                else:
                    pts = xpts.size

                for pt in np.arange(pts-1):
                    mymap.arrow(xpts[pt], ypts[pt],
                                xpts[pt+1] - xpts[pt],
                                ypts[pt+1] - ypts[pt],
                                head_width=head_width,
                                head_length=head_length,
                                fc=fc, ec=ec,
                                length_includes_head=True,
                                zorder=plot_zorder, clip_on=True,
                                transform=ccrs.PlateCarree())

    # Plot different colour markers based on a user set of levels
    if legend:

        # For polar stereographic plots mask any points outside the plotting limb
        if plotvars.proj == 'npstere':
            pts = np.where(lats < plotvars.boundinglat)
            if np.size(pts) > 0:
                lats[pts] = np.nan

        if plotvars.proj == 'spstere':
            pts = np.where(lats > plotvars.boundinglat)
            if np.size(pts) > 0:
                lats[pts] = np.nan

        for track in np.arange(ntracks):
            xpts = lons[track, :]
            ypts = lats[track, :]
            data2 = data[track, :]



            for i in np.arange(np.size(levs)-1):
                color = plotvars.cs[i]

                if np.ma.is_masked(data2):
                    pts = np.ma.where(np.logical_and(data2 >= levs[i], data2 <= levs[i+1]))
                else:
                    pts = np.where(np.logical_and(data2 >= levs[i], data2 <= levs[i+1]))

                if zorder is None:
                    plot_zorder = 101
                else:
                    plot_zorder = zorder
                if np.size(pts) > 0:

                    mymap.scatter(xpts[pts], ypts[pts],
                                  s=markersize*15,
                                  c=color,
                                  marker=marker,
                                  edgecolors=markeredgecolor,
                                  transform=ccrs.PlateCarree(), zorder=plot_zorder)

    # Axes
    plot_map_axes(axes=axes, xaxis=xaxis, yaxis=yaxis,
                  xticks=xticks, xticklabels=xticklabels,
                  yticks=yticks, yticklabels=yticklabels,
                  user_xlabel=user_xlabel, user_ylabel=user_ylabel,
                  verbose=verbose)

    # Coastlines
    feature = cfeature.NaturalEarthFeature(name='land', category='physical',
                                           scale=plotvars.resolution,
                                           facecolor='none')

    mymap.add_feature(feature, edgecolor=continent_color,
                      linewidth=continent_thickness,
                      linestyle=continent_linestyle)

    if ocean_color is not None:
        mymap.add_feature(cfeature.OCEAN, edgecolor='face', facecolor=ocean_color,
                          zorder=100)
    if land_color is not None:
        mymap.add_feature(cfeature.LAND, edgecolor='face', facecolor=land_color,
                          zorder=100)
    if lake_color is not None:
        mymap.add_feature(cfeature.LAKES, edgecolor='face', facecolor=lake_color,
                          zorder=100)

    # Title
    if title is not None:
        map_title(title)

    # Color bar
    plot_colorbar = False
    if colorbar is None and legend:
        plot_colorbar = True
    if colorbar is None and legend_lines:
        plot_colorbar = True
    if colorbar:
        plot_colorbar = True

    if plot_colorbar:
        if (colorbar_title is None):
            colorbar_title = 'No Name'
            if hasattr(f, 'id'):
                colorbar_title = f.id
            nc = f.nc_get_variable(False)
            if nc:
                colorbar_title = f.nc_get_variable()
            if hasattr(f, 'short_name'):
                colorbar_title = f.short_name
            if hasattr(f, 'long_name'):
                colorbar_title = f.long_name
            if hasattr(f, 'standard_name'):
                colorbar_title = f.standard_name

            if hasattr(f, 'Units'):
                if str(f.Units) == '':
                    colorbar_title += ''
                else:
                    colorbar_title += '(' + supscr(str(f.Units)) + ')'

        levs = plotvars.levels
        if colorbar_labels is not None:
            levs = colorbar_labels
        cbar(levs=levs, labels=levs,
             orientation=colorbar_orientation,
             position=colorbar_position,
             text_up_down=colorbar_text_up_down,
             text_down_up=colorbar_text_down_up,
             drawedges=colorbar_drawedges,
             fraction=colorbar_fraction,
             thick=colorbar_thick,
             shrink=colorbar_shrink,
             anchor=colorbar_anchor,
             title=colorbar_title,
             verbose=verbose)

    ##########
    # Save plot
    ##########
    if plotvars.user_plot == 0:
        gclose()


def cbar(labels=None,
         orientation=None,
         position=None,
         shrink=None,
         fraction=None,
         title=None,
         fontsize=None,
         fontweight=None,
         text_up_down=None,
         text_down_up=None,
         drawedges=None,
         levs=None,
         thick=None,
         anchor=None,
         extend=None,
         mid=None,
         verbose=None):
    """
    | cbar is the cf-plot interface to the Matplotlib colorbar routine
    |
    | labels - colorbar labels
    | orientation - orientation 'horizontal' or 'vertical'
    | position - user specified colorbar position in normalised
    |            plot coordinates [left, bottom, width, height]
    | shrink - default=1.0 - scale colorbar along length
    | fraction - default = 0.21 - space for the colorbar in
    |            normalised plot coordinates
    | title - title for the colorbar
    | fontsize - font size for the colorbar text
    | fontweight - font weight for the colorbar text
    | text_up_down - label division text up and down starting with up
    | text_down_up - label division text down and up starting with down
    | drawedges - Draw internal delimeter lines in colorbar
    | levs - colorbar levels
    | thick - set height of colorbar - default = 0.015,
    |         in normalised plot coordinates
    | anchor - default=0.3 - anchor point of colorbar within the fraction space.
    |                        0.0 = close to plot, 1.0 = further away
    | extend = None - extensions for colorbar.  The default is for extensions at
    |                 both ends.
    | mid = False - label mid points of colours rather than the boundaries
    | verbose = None
    |
    |
    |
    """

    if verbose:
        print('con - adding a colour bar')
        
        
    if fontsize is None:
        fontsize = plotvars.colorbar_fontsize
    if fontweight is None:
        fontweight = plotvars.colorbar_fontweight
    if thick is None:
        thick = 0.012
        if plotvars.rows == 2:
            thick = 0.008
        if plotvars.rows == 3:
            thick = 0.005
        if plotvars.rows >= 4:
            thick = 0.003
    if drawedges is None:
        drawedges = True
    if orientation is None:
        orientation = 'horizontal'
    if fraction is None:
        fraction = 0.12
        if plotvars.rows == 2:
            fraction = 0.08
        if plotvars.rows == 3:
            fraction = 0.06
        if plotvars.rows >= 4:
            fraction = 0.04
            
    if shrink is None:
        shrink = 1.0

    if anchor is None:
        anchor = 0.3
        if plotvars.plot_type > 1:
            anchor = 0.5
    
    
 
        
        
    # Code for when the user specifies nlevs to the contour command rather than 
    # letting cf-plot work out some levels
    if type(levs) == int:
        if plotvars.plot_type == 0:
            myplot = plotvars.mymap
        else:
            myplot = plotvars.plot
            
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        divider = make_axes_locatable(myplot)
        if orientation == 'horizontal':
            if plotvars.plot_type == 1:
                cax = divider.append_axes("bottom", size="2%", pad=0.3, title=title)
            else:
                cax = divider.append_axes("bottom", size="2%", pad=1.0, title=title)
        else:
            cax = divider.append_axes("right", size="2%", pad=0.5, title=title)


        plotvars.master_plot.colorbar(plotvars.image, cax=cax, orientation=orientation)                       
            
        
        return


    # Change plot position based on colorbar location  
    if position is None:
        # Work out whether the plot is a map plot or normal plot
        if (plotvars.plot_type == 1 or plotvars.plot_type == 6):
            this_plot = plotvars.mymap
        else:
            this_plot = plotvars.plot

        if plotvars.plot_type == 6 and (plotvars.proj == 'rotated' or plotvars.proj == 'UKCP'):
            this_plot = plotvars.plot     

        l, b, w, h = this_plot.get_position().bounds

        if orientation == 'horizontal':
            if plotvars.plot_type > 1 or plotvars.plot == 0 or plotvars.proj != 'cyl':
                this_plot.set_position([l, b + fraction, w, h - fraction])

            if plotvars.plot_type == 1 and plotvars.proj == 'cyl':

                # Move plot up if aspect ratio is < 1.5
                lonrange = plotvars.lonmax - plotvars.lonmin
                latrange = plotvars.latmax - plotvars.latmin
                
                if (lonrange / latrange) <= 1.5:
                    this_plot.set_position([l, b + 0.08, w, h - 0.12])
                    l, b, w, h = this_plot.get_position().bounds

                ax1 = plotvars.master_plot.add_axes([l + w * (1.0 - shrink)/2.0,
                                                     b - fraction * (1.0 - anchor),
                                                     w * shrink,
                                                     thick])
            else:


                ax1 = plotvars.master_plot.add_axes([l + w * (1.0 - shrink)/2.0,
                                                     b,
                                                     w * shrink,
                                                     thick])

            if plotvars.plot_type > 1 or plotvars.plot_type == 0:
                this_plot.set_position([l, b + fraction, w, h - fraction])

        else:
            ax1 = plotvars.master_plot.add_axes([l + w + fraction * (anchor - 1),
                                                 b + h * (1.0 - shrink) / 2.0,
                                                 thick,
                                                 h * shrink])
            this_plot.set_position([l, b, w - fraction, h])        
        
        
        
        
    if levs is None:
        if plotvars.levels is not None:
            levs = np.array(plotvars.levels)
        else:
            if labels is None:
                errstr = "\n\ncbar error - No levels or labels supplied \n\n"
                raise TypeError(errstr)
            else:
                levs = np.arange(len(labels))





    if labels is None:
        labels = levs

    # Work out colour bar labeling
    lbot = levs
    if text_up_down:
        lbot = levs[1:][::2]
        ltop = levs[::2]

    if text_down_up:
        lbot = levs[::2]
        ltop = levs[1:][::2]

    # Get the colour map
    colmap = cscale_get_map()
    cmap = matplotlib.colors.ListedColormap(colmap)
    if extend is None:
        extend = plotvars.levels_extend


    ncolors = np.size(levs)

         
    if extend == 'both' or extend == 'max':
        ncolors = ncolors - 1
        
    if type(levs) != int:
        plotvars.norm = matplotlib.colors.BoundaryNorm(boundaries=levs, ncolors=ncolors)

        # Change boundaries to floats
        boundaries = levs.astype(float)

        # Add colorbar extensions if definded by levs.  Using boundaries[0]-1
        # for the lower and boundaries[-1]+1 is just for the colorbar and
        # has no meaning for the plot.
        if (extend == 'min' or extend == 'both'):
            cmap.set_under(plotvars.cs[0])
            boundaries = np.insert(boundaries, 0, boundaries[0]-1)
        if (extend == 'max' or extend == 'both'):
            cmap.set_over(plotvars.cs[-1])
            boundaries = np.insert(boundaries, len(boundaries), boundaries[-1]+1)



        if mid is not None:
            lbot_new = []
            for i in np.arange(len(labels)):
                mid_point = (lbot[i+1]-lbot[i])/2.0+lbot[i]
                lbot_new.append(mid_point)
            lbot = lbot_new

        if type(levs) != list:
            lbot = None

        colorbar = matplotlib.colorbar.ColorbarBase(ax1, cmap=cmap,
                                                    norm=plotvars.norm,
                                                    extend=extend,
                                                    extendfrac='auto',
                                                    boundaries=boundaries,
                                                    ticks=lbot,
                                                    spacing='uniform',
                                                    orientation=orientation,
                                                    drawedges=drawedges)

    else:

        if mid is not None:
            lbot_new = []
            for i in np.arange(len(labels)):
                mid_point = (lbot[i+1]-lbot[i])/2.0+lbot[i]
                lbot_new.append(mid_point)
            lbot = lbot_new

        ax1 = plotvars.master_plot.add_axes(position)
        colorbar = matplotlib.colorbar.ColorbarBase(
                    ax1, cmap=cmap,
                    norm=plotvars.norm,
                    extend=extend,
                    extendfrac='auto',
                    boundaries=boundaries,
                    ticks=lbot,
                    spacing='uniform',
                    orientation=orientation,
                    drawedges=drawedges)

    colorbar.set_label(title, fontsize=fontsize,
                       fontweight=fontweight)

    # Bug in Matplotlib colorbar labelling
    # With clevs=[-1, 1, 10000, 20000, 30000, 40000, 50000, 60000]
    # Labels are [0, 2, 10001, 20001, 30001, 40001, 50001, 60001]
    # With a +1 near to the colorbar label


    # Check for an extraneous level compared to the levs
    if len(labels) > len(levs):
        labels = labels[:len(levs)]

    colorbar.set_ticklabels([str(i) for i in labels])
    if orientation == 'horizontal':
        for tick in colorbar.ax.xaxis.get_ticklines():
            tick.set_visible(False)
        for t in colorbar.ax.get_xticklabels():
            t.set_fontsize(fontsize)
            t.set_fontweight(fontweight)
    else:
        for tick in colorbar.ax.yaxis.get_ticklines():
            tick.set_visible(False)
        for t in colorbar.ax.get_yticklabels():
            t.set_fontsize(fontsize)
            t.set_fontweight(fontweight)

    # Alternate text top and bottom on a horizontal colorbar if requested
    # Use method described at:
    # https://stackoverflow.com/questions/37161022/matplotlib-colorbar-
    # alternating-top-bottom-labels
    if text_up_down or text_down_up:

        vmin = colorbar.norm.vmin
        vmax = colorbar.norm.vmax

        if colorbar.extend == 'min':
            shift_l = 0.05
            scaling = 0.95
        elif colorbar.extend == 'max':
            shift_l = 0.
            scaling = 0.95
        elif colorbar.extend == 'both':
            shift_l = 0.05
            scaling = 0.9
        else:
            shift_l = 0.
            scaling = 1.0

        # Print bottom tick labels
        colorbar.ax.set_xticklabels(lbot)

        # Print top tick labels
        for ii in ltop:
            colorbar.ax.text(shift_l + scaling*(ii-vmin)/(vmax-vmin),
                             1.5, str(ii), transform=colorbar.ax.transAxes,
                             va='bottom', ha='center', fontsize=fontsize,
                             fontweight=fontweight)

        for t in colorbar.ax.get_xticklabels():
            t.set_fontsize(fontsize)
            t.set_fontweight(fontweight)


def map_title(title=None, dims=False):
    """
    | map_title is an internal routine to draw a title on a map plot
    |
    | title=None - title to put on map plot
    | dim=False - draw a set of dimension titles
    |
    |
    |
    |
    |
    """

    boundinglat = plotvars.boundinglat
    lon_0 = plotvars.lon_0
    lonmin = plotvars.lonmin
    lonmax = plotvars.lonmax
    latmin = plotvars.latmin
    latmax = plotvars.latmax
    polar_range = 90-abs(boundinglat)

    if plotvars.proj == 'cyl':
        lon_mid = lonmin + (lonmax - lonmin) / 2.0
        mylon = lon_mid
        if dims:
            mylon = lonmin
        proj = ccrs.PlateCarree(central_longitude=lon_mid)
        mylat = latmax
        xpt, ypt = proj.transform_point(mylon, mylat, ccrs.PlateCarree())
        ypt = ypt + (latmax - latmin) / 40.0


    if plotvars.proj == 'npstere':
        mylon = lon_0 + 180
        mylat = boundinglat-polar_range/15.0
        proj = ccrs.NorthPolarStereo(central_longitude=lon_0)
        xpt, ypt = proj.transform_point(mylon, mylat, ccrs.PlateCarree())
        if dims:
            mylon = lon_0 + 180
            mylat = boundinglat-polar_range/15.0
            xpt_mid, ypt = proj.transform_point(mylon, mylat, ccrs.PlateCarree())
            mylon = lon_0 - 90
            xpt, ypt_mid = proj.transform_point(mylon, mylat, ccrs.PlateCarree())

    if plotvars.proj == 'spstere':
        mylon = lon_0
        mylat = boundinglat+polar_range/15.0
        proj = ccrs.SouthPolarStereo(central_longitude=lon_0)
        xpt, ypt = proj.transform_point(mylon, mylat, ccrs.PlateCarree())
        if dims:
            mylon = lon_0 + 0
            #mylat = boundinglat-polar_range/15.0
            mylat = boundinglat-polar_range/15.0
            xpt_mid, ypt = proj.transform_point(mylon, mylat, ccrs.PlateCarree())
            mylon = lon_0 - 90
            xpt, ypt_mid = proj.transform_point(mylon, mylat, ccrs.PlateCarree())
        


    if plotvars.proj == 'lcc':
        mylon = lonmin + (lonmax - lonmin) / 2.0
        if dims:
            mylon = lonmin
        lat_0 = 40
        if latmin <= 0 and latmax <= 0:
            lat_0 = 40
        proj = ccrs.LambertConformal(central_longitude=plotvars.lon_0,
                                     central_latitude=lat_0,
                                     cutoff=plotvars.latmin)
        mylat = latmax
        xpt, ypt = proj.transform_point(mylon, mylat, ccrs.PlateCarree())

    fontsize = plotvars.title_fontsize

    if dims:
        halign = 'left'
        fontsize = plotvars.axis_label_fontsize

        # Get plot position
        this_plot = plotvars.plot
        l, b, w, h = this_plot.get_position().bounds
 
        # Shift to left
        #if plotvars.plot_type == 1 and plotvars.proj !=cyl:
        l = l - 0.1
        this_plot.set_position([l, b, w, h])

        l, b, w, h = this_plot.get_position().bounds


        plotvars.plot.text(l + w , b + h, title, va='bottom',
                            ha=halign,
                            rotation='horizontal', rotation_mode='anchor',
                            fontsize=fontsize,
                            fontweight=plotvars.title_fontweight)


    else:
        halign = 'center'
        plotvars.mymap.text(xpt, ypt, title, va='bottom',
                            ha=halign,
                            rotation='horizontal', rotation_mode='anchor',
                            fontsize=fontsize,
                            fontweight=plotvars.title_fontweight)




def dim_titles(title=None, title2=None, title3=None, dims=False):
    """
    | dim_titles is an internal routine to draw a set of dimension titles on a  plot
    |
    | title=None - title to put on the plot
    | title2=None - additional title to put to the right of the first title
    | dim=False - draw a set of dimension titles
    |
    |
    |
    |
    |
    """

    # Get plot position
    if plotvars.plot_type == 1:
        this_plot = plotvars.mymap
    else:
        this_plot = plotvars.plot

    l, b, w, h = this_plot.get_position().bounds

    valign = 'bottom'
 
    # Shift down if a cylindrical plot else to the left
    if plotvars.plot_type == 1 and plotvars.proj != 'cyl':
        l = l - 0.1
        myx = 1.2
        myy = 1.0
        valign = 'top'
    elif plotvars.plot_type == 1 and plotvars.proj == 'cyl':
        lonrange = plotvars.lonmax - plotvars.lonmin
        latrange = plotvars.latmax - plotvars.latmin
        if (lonrange / latrange) > 1.5:
            myx = 0.0
            myy = 1.02
            #h = h - 0.015
            
        if (lonrange / latrange) > 1.2 and (lonrange / latrange) <= 1.5:
            myx = 0.0
            myy = 1.02
            h = h - 0.015        
        
        
        if (lonrange / latrange) <= 1.2:
            l = l - 0.1
            myx = 1.1
            myy = 1.0
            valign = 'top'
    else:
        h = h - 0.1
        myx = 0.0
        myy = 1.02


    this_plot.set_position([l, b, w, h])

    if title3 is not None:
        this_plot.text(myx + 0.3, myy, title2, va=valign,
                   ha='left',
                   fontsize=plotvars.axis_label_fontsize,
                   fontweight=plotvars.axis_label_fontweight,
                   transform=this_plot.transAxes)

        this_plot.text(myx + 0.6, myy, title3, va=valign,
                   ha='left',
                   fontsize=plotvars.axis_label_fontsize,
                   fontweight=plotvars.axis_label_fontweight,
                   transform=this_plot.transAxes)

        return


    this_plot.text(myx, myy, title, va=valign,
                   ha='left',
                   fontsize=plotvars.axis_label_fontsize,
                   fontweight=plotvars.axis_label_fontweight,
                   transform=this_plot.transAxes)

    if title2 is not None:
        this_plot.text(myx + 0.3, myy, title2, va=valign,
                   ha='left',
                   fontsize=plotvars.axis_label_fontsize,
                   fontweight=plotvars.axis_label_fontweight,
                   transform=this_plot.transAxes)







def plot_map_axes(axes=None, xaxis=None, yaxis=None,
                  xticks=None, xticklabels=None,
                  yticks=None, yticklabels=None,
                  user_xlabel=None, user_ylabel=None,
                  verbose=None):
    """
    | plot_map_axes is an internal routine to draw the axes on a map plot
    |
    | axes=None - drawing axes
    | xaxis=None - drawing x-axis
    | yaxis=None - drawing x-axis
    | xticks=None - user defined xticks
    | xticklabels=None - user defined xtick labels
    | yticks=None - user defined yticks
    | yticklabels=None - user defined ytick labels
    | user_xlabel=None - user defined xlabel
    | user_ylabel=None - user defined ylabel
    | verbose=None
    |
    |
    |
    |
    |
    """
    # Font definitions
    axis_label_fontsize = plotvars.axis_label_fontsize
    axis_label_fontweight = plotvars.axis_label_fontweight

    # Map parameters
    boundinglat = plotvars.boundinglat
    lon_0 = plotvars.lon_0
    lonmin = plotvars.lonmin
    lonmax = plotvars.lonmax
    latmin = plotvars.latmin
    latmax = plotvars.latmax

    # Cylindrical
    if plotvars.proj == 'cyl':

        if verbose:
            print('con - adding cylindrical axes')
        lonticks, lonlabels = mapaxis(
            min=plotvars.lonmin, max=plotvars.lonmax, type=1)
        latticks, latlabels = mapaxis(
            min=plotvars.latmin, max=plotvars.latmax, type=2)

        if axes:
            if xaxis:
                if xticks is None:
                    axes_plot(xticks=lonticks, xticklabels=lonlabels)
                else:
                    if xticklabels is None:
                        axes_plot(xticks=xticks, xticklabels=xticks)
                    else:
                        axes_plot(xticks=xticks, xticklabels=xticklabels)
            if yaxis:
                if yticks is None:
                    axes_plot(yticks=latticks, yticklabels=latlabels)
                else:
                    if yticklabels is None:
                        axes_plot(yticks=yticks, yticklabels=yticks)
                    else:
                        axes_plot(yticks=yticks, yticklabels=yticklabels)

            if user_xlabel is not None:
                plot.text(0.5, -0.10, user_xlabel, va='bottom',
                          ha='center',
                          rotation='horizontal', rotation_mode='anchor',
                          transform=plotvars.mymap.transAxes,
                          fontsize=axis_label_fontsize,
                          fontweight=axis_label_fontweight)

            if user_ylabel is not None:
                plot.text(-0.05, 0.50, user_ylabel, va='bottom',
                          ha='center',
                          rotation='vertical', rotation_mode='anchor',
                          transform=plotvars.mymap.transAxes,
                          fontsize=axis_label_fontsize,
                          fontweight=axis_label_fontweight)

    # Polar stereographic
    if plotvars.proj == 'npstere' or plotvars.proj == 'spstere':
        if verbose:
            print('con - adding stereographic axes')

        mymap = plotvars.mymap
        latrange = 90-abs(boundinglat)
        proj = ccrs.Geodetic()

        # Add
        if axes:
            if xaxis:
                if yticks is None:
                    latvals = np.arange(5)*30-60
                else:
                    latvals = np.array(yticks)

                if plotvars.proj == 'npstere':
                    latvals = latvals[np.where(latvals >= boundinglat)]
                else:
                    latvals = latvals[np.where(latvals <= boundinglat)]

                for lat in latvals:
                    if abs(lat - boundinglat) > 1:
                        lons = np.arange(361)
                        lats = np.zeros(361)+lat
                        mymap.plot(lons, lats, color=plotvars.grid_colour,
                                   linewidth=plotvars.grid_thickness,
                                   linestyle=plotvars.grid_linestyle,
                                   transform=proj)

            if yaxis:
                if xticks is None:
                    lonvals = np.arange(7)*60
                else:
                    lonvals = xticks

                for lon in lonvals:
                    label = mapaxis(lon, lon, 1)[1][0]

                    if plotvars.proj == 'npstere':
                        lats = np.arange(90-boundinglat)+boundinglat
                    else:
                        lats = np.arange(boundinglat+91)-90
                    lons = np.zeros(np.size(lats))+lon
                    mymap.plot(lons, lats, color=plotvars.grid_colour,
                               linewidth=plotvars.grid_thickness,
                               linestyle=plotvars.grid_linestyle,
                               transform=proj)

            # Add longitude labels
            if plotvars.proj == 'npstere':
                proj = ccrs.NorthPolarStereo(central_longitude=lon_0)
                pole = 90
                latpt = boundinglat - latrange/40.0
            else:
                proj = ccrs.SouthPolarStereo(central_longitude=lon_0)
                pole = -90
                latpt = boundinglat + latrange / 40.0

            lon_mid, lat_mid = proj.transform_point(0, pole, ccrs.PlateCarree())

            if xaxis and axis_label_fontsize > 0.0:
                for xtick in lonvals:
                    label = mapaxis(xtick, xtick, 1)[1][0]
                    lonr, latr = proj.transform_point(xtick, latpt, ccrs.PlateCarree())

                    v_align = 'center'
                    if lonr < 1:
                        h_align = 'right'
                    if lonr > 1:
                        h_align = 'left'
                    if abs(lonr) <= 1:
                        h_align = 'center'
                        if latr < 1:
                            v_align = 'top'
                        if latr > 1:
                            v_align = 'bottom'

                    mymap.text(lonr, latr, label, horizontalalignment=h_align,
                               verticalalignment=v_align,
                               fontsize=axis_label_fontsize,
                               fontweight=axis_label_fontweight, zorder=101)

        # Make the plot circular by blanking off around the plot
        # Find min and max of plotting region in map coordinates
        lons = np.arange(360)
        lats = np.zeros(np.size(lons))+boundinglat
        device_coords = proj.transform_points(ccrs.PlateCarree(), lons, lats)
        xmin = np.min(device_coords[:, 0])
        xmax = np.max(device_coords[:, 0])
        ymin = np.min(device_coords[:, 1])
        ymax = np.max(device_coords[:, 1])

        # blank off data past the bounding latitude
        pts = np.where(device_coords[:, 0] >= 0.0)
        xpts = np.append(device_coords[:, 0][pts], np.zeros(np.size(pts)) + xmax)
        ypts = np.append(device_coords[:, 1][pts], device_coords[:, 1][pts][::-1])
        mymap.fill(xpts, ypts, alpha=1.0, color='w', zorder=100)

        xpts = np.append(np.zeros(np.size(pts)) + xmin, -1.0 * device_coords[:, 0][pts])
        ypts = np.append(device_coords[:, 1][pts], device_coords[:, 1][pts][::-1])
        mymap.fill(xpts, ypts, alpha=1.0, color='w', zorder=100)

        # Turn off map outside the cicular plot area
        mymap.outline_patch.set_visible(False)

        # Draw a line around the bounding latitude
        lons = np.arange(361)
        lats = np.zeros(np.size(lons)) + boundinglat
        device_coords = proj.transform_points(ccrs.PlateCarree(), lons, lats)
        mymap.plot(device_coords[:, 0], device_coords[:, 1], color='k',
                   zorder=100, clip_on=False)

        # Modify xlim and ylim values as the default values clip the plot slightly
        xmax = np.max(np.abs(mymap.set_xlim(None)))
        mymap.set_xlim((-xmax, xmax), emit=False)
        ymax = np.max(np.abs(mymap.set_ylim(None)))
        mymap.set_ylim((-ymax, ymax), emit=False)

    # Lambert conformal
    if plotvars.proj == 'lcc':
        lon_0 = plotvars.lonmin+(plotvars.lonmax-plotvars.lonmin)/2.0
        lat_0 = plotvars.latmin+(plotvars.latmax-plotvars.latmin)/2.0

        mymap = plotvars.mymap
        standard_parallels = [33, 45]
        if latmin <= 0 and latmax <= 0:
            standard_parallels = [-45, -33]
        proj = ccrs.LambertConformal(central_longitude=lon_0,
                                     central_latitude=lat_0,
                                     cutoff=40,
                                     standard_parallels=standard_parallels)

        lonmin = plotvars.lonmin
        lonmax = plotvars.lonmax
        latmin = plotvars.latmin
        latmax = plotvars.latmax

        # Modify xlim and ylim values as the default values clip the plot slightly
        xmin = mymap.set_xlim(None)[0]
        xmax = mymap.set_xlim(None)[1]
        ymin = mymap.set_ylim(None)[0]
        ymax = mymap.set_ylim(None)[1]

        mymap.set_ylim(ymin*1.05, ymax, emit=False)
        mymap.set_ylim(None)

        # Mask off contours that appear because of the plot extention
        # mymap.add_patch(mpatches.Polygon([[xmin, ymin], [xmax,ymin],
        #                                  [xmax, ymin*1.05], [xmin, ymin*1.05]],
        #                                  facecolor='red'))
        # transform=ccrs.PlateCarree()))

        lons = np.arange(lonmax-lonmin+1) + lonmin
        lats = np.arange(latmax-latmin+1) + latmin
        verts = []
        for lat in lats:
            verts.append([lonmin, lat])
        for lon in lons:
            verts.append([lon, latmax])
        for lat in lats[::-1]:
            verts.append([lonmax, lat])
        for lon in lons[::-1]:
            verts.append([lon, latmin])

        # Mask left and right of plot
        lats = np.arange(latmax-latmin+1) + latmin
        lons = np.zeros(np.size(lats)) + lonmin
        device_coords = proj.transform_points(ccrs.PlateCarree(), lons, lats)
        xmin = np.min(device_coords[:, 0])
        xmax = np.max(device_coords[:, 0])
        if lat_0 > 0:
            ymin = np.min(device_coords[:, 1])
            ymax = np.max(device_coords[:, 1])
        else:
            ymin = np.max(device_coords[:, 1])
            ymax = np.min(device_coords[:, 1])

        # Left
        mymap.fill([xmin, xmin, xmax, xmin],
                   [ymin, ymax, ymax, ymin],
                   alpha=1.0, color='w', zorder=100)
        mymap.plot([xmin, xmax], [ymin, ymax], color='k', zorder=101, clip_on=False)

        # Right
        mymap.fill([-xmin, -xmin, -xmax, -xmin],
                   [ymin, ymax, ymax, ymin],
                   alpha=1.0, color='w', zorder=100)
        mymap.plot([-xmin, -xmax], [ymin, ymax], color='k', zorder=101, clip_on=False)

        # Upper
        lons = np.arange(lonmax-lonmin+1) + lonmin
        lats = np.zeros(np.size(lons)) + latmax
        device_coords = proj.transform_points(ccrs.PlateCarree(), lons, lats)
        ymax = np.max(device_coords[:, 1])

        xpts = np.append(device_coords[:, 0], device_coords[:, 0][::-1])
        ypts = np.append(device_coords[:, 1], np.zeros(np.size(lons))+ymax)

        mymap.fill(xpts, ypts, alpha=1.0, color='w', zorder=100)
        mymap.plot(device_coords[:, 0], device_coords[:, 1], color='k', zorder=101, clip_on=False)

        # Lower
        lons = np.arange(lonmax-lonmin+1) + lonmin
        lats = np.zeros(np.size(lons)) + latmin
        device_coords = proj.transform_points(ccrs.PlateCarree(), lons, lats)
        ymin = np.min(device_coords[:, 1]) * 1.05

        xpts = np.append(device_coords[:, 0], device_coords[:, 0][::-1])
        ypts = np.append(device_coords[:, 1], np.zeros(np.size(lons))+ymin)

        mymap.fill(xpts, ypts, alpha=1.0, color='w', zorder=100)
        mymap.plot(device_coords[:, 0], device_coords[:, 1], color='k', zorder=101, clip_on=False)

        # Turn off drawing of the rectangular box around the plot
        mymap.outline_patch.set_visible(False)

        if lat_0 < 0:
            lons = np.arange(lonmax - lonmin + 1) + lonmin
            lats = np.zeros(np.size(lons)) + latmax
            device_coords = proj.transform_points(ccrs.PlateCarree(), lons, lats)
            xmin = np.min(device_coords[:, 0])
            xmax = np.max(device_coords[:, 0])

            lons = np.arange(lonmax-lonmin+1) + lonmin
            lats = np.zeros(np.size(lons)) + latmin
            device_coords = proj.transform_points(ccrs.PlateCarree(), lons, lats)
            ymax = np.min(device_coords[:, 1])
            ymin = ymax * 1.1

            xpts = [xmin, xmax, xmax, xmin, xmin]
            ypts = [ymin, ymin, ymax, ymax, ymin]
            mymap.fill(xpts, ypts, alpha=1.0, color='w', zorder=100)

        # Draw longitudes and latitudes if requested
        fs = plotvars.axis_label_fontsize
        fw = plotvars.axis_label_fontweight
        if axes and xaxis:
            if xticks is None:
                map_xticks, map_xticklabels = mapaxis(min=plotvars.lonmin,
                                                      max=plotvars.lonmax, type=1)
            else:
                map_xticks = xticks
                if xticklabels is None:
                    map_xticklabels = xticks
                else:
                    map_xticklabels = xticklabels

            if axes and xaxis:
                lats = np.arange(latmax - latmin + 1) + latmin
                for tick in np.arange(np.size(map_xticks)):
                    lons = np.zeros(np.size(lats)) + map_xticks[tick]
                    device_coords = proj.transform_points(ccrs.PlateCarree(), lons, lats)
                    mymap.plot(device_coords[:, 0], device_coords[:, 1],
                               linewidth=plotvars.grid_thickness,
                               linestyle=plotvars.grid_linestyle,
                               color=plotvars.grid_colour,
                               zorder=101)

                    latpt = latmin - 3
                    if lat_0 < 0:
                        latpt = latmax + 1
                    device_coords = proj.transform_point(map_xticks[tick], latpt,
                                                         ccrs.PlateCarree())
                    mymap.text(device_coords[0], device_coords[1],
                               map_xticklabels[tick],
                               horizontalalignment='center',
                               fontsize=fs,
                               fontweight=fw,
                               zorder=101)

        if yticks is None:
            map_yticks, map_yticklabels = mapaxis(min=plotvars.latmin,
                                                  max=plotvars.latmax,
                                                  type=2)
        else:
            map_yticks = yticks
            if yticklabels is None:
                map_yticklabels = yticks
            else:
                map_yticklabels = yticklabels

        if axes and yaxis:
            lons = np.arange(lonmax-lonmin+1) + lonmin
            for tick in np.arange(np.size(map_yticks)):
                lats = np.zeros(np.size(lons)) + map_yticks[tick]
                device_coords = proj.transform_points(ccrs.PlateCarree(), lons, lats)
                mymap.plot(device_coords[:, 0],
                           device_coords[:, 1],
                           linewidth=plotvars.grid_thickness,
                           linestyle=plotvars.grid_linestyle,
                           color=plotvars.grid_colour,
                           zorder=101)

                device_coords = proj.transform_point(lonmin-1,
                                                     map_yticks[tick],
                                                     ccrs.PlateCarree())
                mymap.text(device_coords[0],
                           device_coords[1],
                           map_yticklabels[tick],
                           horizontalalignment='right',
                           verticalalignment='center',
                           fontsize=fs,
                           fontweight=fw,
                           zorder=101)

                device_coords = proj.transform_point(lonmax+1,
                                                     map_yticks[tick],
                                                     ccrs.PlateCarree())
                mymap.text(device_coords[0],
                           device_coords[1],
                           map_yticklabels[tick],
                           horizontalalignment='left',
                           verticalalignment='center',
                           fontsize=fs,
                           fontweight=fw,
                           zorder=101)

    # UKCP grid
    if plotvars.proj == 'UKCP' and plotvars.grid:
        lonmin = -11
        lonmax = 3
        latmin = 49
        latmax = 61
        spacing = plotvars.grid_spacing
        if xticks is None:
            lons = np.arange(30 / spacing + 1) * spacing
            lons = np.append((lons*-1)[::-1], lons[1:])
        else:
            lons = xticks
        if yticks is None:
            lats = np.arange(90.0 / spacing + 1) * spacing
        else:
            lats = yticks

        if plotvars.grid:
            plotvars.mymap.gridlines(color=plotvars.grid_colour,
                                     linewidth=plotvars.grid_thickness,
                                     linestyle=plotvars.grid_linestyle,
                                     xlocs=lons, ylocs=lats)


def add_cyclic(field, lons):
    """
    | add_cyclic is a wrapper for cartopy_util.add_cyclic_point(field, lons)
    | This is needed for the case of when the longitudes are not evenly spaced
    | due to numpy rounding which causes an error from the cartopy wrapping routine.
    | In this case the longitudes are promoted to 64 bit and then rounded
    | to an appropriate number of decimal places before passing to the cartopy
    | add_cyclic routine.
    """


    try:
        field, lons = cartopy_util.add_cyclic_point(field, lons)
    except Exception:
        ndecs_max = max_ndecs_data(lons)
        lons = np.float64(lons).round(ndecs_max)
        field, lons = cartopy_util.add_cyclic_point(field, lons)

    return field, lons



def ugrid_window(field, lons,lats):

    field_ugrid = deepcopy(field)
    lons_ugrid = deepcopy(lons)
    lats_ugrid = deepcopy(lats)


    # Fix longitudes to be -180 to 180
    # lons_ugrid = ((lons_ugrid + plotvars.lonmin) % 360) + plotvars.lonmin

    # Test data to get appropiate longitude offset to perform remapping
    found_lon = False
    for ilon in [-360, 0, 360]:
        lons_test = lons_ugrid + ilon
        if np.min(lons_test) <= plotvars.lonmin:
            found_lon = True
            lons_offset = ilon

    if found_lon:
        lons_ugrid = lons_ugrid + lons_offset
        pts = np.where(lons_ugrid < plotvars.lonmin)
        lons_ugrid[pts] = lons_ugrid[pts] + 360.0
    else:
        errstr = '/n/n cf-plot error - cannot determine grid offset in add_cyclic_ugrid/n/n'
        raise Warning(errstr)

    field_wrap = deepcopy(field_ugrid)
    lons_wrap = deepcopy(lons_ugrid)
    lats_wrap = deepcopy(lats_ugrid)
    delta = 120.0

    pts_left = np.where(lons_wrap >= plotvars.lonmin + 360 - delta)
    lons_left = lons_wrap[pts_left] - 360.0
    lats_left = lats_wrap[pts_left]
    field_left = field_wrap[pts_left]

    field_wrap = np.concatenate([field_wrap, field_left])
    lons_wrap = np.concatenate([lons_wrap, lons_left])
    lats_wrap = np.concatenate([lats_wrap, lats_left])

    # Make a line of interpolated data on left hand side of plot and insert this into the data 
    # on both the left and the right before contouring
    lons_new = np.zeros(181) + plotvars.lonmin
    lats_new = np.arange(181) - 90
    field_new = griddata((lons_wrap, lats_wrap), field_wrap, (lons_new, lats_new), method='linear')

    # Remove any non finite points in the interpolated data
    pts = np.where(np.isfinite(field_new))
    field_new = field_new[pts]
    lons_new = lons_new[pts]
    lats_new = lats_new[pts]

    # Add the interpolated data to the left
    field_ugrid = np.concatenate([field_ugrid, field_new])
    lons_ugrid = np.concatenate([lons_ugrid, lons_new])
    lats_ugrid = np.concatenate([lats_ugrid, lats_new])

    # Add to the right if a fiull globe is being plotted
    # The 359.99 here is needed or Cartopy will map 360 back to 0

    if plotvars.lonmax - plotvars.lonmin == 360:
        field_ugrid = np.concatenate([field_ugrid, field_new])
        lons_ugrid = np.concatenate([lons_ugrid, lons_new + 359.95])
        lats_ugrid = np.concatenate([lats_ugrid, lats_new])
    else:
        lons_new2 = np.zeros(181) + plotvars.lonmax
        lats_new2 = np.arange(181) - 90
        field_new2 = griddata((lons_wrap, lats_wrap), field_wrap, (lons_new2, lats_new2), method='linear')

        # Remove any non finite points in the interpolated data
        pts = np.where(np.isfinite(field_new2))
        field_new2 = field_new2[pts]
        lons_new2 = lons_new2[pts]
        lats_new2 = lats_new2[pts]

        # Add the interpolated data to the right
        field_ugrid = np.concatenate([field_ugrid, field_new2])
        lons_ugrid = np.concatenate([lons_ugrid, lons_new2])
        lats_ugrid = np.concatenate([lats_ugrid, lats_new2])

    # Finally remove any point off to the right of plotvars.lonmax
    pts = np.where(lons_ugrid <= plotvars.lonmax)
    if np.size(pts) > 0:
        field_ugrid = field_ugrid[pts]
        lons_ugrid = lons_ugrid[pts]
        lats_ugrid = lats_ugrid[pts]

    return field_ugrid, lons_ugrid, lats_ugrid



def max_ndecs_data(data):
    ndecs_max = 1
    data_ndecs = np.zeros(len(data))
    for i in np.arange(len(data)):
        data_ndecs[i] = len(str(data[i]).split('.')[1])

    if max(data_ndecs) >= ndecs_max:
        # Reset large decimal vales to zero
        if min(data_ndecs) < 10:
            pts = np.where(data_ndecs >= 10)
            data_ndecs[pts] = 0
            ndecs_max = int(max(data_ndecs))

    return ndecs_max


def fix_floats(data):
    """
    | fix_floats fixes numpy rounding issues where 0.4 becomes
    | 0.399999999999999999999
    |
    """

    # Return unchecked if any values have an e in them, for example 7.85e-8
    has_e = False
    for val in data:
        if 'e' in str(val):
            has_e = True
    if has_e:
        return(data)

    data_ndecs = np.zeros(len(data))
    for i in np.arange(len(data)):
        data_ndecs[i] = len(str(float(data[i])).split('.')[1])

    if max(data_ndecs) >= 10:
        # Reset large decimal vales to zero
        if min(data_ndecs) < 10:
            pts = np.where(data_ndecs >= 10)
            data_ndecs[pts] = 0
            ndecs_max = int(max(data_ndecs))
            # Reset to new ndecs_max decimal places
            for i in np.arange(len(data)):
                data[i] = round(data[i], ndecs_max)
        else:
            # fix to two or more decimal places
            nd = 2
            data_range = 0.0
            data_temp = data

            while data_range == 0.0:
                data_temp = deepcopy(data)

                for i in np.arange(len(data_temp)):
                    data_temp[i] = round(data_temp[i], nd)

                data_range = np.max(data_temp) - np.min(data_temp)
                nd = nd + 1

            data = data_temp

    return(data)


def calculate_levels(field=None, level_spacing=None, verbose=None):

    dmin = np.nanmin(field)
    dmax = np.nanmax(field)

    tight = True

    field2 = deepcopy(field)




    if plotvars.user_levs == 1:
        # User defined
        if verbose:
            print('cfp.calculate_levels - using user defined contour levels')
        clevs = plotvars.levels
        mult = 0
        fmult = 1
    else:
        if plotvars.levels_step is None:
            # Automatic levels
            mult = 0
            fmult = 1
            if verbose:
                print('cfp.calculate_levels - generating automatic contour levels')

            if level_spacing == 'outlier' or level_spacing == 'inspect':
                hist = np.histogram(field, 100)[0]
                pts = np.size(field)
                rate = 0.01
                outlier_detected = False

                if sum(hist[1:-2]) ==0:
                    if hist[0] / hist[-1] < rate:
                        outlier_detected = True
                        pts = np.where(field == dmin)
                        field2[pts] = dmax
                        dmin = np.nanmin(field2)
                            
                    if hist[-1] / hist[0] < rate:
                        outlier_detected = True
                        pts = np.where(field == dmax)
                        field2[pts] = dmin
                        dmax = np.nanmax(field2)
                            
                clevs, mult = gvals(dmin=dmin, dmax=dmax)
                fmult = 10**-mult
                tight = False

            if level_spacing == 'linear':
                if isinstance(np.ma.min(dmin), np.ma.core.MaskedConstant) or \
                   isinstance(np.ma.min(dmax), np.ma.core.MaskedConstant):
                   errstr = 'cf-plot calculate_levels error - data is entirely masked\n'
                   errstr += 'setting levels to 0 and 0.1 to produce a plot'
                   print(errstr)
                   dmin = 0.0
                   dmax = 0.1

                #if dmax - dmin < 1e-12:
                #   errstr = 'cf-plot calculate_levels error - field difference is < 1e-12\n'
                #   errstr += 'setting levels to min-0.1 and min+0.1 to produce a plot'
                #   print(errstr)
                #   dmin = dmin - 1
                #   dmax = dmin + 1
                   
                clevs, mult = gvals(dmin=dmin, dmax=dmax)
                fmult = 10**-mult
                tight = False

            if level_spacing == 'log' or level_spacing == 'loglike':

                if dmin < 0.0 and dmax < 0.0:
                    dmin1 = abs(dmax)
                    dmax1 = abs(dmin)

                if dmin > 0.0 and dmax > 0.0:
                    dmin1 = abs(dmin)
                    dmax1 = abs(dmax)

                if dmin <= 0.0 and dmax >= 0.0:
                    dmax1 = max(abs(dmin), dmax)
                    pts = np.where(field < 0.0)
                    close_below = np.max(field[pts])
                    pts = np.where(field > 0.0)
                    close_above = np.min(field[pts])
                    dmin1 = min(abs(close_below), close_above)

                # Generate levels 
                if level_spacing == 'log':
                    clevs = []
                    for i in np.arange(31):
                        val = 10**(i-30.)
                        clevs.append("{:.0e}".format(val))

                if level_spacing == 'loglike':
                    clevs = []
                    for i in np.arange(61):
                        val = 10**(i-30.)
                        clevs.append("{:.0e}".format(val))
                        clevs.append("{:.0e}".format(val*2))
                        clevs.append("{:.0e}".format(val*5))
                    clevs = np.float64(clevs)

                # Remove out of range levels
                clevs = np.float64(clevs)
                pts = np.where(np.logical_and(clevs >= abs(dmin1), clevs <= abs(dmax1)))
                clevs = clevs[pts]

                if dmin < 0.0 and dmax < 0.0:
                    clevs = -1.0*clevs[::-1]

                if dmin <= 0.0 and dmax >= 0.0:
                    clevs = np.concatenate([-1.0*clevs[::-1], [0.0], clevs])

    # Use step to generate the levels
    if plotvars.levels_step is not None:
        if verbose:
            print('calculate_levels - using specified step to generate contour levels')

        step = plotvars.levels_step

        if isinstance(step, int):
            dmin = int(dmin)
            dmax = int(dmax)

        fmult = 1
        mult = 0
        clevs = []
        if dmin < 0:
            clevs = ((np.arange(-1*dmin/step+1)*-step)[::-1])
        if dmax > 0:
            if np.size(clevs) > 0:
                clevs = np.concatenate((clevs[:-1], np.arange(dmax/step+1)*step))
            else:
                clevs = np.arange(dmax/step+1)*step
        if isinstance(step, int):
            clevs = clevs.astype(int)

    # Remove any out of data range values
    if tight:
        pts = np.where(np.logical_and(clevs >= dmin, clevs <= dmax))
        clevs = clevs[pts]

    # Add an extra contour level if less than two levels are present
    if np.size(clevs) < 2:
        clevs.append(clevs[0]+0.001)

    # Test for large numer of decimal places and fix if necessary
    if plotvars.levels is None:
        if isinstance(clevs[0], float):
            clevs = fix_floats(clevs)

    return(clevs, mult, fmult)


def stream(u=None, v=None, x=None, y=None, density=None, linewidth=None,
           color=None, arrowsize=None, arrowstyle=None, minlength=None,
           maxlength=None, axes=True,
           xaxis=True, yaxis=True, xticks=None, xticklabels=None, yticks=None,
           yticklabels=None, xlabel=None, ylabel=None, title=None,
           zorder=None):
    """
     | stream - plot a streamplot which is used to show fluid flow and 2D field gradients
     |
     | u=None - u wind
     | v=None - v wind
     | x=None - x locations of u and v
     | y=None - y locations of u and v
     | density=None - controls the closeness of streamlines. When density = 1,
     |                the domain is divided into a 30x30 grid
     | linewidth=None - the width of the stream lines. With a 2D array the line width
     |                  can be varied across the grid. The array must have the same shape
     |                  as u and v
     | color=None - the streamline color
     | arrowsize=None - scaling factor for the arrow size
     | arrowstyle=None - arrow style specification
     | minlength=None - minimum length of streamline in axes coordinates
     | maxlength=None - maximum length of streamline in axes coordinates
     | axes=True - plot x and y axes
     | xaxis=True - plot xaxis
     | yaxis=True - plot y axis
     | xticks=None - xtick positions
     | xticklabels=None - xtick labels
     | yticks=None - y tick positions
     | yticklabels=None - ytick labels
     | xlabel=None - label for x axis
     | ylabel=None - label for y axis
     | title=None - title for plot
     | zorder=None - plotting order
     |
     :Returns:
      None
     |
     |
     |
    """

    colorbar_title = ''
    if title is None:
        title = ''
    text_fontsize = plotvars.text_fontsize
    continent_thickness = plotvars.continent_thickness
    continent_color = plotvars.continent_color
    if text_fontsize is None:
        text_fontsize = 11
    if continent_thickness is None:
        continent_thickness = 1.5
    if continent_color is None:
        continent_color = 'k'
    title_fontsize = plotvars.title_fontsize
    if title_fontsize is None:
        title_fontsize = 15
    resolution_orig = plotvars.resolution
    rotated_vect = False

    # Set potential user axis labels
    user_xlabel = xlabel
    user_ylabel = ylabel

    # Set any additional arguments to streamplot
    plotargs = {}
    if density is not None:
        plotargs['density'] = density
    if linewidth is not None:
        plotargs['linewidth'] = linewidth
    if color is not None:
        plotargs['color'] = color
    if arrowsize is not None:
        plotargs['arrowsize'] = arrowsize
    if arrowstyle is not None:
        plotargs['arrowstyle'] = arrowstyle
    if minlength is not None:
        plotargs['minlength'] = minlength
    if maxlength is not None:
        plotargs['maxlength'] = maxlength

    # Extract required data
    # If a cf-python field
    if isinstance(u, cf.Field):

        # Check data is 2D
        ndims = np.squeeze(u.data).ndim
        if ndims != 2:
            errstr = "\n\ncfp.vect error need a 2 dimensonal u field to make vectors\n"
            errstr += "received " + str(np.squeeze(u.data).ndim)
            if ndims == 1:
                errstr += " dimension\n\n"
            else:
                errstr += " dimensions\n\n"
            raise TypeError(errstr)

        u_data, u_x, u_y, ptype, colorbar_title, xlabel, ylabel, xpole, \
            ypole = cf_data_assign(u, colorbar_title, rotated_vect=rotated_vect)
    elif isinstance(u, cf.FieldList):
        raise TypeError("Can't plot a field list")
    else:
        # field=f #field data passed in as f
        check_data(u, x, y)
        u_data = deepcopy(u)
        u_x = deepcopy(x)
        u_y = deepcopy(y)
        xlabel = ''
        ylabel = ''

    if isinstance(v, cf.Field):

        # Check data is 2D
        ndims = np.squeeze(v.data).ndim
        if ndims != 2:
            errstr = "\n\ncfp.vect error need a 2 dimensonal v field to make vectors\n"
            errstr += "received " + str(np.squeeze(v.data).ndim)
            if ndims == 1:
                errstr += " dimension\n\n"
            else:
                errstr += " dimensions\n\n"
            raise TypeError(errstr)

        v_data, v_x, v_y, ptype, colorbar_title, xlabel, ylabel, xpole, \
            ypole = cf_data_assign(v, colorbar_title, rotated_vect=rotated_vect)
    elif isinstance(v, cf.FieldList):
        raise TypeError("Can't plot a field list")
    else:
        # field=f #field data passed in as f
        check_data(v, x, y)
        v_data = deepcopy(v)
        xlabel = ''
        ylabel = ''

    # Reset xlabel and ylabel values with user defined labels in specified
    if user_xlabel is not None:
        xlabel = user_xlabel
    if user_ylabel is not None:
        ylabel = user_ylabel

    # Retrieve any user defined axis labels
    if xlabel == '' and plotvars.xlabel is not None:
        xlabel = plotvars.xlabel
    if ylabel == '' and plotvars.ylabel is not None:
        ylabel = plotvars.ylabel
    if xticks is None and plotvars.xticks is not None:
        xticks = plotvars.xticks
        if plotvars.xticklabels is not None:
            xticklabels = plotvars.xticklabels
        else:
            xticklabels = list(map(str, xticks))
    if yticks is None and plotvars.yticks is not None:
        yticks = plotvars.yticks
        if plotvars.yticklabels is not None:
            yticklabels = plotvars.yticklabels
        else:
            yticklabels = list(map(str, yticks))

    # Open a new plot if necessary
    if plotvars.user_plot == 0:
        gopen(user_plot=0)

    # Call gpos(1) if not already called
    if plotvars.rows > 1 or plotvars.columns > 1:
        if plotvars.gpos_called is False:
            gpos(1)

    # Set plot type if user specified
    if (ptype is not None):
        plotvars.plot_type = ptype

    lonrange = np.nanmax(u_x) - np.nanmin(u_x)
    latrange = np.nanmax(u_y) - np.nanmin(u_y)

    if plotvars.plot_type == 1:
        # Set up mapping
        if (lonrange > 350 and latrange > 170) or plotvars.user_mapset == 1:
            set_map()
        else:
            mapset(lonmin=np.nanmin(u_x), lonmax=np.nanmax(u_x),
                   latmin=np.nanmin(u_y), latmax=np.nanmax(u_y),
                   user_mapset=0, resolution=resolution_orig)
            set_map()

        mymap = plotvars.mymap

    # Map streamplot
    if plotvars.plot_type == 1:

        plotvars.mymap.streamplot(u_x, u_y, u_data, v_data,
                                  transform=ccrs.PlateCarree(),
                                  **plotargs)

        # axes
        plot_map_axes(axes=axes, xaxis=xaxis, yaxis=yaxis,
                      xticks=xticks, xticklabels=xticklabels,
                      yticks=yticks, yticklabels=yticklabels,
                      user_xlabel=user_xlabel, user_ylabel=user_ylabel,
                      verbose=False)

        # Coastlines
        continent_thickness = plotvars.continent_thickness
        continent_color = plotvars.continent_color
        continent_linestyle = plotvars.continent_linestyle
        if continent_thickness is None:
            continent_thickness = 1.5
        if continent_color is None:
            continent_color = 'k'
        if continent_linestyle is None:
            continent_linestyle = 'solid'

        feature = cfeature.NaturalEarthFeature(
                      name='land', category='physical',
                      scale=plotvars.resolution,
                      facecolor='none')
        mymap.add_feature(feature, edgecolor=continent_color,
                          linewidth=continent_thickness,
                          linestyle=continent_linestyle)

        # Title
        if title is not None:
            map_title(title)

    ##########
    # Save plot
    ##########
    if plotvars.user_plot == 0:
        gset()
        cscale()
        gclose()

    if plotvars.user_mapset == 0:
        mapset()
        mapset(resolution=resolution_orig)


def bfill_ugrid(f=None, face_lons=None, face_lats=None, face_connectivity=None, clevs=None,
                alpha=None, zorder=None):

    """
     | bfill_ugrid - block fill a UGRID field with colour rectangles
     | This is an internal routine and is not generally used by the user.
     |
     | f=None - field
     | face_lons=None - longitude points for face vertices
     | face_lats=None - latitude points for face verticies
     | face_connectivity=None - connectivity for face verticies
     | clevs=None - levels for filling
     | lonlat=False - lonlat data
     | bound=False - x and y are cf data boundaries
     | alpha=alpha - transparency setting 0 to 1
     | zorder=None - plotting order
     |
      :Returns:
        None
     |
     |
     |
     |
    """



    # Colour faces according to value
    # Set faces to white initially
    cols = ['#000000' for x in range(len(face_connectivity))]

    levs = deepcopy(np.array(clevs))

    if plotvars.levels_extend == 'min' or plotvars.levels_extend == 'both':
        levs = np.concatenate([[-1e20], levs])
    ilevs_max = np.size(levs)
    if plotvars.levels_extend == 'max' or plotvars.levels_extend == 'both':
        levs = np.concatenate([levs, [1e20]])
    else:
        ilevs_max = ilevs_max - 1

    for ilev in np.arange(ilevs_max):
        lev = levs[ilev]  
        col = plotvars.cs[ilev]
        pts = np.where(f.squeeze() >= lev)[0]


        if np.min(pts) >= 0:
            for val in np.arange(np.size(pts)):
                pt = pts[val]

                cols[pt]=col
    
    plotargs = {'transform': ccrs.PlateCarree()}

    coords_all = []

    for iface in np.arange(len(face_connectivity)):
        lons = np.array([face_lons[i] for i in face_connectivity[iface]])
        lats = np.array([face_lats[i] for i in face_connectivity[iface]])

        coords = [(lons[i], lats[i]) for i in np.arange(len(lons))]

        if (np.max(lons) - np.min(lons)) > 100: 
            if np.max(lons) > 180:
                for i in np.arange(len(lons)):
                    lons[i] = (lons[i] + 180) % 360 - 180

            else:
                for i in np.arange(len(lons)):
                    lons[i] = lons[i] % 360

            coords = [(lons[i], lats[i]) for i in np.arange(len(lons))]

        # Add extra verticies if any of the points are at the north or south pole
        if np.max(lats) == 90 or np.min(lats) == -90:
            geom = sgeom.Polygon([(face_lons[i], face_lats[i]) for i in face_connectivity[iface]])
            geom_cyl = ccrs.PlateCarree().project_geometry(geom, ccrs.Geodetic())
            coords = geom_cyl[0].exterior.coords[:]

        coords_all.append(coords)

    plotvars.mymap.add_collection(PolyCollection(coords_all, facecolors=cols, edgecolors=None,
                                  alpha=alpha, zorder=zorder, **plotargs))











def generate_titles(f=None):
    '''Generate a set of title dims to put at the top of plots'''

    mycoords = find_dim_names(f)
    well_formed = check_well_formed(f)

    title_dims = ''
    if isinstance(f, cf.Field):
        for idim in np.arange(len(mycoords)):
            mycoord = mycoords[idim]
            if mycoord == 'Z':
                mycoord = find_z(f)
            
            title, units = cf_var_name_titles(f, mycoord)
            if not f.coord(mycoord).T:
                values = f.construct(mycoord).array
                if len(values) > 1:
                    value = ''
                else:
                    value = str(values)
                title_dims += mycoord + ': ' + title + ' ' + value + ' '  + units + '\n'
                
            else:
                #if well_formed:
                #    values = f.construct(mycoord).dtarray
                #else:
                #    values = f.construct(mycoord).array
                    
                values = f.construct(mycoord).dtarray    
                    
                    
                if len(values) > 1:
                    value = ''
                else:
                    value = str(cf.Data(values).datetime_as_string)
                title_dims += mycoord + ': '  + title + ' ' + value + '\n'

  
        if len(f.cell_methods()) > 0:                    
            title_dims += 'cell_methods: '
            i = 0

            for method in f.cell_methods():
                axis = f.cell_methods()[method].get_axes()[0]
                try:
                    # Change domainaxis0 etc to an axis
                    myid = f.constructs.domain_axis_identity(axis)
                except:
                    myid = axis
        
                value = ''
                if f.cell_methods()[method].has_method(): 
                    value = f.cell_methods()[method].get_method()       
    
                qualifiers = f.cell_methods()[method].qualifiers()
                qualifier_text = ''
                if len(qualifiers) > 0:
                    qualifier_text = str(qualifiers)   
    
                if i > 0:
                    title_dims += ', '

                title_dims += myid + ': ' + value + ' ' + qualifier_text
        
                i += 1
                                            
    return title_dims


def check_well_formed(field):
    ''' 
        Check the coordinates are all recognizably of the form X, Y, Z, T
        returns boolean
    ''' 
            
    coords = list(field.coords())
    mycoords = deepcopy(coords)
        
    for i in np.arange(len(coords)):
        c = field.coord(coords[i])
        if c.X:
            mycoords[i] = 'X'
        if c.Y:
            mycoords[i] = 'Y'
        if c.Z:
            mycoords[i] = 'Z'
        if c.T:
            mycoords[i] = 'T'
            
        
    # Check if the coordtinates are all of the form X, Y, Z, T    
    well_formed = True
    dimension_coords = ['dimensioncoordinate0','dimensioncoordinate1','dimensioncoordinate2','dimensioncoordinate3']
    for i in np.arange(4):
        if dimension_coords[i] in mycoords:
            well_formed = False
                
        
    return well_formed






def find_dim_names(field):
    ''' Find the field dimension coordinate names
        Ignores auxiliary coordinates (for now)
        returns:
        coordinates in the order [T, X, Y, Z]       
    '''
        
    # Get the field domain axes
    daxes = list(field.get_data_axes())
        
    # Get the field coordinates
    dcoords = list(field.coords())     
        
        
    # Calculate the number of coordinates of type X, Y, Z and T
    nx = 0
    ny = 0
    nz = 0
    nt = 0
    for i in np.arange(len(dcoords)):
        if field.coord(dcoords[i]).X:
            nx += 1
        if field.coord(dcoords[i]).Y:
            ny += 1            
        if field.coord(dcoords[i]).Z:
            nz += 1        
        if field.coord(dcoords[i]).T:
            #print('ajh - t found - ', coords[i])
            nt += 1      
                
                
    #print('ajh - find_dim_names - nx, ny, nz, nt are ', nx, ny, nz, nt)
        
   
    # Strip out any auxiliary coordinates if the field is not a trajectory field
    remove_aux = True
    if field.get_property('featureType', False) is not False:
        if field.featureType == 'trajectory':
            remove_aux = False
                
                
    # Strip out any auxiliary coordinates if the field is not a trajectory field
    if remove_aux:
        for i in np.arange(len(dcoords)):
            if dcoords[i][:-1] == 'auxiliarycoordinate':
                dcoords[i] = 'aux' 
        dcoords = list(filter(('aux').__ne__,dcoords))
        
        
    #print('ajh - daxes are', daxes)
    #print('ajh - dcoords are', dcoords)
        
        
        
    # Convert these into corresponding dimension coordinates
    if remove_aux:
        coords = []
        for i in np.arange(len(daxes)):
            val = daxes[i]
            coord = None
            for j in np.arange(len(dcoords)):
            
                #print(ajh - daxes[i], dcoords[j], field.get_data_axes(dcoords[j])[0])
                
                if daxes[i] == field.get_data_axes(dcoords[j])[0]:
                    coord = dcoords[j]      
        
            if coord is not None:
                coords.append(coord)
            else:
                errstr = 'find_data_names error  - cannot find a coordinate for ' + daxes[i] + '\n'
                errstr += 'in the data\n'
                raise Warning(errstr)
    else:
        coords = dcoords
        
    #print('ajh - coords are', coords)
    #print('ajh - dcoords are', dcoords)
        

                
    # Make a copy of coords in mycoords
    mycoords = deepcopy(coords)
        
    # Convert to X, Y, Z, T if coordinate is one of these
    # If the number of coordinates of this type is greater than 1 then don't do this as f.coord('Z') gives an 
    # error as there are more that one coordinates to return
    for i in np.arange(len(daxes)):
        if field.coord(coords[i]).X:
            if nx == 1:
                mycoords[i] = 'X'
        if field.coord(coords[i]).Y:
            if ny == 1:
                mycoords[i] = 'Y'            
        if field.coord(coords[i]).Z:
            if nz == 1:
                mycoords[i] = 'Z'  
        if field.coord(coords[i]).T:
            if nt == 1:
                mycoords[i] = 'T'            
            
            
    # Return the reverse of the coordinates so that they are in the order [X, Y, Z, T]
    mycoords.reverse()
        
    #print('ajh - find_dim_names - mycoords are ', mycoords)
        
    return mycoords


def find_z(f):
    ''' Find the Z coordinate if it exists'''

    # Return if f is undefined
    if f is None:
        return None
        
        
    myz ='Z'
    z_count = 0
    z_names =[]
    
    mycoords = find_dim_names(f)
    
    myz = None
    for mycoord in mycoords:
        if f.coord(mycoord).Z:
            myz = mycoord

    #if myz is None:
    #    errstr = 'cf-plot error - cannot find the Z coordinate'
    #    raise Warning(errstr)

    return myz









