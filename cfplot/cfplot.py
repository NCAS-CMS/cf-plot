"""
Climate contour/vector plots using cf-python, matplotlib and cartopy.
Andy Heaps NCAS-CMS September 2018
"""
import cf
import numpy as np
import subprocess
from scipy import interpolate
import time
import matplotlib
from copy import deepcopy
import os
import sys
import matplotlib.pyplot as plot
from matplotlib.path import Path
import matplotlib.patches as mpatches
from matplotlib.collections import PolyCollection
from distutils.version import StrictVersion
import cartopy
import cartopy.crs as ccrs
import cartopy.util as cartopy_util
import cartopy.feature as cfeature


class pvars(object):

    def __init__(self, **kwargs):
        '''Initialize a new Pvars instance'''
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

    def __str__(self):
        '''x.__str__() <==> str(x)'''
        out = ['%s = %s' % (a, repr(v))]
        for a, v in self.__dict__.iteritems():
            return '\n'.join(out)

cf_version_min = '1.0.1'
cf_errstr = '\n cf-python > ' + cf_version_min + \
    ' needs to be installed to use cf-plot \n'
try:
    import cf
    if StrictVersion(cf.__version__) < StrictVersion(cf_version_min):
        raise Warning(cf_errstr)
except ImportError:
    raise Warning(cf_errstr)


# Check for a display and use the Agg backing store if none is present
# This is for batch mode processing
try:
    disp = os.environ["DISPLAY"]
except:
    matplotlib.use('Agg')


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
global_fill=True
global_lines=True
global_blockfill=False
global_degsym=False
defaults_file=os.path.expanduser("~")+'/.cfplot_defaults'
if os.path.exists(defaults_file):
    with open(defaults_file) as file: 
        for line in file: 
            vals=line.split(' ')
            com, val = vals
            v=False
            if val.strip() == 'True':
                v=True
            if com == 'blockfill':
                global_blockfill=v
            if com == 'lines':
                global_lines=v
            if com == 'fill':
                 global_fill=v
            if com == 'degsym':
                 global_degsym=v



#####################################
# plotvars - global plotting variables
#####################################
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
                 pos=1, viewer='display',
                 tspace_year=None, tspace_month=None, tspace_day=None,
                 tspace_hour=None, xtick_label_rotation=0,
                 xtick_label_align='center', ytick_label_rotation=0,
                 ytick_label_align='right', legend_text_size=11,
                 legend_text_weight='normal', tight=False,
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
                 grid_lons=None, grid_lats=None,
                 grid_colour='grey', grid_linestyle='--', 
                 grid_thickness=1.0)


# Check for iPython notebook inline
# and set the viewer to None if found
is_inline = 'inline' in matplotlib.get_backend()
if is_inline:
    plotvars.viewer=None





def con(f=None, x=None, y=None, fill=global_fill, lines=global_lines, line_labels=True,
        title=None, colorbar_title=None, colorbar=True,
        colorbar_label_skip=None, ptype=0, negative_linestyle='solid',
        blockfill=global_blockfill, zero_thick=False, colorbar_shrink=None,
        colorbar_orientation=None, colorbar_position=None, xlog=False,
        ylog=False, axes=True, xaxis=True, yaxis=True, xticks=None,
        xticklabels=None, yticks=None, yticklabels=None, xlabel=None,
        ylabel=None, colors='k', swap_axes=False, verbose=None,
        linewidths=None, alpha=1.0, colorbar_text_up_down=False,
        colorbar_text_down_up=False, colorbar_drawedges=True,
        linestyles=None, zorder=None):
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
     | colorbar=1 - add a colour bar if a filled contour plot
     | colorbar_label_skip=None - skip colour bar labels. Set to 2 to skip
     |                            every other label. 
     | colorbar_orientation=None - options are 'horizontal' and 'vertical'
     |                      The default for most plots is horizontal but
     |                      for polar stereographic plots this is vertical.
     | colorbar_shrink=None - value to shrink the colorbar by.  If the colorbar
     |                        exceeds the plot area then values of 1.0, 0.55
     |                        or 0.5m ay help it better fit the plot area.
     | colorbar_position=None - position of colorbar
     |                          [xmin, ymin, x_extent,y_extent] in normalised
     |                          coordinates. Use when a common colorbar
     |                          is required for a set of plots. A typical set
     |                          of values would be [0.1, 0.05, 0.8, 0.02]
     | colorbar_text_up_down=False - if True horizontal colour bar labels alternate
     |                             above (start) and below the colour bar
     | colorbar_text_down_up=False - if True horizontal colour bar labels alternate
     |                             below (start) and above the colour bar
     | colorbar_drawedges=True - Draw internal divisions in the colorbar
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
     | colorbar_text_up_down=False - on a horizontal colorbar alternate the 
     |                               labels top and bottom starting in the up position 
     | colorbar_text_down_up=False - on a horizontal colorbar alternate the 
     |                               labels bottom and top starting in the bottom position 
     | colorbar_drawedges=True - draw internal delimeter lines in the colorbar
     | zorder=None - order of drawing
     :Returns:
      None

    """



    # Turn off divide warning in contour routine which is a numpy issue
    old_settings = np.seterr(all='ignore')
    np.seterr(divide='ignore')

    # Set potential user axis labels
    user_xlabel = xlabel
    user_ylabel = ylabel

    # Extract required data for contouring
    # If a cf-python field
    if isinstance(f, cf.Field):
        # Extract data
        if verbose:
            print 'con - calling cf_data_assign'

        field, x, y, ptype, colorbar_title, xlabel, ylabel, xpole, ypole =\
            cf_data_assign(f, colorbar_title, verbose=verbose)

        if user_xlabel is not None:
            xlabel = user_xlabel
        if user_ylabel is not None:
            ylabel = user_ylabel
    elif isinstance(f, cf.FieldList):
        raise TypeError("Can't plot a field list")
    else:
        if verbose:
            print 'con - using user assigned data'
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
        field_orig = field
        x_orig = x
        y_orig = y

        # Check number of colours and levels match if user has modified the  
        # number of colours
        if plotvars.cscale_flag == 2:
            if plotvars.user_levs == 0:
                errstr = "\n\nBlockfill error - need to match number of "
                errstr += "colours and contour intervals\n"
                raise TypeError(errstr)
            ncols=np.size(plotvars.cs)
            nintervals=np.size(plotvars.levels)-1
            if plotvars.levels_extend == 'min':
                nintervals += 1
            if plotvars.levels_extend == 'max':
                nintervals += 1
            if plotvars.levels_extend == 'both':
                nintervals += 2
            if ncols != nintervals:
                errstr = "\n\nBlockfill error - need to match number of "
                errstr += "colours and contour intervals\n"
                errstr += "Don't forget to take account of the colorbar "
                errstr += "extensions"
                raise TypeError(errstr)

    # Turn off colorbar if fill is turned off
    if not fill and not blockfill:
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
    resolution_orig=plotvars.resolution

    proj = plotvars.proj
    # Set size of color bar if not specified
    if colorbar_shrink is None:
        colorbar_shrink = 1.0
        if plotvars.plot_type == 1:
            scale = (plotvars.lonmax - plotvars.lonmin) / \
                (plotvars.latmax - plotvars.latmin)
            if scale <= 1:
                colorbar_shrink = 0.55
            if plotvars.orientation == 'landscape':
                if (proj == 'cyl' and colorbar_orientation == 'vertical'):
                    colorbar_shrink = 0.5
                if (proj == 'cyl' and colorbar_orientation == 'horizontal'):
                    colorbar_shrink = 1.0
            if plotvars.orientation == 'portrait':
                if (proj == 'cyl' and colorbar_orientation == 'vertical'):
                    colorbar_shrink = 0.25
                if (proj == 'cyl' and colorbar_orientation == 'horizontal'):
                    colorbar_shrink = 1.0

            if plotvars.proj == 'npstere' or plotvars.proj == 'spstere':
                if plotvars.orientation == 'landscape':
                    if colorbar_orientation == 'horizontal':
                        colorbar_shrink = 1.0
                    if colorbar_orientation == 'vertical':
                        colorbar_shrink = 1.0
                if plotvars.orientation == 'portrait':
                    if colorbar_orientation == 'horizontal':
                        colorbar_shrink = 1.0
                    if colorbar_orientation == 'vertical':
                        colorbar_shrink = 1.0

    # Set plot type if user specified
    if (ptype is not None):
        plotvars.plot_type = ptype

    # Get contour levels
    includes_zero = 0
    if plotvars.user_levs == 1:
        # User defined
        if verbose:
            print 'con - using user defined contour levels'
        clevs = plotvars.levels
        mult = 0
        fmult = 1
    else:
        if plotvars.levels_step is None:
            # Automatic levels
            if verbose:
                print 'con - generating automatic contour levels'
            dmin = np.nanmin(field)
            dmax = np.nanmax(field)
            clevs, mult = gvals(dmin=dmin, dmax=dmax, tight=0)
            fmult = 10**-mult
        else:
            # Use step to generate the levels
            step = plotvars.levels_step
            dmin = np.nanmin(field)
            dmax = np.nanmax(field)
            if isinstance(step, (int, long)):
                dmin = int(np.nanmin(field))
                dmax = int(np.nanmax(field))
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

            # Strip out any outlying values
            pts = np.where(np.logical_and(clevs >= dmin, clevs <= dmax))
            clevs = clevs[pts]

            # Throw an error if less than two levels
            if np.size(clevs) < 2:
                errstr = "\n\ncfp.con error - need more than two levels "
                errstr += "to make a contour plot\n"
                raise TypeError(errstr)




    # Set the colour scale
    # Nothing defined
    if plotvars.cscale_flag == 0:
        includes_zero = 0
        col_zero = 0
        for cval in clevs:
            if includes_zero == 0:
                col_zero = col_zero + 1
            if cval == 0:
                includes_zero = 1

        if includes_zero == 1:
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
            ncols=ncols=np.size(clevs)+1
            if plotvars.levels_extend == 'min' or plotvars.levels_extend == 'max':
                ncols=ncols-1
            if plotvars.levels_extend == 'neither':
                ncols=ncols-2
            cscale('viridis', ncols=ncols)

        plotvars.cscale_flag = 0

    # User selected colour map but no mods so fit to levels
    if plotvars.cscale_flag == 1:
        ncols=ncols=np.size(clevs)+1
        if plotvars.levels_extend == 'min' or plotvars.levels_extend == 'max':
            ncols=ncols-1
        if plotvars.levels_extend == 'neither':
            ncols=ncols-2
        cscale(plotvars.cs_user, ncols=ncols)
        plotvars.cscale_flag = 1

    # Set colorbar labels
    # Set a sensible label spacing if the user hasn't already done so
    if colorbar_label_skip is None:
        if colorbar_orientation == 'horizontal':
            nchars = 0
            for lev in clevs:
                nchars = nchars + len(str(lev))
            colorbar_label_skip = nchars / 80 + 1
            if plotvars.columns > 1:
                colorbar_label_skip = nchars * (plotvars.columns) / 80
        else:
            colorbar_label_skip = 1

    if colorbar_label_skip > 1:
        if includes_zero:
            # include zero in the colorbar labels
            zero_pos = [i for i, mylev in enumerate(clevs) if mylev == 0][0]
            colorbar_labels = clevs[zero_pos]
            i = zero_pos + colorbar_label_skip
            while i <= len(clevs) - 1:
                colorbar_labels = np.append(colorbar_labels, clevs[i])
                i = i + colorbar_label_skip
            i = zero_pos - colorbar_label_skip
            if i >= 0:
                while i >= 0:
                    colorbar_labels = np.append(clevs[i], colorbar_labels)
                    i = i - colorbar_label_skip
        else:
            colorbar_labels = clevs[0]
            i = colorbar_label_skip
            while i <= len(clevs) - 1:
                colorbar_labels = np.append(colorbar_labels, clevs[i])
                i = i + colorbar_label_skip
    else:
        colorbar_labels = clevs

    # Make a list of strings of the colorbar levels for later labeling
    clabels=[]
    for i in colorbar_labels:
        clabels.append(str(i))    

    # Add mult to colorbar_title if used
    if (colorbar_title is None):
        colorbar_title = ''
    if (mult != 0):
        colorbar_title = colorbar_title + ' *10$^{' + str(mult) + '}$'



    # Catch null titles
    if title is None:
        title = ''
    if plotvars.title is not None:
        title = plotvars.title

    # Set plot variables
    title_fontsize = plotvars.title_fontsize
    text_fontsize = plotvars.text_fontsize
    colorbar_fontsize = plotvars.colorbar_fontsize
    axis_label_fontsize = plotvars.axis_label_fontsize
    continent_thickness = plotvars.continent_thickness
    continent_color = plotvars.continent_color
    continent_linestyle = plotvars.continent_linestyle
    land_color = plotvars.land_color
    ocean_color = plotvars.ocean_color
    lake_color = plotvars.lake_color
    text_fontweight = plotvars.text_fontweight
    colorbar_fontweight = plotvars.colorbar_fontweight
    title_fontweight = plotvars.title_fontweight
    axis_label_fontweight = plotvars.axis_label_fontweight
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
            xticklabels = map(str, xticks)
    if yticks is None and plotvars.yticks is not None:
        yticks = plotvars.yticks
        if plotvars.yticklabels is not None:
            yticklabels = plotvars.yticklabels
        else:
            yticklabels = map(str, yticks)




    ##########
    # Map plot
    ##########
    if ptype == 1:
        if verbose:
            print 'con - making a map plot'

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
        if lonrange > 350 and np.ndim(y) == 1:
            # Add cyclic information if missing.
            if lonrange < 360:
                field, x = cartopy_util.add_cyclic_point(field, x)

                
                lonrange = np.nanmax(x) - np.nanmin(x)

                if x[-1] - x[0] == 360.0:
                    x[-1] = x[-1] + 0.001 # **cartopy line drawing fix


            # Shift grid if needed
            if plotvars.lonmin < np.nanmin(x):
                x = x - 360
            if plotvars.lonmin > np.nanmax(x):
                x = x + 360


        # Flip latitudes and field if latitudes are in descending order
        if np.ndim(y) == 1:
            if y[0] > y[-1]:
                y = y[::-1]
                field = np.flipud(field)

        # Plotting a sub-area of the grid produces stray contour labels
        # in polar plots. Subsample the grid to remove this problem
        if plotvars.proj == 'npstere':
            myypos = find_pos_in_array(vals=y, val=plotvars.boundinglat)
            if myypos != -1:
                y = y[myypos:]
                field = field[myypos:, :]

        if plotvars.proj == 'spstere':
            myypos = find_pos_in_array(
                vals=y, val=plotvars.boundinglat, above=1)
            if myypos != -1:
                y = y[0:myypos + 1]
                field = field[0:myypos + 1, :]


        # Create the meshgrid if required


        if (np.ndim(field) == 1 and np.ndim(x) == 1 and np.ndim(y) == 1):
            lons = x
            lats = y
        if (np.ndim(field) == 2 and np.ndim(x) == 2 and np.ndim(y) == 2):
            lons = x
            lats = y
        if (np.ndim(field) == 2 and np.ndim(x) == 1 and np.ndim(y) == 1):
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
                gset(
                    xmin=plotvars.lonmin,
                    xmax=plotvars.lonmax,
                    ymin=plotvars.latmin,
                    ymax=plotvars.latmax,
                    user_gset=0)
            else:
                gset(
                    xmin=np.nanmin(lons),
                    xmax=np.nanmax(lons),
                    ymin=np.nanmin(lats),
                    ymax=np.nanmax(lats),
                    user_gset=0)


        # Filled contours
        if fill or blockfill:
            if verbose:
                print 'con - adding filled contours'
            # Get colour scale for use in contouring
            # If colour bar extensions are enabled then the colour map goes
            # from 1 to ncols-2.  The colours for the colour bar extensions
            # are then changed on the colourbar and plot after the plot is made
            cscale_ncols = np.size(plotvars.cs)
            colmap = cscale_get_map()


            cmap = matplotlib.colors.ListedColormap(colmap)
            if (plotvars.levels_extend ==
                    'min' or plotvars.levels_extend == 'both'):
                cmap.set_under(plotvars.cs[0])
            if (plotvars.levels_extend ==
                    'max' or plotvars.levels_extend == 'both'):
                cmap.set_over(plotvars.cs[-1])

            # filled colour contours
            cfill = mymap.contourf(lons, lats, field * fmult, clevs,
                                   extend=plotvars.levels_extend,
                                   cmap=cmap, norm=plotvars.norm,
                                   alpha=alpha, transform=ccrs.PlateCarree(),
                                   zorder=zorder)






        # Block fill
        if blockfill:
            if verbose:
                print 'con - adding blockfill'
            if isinstance(f, cf.Field):


                if f.ref('transverse_mercator'):
                    # Special case for transverse mercator
                    bfill(
                        f=f,
                        clevs=clevs,
                        alpha=alpha, zorder=zorder)

                else:

                    if getattr(f.coord('lon'), 'hasbounds', False):
                        xpts = np.squeeze(f.coord('lon').bounds.array[:, 0])
                        ypts = np.squeeze(f.coord('lat').bounds.array[:, 0])
                        # Add last longitude point
                        xpts = np.append(xpts, f.coord('lon').bounds.array[-1, 1])
                        # Add last latitude point
                        ypts = np.append(ypts, f.coord('lat').bounds.array[-1, 1])
                        
                        bfill(
                            f=field_orig *
                            fmult,
                            x=xpts,
                            y=ypts,
                            clevs=clevs,
                            lonlat=1,
                            bound=1,
                            alpha=alpha, 
                            zorder=zorder)
                    else:
                        bfill(
                            f=field_orig *
                            fmult,
                            x=x_orig,
                            y=y_orig,
                            clevs=clevs,
                            lonlat=1,
                            bound=0,
                            alpha=alpha, 
                            zorder=zorder)

            else:
                bfill(
                    f=field_orig *
                    fmult,
                    x=x_orig,
                    y=y_orig,
                    clevs=clevs,
                    lonlat=1,
                    bound=0,
                    alpha=alpha, 
                    zorder=zorder)





        # Contour lines and labels
        if lines:
            if verbose:
                print 'con - adding contour lines and labels'
            cs = mymap.contour(lons, lats, field * fmult, clevs, colors=colors,
                               linewidths=linewidths, 
                               linestyles=linestyles, alpha=alpha,
                               transform=ccrs.PlateCarree(), zorder=zorder)
            if line_labels:
                nd = ndecs(clevs)
                fmt = '%d'
                if nd != 0:
                    fmt = '%1.' + str(nd) + 'f'
                plotvars.plot.clabel(cs, fmt=fmt, colors=colors,
                                     fontsize=text_fontsize,
                                     fontweight=text_fontweight, zorder=1000)

            # Thick zero contour line
            if zero_thick:
                cs = mymap.contour(lons, lats, field * fmult, [-1e-32, 0],
                                   colors=colors, linewidths=zero_thick,
                                   linestyles=linestyles, alpha=alpha,
                                   transform=ccrs.PlateCarree(), zorder=zorder)





        # axes
        plot_map_axes(axes=axes, xaxis=xaxis, yaxis=yaxis,
                      xticks=xticks, xticklabels=xticklabels,
                      yticks=yticks, yticklabels=yticklabels,
                      user_xlabel=user_xlabel, user_ylabel=user_ylabel,
                      verbose=verbose)




        

        # Coastlines
        feature = cfeature.NaturalEarthFeature(
                      name='land', category='physical',
                      scale=plotvars.resolution,
                      facecolor='none')
        mymap.add_feature(feature, edgecolor=continent_color,
                      linewidth=continent_thickness, 
                      linestyle=continent_linestyle, zorder=zorder)



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



        # Color bar
        if colorbar:
            cfplot_colorbar(cfill=cfill, colorbar_labels=colorbar_labels,
                    colorbar_orientation=colorbar_orientation,
                    colorbar_position=colorbar_position,
                    colorbar_shrink=colorbar_shrink,
                    cb_orient=cb_orient,colorbar_title=colorbar_title,
                    text_fontsize=text_fontsize, 
                    text_fontweight=text_fontweight,
                    colorbar_text_up_down=colorbar_text_up_down,
                    colorbar_text_down_up=colorbar_text_down_up,
                    colorbar_drawedges=colorbar_drawedges,
                    verbose=verbose)



       



        # Reset plot limits if not a user plot
        if plotvars.user_gset == 0:
            gset()

    ########################################
    # Latitude, longitude or time vs Z plots
    ########################################
    if ptype == 2 or ptype == 3 or ptype == 7:

        if verbose:
            if ptype == 2:
                print 'con - making a latitude-pressure plot'
            if ptype == 3:
                print 'con - making a longitude-pressure plot'
            if ptype == 7:
                print 'con - making a time-pressure plot'

        # Work out which way is up
        positive = None
        if isinstance(f, cf.Field):
            if hasattr(f.item('Z'), 'positive'):
                positive = f.item('Z').positive
            else:
                errstr = '\ncf-plot - data error \n'
                errstr += 'data needs a vertical coordinate direction'
                errstr += ' as required in CF data conventions'
                errstr += '\nMaking a contour plot assuming positive is up\n\n'
                errstr += 'If this is incorrect the data needs to be modified to \n'
                errstr += 'include a correct value for the direction attribute\n\n'
                print errstr
                positive='up'
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


        xstep = 10
        if (xmin == -90 and xmax == 90):
            xstep = 30
        ystep = 100
        myrange = abs(ymax - ymin)

        if myrange < 1:
            ystep = abs(ymax - ymin)/10.

        if abs(ymax - ymin) > 2000:
            ystep = 500
        if abs(ymax - ymin) > 5000:
            ystep = 1000
        if abs(ymax - ymin) > 15000:
            ystep = 5000

        # Work out ticks and tick labels
        if ylog is False or ylog == 0:
            heightticks = gvals(
                dmin=min(
                    ymin, ymax), dmax=max(
                    ymin, ymax), tight=1, mystep=ystep, mod=0)[0]

            if myrange < 1 and myrange > 0.1:
                heightticks=np.arange(10)/10.0

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

        if ptype == 7:
            if isinstance(f, cf.Field):
                if plotvars.user_gset == 0:
                    tmin = f.item('T').dtarray[0]
                    tmax = f.item('T').dtarray[-1]
                else:
                    # Use user set values if present
                    tmin = plotvars.xmin
                    tmax = plotvars.xmax

                    ref_time = f.item('T').units
                    ref_calendar = f.item('T').calendar
                    ref_time_origin = str(f.item('T').Units.reftime)
                    time_units = cf.Units(ref_time, ref_calendar)
                    t = cf.Data(cf.dt(tmin), units=time_units)
                    xmin = t.array
                    t = cf.Data(cf.dt(tmax), units=time_units)
                    xmax = t.array

        if xticks is None and xaxis:
            if ptype == 2:
                xticks, xticklabels = mapaxis(
                    min=xmin, max=xmax, type=2)  # lat-pressure
            if ptype == 3:
                xticks, xticklabels = mapaxis(
                    min=xmin, max=xmax, type=1)  # lon-pressure

            if ptype == 7:
                # time-pressure
                if isinstance(f, cf.Field):

                    # Change plotvars.xmin and plotvars.xmax from a date string
                    # to a number
                    ref_time = f.item('T').units
                    ref_calendar = f.item('T').calendar
                    ref_time_origin = str(f.item('T').Units.reftime)
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
                    errstr = srrstr + 'specify axis labels manually\n'
                    raise Warning(errstr)


        # Set plot limits
        if ylog is False or ylog == 0:
            gset(
                xmin=xmin,
                xmax=xmax,
                ymin=ymin,
                ymax=ymax,
                user_gset=user_gset)
        else:
            if ymax == 0:
                ymax = 1  # Avoid zero in a log plot
            gset(
                xmin=xmin,
                xmax=xmax,
                ymin=ymin,
                ymax=ymax,
                ylog=1,
                user_gset=user_gset)



        # Label axes
        axes_plot(xticks=xticks, xticklabels=xticklabels, yticks=heightticks,
                  yticklabels=heightlabels, xlabel=xlabel, ylabel=ylabel)

        # Get colour scale for use in contouring
        # If colour bar extensions are enabled then the colour map goes
        # from 1 to ncols-2.  The colours for the colour bar extensions are
        # then changed on the colourbar and plot after the plot is made
        cscale_ncols = np.size(plotvars.cs)
        colmap = cscale_get_map()

        # Filled contours
        if fill or blockfill:
            colmap = cscale_get_map()
            cmap = matplotlib.colors.ListedColormap(colmap)
            if (plotvars.levels_extend ==
                    'min' or plotvars.levels_extend == 'both'):
                cmap.set_under(plotvars.cs[0])
            if (plotvars.levels_extend ==
                    'max' or plotvars.levels_extend == 'both'):
                cmap.set_over(plotvars.cs[-1])

            cfill = plotvars.plot.contourf(x, y, field * fmult, clevs,
                                           extend=plotvars.levels_extend,
                                           cmap=cmap, 
                                           norm=plotvars.norm, alpha=alpha,
                                           zorder=zorder)

        # Block fill
        if blockfill:
            if isinstance(f, cf.Field): 

                hasbounds = True

                if ptype == 2:
                    if getattr(f.coord('Y'), 'hasbounds', False):
                        hasbounds = False
                        xpts = np.squeeze(f.coord('Y').bounds.array)[:, 0]
                        xpts = np.append(xpts, f.coord('Y').bounds.array[-1, 1])

                if ptype == 3:
                    if getattr(f.coord('X'), 'hasbounds', False):
                        hasbounds = False
                        xpts = np.squeeze(f.coord('X').bounds.array)[:, 0]
                        xpts = np.append(xpts, f.coord('X').bounds.array[-1, 1])

                if ptype == 7:
                    if getattr(f.coord('T'), 'hasbounds', False):
                        hasbounds = False
                        xpts = np.squeeze(f.coord('T').bounds.array)[:, 0]
                        xpts = np.append(xpts, f.coord('T').bounds.array[-1, 1])

                if getattr(f.coord('Z'), 'hasbounds', False):
                    hasbounds = False
                    ypts = np.squeeze(f.coord('Z').bounds.array)[:, 0]
                    ypts = np.append(ypts, f.coord('Z').bounds.array[-1, 1])


                if hasbounds is False:
                    bfill(
                        f=field_orig *
                        fmult,
                        x=xpts,
                        y=ypts,
                        clevs=clevs,
                        lonlat=0,
                        bound=1,
                        alpha=alpha,
                        zorder=zorder)
                else:
                    bfill(
                        f=field_orig *
                        fmult,
                        x=x_orig,
                        y=y_orig,
                        clevs=clevs,
                        lonlat=0,
                        bound=0,
                        alpha=alpha,
                        zorder=zorder)

            else:
                bfill(
                    f=field_orig *
                    fmult,
                    x=x_orig,
                    y=y_orig,
                    clevs=clevs,
                    lonlat=0,
                    bound=0,
                    alpha=alpha,
                    zorder=zorder)

        # Contour lines and labels
        if lines:
            cs = plotvars.plot.contour(
                x, y, field * fmult, clevs, colors=colors, 
                linewidths=linewidths, linestyles=linestyles, zorder=zorder)
            if line_labels:
                nd = ndecs(clevs)
                fmt = '%d'
                if nd != 0:
                    fmt = '%1.' + str(nd) + 'f'
                plotvars.plot.clabel(
                    cs,
                    fmt=fmt,
                    colors=colors,
                    fontsize=text_fontsize,
                    fontweight=text_fontweight)

                # Thick zero contour line
                if zero_thick:
                    cs = plotvars.plot.contour(x, y, field * fmult,
                                               [-1e-32, 0], colors=colors,
                                               linewidths=zero_thick,
                                               linestyles=linestyles, alpha=alpha,
                                               zorder=zorder)
        # Color bar
        if colorbar:
            cfplot_colorbar(cfill=cfill, colorbar_labels=colorbar_labels,
                    colorbar_orientation=colorbar_orientation,
                    colorbar_position=colorbar_position,
                    colorbar_shrink=colorbar_shrink,
                    cb_orient=cb_orient,colorbar_title=colorbar_title,
                    text_fontsize=text_fontsize, 
                    text_fontweight=text_fontweight,
                    colorbar_text_up_down=colorbar_text_up_down,
                    colorbar_text_down_up=colorbar_text_down_up,
                    colorbar_drawedges=colorbar_drawedges,
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

    #################
    # Hovmuller plots
    #################
    if (ptype == 4 or ptype == 5):
        if verbose:
            print 'con - making a Hovmuller plot'
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
            if hasattr(f.item('T'), 'units') is False:
                check_units = False
            if hasattr(f.item('T'), 'calendar') is False:
                check_calendar = False
            if hasattr(f.item('T'), 'Units'):
                if not hasattr(f.item('T').Units, 'reftime'):
                    check_Units_reftime = False
            else:
                check_Units_reftime = False
            if False in [check_units, check_calendar, check_Units_reftime]:
                print '\nThe required CF time information to make the plot'
                print 'is not available please fix the following before'
                print 'trying to plot again'
                if check_units is False:
                    print 'Time axis missing: units'
                if check_calendar is False:
                    print 'Time axis missing: calendar'
                if check_Units_reftime is False:
                    print 'Time axis missing: Units.reftime'
                return

            # Change from date string in ymin and ymax to date as a float
            ref_time = f.item('T').units
            ref_calendar = f.item('T').calendar
            ref_time_origin = str(f.item('T').Units.reftime)

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
        time_ticks, time_labels, ylabel = timeaxis(f.item('T'))

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
            latticks = [100000000]
            timeticks = [100000000]
            xplotlabel = ''
            yplotlabel = ''

        if user_xlabel is not None:
            xplotlabel = user_xlabel
        if user_ylabel is not None:
            yplotlabel = user_ylabel


        # Use the automatically generated labels if none are supplied
        if ylabel is None:
            yplotlabel = time_axis_label
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
        # then changed on the colourbar and plot after the plot is made
        cscale_ncols = np.size(plotvars.cs)
        colmap = cscale_get_map()

        # Filled contours
        if fill or blockfill:
            colmap = cscale_get_map()
            cmap = matplotlib.colors.ListedColormap(colmap)
            if (plotvars.levels_extend ==
                    'min' or plotvars.levels_extend == 'both'):
                cmap.set_under(plotvars.cs[0])
            if (plotvars.levels_extend ==
                    'max' or plotvars.levels_extend == 'both'):
                cmap.set_over(plotvars.cs[-1])

            cfill = plotvars.plot.contourf(x, y, field * fmult, clevs,
                                           extend=plotvars.levels_extend,
                                           cmap=cmap, 
                                           norm=plotvars.norm, alpha=alpha,
                                           zorder=zorder)

        # Block fill
        if blockfill:
            if isinstance(f, cf.Field):
                if f.coord('lon').hasbounds:
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

                    bfill(
                        f=field_orig *
                        fmult,
                        x=xpts,
                        y=ypts,
                        clevs=clevs,
                        lonlat=0,
                        bound=1,
                        alpha=alpha,
                        zorder=zorder)
                else:
                    if swap_axes:
                        x_orig, y_orig = y_orig, x_orig
                        field_orig = np.flipud(np.rot90(field_orig))
                    bfill(
                        f=field_orig *
                        fmult,
                        x=x_orig,
                        y=y_orig,
                        clevs=clevs,
                        lonlat=0,
                        bound=0,
                        alpha=alpha,
                        zorder=zorder)

            else:
                if swap_axes:
                    x_orig, y_orig = y_orig, x_orig
                    field_orig = np.flipud(np.rot90(field_orig))
                bfill(
                    f=field_orig *
                    fmult,
                    x=x_orig,
                    y=y_orig,
                    clevs=clevs,
                    lonlat=0,
                    bound=0,
                    alpha=alpha,
                    zorder=zorder)

        # Contour lines and labels
        if lines:
            cs = plotvars.plot.contour(
                x, y, field * fmult, clevs, colors=colors, 
                linewidths=linewidths, linestyles=linestyles, alpha=alpha)
            if line_labels:
                nd = ndecs(clevs)
                fmt = '%d'
                if nd != 0:
                    fmt = '%1.' + str(nd) + 'f'
                plotvars.plot.clabel(cs, fmt=fmt, colors=colors,
                                     fontsize=text_fontsize,
                                     fontweight=text_fontweight,
                                     zorder=zorder)

                # Thick zero contour line
                if zero_thick:
                    cs = plotvars.plot.contour(x, y, field * fmult,
                                               [-1e-32, 0], colors=colors,
                                               linewidths=zero_thick, 
                                               linestyles=linestyles, alpha=alpha,
                                               zorder=zorder)

        # Color bar
        if colorbar:
            cfplot_colorbar(cfill=cfill, colorbar_labels=colorbar_labels,
                    colorbar_orientation=colorbar_orientation,
                    colorbar_position=colorbar_position,
                    colorbar_shrink=colorbar_shrink,
                    cb_orient=cb_orient,colorbar_title=colorbar_title,
                    text_fontsize=text_fontsize, 
                    text_fontweight=text_fontweight,
                    colorbar_text_up_down=colorbar_text_up_down,
                    colorbar_text_down_up=colorbar_text_down_up,
                    colorbar_drawedges=colorbar_drawedges,
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


    #############
    # Rotated pole
    #############
    if ptype == 6:

        # Extract x and y grid points
        if plotvars.proj == 'cyl':
            xpts = x
            ypts = y

            if f.item('longitude'):
                xpts=f.item('longitude').array
            if f.item('latitude'):
                ypts=f.item('latitude').array
        else:
            xpts = np.arange(np.size(x))
            ypts = np.arange(np.size(y))



        if verbose:
            print 'con - making a rotated pole plot'
        user_gset = plotvars.user_gset
        if plotvars.user_plot == 0:
            gopen(user_plot=0)


         # Set plot limits
        if plotvars.proj == 'rotated':
            plotargs={}
            gset(xmin=0, xmax=np.size(xpts) - 1,
                 ymin=0, ymax=np.size(ypts) - 1,
                 user_gset=user_gset)
            plot=plotvars.plot

        if plotvars.proj == 'cyl':
            rotated_pole = f.ref('rotated_latitude_longitude')
            xpole = rotated_pole['grid_north_pole_longitude']
            ypole = rotated_pole['grid_north_pole_latitude']
            transform = ccrs.RotatedPole(pole_latitude=ypole,
                                         pole_longitude=xpole)
            plotargs={'transform' : transform}
            if plotvars.user_mapset == 1:
                set_map()
            else:

                # Extract lonmin, lonmax, latmin, latmax from rotated grid coordinates
                xvals, yvals = np.meshgrid(xpts, ypts)
                points=ccrs.PlateCarree().transform_points(transform, xvals.flatten(),
                                                           yvals.flatten())
                lons=np.array(points)[:, 0]
                lats=np.array(points)[:, 1]

                mapset(lonmin=np.min(lons), lonmax=np.max(lons),
                       latmin=np.min(lats), latmax=np.max(lats),
                       user_mapset=0, resolution=resolution_orig)
                set_map()
            plot=plotvars.mymap

        # Get colour scale for use in contouring
        # If colour bar extensions are enabled then the colour map goes
        # from 1 to ncols-2.  The colours for the colour bar extensions are
        # then changed on the colourbar and plot after the plot is made
        cscale_ncols = np.size(plotvars.cs)
        colmap = cscale_get_map()

            # Filled contours
        if fill or blockfill:
            colmap = cscale_get_map()
            cmap = matplotlib.colors.ListedColormap(colmap)
            if (plotvars.levels_extend ==
                    'min' or plotvars.levels_extend == 'both'):
                cmap.set_under(plotvars.cs[0])
            if (plotvars.levels_extend ==
                    'max' or plotvars.levels_extend == 'both'):
                cmap.set_over(plotvars.cs[-1])

            cfill = plot.contourf(xpts, ypts, field * fmult, clevs,
                                           extend=plotvars.levels_extend,
                                           cmap=cmap,
                                           norm=plotvars.norm, alpha=alpha,
                                           zorder=zorder, **plotargs)


        # Block fill
        if blockfill:
            bfill(
                f=field_orig *
                fmult,
                x=xpts,
                y=ypts,
                clevs=clevs,
                lonlat=0,
                bound=0,
                alpha=alpha,
                zorder=zorder)

        # Contour lines and labels
        if lines:
            cs = plot.contour(
                xpts, ypts, field * fmult, clevs, colors=colors, 
                linewidths=linewidths, linestyles=linestyles,
                zorder=zorder, **plotargs)
            if line_labels:
                nd = ndecs(clevs)
                fmt = '%d'
                if nd != 0:
                    fmt = '%1.' + str(nd) + 'f'
                plot.clabel(cs, fmt=fmt, colors=colors,
                                     fontsize=text_fontsize,
                                     fontweight=text_fontweight,
                                     zorder=zorder)

            # Thick zero contour line
            if zero_thick:
                cs = plot.contour(xpts, ypts, field * fmult,
                                           [-1e-32, 0], colors=colors,
                                           linewidths=zero_thick, 
                                           linestyles=linestyles, alpha=alpha,
                                           zorder=zorder, **plotargs)

        # Color bar
        if colorbar:
            cfplot_colorbar(cfill=cfill, colorbar_labels=colorbar_labels,
                    colorbar_orientation=colorbar_orientation,
                    colorbar_position=colorbar_position,
                    colorbar_shrink=colorbar_shrink,
                    cb_orient=cb_orient,colorbar_title=colorbar_title,
                    text_fontsize=text_fontsize, 
                    text_fontweight=text_fontweight,
                    colorbar_text_up_down=colorbar_text_up_down,
                    colorbar_text_down_up=colorbar_text_down_up,
                    colorbar_drawedges=colorbar_drawedges,
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


        
        if plotvars.proj == 'rotated':
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
                          linestyle=continent_linestyle, zorder=zorder)


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

    ############
    # Other plots
    ############
    if ptype == 0:

        if verbose:
            print 'con - making an other plot'
        if plotvars.user_plot == 0:
            gopen(user_plot=0)
        user_gset = plotvars.user_gset

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

        xstep = (xmax - xmin) / 10.0
        ystep = (ymax - ymin) / 10.0

        # Set plot limits and set default plot labels
        gset(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, user_gset=user_gset)

        xaxisticks = gvals(
            dmin=xmin,
            dmax=xmax,
            mystep=(
                xmax -
                xmin) /
            10.0,
            tight=1,
            mod=0)[0]
        xaxislabels = xaxisticks
        if ymin < ymax:
            yaxisticks = gvals(
                dmin=ymin, dmax=ymax, mystep=(
                    ymax - ymin) / 10.0, tight=1, mod=0)[0]
        if ymax < ymin:
            yaxisticks = gvals(
                dmin=ymax, dmax=ymin, mystep=(
                    ymin - ymax) / 10.0, tight=1, mod=0)[0]
        yaxislabels = yaxisticks

        if user_xlabel is not None:
            xplotlabel = user_xlabel
        else:
            xplotlabel = ''
        if user_ylabel is not None:
            yplotlabel = user_ylabel
        else:
            yplotlabel = ''

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
            xplotticks = [100000000]
            xplotticks = [100000000]
            xlabel = ''
            ylabel = ''


        axes_plot(xticks=xaxisticks, xticklabels=xaxislabels,
                  yticks=yaxisticks, yticklabels=yaxislabels,
                  xlabel=xplotlabel, ylabel=yplotlabel)

        # Get colour scale for use in contouring
        # If colour bar extensions are enabled then the colour map goes
        # then from 1 to ncols-2.  The colours for the colour bar extensions
        # are changed on the colourbar and plot after the plot is made
        cscale_ncols = np.size(plotvars.cs)
        colmap = cscale_get_map()

        # Filled contours
        if fill or blockfill:
            colmap = cscale_get_map()
            cmap = matplotlib.colors.ListedColormap(colmap)
            if (plotvars.levels_extend ==
                    'min' or plotvars.levels_extend == 'both'):
                cmap.set_under(plotvars.cs[0])
            if (plotvars.levels_extend ==
                    'max' or plotvars.levels_extend == 'both'):
                cmap.set_over(plotvars.cs[-1])

            cfill = plotvars.plot.contourf(x, y, field * fmult, clevs,
                                           extend=plotvars.levels_extend,
                                           cmap=cmap, 
                                           norm=plotvars.norm, alpha=alpha,
                                           zorder=zorder)

        # Block fill
        if blockfill:
            bfill(
                f=field_orig *
                fmult,
                x=x_orig,
                y=y_orig,
                clevs=clevs,
                lonlat=0,
                bound=0,
                alpha=alpha,
                zorder=zorder)

        # Contour lines and labels
        if lines:
            cs = plotvars.plot.contour(
                x, y, field * fmult, clevs, colors=colors, 
                linewidths=linewidths, linestyles=linestyles,
                zorder=zorder)
            if line_labels:
                nd = ndecs(clevs)
                fmt = '%d'
                if nd != 0:
                    fmt = '%1.' + str(nd) + 'f'
                plotvars.plot.clabel(cs, fmt=fmt, colors=colors,
                                     fontsize=text_fontsize,
                                     fontweight=text_fontweight,
                                     zorder=zorder)

            # Thick zero contour line
            if zero_thick:
                cs = plotvars.plot.contour(x, y, field * fmult, [-1e-32, 0],
                                           colors=colors,
                                           linewidths=zero_thick, 
                                           linestyles=linestyles, alpha=alpha,
                                           zorder=zorder)


        # Color bar
        if colorbar:
            cfplot_colorbar(cfill=cfill, colorbar_labels=colorbar_labels,
                    colorbar_orientation=colorbar_orientation,
                    colorbar_position=colorbar_position,
                    colorbar_shrink=colorbar_shrink,
                    cb_orient=cb_orient,colorbar_title=colorbar_title,
                    text_fontsize=text_fontsize, 
                    text_fontweight=text_fontweight,
                    colorbar_text_up_down=colorbar_text_up_down,
                    colorbar_text_down_up=colorbar_text_down_up,
                    colorbar_drawedges=colorbar_drawedges,
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
        for axis in ['top','bottom','left','right']: 
            plotvars.plot.spines[axis].set_linewidth(plotvars.axis_width) 





    ################################
    # Add a master title if reqested
    ################################
    if plotvars.master_title is not None:
        location=plotvars.master_title_location
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
            print 'con - saving or viewing plot'

        np.seterr(**old_settings)  # reset to default numpy error settings

        gclose()




def mapset(lonmin=None, lonmax=None, latmin=None, latmax=None, proj='cyl',
           boundinglat=0, lon_0=0, lat_0=40, resolution='110m', user_mapset=1):
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
           lonmin, lonmax, latmin, latmax]) and proj == 'cyl':
        plotvars.lonmin = -180
        plotvars.lonmax = 180
        plotvars.latmin = -90
        plotvars.latmax = 90
        plotvars.proj = 'cyl'
        plotvars.user_mapset = 0

        plotvars.plot_xmin=None
        plotvars.plot_xmax=None
        plotvars.plot_ymin=None
        plotvars.plot_ymax=None

        return

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
    #set_map()


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
        plotvars.levels = manual
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
            if all(isinstance(item, (int, long)) for item in [min, max, step]):
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

    import numpy as np
    degsym=''
    if plotvars.degsym:
        degsym='$\degree$'


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
                lonlabels.append('0' + degsym )

            if lon == 180 or lon == -180:
                   lonlabels.append('180' + degsym )

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
                latlabels.append(str(abs(lat))  + degsym + 'S')
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

    if plotvars.user_gset != 0:
        if isinstance(plotvars.xmin, str):
            t = cf.Data(cf.dt(plotvars.xmin), units=time_units)
            yearmin = int(t.year)
            t = cf.Data(cf.dt(plotvars.xmax), units=time_units)
            yearmax = int(t.year)
            tmin = cf.dt(plotvars.xmin)
            tmax = cf.dt(plotvars.xmax)
        if isinstance(plotvars.ymin, str):
            t = cf.Data(cf.dt(plotvars.ymin), units=time_units)
            yearmin = int(t.year)
            t = cf.Data(cf.dt(plotvars.ymax), units=time_units)
            yearmax = int(t.year)
            tmin = cf.dt(plotvars.ymin)
            tmax = cf.dt(plotvars.ymax)

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
            tvals = gvals(dmin=yearmin, dmax=yearmax, tight=1)[0]

        for year in tvals:
            time_ticks.append(np.min(
                (cf.Data(cf.dt(str(int(year)) + '-01-01 00:00:00'),
                 units=time_units).array)))
            time_labels.append(str(int(year)))

    # Months
    if yearmax - yearmin <= 4:

        time_label = 'Time (month and year)'
        months = [
            'Jan',
            'Feb',
            'Mar',
            'Apr',
            'May',
            'Jun',
            'Jul',
            'Aug',
            'Sep',
            'Oct',
            'Nov',
            'Dec']

        # Check number of labels with 1 month steps
        tsteps = 0
        for year in np.arange(yearmax - yearmin + 1) + yearmin:
            for month in np.arange(12):
                mytime = cf.dt(str(year) + '-' +
                               str(month + 1) + '-01 00:00:00')
                if mytime >= tmin and mytime <= tmax:
                    tsteps = tsteps + 1

        if tsteps < 17:
            mvals = np.arange(12)
        if tsteps >= 17:
            mvals = np.arange(4) * 3

        for year in np.arange(yearmax - yearmin + 1) + yearmin:
            for month in mvals:
                mytime = cf.dt(str(year) + '-' +
                               str(month + 1) + '-01 00:00:00')
                if mytime >= tmin and mytime <= tmax:
                    time_ticks.append(
                        np.min((cf.Data(mytime, units=time_units).array)))
                    time_labels.append(
                        str(months[month]) + ' ' + str(int(year)))

    # Days and hours
    if np.size(time_ticks) <= 2:
        myday = cf.dt(int(tmin.year), int(tmin.month), int(tmin.day))

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
        span = 0
        axis_label = 'Time (day)'
        if span >= 24:
            axis_label = 'Time (day and hour)'
        time_ticks = []
        time_labels = []

        while not_found <= 48:
            mytime = cf.Data(myday, dtimes.Units) + \
                cf.Data(hour_counter, 'hour')
            if mytime >= tmin and mytime <= tmax:
                time_ticks.append(np.min(mytime.array))
                label = str(mytime.year) + '-' + \
                    str(mytime.month) + '-' + str(mytime.day)
                if step / 24 != step / 24.0:
                    label = label + ' ' + str(mytime.hour) + ':00:00'
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
              xstep=None, ystep=None, xlabel=None, ylabel=None, title=None):
    """
     | axes_plot is a system function to specify axes plotting parameters.
     | The xstep and ystep parameters are used to label the axes starting at
     | the left hand side and bottom of the plot respectively. For tighter
     | control over labelling use xticks, yticks to specify the tick
     | positions and xticklabels, yticklabels to specify the associated
     | labels.

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

     :Returns:
      None
    """

    
    if plotvars.plot_type == 1 or (plotvars.plot_type == 6 and plotvars.proj == 'cyl'):
        xmin = plotvars.lonmin
        xmax = plotvars.lonmax
        ymin = plotvars.latmin
        ymax = plotvars.latmax
    else:
        xmin = plotvars.xmin
        xmax = plotvars.xmax
        ymin = plotvars.ymin
        ymax = plotvars.ymax


    if plotvars.xstep is not None:
        xstep = plotvars.xstep
        xticks = None
        xticklabels = None
    if plotvars.ystep is not None:
        ystep = plotvars.ystep
        yticks = None
        yticklabels = None

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
    text_fontweight = plotvars.text_fontweight


    if (plotvars.plot_type == 1 or plotvars.plot_type == 6) and plotvars.proj == 'cyl':
        plot = plotvars.mymap
        lon_mid = plotvars.lonmin + (plotvars.lonmax - plotvars.lonmin) / 2.0
        plotargs={'crs' : ccrs.PlateCarree()}
        cyl = True
    else:
        plot = plotvars.plot
        plotargs = {}
        cyl = False


    if xlabel is not None:
        plotvars.plot.set_xlabel(xlabel, fontsize=axis_label_fontsize,
                                 fontweight=axis_label_fontweight)
    if ylabel is not None:
        plotvars.plot.set_ylabel(ylabel, fontsize=axis_label_fontsize,
                                 fontweight=axis_label_fontweight)

    if xstep is not None:
        ticks, mult = gvals(plotvars.xmin, plotvars.xmax,
                            tight=1, mystep=xstep)

        plot_xticks = ticks * 10**mult
        plot_xticks_labels = plot_xticks

    if ystep is not None:
        ticks, mult = gvals(plotvars.ymin, plotvars.ymax,
                            tight=1, mystep=ystep)
        plot_yticks = ticks * 10**mult
        plot_yticks_labels = plot_yticks

    if xticks is not None:
        plot_xticks = xticks
        if xticklabels is not None:
            plot_xticks_labels = xticklabels
        else:
            plot_xticks_labels = xticks

    if yticks is not None:
        plot_yticks = yticks
        if yticklabels is not None:
            plot_yticks_labels = yticklabels
        else:
            plot_yticks_labels = yticks


    ticklen=np.min([(plotvars.lonmax - plotvars.lonmin)*0.014, (plotvars.latmax-plotvars.latmin)*0.014])
    lonrange = plotvars.lonmax - plotvars.lonmin
    latrange = plotvars.latmax - plotvars.latmin
    lon_mid = plotvars.lonmin + (plotvars.lonmax - plotvars.lonmin) / 2.0

    # Set the ticks and tick labels
    if xticks is not None:
        # fudge min and max longitude tick positions or the labels wrap
        xticks_new = xticks
        if lonrange >= 360:
            xticks_new[0] = xticks_new[0] + 0.01
            xticks_new[-1] = xticks_new[-1] - 0.01

        plot.set_xticks(xticks_new, **plotargs)
        plot.set_xticklabels(
            xticklabels,
            rotation=plotvars.xtick_label_rotation,
            horizontalalignment=plotvars.xtick_label_align)

        # Plot a corresponding tick on the top of the plot - **cartopy feature?
        proj=ccrs.PlateCarree(central_longitude=lon_mid)
        for xval in xticks_new:    
            xpt, ypt = proj.transform_point(xval, plotvars.latmax, ccrs.PlateCarree())
            ypt2 = ypt + ticklen
            plot.plot([xpt, xpt], [ypt, ypt2], color='k',
                                linewidth=0.8, clip_on=False)

    if yticks is not None:
        plot.set_yticks(yticks, **plotargs)
        plot.set_yticklabels(
            yticklabels,
            rotation=plotvars.ytick_label_rotation,
            horizontalalignment=plotvars.ytick_label_align)

        # Plot a corresponding tick on the right of the plot - **cartopy feature?
        proj=ccrs.PlateCarree(central_longitude=lon_mid)
        for ytick in yticks:
            xpt, ypt = proj.transform_point(plotvars.lonmax-0.001, ytick, ccrs.PlateCarree())
            xpt2 = xpt + ticklen * latrange / lonrange
            plot.plot([xpt, xpt2], [ypt, ypt],
                                color='k', linewidth=0.8, clip_on=False) 

    # Set font size and weight
    for label in plot.xaxis.get_ticklabels():
        label.set_fontsize(axis_label_fontsize)
        label.set_fontweight(axis_label_fontweight)
    for label in plot.yaxis.get_ticklabels():
        label.set_fontsize(axis_label_fontsize)
        label.set_fontweight(axis_label_fontweight)

    # Title
    if title is not None:
        plot.set_title(
            title,
            y=1.03,
            fontsize=title_fontsize,
            fontweight=title_fontweight)


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


    bcount=0
    for val in [xmin, xmax, ymin, ymax]:
        if val is None:
            bcount=bcount + 1

    if bcount !=0 and bcount != 4:
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
    except:
        time_xstr = True
    try:
        float(ymin)
    except:
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
        plotvars.twinx=twinx
    if twiny is not None:
        plotvars.twiny=twiny


    # Turn off default axis tick marks
    #if plotvars.plot is not None:
    #    plotvars.plot.set_xticks([])
    #    plotvars.plot.set_yticks([])



def gopen(rows=1, columns=1, user_plot=1, file='python',
          orientation='landscape', figsize=[11.7, 8.3],
          left=0.12, right=0.92, top=0.92, bottom=0.08, wspace=0.2,
          hspace=0.2, dpi=None, user_position=False):
    """
     | gopen is used to open a graphic file.
     |
     | rows=1 - number of plot rows on the page
     | columns=1 - number of plot columns on the page
     | user_plot=1 - internal plot variable - do not use.
     | file='python' - default file name
     | orientation='landscape' - orientation - also takes 'portrait'
     | figsize=[11.7, 8.3]  - figure size in inches
     | left=0.12 - left margin in normalised coordinates
     | right=0.92 - right margin in normalised coordinates
     | top=0.92 - top margin in normalised coordinates
     | bottom=0.08 - bottom margin in normalised coordinates
     | wspace=0.2 - width reserved for blank space between subplots
     | hspace=0.2 - height reserved for white space between subplots
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
    if file != 'python':
        plotvars.file = file
    plotvars.orientation = orientation
    plotvars.user_plot = user_plot

    # Set user defined plot area to None
    plotvars.plot_xmin = None
    plotvars.plot_xmax = None
    plotvars.plot_ymin = None
    plotvars.plot_ymax = None


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
    if user_position is False:
        gpos(pos=1)

    # Change tick length for plots > 2x2
    if (columns > 2 or rows > 2):
        matplotlib.rcParams['xtick.major.size'] = 2
        matplotlib.rcParams['ytick.major.size'] = 2

    # Set image resolution
    if dpi is not None:
        plotvars.dpi=dpi


def gclose(view=True):
    """
     | gclose saves a graphics file.  The default is to view the file as well
     | - use view=0 to turn this off.

     | view=True - view graphics file

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

    file = plotvars.file
    if file is not None:
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
            file, papertype='a4', orientation=plotvars.orientation, dpi=plotvars.dpi)
        plot.close()
    else:

        if plotvars.viewer == 'display':
            # Use Imagemagick display command if this exists
            disp = which('display')
            if disp is not None:
                tfile = 'cfplot.png'
                plotvars.master_plot.savefig(
                    tfile, papertype='a4', orientation=plotvars.orientation, dpi=plotvars.dpi)
                subprocess.Popen([disp, tfile])
            else:
                plotvars.viewer = 'matplotlib'
        if plotvars.viewer == 'matplotlib':
            # Use Matplotlib viewer
            plot.show()
            plot.close()

    # Reset plotting
    plotvars.plot = None
    plotvars.twinx = None
    plotvars.twiny = None
    plotvars.plot_xmin=None
    plotvars.plot_xmax=None
    plotvars.plot_ymin=None
    plotvars.plot_ymax=None



def showplot(*args):
    for data in args:
        plot = data
        plot.show()



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


    # Write user position values into plotvars as these need to 
    # be retrieved in set_map to add the mymap as a plot
    plot


    if user_pos is False:
        plotvars.plot = plotvars.master_plot.add_subplot(
            plotvars.rows, plotvars.columns, pos)
    else:    
        delta_x = plotvars.plot_xmax - plotvars.plot_xmin
        delta_y = plotvars.plot_ymax - plotvars.plot_ymin
        plotvars.plot = plotvars.master_plot.add_axes([plotvars.plot_xmin,
             plotvars.plot_ymin, delta_x, delta_y])

    plotvars.plot.tick_params(which='both', direction='out', right=True, top=True)

    # Set position in global variables
    plotvars.pos = pos




#######################################
# pcon - convert mb to km and vice-versa
#######################################

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


def gvals(dmin=None, dmax=None, tight=0, mystep=None, mod=1):
    """
     | gvals - work out a sensible set of values between two limits
     | This is an internal routine used for contour levels and axis
     | labelling and is not generally used by the user.

     | dmin=None - minimum
     | dmax=None - maximum
     | tight=0 - return values tight to input min and max
     | mystep=None - use this step
     | mod=1 - modify data to make use of a multipler
     |
     |
     |
     |
     |
     |
    """


    if all(val is None for val in [dmin, dmax]) > 0:
        errstr = '\n gvals error - gvals must have dmin and dmax input\n'
        raise Warning(errstr)

    # Return some values if dmin = dmax
    if dmin == dmax:
        vals = [dmin - 0.001, dmin, dmin + 0.001]
        mult = 0
        return vals, mult

    # Copies of inputs
    dmin1 = deepcopy(dmin)
    dmax1 = deepcopy(dmax)
    dmin2 = deepcopy(dmin)
    dmax2 = deepcopy(dmax)

    mult = 0  # field multiplyer

    # Generate an inital step
    step = (dmax - dmin) / 16.0

    # Don't modify if dmin1 and dmax1 are both negative as this will create a
    # race condition
    if dmin1 < 0 and dmax1 <= 0:
        mod = 0


    # Small range code
    # Return a linspace set of values if dmax1 - dmin1 is <= 3
    if dmax1 - dmin1 <= 3:
        mult = 0
        mindecs = 40 # minimum number of decimal places - a high starting value
        minval = 0 # spacing value of the minimum number of decimal spaces
        for val in np.arange(19)+2:
            vals = np.linspace(dmin, dmax, val)
            nd = ndecs(vals)
            if nd <= mindecs:
                minval = val
                mindecs = nd

        vals = np.linspace(dmin, dmax, minval)

        # Try to recalculate if too many decimal places
        if mindecs >=4:
            step=0.1
            for val in np.arange(40)+1:
                if dmax1-dmin1 <= 1.0/10**val:
                    step = 1.0/(10**(val+1))


            newvals = [float(int(dmin1))]
            while np.max(newvals) < dmax1:
                newvals = np.append(newvals, newvals[-1] + step)


            # Remove any points outside of limits
            pts = np.where((newvals >= dmin1) & (newvals <= dmax1))
            newvals = newvals[pts ] 

            # Remove upper and lower limits if tight=0 - i.e. a contour plot
            if tight == 0 and np.size(vals) > 1:
                if np.nanmax(newvals) >= dmax1:
                    newvals = newvals[0:-1]
                if np.nanmin(newvals) <= dmin1:
                    newvals = newvals[1:]

            if np.size(newvals) >2:
                vals=newvals

        return vals, mult








    if mod == 1:
        if (mystep is not None):
            step = mystep

        if step < 1:
            while dmax1 <= 3:
                step = step * 10.0
                dmin1 = dmin1 * 10.0
                dmax1 = dmax1 * 10.0
                mult = mult - 1

    if int(dmax2 - dmin2) > 3:
        step = 1
        mult = 0
        for val in [2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000,
                    2500, 5000, 10000, 20000, 25000, 50000, 100000,
                    200000, 250000, 500000, 1000000, 10000000 ]:

            if int(dmax2 - dmin2) / val > 10:
                step = val
                mult = 0

        if int(dmax2 - dmin2) / 1000000 > 10:
            step = (dmax2 - dmin2) / 16.0






    # Reset to user or non-zero values
    if (mystep is not None):
        step = mystep
    if (step == 0):
        step = 1

    # Make integer step
    if tight == 0:
        vals = (int(dmin1) / step) * step
    else:
        vals = dmin1
    while (np.nanmax(vals) + step) <= dmax1:
        vals = np.append(vals, np.nanmax(vals) + step)

    # Remove upper and lower limits if tight=0 - i.e. a contour plot
    if tight == 0 and np.size(vals) > 1:
        if np.nanmax(vals) >= dmax1:
            vals = vals[0:-1]
        if np.nanmin(vals) <= dmin1:
            vals = vals[1:]

    # Return values if there are five or more
    if np.size(vals) >= 5:
        return vals, mult

    if mystep is not None:
        if int(mystep) == mystep:
            return vals, mult



    if step == .9:
        step = 1.0
    if step == .8:
        step = 1.0
    if step == .7:
        step = .5
    if step == .6:
        step = .5
    if step == .3:
        step = .25
    if step == .09:
        step = 0.1
    if step == .08:
        step = 0.1
    if step == .07:
        step = .1
    if step == .06:
        step = .1
    if step == .04:
        step = .1
    if step == .03:
        step = .02


    if (dmax1 - dmin1 == step):
        step = step / 10.

    if step == 0.0:
        step = (dmax1-dmin1)/16.
    vals = float("%.2f" % (int(dmin1 / step) * step))
    while (np.nanmax(vals) + step) <= dmax1:
        vals = np.append(vals, float("%.2f" % (np.nanmax(vals) + step)))

    if tight == 0:
        if np.nanmax(vals) >= dmax1:
            vals = vals[0:-1]
        if np.nanmin(vals) <= dmin1:
            vals = vals[1:]

    return vals, mult


def cf_data_assign(f=None, colorbar_title=None, verbose=None):
    """
     | Check cf input data is okay and return data for contour plot.
     | This is an internal routine not used by the user.
     | f=None - input cf field
     | colorbar_title=None - input colour bar title
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
    ndim = len(f.axes(size=cf.gt(1)))
    if f.ref('rotated_latitude_longitude') is None:
        if (ndim > 2 or ndim < 1):
            print ''
            if (ndim > 2):
                errstr = 'cf_data_assign error - data has too many dimensions'
            if (ndim < 1):
                errstr = 'cf_data_assign error - data has too few dimensions'
            errstr += '\n cf-plot requires one or two dimensional data\n'
            for mydim in f.items():
                sn = getattr(f.item(mydim), 'standard_name', False)
                ln = getattr(f.item(mydim), 'long_name', False)
                if sn:
                    errstr = errstr + \
                        str(mydim) + ',' + str(sn) + ',' + \
                        str(f.item(mydim).size) + '\n'
                else:
                    if ln:
                        errstr = errstr + \
                            str(mydim) + ',' + str(ln) + ',' + \
                            str(f.item(mydim).size) + '\n'
            raise Warning(errstr)

    # Set up data arrays and variables
    lons = None
    lats = None
    height = None
    time = None
    xlabel = ''
    ylabel = ''
    has_lons = None
    has_lats = None
    has_height = None
    has_time = None
    xpole = None
    ypole = None
    ptype = None

    # Extract coordinate data if a matching CF standard_name or axis is found
    for mydim in f.items():
        sn = getattr(f.item(mydim), 'standard_name', 'NoName')
        an = getattr(f.item(mydim), 'axis', 'NoName')

        standard_name_x = ['longitude']
        vs = 'cf_data_assign standard_name, axis - assigned '
        if (sn in standard_name_x or an == 'X'):
            if verbose:
                print vs + 'lons -', sn, an
            lons = np.squeeze(f.item(mydim).array)

        standard_name_y = ['latitude']
        if (sn in standard_name_y or an == 'Y'):
            if verbose:
                print vs + 'lats -', sn, an
            lats = np.squeeze(f.item(mydim).array)

        standard_name_z = ['pressure', 'air_pressure', 'height', 'depth']
        if (sn in standard_name_z or an == 'Z'):
            if verbose:
                print vs + 'height -', sn, an
            height = np.squeeze(f.item(mydim).array)

        standard_name_t = ['time']
        if (sn in standard_name_t or an == 'T'):
            if verbose:
                print vs + 'time -', sn, an
            time = np.squeeze(f.item(mydim).array)

    # CF defined units
    lon_units = [
        'degrees_east',
        'degree_east',
        'degree_E',
        'degrees_E',
        'degreeE',
        'degreesE']
    lat_units = [
        'degrees_north',
        'degree_north',
        'degree_N',
        'degrees_N',
        'degreeN',
        'degreesN']
    height_units = ['mb', 'mbar', 'millibar', 'decibar', 'atmosphere',
                    'atm', 'pascal', 'Pa', 'hPa', 'meter', 'metre', 'm',
                    'kilometer', 'kilometre', 'km']
    time_units = ['day', 'days', 'd', 'hour', 'hours', 'hr', 'h', 'minute',
                  'minutes', 'min', 'mins', 'second', 'seconds', 'sec',
                  'secs', 's']

    # Extract coordinate data if a matching CF set of units is found
    for mydim in f.items():
        units = getattr(f.item(mydim), 'units', False)
        if units in lon_units:
            if lons is None:
                if verbose:
                    print 'cf_data_assign units - assigned lons -', units
                lons = np.squeeze(f.item(mydim).array)
        if units in lat_units:
            if lats is None:
                if verbose:
                    print 'cf_data_assign units - assigned lats -', units
                lats = np.squeeze(f.item(mydim).array)
        if units in height_units:
            if height is None:
                if verbose:
                    print 'cf_data_assign units - assigned height -', units
                height = np.squeeze(f.item(mydim).array)
        if units in time_units:
            if time is None:
                if verbose:
                    print 'cf_data_assign units - assigned time -', units
                time = np.squeeze(f.item(mydim).array)

    # Extract coordinate data from variable name if not already assigned
    for mydim in f.items():
        if mydim[:3] == 'dim':
            name = cf_var_name(field=f, dim=mydim)
            vs = 'cf_data_assign dimension name - assigned '
            if name[0:3] == 'lon':
                if lons is None:
                    if verbose:
                        print vs + lons + '-', name
                    lons = np.squeeze(f.item(mydim).array)

            if name[0:3] == 'lat':
                if lats is None:
                    if verbose:
                        print vs+lats + '-', name
                    lats = np.squeeze(f.item(mydim).array)

            if (name[0:5] == 'theta' or
                    name[0:1] == 'p' or
                    name == 'air_pressure'):
                        if height is None:
                            if verbose:
                                print vs+height + '-', name
                            height = np.squeeze(f.item(mydim).array)

            if name[0:1] == 't':
                if time is None:
                    if verbose:
                        print vs+time + '-', name
                    time = np.squeeze(f.item(mydim).array)

    if np.size(lons) > 1:
        has_lons = 1
    if np.size(lats) > 1:
        has_lats = 1
    if np.size(height) > 1:
        has_height = 1
    if np.size(time) > 1:
        has_time = 1

    # assign field data
    field = np.squeeze(f.array)

    # Check what plot type is required.
    # 0=simple contour plot, 1=map plot, 2=latitude-height plot,
    # 3=longitude-time plot, 4=latitude-time plot.
    if (np.size(lons) > 1 and np.size(lats) > 1):
        ptype = 1
        x = lons
        y = lats

    if (np.size(lats) > 1 and np.size(height) > 1):
        ptype = 2
        x = lats
        y = height
        for mydim in f.items():
            name = cf_var_name(field=f, dim=mydim)
            if name[0:3] == 'lat':
                xunits = str(getattr(f.item(mydim), 'Units', ''))
                if (xunits in lat_units):
                    xunits = 'degrees'
                xlabel = name + ' (' + xunits + ')'
            if name[0:1] == 'p' or name[
                    0:5] == 'theta' or name[0:6] == 'height':
                yunits = str(getattr(f.item(mydim), 'Units', ''))
                ylabel = name + ' (' + yunits + ')'

    if (np.size(lons) > 1 and np.size(height) > 1):
        ptype = 3
        x = lons
        y = height
        for mydim in f.items():
            name = cf_var_name(field=f, dim=mydim)
            if name[0:3] == 'lon':
                xunits = str(getattr(f.item(mydim), 'Units', ''))
                if (xunits in lon_units):
                    xunits = 'degrees'
                xlabel = name + ' (' + xunits + ')'
            if name[0:1] == 'p' or name[
                    0:5] == 'theta' or name[0:6] == 'height':
                yunits = str(getattr(f.item(mydim), 'Units', ''))
                ylabel = name + ' (' + yunits + ')'

    if (np.size(lons) > 1 and np.size(time) > 1):
        ptype = 4
        x = lons
        y = time

    if np.size(lats) > 1 and np.size(time) > 1:
        ptype = 5
        x = lats
        y = time

    # Rotated pole
    if f.ref('rotated_latitude_longitude') is not None:
        ptype = 6
        rotated_pole = f.ref('rotated_latitude_longitude')
        xpole = rotated_pole['grid_north_pole_longitude']
        ypole = rotated_pole['grid_north_pole_latitude']

        for mydim in f.items():
            name = cf_var_name(field=f, dim=mydim)
            if mydim[:3] == 'dim':
                if name in ['grid_longitude', 'longitude', 'x']:
                    x = np.squeeze(f.item(mydim).array)
                    xunits = str(getattr(f.item(mydim), 'units', ''))
                    xlabel = cf_var_name(field=f, dim=mydim)

                if name in ['grid_latitude', 'latitude', 'y']:
                    y = np.squeeze(f.item(mydim).array)
                    # Flip y and data if reversed
                    if y[0] > y[-1]:
                        y = y[::-1]
                        field = np.flipud(field)
                    yunits = str(getattr(f.item(mydim), 'Units', ''))
                    ylabel = cf_var_name(field=f, dim=mydim) + yunits




    # time height plot
    if has_height == 1 and has_time == 1:
        ptype = 7
        for mydim in f.items():
            if mydim[:3] == 'dim':
                if np.size(np.squeeze(f.item(mydim).array)
                           ) == np.shape(np.squeeze(f.array))[0]:
                    x = np.squeeze(f.item(mydim).array)
                    xunits = str(getattr(f.item(mydim), 'units', ''))
                    xlabel = cf_var_name(field=f, dim=mydim) + xunits

                if np.size(np.squeeze(f.item(mydim).array)
                           ) == np.shape(np.squeeze(f.array))[1]:
                    y = np.squeeze(f.item(mydim).array)
                    yunits = '(' + str(getattr(f.item(mydim), 'Units', ''))
                    yunits += ')'
                    ylabel = cf_var_name(field=f, dim=mydim) + yunits

        # Rotate array to get it as time vs height
        field = np.rot90(field)
        field = np.flipud(field)


    # UKCP grid
    if f.ref('transverse_mercator'):
        ptype = 1
        field = np.squeeze(f.array)

        # Find the auxiliary lons and lats if provided
        has_lons = False
        has_lats = False
        for mydim in f.items():
            if mydim[:3] == 'aux':
                name = cf_var_name(field=f, dim=mydim)
                if name in ['longitude']:
                    x = np.squeeze(f.item(mydim).array)
                    has_lons = True
                if name in ['latitude']:
                    y = np.squeeze(f.item(mydim).array)
                    has_lats = True


        # Calculate lons and lats if no auxiliary data for these
        if not has_lons or not has_lats:
            xpts = f.item('X').array
            ypts = f.item('Y').array
            field = np.squeeze(f.array)

            false_easting = f.ref('transverse_mercator')['false_easting']
            false_northing = f.ref('transverse_mercator')['false_northing']
            central_longitude = f.ref('transverse_mercator')['longitude_of_central_meridian']
            central_latitude = f.ref('transverse_mercator')['latitude_of_projection_origin']
            scale_factor = f.ref('transverse_mercator')['scale_factor_at_central_meridian']

            # Set the transform
            transform = ccrs.TransverseMercator(false_easting = false_easting,
                                                false_northing = false_northing,
                                                central_longitude = central_longitude,
                                                central_latitude = central_latitude,
                                                scale_factor = scale_factor)

            # Calculate the longitude and latitude points
            xvals, yvals = np.meshgrid(xpts, ypts)
            points = ccrs.PlateCarree().transform_points(transform, xvals, yvals) 
            x = np.array(points)[:, :, 0]
            y = np.array(points)[:, :, 1]




    # None of the above
    if ptype is None:
        ptype = 0
        for mydim in f.items():
            if mydim[:3] == 'dim':
                if np.size(np.squeeze(f.item(mydim).array)
                           ) == np.shape(np.squeeze(f.array))[1]:
                    x = np.squeeze(f.item(mydim).array)
                    xunits = str(getattr(f.item(mydim), 'units', ''))
                    xlabel = cf_var_name(field=f, dim=mydim) + xunits

                if np.size(np.squeeze(f.item(mydim).array)
                           ) == np.shape(np.squeeze(f.array))[0]:
                    y = np.squeeze(f.item(mydim).array)
                    yunits = str(getattr(f.item(mydim), 'Units', ''))
                    ylabel = cf_var_name(field=f, dim=mydim) + yunits

    # Assign colorbar_title
    if (colorbar_title is None):
        colorbar_title = 'No Name'
        if hasattr(f, 'id'):
            colorbar_title = f.id
        if hasattr(f, 'ncvar'):
            colorbar_title = f.ncvar
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


def cscale(cmap=None, ncols=None, white=None, below=None,
           above=None, reverse=False, uniform=False):
    """
    | cscale - choose and manipulate colour maps.  Around 200 colour scales are
    |          available - see the gallery section for more details.
    |
    | cmap=None - name of colour map
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
    if cmap is None:
        cmap = 'scale1'
        plotvars.cscale_flag = 0
        return
    else:
        plotvars.cs_user = cmap
        plotvars.cscale_flag = 1
        vals = [ncols, white, below, above]
        if any(val is not None for val in vals):
            plotvars.cscale_flag = 2
        if reverse is not False or uniform is not False:
            plotvars.cscale_flag = 2


    if cmap == 'scale1' or cmap == '':
        if cmap == 'scale1':
            myscale = cscale1
        if cmap == 'viridis':
            myscale = viridis
        # convert cscale1 or viridis from hex to rgb
        r = []
        g = []
        b = []
        for myhex in myscale:
            myhex = myhex.lstrip('#')
            mylen = len(myhex)
            rgb = tuple(int(myhex[i:i + mylen / 3], 16)
                        for i in range(0, mylen, mylen / 3))
            r.append(rgb[0])
            g.append(rgb[1])
            b.append(rgb[2])

    else:
        import distutils.sysconfig as sysconfig

        package_path = os.path.dirname(__file__)
        file = os.path.join(package_path, 'colourmaps/' + cmap + '.rgb')
        if os.path.isfile(file) is False:
            if os.path.isfile(cmap) is False:
                errstr = '\ncscale error - colour scale not found:\n'
                errstr = errstr + 'File ' + file + ' not found\n'
                errstr = errstr + 'File ' + cmap + ' not found\n'
                raise Warning(errstr)
            else:
                file = cmap

        # Read in rgb values and convert to hex
        f = open(file, 'r')
        lines = f.read()
        lines = lines.splitlines()
        r = []
        g = []
        b = []
        hex = []
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
        npoints = np.size(r) / 2

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
    hex = []
    for col in np.arange(np.size(r)):
        hex.append('#%02x%02x%02x' % (r[col], g[col], b[col]))

    # White requested colour positions
    if white is not None:
        ccols = white
        if np.size(white) == 1:
            hex[white] = '#ffffff'
        else:
            for col in white:
                hex[col] = '#ffffff'

    # Set colour scale
    plotvars.cs = hex


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


def bfill(f=None, x=None, y=None, clevs=False, lonlat=False, bound=False,
          alpha=1.0, single_fill_color=None, white=True, zorder=None):
    """
     | bfill - block fill a field with colour rectangles
     | This is an internal routine and is not generally used by the user.
     |
     | f=None - field
     | x=None - x points for field
     | y=None - y points for field
     | clevs=None - levels for filling
     | lonlat=False - lonlat data
     | bound=False - x and y are cf data boundaries
     | alpha=alpha - transparency setting 0 to 1
     | white=True - colour unplotted areas white
     | single_fill_color=None - colour for a blockfill between two levels 
     |                        - makes maplotlib named colours or 
     |                        - hexadecimal notation - '#d3d3d3' for grey 
     | zorder=None - plotting order
     |
      :Returns:
        None
     |
     |
     |
     |
    """

    # If single_fill_color is defined then turn off whiting out the background.
    if single_fill_color is not None:
        white = False
  

    # Set the default map coordinates for the data to be PlateCarree
    plotargs = {}
    if lonlat:
        plotargs = {'transform' : ccrs.PlateCarree()}

    transverse_mercator = False
    if isinstance(f, cf.Field):
        if f.ref('transverse_mercator'):
            transverse_mercator = True
            lonlat = True

            # Case of transverse mercator of which UKCP is an example
            false_easting = f.ref('transverse_mercator')['false_easting']
            false_northing = f.ref('transverse_mercator')['false_northing']
            central_longitude = f.ref('transverse_mercator')['longitude_of_central_meridian']
            central_latitude = f.ref('transverse_mercator')['latitude_of_projection_origin']
            scale_factor = f.ref('transverse_mercator')['scale_factor_at_central_meridian']
            transform = ccrs.TransverseMercator(false_easting = false_easting,
                                                false_northing = false_northing,
                                                central_longitude = central_longitude,
                                                central_latitude = central_latitude,
                                                scale_factor = scale_factor)

            # Extract the axes and data
            xpts = np.append(f.item('X').bounds.array[:,0], f.item('X').bounds.array[-1,1])
            ypts = np.append(f.item('Y').bounds.array[:,0], f.item('Y').bounds.array[-1,1])
            field = np.squeeze(f.array)


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
            xpts_orig = xpts
            ypts_orig = ypts
    
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
                field, xpts = cartopy_util.add_cyclic_point(field, xpts)


            right_bound = xpts[-1] + (xpts[-1] - xpts[-2])

            # Add end x and y end points
            xpts = np.append(xpts, right_bound)
            ypts = np.append(ypts, upper_bound)



    levels=np.array(deepcopy(clevs)).astype('float')

    # Polar stereograpic
    # Set points past plotting limb to be plotvars.boundinglat 
    # Also set any lats past the pole to be the pole
    if plotvars.proj == 'npstere':
       pts = np.where(ypts < plotvars.boundinglat)
       if np.size(pts) > 0:
           ypts[pts] = plotvars.boundinglat
       pts=np.where(ypts > 90.0)
       if np.size(pts) > 0:
           ypts[pts] = 90.0

    if plotvars.proj == 'spstere':
       pts = np.where(ypts > plotvars.boundinglat)
       if np.size(pts) > 0:
           ypts[pts]=plotvars.boundinglat
       pts=np.where(ypts < -90.0)
       if np.size(pts) > 0:
           ypts[pts] = -90.0



    # Generate a Matplotlib colour map
    if single_fill_color is None:
        cols=plotvars.cs
    else:
        cols=single_fill_color

    cmap = matplotlib.colors.ListedColormap(cols)


    if single_fill_color is None:
        if plotvars.levels_extend == 'both' or plotvars.levels_extend == 'min':
            levels=np.insert(levels, 0, -1e30)
        if plotvars.levels_extend == 'both' or plotvars.levels_extend == 'max':
            levels=np.append(levels, 1e30)


        if plotvars.levels_extend == 'both' or plotvars.levels_extend == 'min':
            cmap.set_under(plotvars.cs[0])
            cols=cols[1:]
        if plotvars.levels_extend == 'both' or plotvars.levels_extend == 'max':
            cmap.set_over(plotvars.cs[-1])
            cols=cols[:-1]


    # Colour array for storing the cell colour.  Start with -1 as the default 
    # as the colours run from 0 to np.size(levels)-1
    colarr=np.zeros([np.shape(field)[0], np.shape(field)[1]])-1
    for i in np.arange(np.size(levels)-1):
        lev=levels[i]
        pts=np.where(np.logical_and(field > lev, field <= levels[i+1]))
        colarr[pts]=int(i)

    # Change points that are masked back to -1
    if isinstance(field, np.ma.MaskedArray):
        pts=np.ma.where(field.mask)
        if np.size(pts) > 0:
            colarr[pts]=-1

    #print 'plotargs are ', **plotargs

    if plotvars.plot_type == 1 and plotvars.proj != 'cyl':

        for i in np.arange(np.size(levels)-1):
            allverts = []
            xy_stack=np.column_stack(np.where(colarr == i))
            
            for pt in np.arange(np.shape(xy_stack)[0]):
                ix = xy_stack[pt][1]
                iy = xy_stack[pt][0]
                lons = [xpts[ix], xpts[ix+1], xpts[ix+1], xpts[ix], xpts[ix]]
                lats = [ypts[iy], ypts[iy], ypts[iy+1], ypts[iy+1], ypts[iy]]
                
                #txpts, typts = plotvars.mymap(lons, lats)
                txpts, typts = lons, lats
                verts=[
                    (txpts[0], typts[0]),
                    (txpts[1], typts[1]), 
                    (txpts[2], typts[2]),
                    (txpts[3], typts[3]),
                    (txpts[4], typts[4]),
                    ]

                allverts.append(verts)

            # Make the collection and add it to the plot.
            if single_fill_color is None:
                color=plotvars.cs[i]
            else: 
                color=single_fill_color
            coll = PolyCollection(allverts, facecolor=color, edgecolors=color, alpha=alpha,
                                  zorder=zorder, **plotargs)

            if lonlat:
                plotvars.mymap.add_collection(coll)
            else:
                plotvars.plot.add_collection(coll)
    else:
        for i in np.arange(np.size(levels)-1):
            allverts = []
            xy_stack=np.column_stack(np.where(colarr == i))
            for pt in np.arange(np.shape(xy_stack)[0]):
                ix = xy_stack[pt][1]
                iy = xy_stack[pt][0]
                verts=[
                    (xpts[ix], ypts[iy]),
                    (xpts[ix+1], ypts[iy]), 
                    (xpts[ix+1], ypts[iy+1]),
                    (xpts[ix], ypts[iy+1]),
                    (xpts[ix], ypts[iy]),
                    ]
        
                allverts.append(verts)

            # Make the collection and add it to the plot.
            if single_fill_color is None:
                color=plotvars.cs[i]
            else: 
                color=single_fill_color

            coll = PolyCollection(allverts, facecolor=color, edgecolors=color,
                                  alpha=alpha, zorder=zorder, **plotargs)

            if lonlat:
                plotvars.mymap.add_collection(coll)
            else:
                plotvars.plot.add_collection(coll)



    # Add white for undefined areas
    if white:
        allverts = []
        xy_stack=np.column_stack(np.where(colarr == -1))
        for pt in np.arange(np.shape(xy_stack)[0]):
            ix = xy_stack[pt][1]
            iy = xy_stack[pt][0]

            verts=[
                (xpts[ix], ypts[iy]),
                (xpts[ix+1], ypts[iy]), 
                (xpts[ix+1], ypts[iy+1]),
                (xpts[ix], ypts[iy+1]),
                (xpts[ix], ypts[iy]),
                ]
        
            allverts.append(verts)

        # Make the collection and add it to the plot.
        color=plotvars.cs[i]
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

    # reassign input arrays
    regrid_f = f
    regrid_x = x
    regrid_y = y

    fieldout = []

    # Reverse xpts and field if necessary
    if regrid_x[0] > regrid_x[-1]:
        regrid_x = regrid_x[::-1]
        field = np.fliplr(regrid_f)

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
        #print 'xval is ', xval
        #print 'vals are ', regrid_x
        #print 'myxpos is ', myxpos
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
            alpha=1.0, ylog=False, zorder=None):
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
     | zorder=None - plotting order
     |
     |
     :Returns:
        None
     |
     |
    """

    if plotvars.plot_type not in [1,2,3]:
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
            field, xpts = cartopy_util.add_cyclic_point(field, xpts)




        if plotvars.proj == 'cyl':
            # Calculate interpolation points
            xnew, ynew = stipple_points(xmin=np.nanmin(xpts),
                                        xmax=np.nanmax(xpts),
                                        ymin=np.nanmin(ypts),
                                        ymax=np.nanmax(ypts),
                                        pts=pts, stype=2)

            # Calculate points in map space
            xnew_map=xnew
            ynew_map=ynew


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
        proj=ccrs.PlateCarree()

        if np.size(valid_points) > 0:
            plotvars.mymap.scatter(
                xnew[valid_points],
                ynew[valid_points],
                s=size,
                c=color,
                marker=marker,
                edgecolors=edgecolors,
                alpha=alpha, transform=proj, zorder=zorder)



    if plotvars.plot_type >= 2 and plotvars.plot_type <= 3:
        plotvars.plot.scatter(
            xnew[valid_points],
            ynew[valid_points],
            s=size,
            c=color,
            marker=marker,
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
    nxpts = np.size(x1)

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

    if above is 1:
        for myval in vals:
            if val >= myval:
                pos = pos + 1

        if np.size(vals) - 1 > pos:
            pos = pos + 1

    return pos


def vect(u=None, v=None, x=None, y=None, scale=None, stride=None, pts=None,
         key_length=None, key_label=None, ptype=None, title=None,
         width=0.02, headwidth=3, headlength=5, headaxislength=4.5,
         pivot='middle', key_location=[0.95, -0.06], key_show=True, axes=True,
         xaxis=True, yaxis=True, xticks=None, xticklabels=None, yticks=None,
         yticklabels=None, xlabel=None, ylabel=None, ylog=False, color='k',
         zorder=None):
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
     | zorder=None - plotting order
     |
     :Returns:
      None
     |
     |
     |
    """

    # If the vector color is white set the quicker key colour to black
    # so that it can be seen
    qkey_color=color
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
    resolution_orig=plotvars.resolution


    # Set potential user axis labels
    user_xlabel = xlabel
    user_ylabel = ylabel

    # Extract required data for contouring
    # If a cf-python field
    if isinstance(u, cf.Field):
        u_data, u_x, u_y, ptype, colorbar_title, xlabel, ylabel, xpole, \
            ypole = cf_data_assign(u, colorbar_title)
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
        v_data, v_x, v_y, ptype, colorbar_title, xlabel, ylabel, xpole, \
            ypole = cf_data_assign(v, colorbar_title)
    elif isinstance(v, cf.FieldList):
        raise TypeError("Can't plot a field list")
    else:
        # field=f #field data passed in as f
        check_data(v, x, y)
        v_data = deepcopy(v)
        v_x = deepcopy(x)
        v_y = deepcopy(y)
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
            xticklabels = map(str, xticks)
    if yticks is None and plotvars.yticks is not None:
        yticks = plotvars.yticks
        if plotvars.yticklabels is not None:
            yticklabels = plotvars.yticklabels
        else:
            yticklabels = map(str, yticks)


    if scale is None:
        scale = np.nanmax(u_data) / 4.0

    if key_length is None:
        key_length = scale

    # Open a new plot if necessary
    if plotvars.user_plot == 0:
        gopen(user_plot=0)

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

        u_data, u_x = cartopy_util.add_cyclic_point(u_data, u_x)
        v_data, v_x = cartopy_util.add_cyclic_point(v_data, v_x)



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
        lonmin=plotvars.lonmin
        lonmax=plotvars.lonmax
        proj=ccrs.PlateCarree()
  

        if pts is None:
            quiv = plotvars.mymap.quiver(u_x, u_y, u_data, v_data, scale=scale,
                                         pivot=pivot, units='inches',
                                         width=width, headwidth=headwidth,
                                         headlength=headlength,
                                         headaxislength=headaxislength,
                                         color=color, transform=proj,
                                         zorder=zorder)
        else:
            if plotvars.proj == 'cyl':
                # **cartopy 0.16 fix for longitide points in cylindrical projection
                # when regridding to a number of points
                # Make points within the plotting region
                for pt in np.arange(np.size(u_x)):
                    if u_x[pt] > lonmax:
                        u_x[pt]=u_x[pt]-360


            quiv = plotvars.mymap.quiver(u_x, u_y, u_data, v_data, scale=scale,
                                    pivot=pivot, units='inches',
                                    width=width, headwidth=headwidth,
                                    headlength=headlength,
                                    headaxislength=headaxislength,
                                    color=color,
                                    regrid_shape=pts, transform=proj,
                                    zorder=zorder)



        # Make key_label if none exists
        if key_label is None:
            key_label = str(key_length)
        if isinstance(u, cf.Field):
            key_label = supscr(key_label + u.units)
        if key_show:
            quiv_key = plotvars.mymap.quiverkey(quiv, key_location[0], 
                                                key_location[1],
                                                key_length,
                                                key_label, labelpos='W',
                                                color=qkey_color,
                                                fontproperties={'size':str(plotvars.axis_label_fontsize)},
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


    if plotvars.plot_type == 6:
        if u.ref('rotated_latitude_longitude') is not None:

            rotated_pole = u.ref('rotated_latitude_longitude')
            xpole = float(rotated_pole['grid_north_pole_longitude'])
            ypole = float(rotated_pole['grid_north_pole_latitude'])

            proj=ccrs.PlateCarree() 

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
                                         color=color, zorder=zorder)
            

            # Make key_label if none exists
            if key_label is None:
                key_label = str(key_length)
            if isinstance(u, cf.Field):
                key_label = supscr(key_label + u.units)

            if key_show:
                quiv_key = plotvars.mymap.quiverkey(quiv, key_location[0], 
                                                    key_location[1],
                                                    key_length,
                                                    key_label, labelpos='W',
                                                    color=qkey_color,
                                                    fontproperties={'size':str(plotvars.axis_label_fontsize)},
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

        xstep = None
        if ptype == 1:
            if (xmin == -90 and xmax == 90):
                xstep = 30
        if ptype == 2:
            if xmax - xmax >= 160:
                xstep = 60
            else:
                xstep = 30

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
            lltype=1
            if plotvars.plot_type == 2:
                lltype = 2
            llticks, lllabels = mapaxis(min=xmin, max=xmax, type=lltype)


            heightticks = gvals(
                dmin=ymin,
                dmax=ymax,
                tight=1,
                mystep=ystep,
                mod=0)[0]
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
            gset(
                xmin=xmin,
                xmax=xmax,
                ymin=ymax,
                ymax=ymin,
                ylog=1,
                user_gset=user_gset)
            llticks, lllabels = mapaxis(min=xmin, max=xmax,
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
                                    color=color, zorder=zorder)

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
                quiv_key = plotvars.plot.quiverkey(quiv, key_location[0],
                                                   key_location[1],
                                                   key_length_u, key_label_u,
                                                   labelpos='W',
                                                   color=qkey_color,
                                                   fontproperties={'size':str(plotvars.axis_label_fontsize)})

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
                quiv1 = plotvars.plot.quiver(xpos, ypos, key_length[0], 0,
                                             pivot='tail', units='inches',
                                             scale=scale[0],
                                             headaxislength=headaxislength,
                                             width=width, headwidth=headwidth,
                                             headlength=headlength,
                                             clip_on=False,
                                             color=qkey_color)

                quiv2 = plotvars.plot.quiver(xpos, ypos, 0, key_length[1],
                                             pivot='tail', units='inches',
                                             scale=scale[1],
                                             headaxislength=headaxislength,
                                             width=width, headwidth=headwidth,
                                             headlength=headlength,
                                             clip_on=False,
                                             color=qkey_color)

                plotvars.plot.text(
                    xpos,
                    ypos + yoffset,
                    key_label_u,
                    horizontalalignment='left',
                    verticalalignment='top')
                plotvars.plot.text(
                    xpos - xoffset,
                    ypos,
                    key_label_v,
                    horizontalalignment='right',
                    verticalalignment='bottom')

        if title is not None:
            plotvars.plot.set_title(
                title,
                y=1.03,
                fontsize=plotvars.title_fontsize,
                fontweight=title_fontweight)

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


    # Set up mapping
    extent = True
    lon_mid = plotvars.lonmin + (plotvars.lonmax - plotvars.lonmin) / 2.0
    lat_mid = plotvars.latmin + (plotvars.latmax - plotvars.latmin) / 2.0
    lonmin = plotvars.lonmin
    lonmax = plotvars.lonmax
    latmin = plotvars.latmin
    latmax = plotvars.latmax

    if plotvars.proj == 'cyl':
        proj=ccrs.PlateCarree(central_longitude=lon_mid)



        
        # Cartopy line plotting and identical left == right fix

        if lonmax - lonmin == 360.0:
            lonmax = lonmax + 0.01



    
    if plotvars.proj == 'merc':
        min_latitude=-80.0
        if plotvars.lonmin > min_latitude:
            min_latitude=plotvars.lonmin
        max_latitude=84.0
        if plotvars.lonmax < max_latitude:
             max_latitude=plotvars.lonmax
        proj=ccrs.Mercator(central_longitude=plotvars.lon_0,
                           min_latitude=min_latitude,
                           max_latitude=max_latitude)
        


    if plotvars.proj == 'npstere':
        proj = ccrs.NorthPolarStereo(central_longitude=plotvars.lon_0)
        #mymap=plot.subplot(plotvars.rows, plotvars.columns, plotvars.pos, projection=proj)
        # **cartopy 0.16 fix
        # Here we add in 0.01 to the longitude extent as this helps with plotting 
        # lines and line labels
        lonmin = plotvars.lon_0-180
        lonmax = plotvars.lon_0+180.01
        latmin = plotvars.boundinglat
        latmax = 90





    if plotvars.proj == 'spstere':
        proj = ccrs.SouthPolarStereo(central_longitude=plotvars.lon_0)
        #mymap=plot.subplot(plotvars.rows, plotvars.columns, plotvars.pos, projection=proj)
        # **cartopy 0.16 fix
        # Here we add in 0.01 to the longitude extent as this helps with plotting 
        # lines and line labels
        lonmin = plotvars.lon_0-180
        lonmax = plotvars.lonmax+180.01
        latmin = -90
        latmax = plotvars.boundinglat



    if plotvars.proj == 'ortho':
        proj=ccrs.Orthographic(central_longitude=plotvars.lon_0,
                               central_latitude=plotvars.lat_0)
        lonmin = plotvars.lon_0-180.0
        lonmax = plotvars.lon_0+180.01
        extent = False
    


    if plotvars.proj == 'moll':
        proj=ccrs.Mollweide(central_longitude=plotvars.lon_0)
        lonmin = plotvars.lon_0-180.0
        lonmax = plotvars.lon_0+180.01
        extent = False



    if plotvars.proj == 'robin':
        proj=ccrs.Robinson(central_longitude=plotvars.lon_0)


    if plotvars.proj == 'lcc':
        lon_0=plotvars.lonmin+(plotvars.lonmax-plotvars.lonmin)/2.0
        lat_0=plotvars.latmin+(plotvars.latmax-plotvars.latmin)/2.0
        proj=ccrs.LambertConformal(central_longitude=lon_0,
                                   central_latitude=lat_0,
                                   cutoff=-40)

    if plotvars.proj == 'rotated':
        proj=ccrs.PlateCarree(central_longitude=lon_mid)



    if plotvars.proj == 'OSGB':
        proj=ccrs.OSGB()

    if plotvars.proj == 'EuroPP':
        proj=ccrs.EuroPP()


    if plotvars.proj == 'UKCP':
        # Special case of TransverseMercator for UKCP
        proj=ccrs.TransverseMercator()

    if plotvars.proj == 'TransverseMercator':
        proj=ccrs.TransverseMercator()
        lonmin = plotvars.lon_0-180.0
        lonmax = plotvars.lon_0+180.01
        extent = False


    # Add a plot containing the projection
    if plotvars.plot_xmin:
        delta_x = plotvars.plot_xmax - plotvars.plot_xmin
        delta_y = plotvars.plot_ymax - plotvars.plot_ymin
        mymap = plotvars.master_plot.add_axes([plotvars.plot_xmin,
                                                   plotvars.plot_ymin,
                                                   delta_x, delta_y],
                                                   projection=proj)
    else:    
        mymap=plotvars.master_plot.add_subplot(plotvars.rows,
                                               plotvars.columns,
                                               plotvars.pos,
                                               projection=proj)

        


    # Set map extent
    set_extent = True
    if plotvars.proj == 'OSGB' or plotvars.proj == 'EuroPP' or plotvars.proj == 'UKCP':
        set_extent = False

    if extent and set_extent:
        mymap.set_extent((lonmin, lonmax, latmin, latmax), crs=ccrs.PlateCarree())


    if plotvars.proj == 'UKCP':
        # Special case of TransverseMercator for UKCP
        mymap.set_extent((-11, 3, 49, 61), crs=ccrs.PlateCarree())

    if plotvars.proj == 'EuroPP':
        # EuroPP somehow needs some limits setting.
        mymap.set_extent((-12, 25, 30, 75), crs=ccrs.PlateCarree())



    # Remove any plotvars.plot axes leaving just the plotvars.mymap axes
    #if plotvars.plot is not None:
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

    mymap = plotvars.mymap

    boundinglat = plotvars.boundinglat
    lon_0 = plotvars.lon_0


    if plotvars.proj == 'npstere':
        thisproj=ccrs.NorthPolarStereo(central_longitude=lon_0)
    else:
        thisproj=ccrs.SouthPolarStereo(central_longitude=lon_0)

    # Find min and max of plotting region in device coordinates
    lons=np.array([lon_0-90, lon_0, lon_0+90, lon_0+180])
    lats=np.array([boundinglat, boundinglat, boundinglat, boundinglat])
    extent=thisproj.transform_points(ccrs.PlateCarree(), lons, lats)    

    xmin=np.min(extent[:,0])
    xmax=np.max(extent[:,0])  
    ymin=np.min(extent[:,1])
    ymax=np.max(extent[:,1])

    



    # Make up a stipple of points for cover the pole
    points_device = stipple_points(
        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, pts=pts, stype=2)

    xnew = np.array(points_device)[0, :]
    ynew = np.array(points_device)[1, :]

    points_polar=ccrs.PlateCarree().transform_points(thisproj, xnew, ynew) 

    lons=np.array(points_polar)[:, 0]
    lats=np.array(points_polar)[:, 1]


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

    id = getattr(field.item(dim), 'id', False)
    ncvar = getattr(field.item(dim), 'ncvar', False)
    short_name = getattr(field.item(dim), 'short_name', False)
    long_name = getattr(field.item(dim), 'long_name', False)
    standard_name = getattr(field.item(dim), 'standard_name', False)

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
            print title
            print '----------------------------------------------'
            print ''
            print div
            print 'Name               Scale'
            print div

        if category == 'ncl_meteoswiss':
            scales = ncl_meteoswiss
            div = '================== ====='
            chars = 19
            print 'NCAR Command Language - MeteoSwiss colour maps'
            print '----------------------------------------------'
            print ''
            print div
            print 'Name               Scale'
            print div
        if category == 'ncl_small':
            scales = ncl_small
            div = '=================== ====='
            chars = 20
            print 'NCAR Command Language - small color maps (<50 colours)'
            print '------------------------------------------------------'
            print ''
            print div
            print 'Name                Scale'
            print div
        if category == 'ncl_large':
            scales = ncl_large
            div = '======================= ====='
            chars = 24
            print 'NCAR Command Language - large colour maps (>50 colours)'
            print '-------------------------------------------------------'
            print ''
            print div
            print 'Name                    Scale'
            print div
        if category == 'ncl_color_blindness':
            scales = ncl_color_blindness
            div = '================ ====='
            chars = 17
            title = 'NCAR Command Language - Enhanced to help with colour'
            title += 'blindness'
            print title
            title = '-----------------------------------------------------'
            title += '---------'
            print title
            print ''
            print div
            print 'Name             Scale'
            print div
            chars = 17
        if category == 'orography':
            scales = orography
            div = '================ ====='
            chars = 17
            print 'Orography/bathymetry colour scales'
            print '----------------------------------'
            print ''
            print div
            print 'Name             Scale'
            print div
            chars = 17
        if category == 'idl_guide':
            scales = idl_guide
            div = '======= ====='
            chars = 8
            print 'IDL guide scales'
            print '----------------'
            print ''
            print div
            print 'Name    Scale'
            print div
            chars = 8

        for scale in scales:
            # Make image of scale
            fig = plot.figure(figsize=(8, 0.5))
            ax1 = fig.add_axes([0.05, 0.1, 0.9, 0.2])
            cscale(scale)
            ncols = np.size(plotvars.cs)
            cmap = matplotlib.colors.ListedColormap(plotvars.cs)
            cb1 = matplotlib.colorbar.ColorbarBase(
                ax1, cmap=cmap, orientation='horizontal', ticks=None)
            cb1.set_ticks([0.0, 1.0])
            cb1.set_ticklabels(['', ''])
            file = '/home/andy/cf-docs/cfplot_sphinx/images/'
            file += 'colour_scales/' + scale + '.png'
            plot.savefig(file)
            plot.close()

            # Use covert to trim the png file to remove white space
            subprocess.call(["convert", "-trim", file, file])

            name_pad = scale
            while len(name_pad) < chars:
                name_pad = name_pad + ' '
            fn = name_pad + '.. image:: images/colour_scales/' + scale + '.png'
            print fn

        print div
        print ''
        print ''


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
            grid_spacing=None, grid_lons=None, grid_lats=None,
            grid_colour=None, grid_linestyle=None, grid_thickness=None):
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
     | colorbar_textsize='11' - colorbar text size
     | colorbar_fontweight='normal' - colorbar font weight
     | legend_text_weight='normal' - legend text weight
     | master_title_fontsize=30 - master title font size
     | master_title_fontweight='normal' - master title font weight
     | continent_thickness=1.5 - default=1.5
     | continent_color='k' - default='k' (black)
     | continent_linestyle='solid' - default='k' (black)
     | viewer='display' - use ImageMagick display program to display
     |                    the pictures.  Set to 'matplotlib' to use the
     |                    built in matplotlib viewer.  display is non-blocking
     |                    of the command prompt while the built in matplotlib
     |                    viewer is blocking.  Set to anything else to not
     |                    view the picture.  
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
     | grid_lons=None - grid longitudes
     | grid_lats=None - grid latitudes
     | grid_colour='grey' - grid colour
     | grid_linestyle='--' - grid line style
     | grid_thickness=1.0 - grid thickness
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
            degsym, axis_width, grid, grid_spacing, grid_lons, grid_lats,
            grid_colour, grid_linestyle, grid_thickness]
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
        plotvars.viewer = 'display'
        plotvars.master_title = None
        plotvars.master_title_location = [0.5, 0.95]
        plotvars.master_title_fontsize = 30
        plotvars.master_title_fontweight = 'normal'
        plotvars.dpi=None
        plotvars.land_color=None
        plotvars.ocean_color=None
        plotvars.lake_color=None
        plotvars.rotated_grid_spacing=10
        plotvars.rotated_deg_spacing=0.75
        plotvars.rotated_grid_thickness=1.0
        plotvars.rotated_continents=True
        plotvars.rotated_grid=True
        plotvars.rotated_labels=True
        plotvars.legend_frame=True
        plotvars.legend_frame_edge_color='k'
        plotvars.legend_frame_face_color=None
        plotvars.degsym=False
        plotvars.axis_width=None
        plotvars.grid=True 
        plotvars.grid_spacing=1
        plotvars.grid_lons=None
        plotvars.grid_lats=None
        plotvars.grid_colour='grey' 
        plotvars.grid_linestyle='--' 
        plotvars.grid_thickness=1.0


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
        plotvars.land_color=land_color
    if ocean_color is not None:
        plotvars.ocean_color=ocean_color
    if lake_color is not None:
        plotvars.lake_color=lake_color

    if rotated_grid_spacing is not None:
        plotvars.rotated_grid_spacing=rotated_grid_spacing
    if rotated_deg_spacing is not None:
        plotvars.rotated_deg_spacing=rotated_deg_spacing
    if rotated_grid_thickness is not None:
        plotvars.rotated_grid_thickness=rotated_grid_thickness
    if rotated_continents is not None:
        plotvars.rotated_continents=rotated_continents
    if rotated_grid is not None:
        plotvars.rotated_grid=rotated_grid
    if rotated_labels is not None:
        plotvars.rotated_labels=rotated_labels
    if legend_frame is not None:
        plotvars.legend_frame=legend_frame
    if legend_frame_edge_color is not None:
        plotvars.legend_frame_edge_color=legend_frame_edge_color
    if legend_frame_face_color is not None:
        plotvars.legend_frame_face_color=legend_frame_face_color
    if degsym is not None:
        plotvars.degsym=degsym
    if axis_width is not None:
        plotvars.axis_width=axis_width
    if grid is not None:
        plotvars.grid=grid
    if grid_spacing is not None:
        plotvars.grid_spacing=grid_spacing
    if grid_lons is not None:
        plotvars.grid_lons=grid_lons
    if grid_lats is not None:
        plotvars.grid_lats=grid_lats
    if grid_colour is not None:
        plotvars.grid_colour=grid_colour
    if grid_linestyle is not None:
        plotvars.grid_linestyle=grid_linestyle
    if grid_thickness is not None:
        plotvars.grid_thickness=grid_thickness





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

    import numpy as np

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
    grid_thickness=plotvars.rotated_grid_thickness



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
        shpfilename = shpreader.natural_earth(resolution=plotvars.resolution, category='physical', name='coastline')
        reader = shapefile.Reader(shpfilename)
        shapes = [s.points for s in reader.shapes()]
        for shape in shapes:
            lons, lats = zip(*shape)
            lons=np.array(lons)
            lats=np.array(lats)

            rotated_transform = ccrs.RotatedPole(pole_latitude=ypole, pole_longitude=xpole)
            points=rotated_transform.transform_points(ccrs.PlateCarree(), lons, lats) 
            xout = np.array(points)[:, 0]
            yout = np.array(points)[:, 1]

            xpts, ypts = vloc(lons=xout, lats=yout, xvec=xvec, yvec=yvec)
            plotvars.plot.plot(xpts, ypts, linewidth=continent_thickness,
                               color=continent_color)



    if xticks is None:
        lons = -180 + np.arange(360 / spacing + 1) * spacing
    else:
        lons=xticks
    if yticks is None:
        lats = -90 + np.arange(180 / spacing + 1) * spacing
    else:
        lats=yticks


    # Latitudes
    if axes:
        if xaxis:
            for val in np.arange(np.size(lons)):
                ipts = 179.0 / degspacing
                lona = np.zeros(int(ipts)) + lons[val]
                lata = -90 + np.arange(ipts - 1) * degspacing

                rotated_transform = ccrs.RotatedPole(pole_latitude=ypole, pole_longitude=xpole)
                points=rotated_transform.transform_points(ccrs.PlateCarree(), lona, lata) 
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
                                       [xpts[loc], xpts[loc]], [0, -2], color='k')
                                plotvars.plot.add_line(line)
                                line.set_clip_on(False)
                                fw = plotvars.text_fontweight
                                if xticklabels is None:
                                    xticklabel=mapaxis(lons[val], lons[val], type=1)[1][0]
                                else:
                                    xticklabel=xticks[val]
                                plotvars.plot.text(xpts[loc], -5,
                                                   xticklabel,
                                                   horizontalalignment='center',
                                                   verticalalignment='top',
                                                   fontsize=plotvars.text_fontsize,
                                                   fontweight=fw)


    # Longitudes
    if axes:
        if yaxis:
            for val in np.arange(np.size(lats)):
                ipts = 359.0 / degspacing
                lata = np.zeros(int(ipts)) + lats[val]
                lona = -180.0 + np.arange(ipts - 1) * degspacing

                rotated_transform = ccrs.RotatedPole(pole_latitude=ypole, pole_longitude=xpole)
                points=rotated_transform.transform_points(ccrs.PlateCarree(), lona, lata) 
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
                                           [0, -2], [ypts[loc], ypts[loc]], color='k')
                                    plotvars.plot.add_line(line)
                                    line.set_clip_on(False)
                                    fw = plotvars.text_fontweight
                                    if yticklabels is None:
                                        yticklabel=mapaxis(lats[val], lats[val], type=2)[1][0]
                                    else:
                                        yticklabel=yticks[val]
    
                                    plotvars.plot.text(-5, ypts[loc],
                                                       yticklabel,
                                                       horizontalalignment='right',
                                                       verticalalignment='center',
                                                       fontsize=plotvars.text_fontsize,
                                                       fontweight=fw)

    # Reset yvec
    yvec = yvec_orig


def lineplot(f=None, x=None, y=None, fill=True, lines=True, line_labels=True,
             title=None, ptype=0, linestyle='-', linewidth=1.0, color='k',
             xlog=False, ylog=False, verbose=None, swap_xy=False,
             marker=None, markersize=5.0, markeredgecolor = 'k',
             markeredgewidth=0.5, label=None,
             legend_location='upper right', xunits=None, yunits=None,
             xlabel=None, ylabel=None, xticks=None, yticks=None,
             xticklabels=None, yticklabels=None, xname=None, yname=None,
             axes=True, xaxis=True, yaxis=True,zorder=None):
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
    | color='k - line color
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
    |
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
    | When making a multiple lineplot the last call to lineplot is the one that
    | any of the above axis overrides should be placed in.
    |
    |
    """
    if verbose:
        print 'lineplot - making a line plot'

    # Catch depreciated keywords
    if xname is not None or yname is not None:
        print '\nlineplot error'
        print 'xname and yname are now depreciated keywords'
        print 'Please use xlabel and ylabel\n'
        return

    ##################
    # Open a new plot is necessary
    ##################
    if plotvars.user_plot == 0:
        gopen(user_plot=0)

    ##################
    # Extract required data
    # If a cf-python field
    ##################
    cf_field = False
    if f is not None:
        if isinstance(f, cf.Field):
            cf_field = True
        elif isinstance(f, cf.FieldList):
            raise TypeError("Can't plot a field list")


    plot_xlabel = ''
    plot_ylabel = ''
    xlabel_units=''
    ylabel_units=''

    if cf_field:
        # Extract data
        if verbose:
            print 'lineplot - CF field, extracting data'

        has_count = 0
        for mydim in f.items():
            if np.size(np.squeeze(f.item(mydim).array)) > 1:
                has_count = has_count + 1
                x = np.squeeze(f.item(mydim).array)

                #x label
                xlabel_units = str(getattr(f.item(mydim), 'Units', ''))
                plot_xlabel = cf_var_name(field=f, dim=mydim) + ' ('
                plot_xlabel += xlabel_units + ')'
                y = np.squeeze(f.array)

                #y label
                if hasattr(f, 'id'):
                    plot_ylabel = f.id
                if hasattr(f, 'ncvar'):
                    plot_ylabel = f.ncvar
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
            for mydim in f.items():
                sn = getattr(f.item(mydim), 'standard_name', False)
                ln = getattr(f.item(mydim), 'long_name', False)
                if sn:
                    errstr = errstr + \
                        str(mydim) + ',' + str(sn) + ',' + \
                        str(f.item(mydim).size) + '\n'
                else:
                    if ln:
                        errstr = errstr + \
                            str(mydim) + ',' + str(ln) + ',' + \
                            str(f.item(mydim).size) + '\n'
            raise Warning(errstr)
    else:
        if verbose:
            print 'lineplot - not a CF field, using passed data'
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

    if ztype is not None:
        temporary_xpts = x
        temporary_ypts = y
        temporary_xlabel = plot_xlabel
        temporary_ylabel = plot_ylabel
        x = temporary_ypts
        y = temporary_xpts
        plot_xlabel = temporary_ylabel
        plot_ylabel = temporary_xlabel



    # Set data values
    if verbose:
        print 'lineplot - setting data values'
    xpts = np.squeeze(x)
    ypts = np.squeeze(y)
    minx = np.min(x)
    miny = np.min(y)
    maxx = np.max(x)
    maxy = np.max(y)
    if cf_field:
        taxis = f.item('T')


    if ztype == 1:
        miny = np.max(y)
        maxy = np.min(y)

    if ztype == 2:
        if f.positive == 'down':
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
        except:
            time_xstr = True
        try:
            float(miny)
        except:
            time_ystr = True



        if cf_field:
            taxis = f.item('T')
            if time_xstr or time_ystr:
                ref_time = f.item('T').units
                ref_calendar = f.item('T').calendar
                ref_time_origin = str(f.item('T').Units.reftime)
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
            xticklabels = map(str, xticks)
    if yticks is None and plotvars.yticks is not None:
        yticks = plotvars.yticks
        if plotvars.yticklabels is not None:
            yticklabels = plotvars.yticklabels
        else:
            yticklabels = map(str, yticks)

    mod = 0
    tight = 0
    if plotvars.user_gset == 1:
        tight = 1




    if xticks is None:
        if plot_xlabel[0:3].lower() == 'lon':
            xticks, xticklabels = mapaxis(minx, maxx, type=1)
        if plot_xlabel[0:3].lower() == 'lat':
            xticks, xticklabels = mapaxis(minx, maxx, type=2)
    if cf_field:
        if xticks is None:
            if f.item('T') is not None:
                if np.size(f.item('T').array) > 1:
                    xticks, xticklabels, plot_xlabel = timeaxis(taxis)
    if xticks is None:
        xticks = gvals(dmin=minx, dmax=maxx, tight=tight, mod=mod)[0]
        xticklabels = xticks
    else:
        if xticklabels is None:
            xticklabels=[]
            for val in xticks:
                xticklabels.append('{}'.format(val))




    if yticks is None:
        if abs(maxy - miny) > 1:
             if miny < maxy:
                 yticks = gvals(dmin=miny, dmax=maxy, tight=tight, mod=mod)[0]
             if maxy < miny:
                 yticks = gvals(dmin=maxy, dmax=miny, tight=tight, mod=mod)[0]

        else:
             yticks = gvals(dmin=miny, dmax=maxy, tight=tight, mod=0)[0]
    if yticklabels is None:
        yticklabels=[]
        for val in yticks:
            yticklabels.append('{}'.format(val))

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
            print 'lineplot - swapping x and y'

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


    # Make graph
    if verbose:
        print 'lineplot - making graph'

    xlabelalignment=plotvars.xtick_label_align
    ylabelalignment=plotvars.ytick_label_align


    graph=plotvars.plot

    if plotvars.twinx:
        graph=graph.twinx()
        ylabelalignment='left'

    if plotvars.twiny:
        graph=graph.twiny()

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
        graph.set_xticklabels(
            xticklabels,
            rotation=plotvars.xtick_label_rotation,
            horizontalalignment=xlabelalignment, fontsize=plotvars.axis_label_fontsize,
                                 fontweight=plotvars.axis_label_fontweight)
    if yticks is not None:
        graph.set_yticks(yticks)
        graph.set_yticklabels(
            yticklabels,
            rotation=plotvars.ytick_label_rotation,
            horizontalalignment=ylabelalignment, fontsize=plotvars.axis_label_fontsize,
                                 fontweight=plotvars.axis_label_fontweight)


    graph.plot(xpts, ypts, color=color, linestyle=linestyle,
                       linewidth=linewidth, marker=marker,
                       markersize=markersize,
                       markeredgecolor=markeredgecolor, 
                       markeredgewidth=markeredgewidth,
                       label=label, zorder=zorder)

    # Time axes sometimes spill over the edge of the plot limits so
    # use tight_layout() to adjust these plots
    #if cf_field:
    #    if f.item('T') is not None:
    #        if np.size(f.item('T').array) > 1:
    #            plotvars.master_plot.tight_layout()


    # Set axis width if required
    if plotvars.axis_width is not None:
        for axis in ['top','bottom','left','right']: 
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







    ##################
    # Save or view plot
    ##################
    if plotvars.user_plot == 0:
        if verbose:
            print 'Saving or viewing plot'
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

    print '=================='
    print 'Regression testing'
    print '=================='
    print ''

    print '------------------'
    print 'Testing for levels'
    print '------------------'
    ref_answer = [-35, -30, -25, -20, -15, -10, -5, 0, 5,
                  10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65]
    compare_arrays(ref=ref_answer, levs_test=True, min=-35, max=65, step=5)

    ref_answer = [-6., -4.8, -3.6, -2.4, -1.2, 0., 1.2, 2.4, 3.6, 4.8, 6.]
    compare_arrays(ref=ref_answer, levs_test=True, min=-6, max=6, step=1.2)

    ref_answer = [50000, 51000, 52000, 53000, 54000, 55000, 56000, 57000,
                  58000, 59000, 60000]
    compare_arrays(ref=ref_answer, levs_test=True, min=50000, max=60000,
                   step=1000)

    ref_answer = [-7000, -6500, -6000, -5500, -5000, -4500, -4000, -3500,
                  -3000, -2500, -2000, -1500, -1000, -500]
    compare_arrays(
        ref=ref_answer,
        levs_test=True,
        min=-7000,
        max=-300,
        step=500)

    print ''
    print '-----------------'
    print 'Testing for gvals'
    print '-----------------'
    ref_answer = [281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292,
                  293]
    compare_arrays(ref=ref_answer, min=280.50619506835938,
                   max=293.48431396484375, mult=0, gvals_test=True)

    ref_answer = [0.356,  0.385,  0.414,  0.443,  0.472,  0.501,  0.53 ,  0.559,
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

    ref_answer = [-1. , -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1,  0. ,
        0.1]
    compare_arrays(ref=ref_answer, min=-1.0, max=0.1, mult=0,
                   gvals_test=True)



    print ''
    print '----------------------------------------'
    print 'Testing for longitude/latitude labelling'
    print '----------------------------------------'
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

    print ''
    print '-----------------'
    print 'Testing for plots'
    print '-----------------'

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
    xvec = f.item('dim1').array
    yvec = f.item('dim0').array
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
        print '***Failed example ' + str(example) + '**'
        error_image = '/home/andy/cfplot.src/cfplot/' + 'error_' + file
        diff_image = '/home/andy/cfplot.src/cfplot/' + 'difference_' + file
        p = subprocess.Popen([comp, file_new, file_ref, diff_image])
        (output, err) = p.communicate()
        p_status = p.wait()
        p = subprocess.Popen([conv, "+append", file_new,
                             file_ref, error_image])
        (output, err) = p.communicate()
        p_status = p.wait()
        subprocess.Popen([disp, diff_image])

    else:
        print 'Passed example ' + str(example)


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
            print '***levs failure***'
            print 'min, max, step are', min, max, step
            print 'generated levels are:'
            print plotvars.levels
            print 'expected levels:'
            print ref
        else:
            pass_str = 'Passed cfp.levs(min=' + str(min) + ', max='
            pass_str += str(max) + ', step=' + str(step) + ')'
            print pass_str

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
            print '***gvals failure***'
            print 'cfp.gvals(' + str(min) + ', ' + str(max) + ')'
            print ''
            print 'generated values are:', vals
            print 'with a  multiplier of ', testmult
            print ''
            print 'expected values:', ref
            print 'with a  multiplier of ', mult
        else:
            pass_str = 'Passed cfp.gvals(' + str(min) + ', '+ str(max) + ')'
            print pass_str

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
            print '***mapaxis failure***'
            print ''
            print 'cfp.mapaxis(min=' + str(min) + ', max=' + str(max)
            print ', type=' + str(type) + ')'
            print 'generated values are:', test_ticks
            print 'with labels:', test_labels
            print ''
            print 'expected ticks:', ref_ticks
            print 'with labels:', ref_labels
        else:
            pass_str = 'Passed cfp.mapaxis(min=' + str(min) + ', max='
            pass_str += str(max) + ', type=' + str(type) + ')'
            print pass_str



def traj(f=None, title=None, ptype=0, linestyle='-', linewidth=1.0, linecolor='b',
         marker='o', markersize=5.0, markerfacecolor='r',
         markeredgecolor='g', latmax = None, latmin=None,
         axes=True, xaxis=True, yaxis=True,
         verbose=None, legend=False,
         xlabel=None, ylabel=None, xticks=None, yticks=None,
         xticklabels=None, yticklabels=None, colorbar=None,
         colorbar_position=None, colorbar_orientation='horizontal',
         colorbar_title=None,
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
    |
    | Vector options
    | vector=False - Draw vectors
    | head_width=2.0 - vector head width
    | head_length=2.0 - vector head length
    | fc='k' - vector face colour
    | ec='k' - vector edge colour


    """
    if verbose:
        print 'traj - making a trajectory plot'




    # Read in data
    # Find the auxiliary lons and lats if provided
    has_lons = False
    has_lats = False
    for mydim in f.items():
        if mydim[:3] == 'aux':
            name = cf_var_name(field=f, dim=mydim)
            if name in ['longitude']:
                lons = np.squeeze(f.item(mydim).array)
                has_lons = True
            if name in ['latitude']:
                lats = np.squeeze(f.item(mydim).array)
                has_lats = True

    data=f.array

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
        pts=np.where(lats >= latmax)
        if np.size(pts) > 0:
            lons[pts] = np.nan
            lats[pts] = np.nan

    if latmin is not None:
        pts=np.where(lats <= latmin)
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

    # Set up mapping
    if plotvars.user_mapset == 0:
        plotvars.lonmin = -180
        plotvars.lonmax = 180
        plotvars.latmin = -90
        plotvars.latmax = 90

    set_map()
    mymap = plotvars.mymap
    user_mapset = plotvars.user_mapset

    # Set the plot limits
    gset(xmin=plotvars.lonmin, xmax=plotvars.lonmax,
         ymin=plotvars.latmin, ymax=plotvars.latmax, user_gset=0)

    # Set the map projection
    if plotvars.proj == 'cyl':
        lon_mid=(plotvars.lonmax - plotvars.lonmin)/2.0 + plotvars.lonmin
        proj=ccrs.PlateCarree()
    if plotvars.proj == 'npstere':
        proj = ccrs.NorthPolarStereo(central_longitude=plotvars.lon_0)
    if plotvars.proj == 'spstere':
        proj = ccrs.SouthPolarStereo(central_longitude=plotvars.lon_0)

      
    ##################################
    # Line, symbol and vector plotting
    ##################################
    for track in np.arange(np.shape(lons)[0]):
        
        xpts = lons[track, :]
        ypts = lats[track, :]

        xpts_orig = deepcopy(xpts)
        xpts = np.mod(xpts + 180, 360) - 180

        # Check if xpts are only within the remapped longitudes above
        if np.min(xpts) < -170 or np.max(xpts) > 170:
            xpts = xpts_orig

            for ix in np.arange(np.size(xpts)-1):
                diff = xpts[ix+1] - xpts[ix]
                diff_limit = 60
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
                print 'plotting lines'
            if verbose and track == 0 and markersize > 0.0:
                print 'plotting markers'

            mymap.plot(xpts, ypts, color=linecolor,
                       linewidth=plot_linewidth, linestyle=linestyle,
                       marker=marker, markersize=plot_markersize,
                       markerfacecolor=markerfacecolor, markeredgecolor=markeredgecolor,
                       zorder=zorder, clip_on=True, transform=ccrs.PlateCarree())


        # Plot vectors
        if vector:
            if verbose and track == 0:
                print 'plotting vectors'
            if zorder is None:
                plot_zorder = 101
            else:
                plot_zorder = zorder
            if plotvars.proj == 'cyl':
                pts = np.ma.MaskedArray.count(xpts)
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
        # Check levels are not None
        levs = plotvars.levels
        if plotvars.levels is not None:
            if verbose:
                print 'traj - plotting different colour markers based on a user set of levels'
            levs = plotvars.levels
            
        else:             
            # Automatic levels
            if verbose:
                print 'traj - generating automatic legend levels'
            dmin = np.nanmin(data)
            dmax = np.nanmax(data)
            levs, mult = gvals(dmin=dmin, dmax=dmax, tight=0, mod=0)

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




        for track in np.arange(np.shape(lons)[0]):
            xpts = lons[track, :]
            ypts = lats[track, :]
            data2 = data[track, :]


            for i in np.arange(np.size(levs)-1):
                color = plotvars.cs[i]
                pts = np.where(np.logical_and(data2 >= levs[i], data2 <= levs[i+1]))
                if zorder is None:
                    plot_zorder = 101
                else:
                    plot_zorder = zorder
                if np.size(pts) > 0:
                    mymap.scatter(
                        xpts[pts], ypts[pts],
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
                  scale=plotvars.resolution, facecolor='none')

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
    if colorbar:
        plot_colorbar = True


    if plot_colorbar:
        if verbose:
            print 'traj - adding colour bar'

        if colorbar is None:
            colorbar_orientation='horizontal'
            if plotvars.proj == 'npstere' or plotvars.proj == 'spstere':
                colorbar_orientation='vertical'


        # Get plotting window coordinates and set colorbar coordinates
        if colorbar_position is None:
            bbox=plotvars.plot.get_position()
            if colorbar_orientation == 'horizontal':
                ax1 = plotvars.master_plot.add_axes([bbox.x0, bbox.y0, bbox.x1-bbox.x0, 0.02])
            else:
                ax1 = plotvars.master_plot.add_axes([bbox.x1, bbox.y0, 0.02, bbox.y1-bbox.y0])
        else:
            ax1 = plotvars.master_plot.add_axes(colorbar_position)



        if (colorbar_title is None):
            colorbar_title = 'No Name'
            if hasattr(f, 'id'):
                colorbar_title = f.id
            if hasattr(f, 'ncvar'):
                colorbar_title = f.ncvar
            if hasattr(f, 'short_name'):
                colorbar_title = f.short_name
            if hasattr(f, 'long_name'):
                colorbar_title = f.long_name
            if hasattr(f, 'standard_name'):
                colorbar_title = f.standard_name

            if hasattr(f, 'Units'):
                if str(f.Units) == '':
                    colorbar_title +=  ''
                else:
                    colorbar_title += '(' + supscr(str(f.Units)) + ')'


        # Get the colour map
        colmap = cscale_get_map()
        cmap = matplotlib.colors.ListedColormap(colmap)
        extend=plotvars.levels_extend
        if plotvars.levels is not None:
            boundaries=plotvars.levels.astype(float)
        else:
            boundaries=levs[1:-1].astype(float)

        # Add colorbar extensions if definded by levs.  Using boundaries[0]-1 
        # for the lower and boundaries[-1]+1 is just for the colorbar and
        # has no meaning for the plot.
        if (extend == 'min' or extend == 'both'):
            cmap.set_under(plotvars.cs[0])
            boundaries = np.insert(boundaries, 0, boundaries[0]-1)
        if (extend == 'max' or extend == 'both'):
            cmap.set_over(plotvars.cs[-1])
            boundaries = np.insert(boundaries, len(boundaries), boundaries[-1]+1)


        cbar = matplotlib.colorbar.ColorbarBase(ax1, cmap=cmap,
                            norm=plotvars.norm,
                            extend=extend,
                            extendfrac='auto',
                            boundaries=boundaries,
                            ticks=plotvars.levels,
                            spacing='uniform',
                            orientation=colorbar_orientation)

        # Reset plot position
        gpos(pos=plotvars.pos)





        cbar.set_label(colorbar_title, fontsize=plotvars.colorbar_fontsize,
                       fontweight=plotvars.colorbar_fontweight)

        # Bug in Matplotlib colorbar labelling
        # With clevs=[-1, 1, 10000, 20000, 30000, 40000, 50000, 60000]
        # Labels are [0, 2, 10001, 20001, 30001, 40001, 50001, 60001]
        # With a +1 near to the colorbar label
        if plotvars.levels is not None:
            cbar.set_ticks([i for i in plotvars.levels])
        else:
            cbar.set_ticks([i for i in levs[1:-1]])


        for t in cbar.ax.get_xticklabels():
           t.set_fontsize(plotvars.colorbar_fontsize)
           t.set_fontweight(plotvars.colorbar_fontweight)




    # reset plot limits if not a user plot
    if plotvars.user_gset == 0:
        gset()







    ##########
    # Save plot
    ##########
    if plotvars.user_plot == 0:
        gclose()




def cfplot_colorbar(cfill=None, colorbar_labels=None,
                    colorbar_orientation=None,
                    colorbar_position=None,
                    colorbar_shrink=None,
                    cb_orient=None, colorbar_title=None,
                    text_fontsize=None, 
                    text_fontweight=None,
                    colorbar_text_up_down=None,
                    colorbar_text_down_up=None,
                    colorbar_drawedges=None,
                    verbose=None):
    """
    | cfplot_colorbar is the internal interface to the Matplotlib
    | colorbar routine
    | 
    | cfill=None
    | colorbar_labels=None - colorbar labels
    | colorbar_orientation=None - orientation 'horizontal' or 'vertical'
    | colorbar_position=None
    | colorbar_shrink=None
    | cb_orient=None
    | colorbar_title=None
    | text_fontsize=None
    | text_fontweight=None
    | colorbar_text_up_down=None
    | colorbar_text_down_up=None
    | colorbar_drawedges=None - Draw internal delimeter lines in colorbar
    | verbose=None
    |
    |
    |
    """



    if verbose:
        print 'con - adding colour bar'

    colorbar_fontsize = plotvars.colorbar_fontsize
    colorbar_fontweight = plotvars.colorbar_fontweight

    # Work out colour bar labeling
    lbot=colorbar_labels
    if colorbar_text_up_down:
        lbot=colorbar_labels[1:][::2]
        ltop=colorbar_labels[::2]

    if colorbar_text_down_up:
        lbot=colorbar_labels[::2]
        ltop=colorbar_labels[1:][::2]

    
            
    pad = 0.10
    if plotvars.rows >= 3:
        pad = 0.15
    if plotvars.rows >= 5:
        pad = 0.20
    if colorbar_position is None:
        cbar = plotvars.master_plot.colorbar(cfill,
                                             ticks=lbot,
                                             orientation=cb_orient,
                                             aspect=75, pad=pad,
                                             shrink=colorbar_shrink,
                                             drawedges=colorbar_drawedges)
    else:
        position = plotvars.master_plot.add_axes(colorbar_position)
        cbar = plotvars.master_plot.colorbar(
                    cfill, cax=position, ticks=lbot,
                    orientation=colorbar_orientation,
                    drawedges=colorbar_drawedges)
        gpos(pos=plotvars.pos)

    cbar.set_label(colorbar_title, fontsize=colorbar_fontsize,
                   fontweight=colorbar_fontweight)

    #print dir(cbar.ax.xaxis)
    #for tick in cbar.ax.xaxis.get_ticklines():
    #    tick.set_visible(False)

    # Bug in Matplotlib colorbar labelling
    # With clevs=[-1, 1, 10000, 20000, 30000, 40000, 50000, 60000]
    # Labels are [0, 2, 10001, 20001, 30001, 40001, 50001, 60001]
    # With a +1 near to the colorbar label
    cbar.set_ticklabels([str(i) for i in colorbar_labels])
    if colorbar_orientation == 'horizontal':
        for tick in cbar.ax.xaxis.get_ticklines():
            tick.set_visible(False)
        for t in cbar.ax.get_xticklabels():
            t.set_fontsize(colorbar_fontsize)
            t.set_fontweight(colorbar_fontweight)
    else:
        for tick in cbar.ax.yaxis.get_ticklines():
            tick.set_visible(False)
        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(colorbar_fontsize)
            t.set_fontweight(colorbar_fontweight)



    # Alternate text top and bottom on a horizontal colorbar if requested
    # Use method described at:
    # https://stackoverflow.com/questions/37161022/matplotlib-colorbar-
    # alternating-top-bottom-labels
    if colorbar_text_up_down or colorbar_text_down_up:

        vmin=cbar.norm.vmin
        vmax=cbar.norm.vmax

        if cbar.extend=='min':
            shift_l=0.05
            scaling=0.95
        elif cbar.extend=='max':
            shift_l=0.
            scaling=0.95
        elif cbar.extend=='both':
            shift_l=0.05
            scaling=0.9
        else:
            shift_l=0.
            scaling=1.0



        #-------------Print bottom tick labels-------------
        cbar.ax.set_xticklabels(lbot)


        #--------------Print top tick labels--------------
        for ii in ltop:
            cbar.ax.text(shift_l + scaling*(ii-vmin)/(vmax-vmin),
                1.5, str(ii), transform=cbar.ax.transAxes,
                va='bottom', ha='center', fontsize=colorbar_fontsize,
                fontweight=colorbar_fontweight)


        for t in cbar.ax.get_xticklabels():
            t.set_fontsize(colorbar_fontsize)
            t.set_fontweight(colorbar_fontweight)






def map_title(title=None):
    """
    | map_title is an internal routine to draw a title on a map plot
    |
    | title=None - title to put on map plot
    |
    |
    |
    |
    |
    |
    """

    boundinglat=plotvars.boundinglat
    lon_0=plotvars.lon_0
    lonmin=plotvars.lonmin
    lonmax=plotvars.lonmax
    latmin=plotvars.latmin
    latmax=plotvars.latmax
    polar_range=90-abs(boundinglat)

    if plotvars.proj == 'npstere':
        mylon=lon_0+180
        mylat=boundinglat-polar_range/15.0
        proj=ccrs.NorthPolarStereo(central_longitude=lon_0)
        lon_mid=lon_0
        xpt, ypt = proj.transform_point(mylon, mylat, ccrs.PlateCarree())

    if plotvars.proj == 'spstere':
        mylon=lon_0
        mylat=boundinglat+polar_range/15.0
        proj=ccrs.SouthPolarStereo(central_longitude=lon_0)
        lon_mid=lon_0
        xpt, ypt = proj.transform_point(mylon, mylat, ccrs.PlateCarree())

    if plotvars.proj == 'cyl':
        lon_mid = lonmin + (lonmax - lonmin) / 2.0
        proj=ccrs.PlateCarree(central_longitude=lon_mid)
        mylon=lon_mid
        mylat=latmax        
        xpt, ypt = proj.transform_point(mylon, mylat, ccrs.PlateCarree())
        ypt=ypt+(latmax-latmin)/40.0

    if plotvars.proj=='lcc':
        lon_mid = lonmin + (lonmax - lonmin) / 2.0
        proj=ccrs.LambertConformal(central_longitude=plotvars.lon_0,
                                   central_latitude=plotvars.lat_0,
                                   cutoff=plotvars.latmin)
        mylon=lon_mid
        mylat=latmax 
        xpt, ypt = proj.transform_point(0.0, mylat, ccrs.PlateCarree())



    plotvars.mymap.text(xpt, ypt, title, va='bottom', 
        ha='center',
        rotation='horizontal', rotation_mode='anchor',
        fontsize=plotvars.title_fontsize,
        fontweight=plotvars.title_fontweight)




def plot_map_axes(axes=None, xaxis=None, yaxis=None,
                  xticks=None, xticklabels=None,
                  yticks=None, yticklabels=None,
                  user_xlabel=None, user_ylabel=None,
                  verbose=None):
    """
    | plot_map_axes is an internal routine to draw the axes on a map plot
    |
    | axes=None - Boolean for drawing axes
    | xaxis=None - Boolean for drawing x-axis
    | yaxis=None - Boolean for drawing x-axis
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
    title_fontsize = plotvars.title_fontsize
    text_fontsize = plotvars.text_fontsize
    axis_label_fontsize = plotvars.axis_label_fontsize
    text_fontweight = plotvars.text_fontweight
    title_fontweight = plotvars.title_fontweight
    axis_label_fontweight = plotvars.axis_label_fontweight


    # Map parameters
    boundinglat=plotvars.boundinglat
    lon_0=plotvars.lon_0
    lonmin=plotvars.lonmin
    lonmax=plotvars.lonmax
    latmin=plotvars.latmin
    latmax=plotvars.latmax
    polar_range=90-abs(boundinglat)



    # Cylindrical
    if plotvars.proj == 'cyl':

        if verbose:
            print 'con - adding cylindrical axes'
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
            print 'con - adding stereographic axes'

        mymap=plotvars.mymap
        latrange = 90-abs(boundinglat)
        latstep = 30
        if 90 - abs(boundinglat) <= 50:
            latstep = 10

        proj=ccrs.Geodetic()

        # Add 
        if axes:
            if xaxis:
               if yticks is None:
                   latvals=np.arange(5)*30-60
               else:
                   latvals=np.array(yticks)

               if plotvars.proj == 'npstere':
                   latvals=latvals[np.where(latvals>=boundinglat)]
               else:
                   latvals=latvals[np.where(latvals<=boundinglat)]

               for lat in latvals:
                   if abs(lat - boundinglat) > 1:
                       lons=np.arange(361)
                       lats=np.zeros(361)+lat
                       mymap.plot(lons, lats, color='k', 
                                  linewidth=1, linestyle='--',
                                  transform=proj) 

            if yaxis:
                if xticks is None:
                    lonvals=np.arange(7)*60
                else:
                    lonvals=xticks

                for lon in lonvals:
                    label = mapaxis(lon, lon, 1)[1][0]

                    if plotvars.proj == 'npstere':
                        lats=np.arange(90-boundinglat)+boundinglat
                    else:
                        lats=np.arange(boundinglat+91)-90
                    lons=np.zeros(np.size(lats))+lon
                    mymap.plot(lons, lats, color='k', 
                               linewidth=1, linestyle='--',
                               transform=proj) 




            # Add longitude labels
            if plotvars.proj == 'npstere':
                proj=ccrs.NorthPolarStereo(central_longitude=lon_0)
                pole=90
                latpt = boundinglat - latrange/40.0
            else:
                proj=ccrs.SouthPolarStereo(central_longitude=lon_0)
                pole=-90
                latpt = boundinglat + latrange/40.0

            lon_mid, lat_mid =  proj.transform_point(0,pole, ccrs.PlateCarree())


            for xtick in lonvals:
                label = mapaxis(xtick, xtick, 1)[1][0]
                lonr, latr = proj.transform_point(xtick,latpt, ccrs.PlateCarree())

                v_align='center'
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
        lons=np.arange(360)
        lats=np.zeros(np.size(lons))+boundinglat
        device_coords=proj.transform_points(ccrs.PlateCarree(), lons, lats)    

        xmin=np.min(device_coords[:,0])
        xmax=np.max(device_coords[:,0])  
        ymin=np.min(device_coords[:,1])
        ymax=np.max(device_coords[:,1])


        # blank off data past the bounding latitude
        pts=np.where(device_coords[:,0] >= 0.0)
        xpts=np.append(device_coords[:,0][pts], np.zeros(np.size(pts))+xmax)
        ypts=np.append(device_coords[:,1][pts], device_coords[:,1][pts][::-1])
        mymap.fill(xpts, ypts, alpha=1.0, color='w', zorder=100)

        xpts=np.append(np.zeros(np.size(pts))+xmin, -1.0* device_coords[:,0][pts])
        ypts=np.append(device_coords[:,1][pts], device_coords[:,1][pts][::-1])
        mymap.fill(xpts, ypts, alpha=1.0, color='w', zorder=100)


        # Turn off map outside the cicular plot area
        mymap.outline_patch.set_visible(False)


        # Draw a line around the bounding latitude
        lons=np.arange(361)
        lats=np.zeros(np.size(lons))+boundinglat
        device_coords=proj.transform_points(ccrs.PlateCarree(), lons, lats)    
        mymap.plot(device_coords[:,0], device_coords[:,1], color='k',
                   zorder=100, clip_on=False)

        # Modify xlim and ylim values as the default values clip the plot slightly
        xmax = np.max(np.abs(mymap.set_xlim(None)))
        mymap.set_xlim((-xmax, xmax), emit=False)
        ymax = np.max(np.abs(mymap.set_ylim(None)))
        mymap.set_ylim((-ymax, ymax), emit=False)




    # Lambert conformal 
    if plotvars.proj == 'lcc':
        lon_0=plotvars.lonmin+(plotvars.lonmax-plotvars.lonmin)/2.0
        lat_0=plotvars.latmin+(plotvars.latmax-plotvars.latmin)/2.0

        mymap=plotvars.mymap
        proj=ccrs.LambertConformal(central_longitude=lon_0,
                                   central_latitude=lat_0,
                                   cutoff=-40)

        lonmin=plotvars.lonmin
        lonmax=plotvars.lonmax
        latmin=plotvars.latmin
        latmax=plotvars.latmax

        # Modify xlim and ylim values as the default values clip the plot slightly
        xmin = mymap.set_xlim(None)[0]
        xmax = mymap.set_xlim(None)[1]
        ymin = mymap.set_ylim(None)[0]
        ymax = mymap.set_ylim(None)[1]

        mymap.set_ylim(ymin*1.05, ymax, emit=False)
        mymap.set_ylim(None)

        # Mask off contours that appear because of the plot extention
        #mymap.add_patch(mpatches.Polygon([[xmin, ymin], [xmax,ymin],
        #                                  [xmax, ymin*1.05], [xmin, ymin*1.05]],
        #                         facecolor='red'))

                                 #transform=ccrs.PlateCarree()))

        lons=np.arange(lonmax-lonmin+1)+lonmin
        lats=np.arange(latmax-latmin+1)+latmin
        nlons=np.size(lons)
        nlats=np.size(lats)
        verts=[]
        for lat in lats:
            verts.append([lonmin, lat])
        for lon in lons:
            verts.append([lon, latmax])
        for lat in lats[::-1]:
            verts.append([lonmax, lat])
        for lon in lons[::-1]:
            verts.append([lon, latmin])


        # Mask left and right of plot
        lats=np.arange(latmax-latmin+1)+latmin
        lons=np.zeros(np.size(lats))+lonmin
        npts=np.size(lats)
        device_coords=proj.transform_points(ccrs.PlateCarree(), lons, lats)
        xmin=np.min(device_coords[:,0]) 
        xmax=np.max(device_coords[:,0]) 
        ymin=np.min(device_coords[:,1]) 
        ymax=np.max(device_coords[:,1]) 

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
        lons=np.arange(lonmax-lonmin+1)+lonmin
        lats=np.zeros(np.size(lons))+latmax
        device_coords=proj.transform_points(ccrs.PlateCarree(), lons, lats)
        ymax=np.max(device_coords[:,1]) 

        xpts=np.append(device_coords[:,0], device_coords[:,0][::-1])
        ypts=np.append(device_coords[:,1], np.zeros(np.size(lons))+ymax)

        mymap.fill(xpts, ypts, alpha=1.0, color='w', zorder=100)
        mymap.plot(device_coords[:,0], device_coords[:,1], color='k', zorder=101, clip_on=False)



        # Lower
        lons=np.arange(lonmax-lonmin+1)+lonmin
        lats=np.zeros(np.size(lons))+latmin
        device_coords=proj.transform_points(ccrs.PlateCarree(), lons, lats)
        ymin=np.min(device_coords[:,1])*1.05

        xpts=np.append(device_coords[:,0], device_coords[:,0][::-1])
        ypts=np.append(device_coords[:,1], np.zeros(np.size(lons))+ymin)

        mymap.fill(xpts, ypts, alpha=1.0, color='w', zorder=100)
        mymap.plot(device_coords[:,0], device_coords[:,1], color='k', zorder=101, clip_on=False)
           
        # Turn off drawing of the rectangular box around the plot
        mymap.outline_patch.set_visible(False)


 
        # Draw longitudes and latitudes if requested
        fs = plotvars.axis_label_fontsize
        fw = plotvars.axis_label_fontweight
        lw=1.0
        if axes and xaxis:
            if xticks is None:
                map_xticks, map_xticklabels=mapaxis(min=plotvars.lonmin, max=plotvars.lonmax, type=1)
            else:
                map_xticks=xticks
                if xticklabels is None:
                    map_xticklabels=xticks
                else:
                    map_xticklabels=xticklabels

            if axes and xaxis:
                lats=np.arange(latmax-latmin+1)+latmin
                for tick in np.arange(np.size(map_xticks)):
                    lons=np.zeros(np.size(lats))+map_xticks[tick]
                    device_coords=proj.transform_points(ccrs.PlateCarree(), lons, lats)
                    mymap.plot(device_coords[:,0], device_coords[:,1], 
                               linewidth=lw, linestyle='--', color='k', zorder=101)

                    device_coords=proj.transform_point(map_xticks[tick], latmin-3, ccrs.PlateCarree())
                    mymap.text(device_coords[0], device_coords[1],
                               map_xticklabels[tick], 
                               horizontalalignment='center', 
                               fontsize=fs,
                               fontweight=fw,
                               zorder=101)




        if yticks is None:
            map_yticks, map_yticklabels=mapaxis(min=plotvars.latmin, max=plotvars.latmax, type=2)
        else:
            map_yticks=yticks
            if yticklabels is None:
                map_yticklabels=yticks
            else:
                map_yticklabels=yticklabels

        if axes and yaxis:
            lons=np.arange(lonmax-lonmin+1)+lonmin
            for tick in np.arange(np.size(map_yticks)):
                lats=np.zeros(np.size(lons))+map_yticks[tick]
                device_coords=proj.transform_points(ccrs.PlateCarree(), lons, lats)
                mymap.plot(device_coords[:,0], device_coords[:,1],
                           linewidth=lw, linestyle='--', color='k', zorder=101)

                device_coords=proj.transform_point(lonmin-1, map_yticks[tick], ccrs.PlateCarree())
                mymap.text(device_coords[0], device_coords[1],
                           map_yticklabels[tick], 
                           horizontalalignment='right',
                           verticalalignment='center', 
                           fontsize=fs,
                           fontweight=fw,
                           zorder=101)

                device_coords=proj.transform_point(lonmax+1, map_yticks[tick], ccrs.PlateCarree())
                mymap.text(device_coords[0], device_coords[1],
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
        if plotvars.grid_lons is None:
            lons = np.arange(30 / spacing + 1) * spacing
            lons = np.append((lons*-1)[::-1], lons[1:])
        else:
            lons=plotvars.grid_lons
        if plotvars.grid_lats is None:
            lats = np.arange(90.0 / spacing + 1) * spacing
        else:
            lats=plotvars.grid_lats



        plotvars.mymap.gridlines(color=plotvars.grid_colour, 
                                 linewidth=plotvars.grid_thickness, 
                                 linestyle=plotvars.grid_linestyle,
                                 xlocs=lons, ylocs=lats)






