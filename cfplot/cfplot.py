"""
Routines for making climate contour/vector plots using cf-python, matplotlib and basemap.
Andy Heaps NCAS-CMS September 2016
"""


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

import os
import sys
cf_version_min='1.0.1'
cf_errstr='\n cf-python > '+cf_version_min+' needs to be installed to use cf-plot \n'
try: 
   import cf
   if cf.__version__ < cf_version_min: raise  Warning(cf_errstr) 
except ImportError:
   raise  Warning(cf_errstr) 

import numpy as np
import subprocess
from scipy import interpolate
import time
import matplotlib
from copy import deepcopy


#Check for a display and use the Agg backing store if none is present
#This is for batch mode processing
try:
   disp=os.environ["DISPLAY"]
except:
   matplotlib.use('Agg')
import matplotlib.pyplot as plot
from mpl_toolkits.basemap import Basemap, shiftgrid, addcyclic



#Code to check if the ImageMagick display command is available
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


#Default colour scales
#cscale1 is a differential data scale - blue to red
cscale1=['#0a3278', '#0f4ba5', '#1e6ec8', '#3ca0f0', '#50b4fa', '#82d2ff', '#a0f0ff', \
         '#c8faff', '#e6ffff', '#fffadc', '#ffe878', '#ffc03c', '#ffa000', '#ff6000', \
         '#ff3200', '#e11400', '#c00000', '#a50000']

#viridis is a continuous data scale - blue, green, yellow
viridis=['#440154', '#440255', '#440357', '#450558', '#45065a', '#45085b', '#46095c', '#460b5e', '#460c5f', '#460e61', \
'#470f62', '#471163', '#471265', '#471466', '#471567', '#471669', '#47186a', '#48196b', '#481a6c', '#481c6e', '#481d6f', \
'#481e70', '#482071', '#482172', '#482273', '#482374', '#472575', '#472676', '#472777', '#472878', '#472a79', '#472b7a', \
'#472c7b', '#462d7c', '#462f7c', '#46307d', '#46317e', '#45327f', '#45347f', '#453580', '#453681', '#443781', '#443982', \
'#433a83', '#433b83', '#433c84', '#423d84', '#423e85', '#424085', '#414186', '#414286', '#404387', '#404487', '#3f4587', \
'#3f4788', '#3e4888', '#3e4989', '#3d4a89', '#3d4b89', '#3d4c89', '#3c4d8a', '#3c4e8a', '#3b508a', '#3b518a', '#3a528b', \
'#3a538b', '#39548b', '#39558b', '#38568b', '#38578c', '#37588c', '#37598c', '#365a8c', '#365b8c', '#355c8c', '#355d8c', \
'#345e8d', '#345f8d', '#33608d', '#33618d', '#32628d', '#32638d', '#31648d', '#31658d', '#31668d', '#30678d', '#30688d', \
'#2f698d', '#2f6a8d', '#2e6b8e', '#2e6c8e', '#2e6d8e', '#2d6e8e', '#2d6f8e', '#2c708e', '#2c718e', '#2c728e', '#2b738e', \
'#2b748e', '#2a758e', '#2a768e', '#2a778e', '#29788e', '#29798e', '#287a8e', '#287a8e', '#287b8e', '#277c8e', '#277d8e', \
'#277e8e', '#267f8e', '#26808e', '#26818e', '#25828e', '#25838d', '#24848d', '#24858d', '#24868d', '#23878d', '#23888d', \
'#23898d', '#22898d', '#228a8d', '#228b8d', '#218c8d', '#218d8c', '#218e8c', '#208f8c', '#20908c', '#20918c', '#1f928c', \
'#1f938b', '#1f948b', '#1f958b', '#1f968b', '#1e978a', '#1e988a', '#1e998a', '#1e998a', '#1e9a89', '#1e9b89', '#1e9c89', \
'#1e9d88', '#1e9e88', '#1e9f88', '#1ea087', '#1fa187', '#1fa286', '#1fa386', '#20a485', '#20a585', '#21a685', '#21a784', \
'#22a784', '#23a883', '#23a982', '#24aa82', '#25ab81', '#26ac81', '#27ad80', '#28ae7f', '#29af7f', '#2ab07e', '#2bb17d', \
'#2cb17d', '#2eb27c', '#2fb37b', '#30b47a', '#32b57a', '#33b679', '#35b778', '#36b877', '#38b976', '#39b976', '#3bba75', \
'#3dbb74', '#3ebc73', '#40bd72', '#42be71', '#44be70', '#45bf6f', '#47c06e', '#49c16d', '#4bc26c', '#4dc26b', '#4fc369', \
'#51c468', '#53c567', '#55c666', '#57c665', '#59c764', '#5bc862', '#5ec961', '#60c960', '#62ca5f', '#64cb5d', '#67cc5c', \
'#69cc5b', '#6bcd59', '#6dce58', '#70ce56', '#72cf55', '#74d054', '#77d052', '#79d151', '#7cd24f', '#7ed24e', '#81d34c', \
'#83d34b', '#86d449', '#88d547', '#8bd546', '#8dd644', '#90d643', '#92d741', '#95d73f', '#97d83e', '#9ad83c', '#9dd93a', \
'#9fd938', '#a2da37', '#a5da35', '#a7db33', '#aadb32', '#addc30', '#afdc2e', '#b2dd2c', '#b5dd2b', '#b7dd29', '#bade27', \
'#bdde26', '#bfdf24', '#c2df22', '#c5df21', '#c7e01f', '#cae01e', '#cde01d', '#cfe11c', '#d2e11b', '#d4e11a', '#d7e219', \
'#dae218', '#dce218', '#dfe318', '#e1e318', '#e4e318', '#e7e419', '#e9e419', '#ece41a', '#eee51b', '#f1e51c', '#f3e51e', \
'#f6e61f', '#f8e621', '#fae622', '#fde724']


#####################################
#plotvars - global plotting variables
#####################################
plotvars=pvars(lonmin=-180, lonmax=180, latmin=-90, latmax=90, proj='cyl', \
               resolution='c', plot_type=1, boundinglat=0, lon_0=0, \
               levels=None, levels_min=None, levels_max=None, levels_step=None, \
               levels_extend='both', xmin=None, xmax=None, ymin=None, ymax=None, \
               xlog=None, ylog=None,\
               rows=1, columns=1, file=None, orientation='landscape',\
               user_mapset=0, user_gset=0, cscale_flag=0, user_levs=0, user_plot=0,\
               master_plot=None, plot=None, cs=cscale1, cs_user='cscale1',\
               mymap=None, \
               xticks=None, yticks=None, xticklabels=None, yticklabels=None, \
               xstep=None, ystep=None, xlabel=None, ylabel=None, title=None, \
               title_fontsize=15, axis_label_fontsize=11, text_fontsize=11, \
               text_fontweight='normal', axis_label_fontweight='normal', \
               title_fontweight='normal', \
               continent_thickness=None, continent_color=None, pos=1, viewer='display', \
               tspace_year=None, tspace_month=None, tspace_day=None, tspace_hour=None)


def con(f=None, x=None, y=None, fill=True, lines=True, line_labels=True, title=None, \
        colorbar_title=None, colorbar=1, colorbar_label_skip=None, ptype=0, \
        negative_linestyle=None, blockfill=None, zero_thick=None, colorbar_shrink=None, \
        colorbar_orientation=None, colorbar_position=None, xlog=False, ylog=False, \
        axes=True, xaxis=True, yaxis=True, xticks=None, xticklabels=None, \
        yticks=None, yticklabels=None, xlabel=None, ylabel=None, verbose=None):
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
    | negative_linestyle=None - set to 1 to get dashed negative contours
    | zero_thick=None - add a thick zero contour line. Set to 3 for example.
    | blockfill=None - set to 1 for a blockfill plot
    | colbar_title=colbar_title - title for the colour bar
    | colorbar=1 - add a colour bar if a filled contour plot
    | colorbar_label_skip=None - skip colour bar labels. Set to 2 to skip every
    |                            other label.
    | colorbar_orientation=None - options are 'horizontal' and 'vertical'
    |                      The default for most plots is horizontal but
    |                      for polar stereographic plots this is vertical.
    | colorbar_shrink=None - value to shrink the colorbar by.  If the colorbar 
    |                        exceeds the plot area then values of 1.0, 0.55 or 0.5
    |                        may help it better fit the plot area.
    | colorbar_position=None - position of colorbar [xmin, ymin, x_extent, y_extent]
    |                          in normalised coordinates. Use when a common colorbar 
                               is required for a set of plots. A typical set of values
                               would be [0.1, 0.05, 0.8, 0.02]
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
    | verbose=None - change to 1 to get a verbose listing of what con is doing
    |
    :Returns:
     None

   """ 


   #Turn off divide warning in contour routine which is a numpy issue
   old_settings = np.seterr(all='ignore')
   np.seterr(divide='ignore')

   #Set potential user axis labels
   user_xlabel=xlabel
   user_ylabel=ylabel

   #Extract required data for contouring
   #If a cf-python field
   if isinstance(f[0], cf.Field):
      #Check if this is a cf.Fieldlist and reject if it is
      if len(f) > 1:
         errstr='\n cf_data_assign error - passed field is a cf.Fieldlist\n'
         errstr=errstr+'Please pass one field for contouring\n'
         errstr=errstr+'i.e. f[0]\n'
         raise  Warning(errstr) 

      #Extract data
      if verbose: print 'con - calling cf_data_assign'
      f=f[0]
      field, x, y, ptype, colorbar_title, xlabel, ylabel, xpole, ypole=\
             cf_data_assign(f, colorbar_title, verbose=verbose)
      if user_xlabel is not None: xlabel=user_xlabel
      if user_ylabel is not None: ylabel=user_ylabel
   else:
      if verbose: print 'con - using user assigned data'
      field=f #field data passed in as f
      check_data(field, x, y)
      xlabel=''
      ylabel=''


   #Set contour line styles
   if negative_linestyle is None: matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
   else: matplotlib.rcParams['contour.negative_linestyle'] = 'Dashed'


   #Set contour lines off on block plots
   if blockfill: 
      fill=False
      if lines is True: lines=False
      field_orig=field  
      x_orig=x
      y_orig=y   

      if (plotvars.proj == 'npstere' or plotvars.proj == 'spstere'):         
         errstr='\n\n con error - blockfill not supported for polar stereograpic plots\n\n'
         raise  Warning(errstr)

   #Turn off colorbar if fill is turned off
   if fill == 0 and blockfill is None: colorbar=0

   #Revert to default colour scale if cscale_flag flag is set
   if plotvars.cscale_flag == 0: plotvars.cs=cscale1


   #Set the orientation of the colorbar
   if plotvars.plot_type == 1:
      if plotvars.proj == 'npstere' or plotvars.proj == 'spstere':
         if colorbar_orientation is None: colorbar_orientation='vertical'
   if colorbar_orientation is None: colorbar_orientation='horizontal'



   #Set size of color bar if not specified
   if colorbar_shrink is None:
      colorbar_shrink=1.0
      if plotvars.plot_type == 1:
         scale=(plotvars.lonmax-plotvars.lonmin)/(plotvars.latmax-plotvars.latmin)
         if scale <= 1: colorbar_shrink=0.55
         if plotvars.orientation == 'landscape':
            if (plotvars.proj == 'cyl' and colorbar_orientation == 'vertical'): colorbar_shrink=0.5
            if (plotvars.proj == 'cyl' and colorbar_orientation == 'horizontal'): colorbar_shrink=1.0
         if plotvars.orientation == 'portrait':
            if (plotvars.proj == 'cyl' and colorbar_orientation == 'vertical'): colorbar_shrink=0.25
            if (plotvars.proj == 'cyl' and colorbar_orientation == 'horizontal'): colorbar_shrink=1.0       

         if plotvars.proj == 'npstere' or plotvars.proj == 'spstere': 
            if plotvars.orientation == 'landscape':
               if colorbar_orientation == 'horizontal': colorbar_shrink=1.0
               if colorbar_orientation == 'vertical': colorbar_shrink=1.0
            if plotvars.orientation == 'portrait':
               if colorbar_orientation == 'horizontal': colorbar_shrink=1.0
               if colorbar_orientation == 'vertical': colorbar_shrink=1.0




   #Set plot type if user specified
   if (ptype != None): plotvars.plot_type=ptype
 
 
   #Get contour levels      
   includes_zero=0
   if plotvars.user_levs == 1:
      #User defined    
      if verbose: print 'con - using user defined contour levels'
      clevs=plotvars.levels
      mult=0
      fmult=1
   else:
      #Automatic levels  
      if verbose: print 'con - generating automatic contour levels'
      clevs, mult = gvals(dmin=np.nanmin(field), dmax=np.nanmax(field), tight=0)
      fmult=10**-mult      



   #Set the colour scale
   #Nothing defined
   if plotvars.cscale_flag == 0:
       includes_zero=0
       col_zero=0
       for cval in clevs:
           if includes_zero == 0: col_zero=col_zero+1   
           if cval == 0: includes_zero=1

       if includes_zero == 1:
           cs_below=col_zero
           cs_above=np.size(clevs)-col_zero+1
           if plotvars.levels_extend == 'max':
               cs_below=cs_below-1
               cs_above=cs_above+1
           cscale('scale1', below=cs_below, above=cs_above)
       else:
           cscale('viridis', ncols=np.size(clevs)+1)   

       plotvars.cscale_flag=0 

   #User selected colour map but no mods so fit to levels
   if plotvars.cscale_flag == 1: 
      cscale(plotvars.cs_user, ncols=np.size(clevs)+1)  
      plotvars.cscale_flag=1

   #User selected colour map with mods so leave as is
   #if plotvars.cscale_flag == 2:





   #Set colorbar labels
   #Set a sensible label spacing if the user hasn't already done so   
   if colorbar_label_skip is None:
      if colorbar_orientation == 'horizontal':
         nchars=0
         for lev in clevs: nchars=nchars+len(str(lev))
         colorbar_label_skip=nchars/80+1
         if plotvars.columns > 1: colorbar_label_skip=nchars*(plotvars.columns)/80
      else:
         colorbar_label_skip=1
      
   if colorbar_label_skip > 1:
      if includes_zero: 
         #include zero in the colorbar labels
         zero_pos=[i for i,mylev in enumerate(clevs) if mylev == 0][0]
         colorbar_labels=clevs[zero_pos]
         i=zero_pos+colorbar_label_skip
         while i <= len(clevs)-1:
            colorbar_labels=np.append(colorbar_labels, clevs[i])
            i=i+colorbar_label_skip
         i=zero_pos-colorbar_label_skip
         if i >=0:
            while i >= 0:
               colorbar_labels=np.append(clevs[i], colorbar_labels)
               i=i-colorbar_label_skip
      else: 
         colorbar_labels=clevs[0]
         i=colorbar_label_skip
         while i <= len(clevs)-1:
            colorbar_labels=np.append(colorbar_labels, clevs[i])
            i=i+colorbar_label_skip        
   else: 
      colorbar_labels=clevs


   #Add mult to colorbar_title if used 
   if (colorbar_title == None): 
      colorbar_title=''
   else:
      if (mult != 0): colorbar_title=colorbar_title+' *10$^{'+str(mult)+'}$' 


   #Catch null titles
   if title is None: title=''
   if plotvars.title is not None: title=plotvars.title
  
   #Set plot variables
   title_fontsize=plotvars.title_fontsize
   text_fontsize=plotvars.text_fontsize
   axis_label_fontsize=plotvars.axis_label_fontsize
   continent_thickness=plotvars.continent_thickness
   continent_color=plotvars.continent_color
   text_fontweight=plotvars.text_fontweight
   title_fontweight=plotvars.title_fontweight
   axis_label_fontweight=plotvars.axis_label_fontweight
   if continent_thickness is None: continent_thickness=1.5
   if continent_color is None: continent_color='k'

 
   #Select contour triangulation based on input grid dimensions
   if (np.ndim(field) == 1 and   np.ndim(x) == 1 and np.ndim(y) == 1):  
      tri=1      
   if (np.ndim(field) == 2 and   np.ndim(x) == 2 and np.ndim(y) == 2):  
      tri=0      
   if (np.ndim(field) == 2 and   np.ndim(x) == 1 and np.ndim(y) == 1):
      tri=0





   ########## 
   # Map plot
   ##########
   if ptype == 1: 
      if verbose: print 'con - making a map plot'
      #Open a new plot is necessary
      if plotvars.user_plot == 0: gopen(user_plot=0)

      #Set up mapping
      lonrange=np.nanmax(x)-np.nanmin(x)
      #Reset mapping
      if plotvars.user_mapset == 0:
         plotvars.lonmin=-180
         plotvars.lonmax=180
         plotvars.latmin=-90
         plotvars.latmax=90

      if lonrange > 350 or plotvars.user_mapset == 1:
         set_map()  
      else:
         mapset(lonmin=np.nanmin(x), lonmax=np.nanmax(x), latmin=np.nanmin(y), \
                latmax=np.nanmax(y), user_mapset=0)
         set_map()  


      mymap=plotvars.mymap   
      user_mapset=plotvars.user_mapset
   
      lonrange=np.nanmax(x)-np.nanmin(x) 
      if lonrange >350 and np.ndim(y) == 1:
      
         #Add cyclic information if missing.
         if lonrange < 360:
            field, x = addcyclic(field, x)
            lonrange=np.nanmax(x)-np.nanmin(x)

         #Shift grid if needed
         if plotvars.lonmin < np.nanmin(x): x=x-360
         if plotvars.lonmin > np.nanmax(x): x=x+360
         field, x=shiftgrid(plotvars.lonmin, field, x)   

         #Add cyclic information if missing.
         lonrange=np.nanmax(x)-plotvars.lonmin
         if lonrange < 360:
            field, x = addcyclic(field, x)
            lonrange=np.nanmax(x)-np.nanmin(x)


      #Flip latitudes and field if latitudes are in descending order
      if np.ndim(y) == 1:
         if y[0] > y[-1]:
            y=y[::-1] 
            field=np.flipud(field)
   
      #Plotting a sub-area of the grid produces stray contour labels in polar plots
      #Subsample the grid to remove this problem
      if plotvars.proj == 'npstere':
         myypos=find_pos_in_array(vals=y, val=plotvars.boundinglat)
         y=y[myypos:]
         field=field[myypos:, :]

      if plotvars.proj == 'spstere':
         myypos=find_pos_in_array(vals=y, val=plotvars.boundinglat, above=1)     
         y=y[0:myypos+1]
         field=field[0:myypos+1, :]

      #Create the meshgrid if required
      if (np.ndim(field) == 1 and   np.ndim(x) == 1 and np.ndim(y) == 1):     
         lons=x
         lats=y
      if (np.ndim(field) == 2 and   np.ndim(x) == 2 and np.ndim(y) == 2):      
         lons=x
         lats=y
      if (np.ndim(field) == 2 and   np.ndim(x) == 1 and np.ndim(y) == 1):
         lons, lats=mymap(*np.meshgrid(x, y))



      #Set the plot limits
      if lonrange > 350:
         gset(xmin=plotvars.lonmin, xmax=plotvars.lonmax, ymin=plotvars.latmin, ymax=plotvars.latmax, user_gset=0)
      else:
         if user_mapset == 1:
            gset(xmin=plotvars.lonmin, xmax=plotvars.lonmax, ymin=plotvars.latmin, ymax=plotvars.latmax, user_gset=0)
         else:
            gset(xmin=np.nanmin(lons), xmax=np.nanmax(lons), ymin=np.nanmin(lats), ymax=np.nanmax(lats), user_gset=0)


      #Filled contours
      if fill == True or blockfill == 1:
         if verbose: print 'con - adding filled contours'
         #Get colour scale for use in contouring
         #If colour bar extensions are enabled then the colour map goes
         #from 1 to ncols-2.  The colours for the colour bar extensions are then 
         #changed on the colourbar and plot after the plot is made 
         cscale_ncols=np.size(plotvars.cs)
         colmap=cscale_get_map()

         cmap = matplotlib.colors.ListedColormap(colmap)
         if (plotvars.levels_extend == 'min' or plotvars.levels_extend == 'both'):
             cmap.set_under(plotvars.cs[0])
         if (plotvars.levels_extend == 'max' or plotvars.levels_extend == 'both'):
             cmap.set_over(plotvars.cs[-1])

         #filled colour contours
         cfill = mymap.contourf(lons,lats,field*fmult,clevs,extend=plotvars.levels_extend,\
                 cmap=cmap, tri=tri)


      #Block fill
      if blockfill == 1:
         if verbose: print 'con - adding blockfill'
         if isinstance(f[0], cf.Field):  
            if getattr(f[0].coord('lon'), 'hasbounds', False):
               xpts=np.squeeze(f.coord('lon').bounds.array[:,0])
               xpts=np.append(xpts, f.coord('lon').bounds.array[-1,1]) # Add last longitude point
               ypts=np.squeeze(f.coord('lat').bounds.array[:,0]) 
               ypts=np.append(ypts, f.coord('lat').bounds.array[-1,1]) # Add last latitude point
               bfill(f=field_orig*fmult, x=xpts, y=ypts, clevs=clevs, lonlat=1, bound=1)  
            else:
               bfill(f=field_orig*fmult, x=x_orig, y=y_orig, clevs=clevs, lonlat=1, bound=0)  

         else:
            bfill(f=field_orig*fmult, x=x_orig, y=y_orig, clevs=clevs, lonlat=1, bound=0)  



      #Contour lines and labels  
      if lines == True: 
         if verbose: print 'con - adding contour lines and labels'
         cs = mymap.contour(lons,lats,field*fmult,clevs,colors='k', tri=tri)
         if line_labels == True:
            nd=ndecs(clevs)
            fmt='%d'
            if nd != 0: fmt='%1.'+str(nd)+'f'
            plotvars.plot.clabel(cs, fmt=fmt, colors = 'k', fontsize=text_fontsize, fontweight=text_fontweight) 

         #Thick zero contour line   
         if zero_thick is not None:
            cs = mymap.contour(lons,lats,field*fmult,[-1e-32, 0], colors='k', linewidths=zero_thick, tri=tri) 

      

      #axes
      if plotvars.proj == 'cyl':      
         if verbose: print 'con - adding cylindrical axes'
         lonticks,lonlabels=mapaxis(min=plotvars.lonmin, max=plotvars.lonmax, type=1)
         latticks,latlabels=mapaxis(min=plotvars.latmin, max=plotvars.latmax, type=2)
         if axes is True:
             if xaxis is True:
                 if xticks is None:
                     axes_plot(xticks=lonticks, xticklabels=lonlabels)
                 else:
                     if xticklabels is None:
                         axes_plot(xticks=xticks, xticklabels=xticks)
                     else:
                         axes_plot(xticks=xticks, xticklabels=xticklabels)
             if yaxis is True:
                 if yticks is None:
                     axes_plot(yticks=latticks, yticklabels=latlabels)
                 else:
                     if yticklabels is None:
                         axes_plot(yticks=yticks, yticklabels=yticks)
                     else:
                         axes_plot(yticks=yticks, yticklabels=yticklabels)

             if user_xlabel is not None: plotvars.plot.set_xlabel(user_xlabel)
             if user_ylabel is not None: plotvars.plot.set_ylabel(user_ylabel)
   
      if plotvars.proj == 'npstere' or plotvars.proj == 'spstere': 
         if verbose: print 'con - adding stereograpic axes'
         latstep=30
         if 90-abs(plotvars.boundinglat) <= 50: latstep=10
         if axes is True:
             if xaxis is True:
                 if xticks is None:
                     mymap.drawmeridians(np.arange(0,360,60), labels=[1,1,1,1]) 
                 else:
                     mymap.drawmeridians(xticks, labels=[1,1,1,1]) 
             if yaxis is True:
                 if yticks is None:
                     mymap.drawparallels(np.arange(-90,120,latstep))
                 else:
                     mymap.drawparallels(yticks)


      #Coastlines and title         
      mymap.drawcoastlines(linewidth=continent_thickness, color=continent_color)
      plotvars.plot.set_title(title, y=1.03, fontsize=title_fontsize, fontweight=title_fontweight)


      #Color bar
      if colorbar == 1: 
         if verbose: print 'con - adding colour bar'    
         pad=0.10
         if plotvars.rows >= 3: pad=0.15
         if plotvars.rows >= 5: pad=0.20 
         if colorbar_position is None:
             cbar=plotvars.master_plot.colorbar(cfill, ticks=colorbar_labels,\
                                                orientation=colorbar_orientation, aspect=75, pad=pad,\
                                                shrink=colorbar_shrink)
         else:
             position=plotvars.master_plot.add_axes(colorbar_position)  
             cbar=plotvars.master_plot.colorbar(cfill, cax=position, ticks=colorbar_labels, orientation=colorbar_orientation)
             gpos(pos=plotvars.pos)

             

         cbar.set_label(colorbar_title, fontsize=text_fontsize, fontweight=title_fontweight)

         #Bug in Matplotlib colorbar labelling
         #With clevs=[-1, 1, 10000, 20000, 30000, 40000, 50000, 60000]
         #Labels are [0, 2, 10001, 20001, 30001, 40001, 50001, 60001]
         #With a +1 near to the colorbar label
         cbar.set_ticks([i for i in colorbar_labels]) 

         
         for t in cbar.ax.get_xticklabels(): 
             t.set_fontsize(text_fontsize)
             t.set_fontweight(text_fontweight)

         


  
   ########################
   # Latitude-pressure plot
   ########################
   if ptype == 2:
      if verbose: print 'con - making a latitude-pressure plot'


      if plotvars.user_plot == 0: gopen(user_plot=0)

      #Set plot limits
      user_gset=plotvars.user_gset
      if user_gset == 0:
         #Program selected data plot limits
         xmin=np.nanmin(x)
         if xmin < -80 and xmin >= -90: xmin=-90
         xmax=np.nanmax(x)
         if xmax > 80 and xmax <= 90: xmax=90 
         ymin=np.nanmin(y)
         if ymin <= 10: ymin=0
         ymax=np.nanmax(y)
      else:
         #User specified plot limits
         xmin=plotvars.xmin
         xmax=plotvars.xmax
         if plotvars.ymin < plotvars.ymax: 
            ymin=plotvars.ymin
            ymax=plotvars.ymax
         else:
            ymin=plotvars.ymax
            ymax=plotvars.ymin


      xstep=None
      if (xmin == -90 and xmax == 90): xstep=30
      ystep=None
      if (ymax == 1000): ystep=100
      if (ymax == 100000): ystep=10000

      ytype=0 #pressure or similar y axis
      if 'theta' in ylabel.split(' '): ytype=1
      if 'height' in ylabel.split(' '): 
         ytype=1
         ystep=100
         if (ymax - ymin) > 5000: ystep=500.0
         if (ymax - ymin) > 10000: ystep=1000.0
         if (ymax - ymin) > 50000: ystep=10000.0

      #Set plot limits and draw axes

      if ylog is False or ylog == 0:   
         if ytype == 1: 
             gset(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, user_gset=user_gset)
             latticks,latlabels=mapaxis(min=xmin, max=xmax, type=2)

         else: 
             gset(xmin=xmin, xmax=xmax, ymin=ymax, ymax=ymin, user_gset=user_gset)
             latticks,latlabels=mapaxis(min=xmin, max=xmax, type=2)

         heightticks=gvals(dmin=ymin, dmax=ymax, tight=1, mystep=ystep, mod=0)[0]
         heightlabels=heightticks

         if axes is True:
             if xaxis is True:
                 if xticks is not None:
                     latticks=xticks
                     latlabels=xticks
                     if xticklabels is not None: latlabels=xticklabels
             else:
                 latticks=[100000000]
                 xlabel=''

             if yaxis is True:
                 if yticks is not None:
                     heightticks=yticks
                     heightlabels=yticks
                     if yticklabels is not None: heightlabels=yticklabels
             else:
                 heightticks=[100000000]
                 ylabel=''


         else:
             latticks=[100000000]
             heightticks=[100000000]
             xlabel=''
             ylabel=''

         axes_plot(xticks=latticks, xticklabels=latlabels,\
                   yticks=heightticks, yticklabels=heightlabels,\
                   xlabel=xlabel, ylabel=ylabel)



      #Log y axis 
      if ylog is True or ylog == 1:
          if ymin == 0: ymin=1
          gset(xmin=xmin, xmax=xmax, ymin=ymax, ymax=ymin, ylog=1, user_gset=user_gset)
          latticks,latlabels=mapaxis(min=xmin, max=xmax, type=2)

          if axes is True:
              if xaxis is True:
                  if xticks is not None:
                      latticks=xticks
                      latlabels=xticks
                      if xticklabels is not None: latlabels=xticklabels
              else:
                  latticks=[100000000]
                  xlabel=''

              if yaxis is True:
                  if yticks is not None:
                      heightticks=yticks
                      heightlabels=yticks
                      if yticklabels is not None: heightlabels=yticklabels
              else:
                  latticks=[100000000]
                  xlabel=''

          if yticks is None:
              axes_plot(xticks=latticks, xticklabels=latlabels, xlabel=xlabel, ylabel=ylabel)
          else:
              axes_plot(xticks=latticks, xticklabels=latlabels, yticks=heightticks, yticklabels=heightlabels, \
                        xlabel=xlabel, ylabel=ylabel)


      #Get colour scale for use in contouring
      #If colour bar extensions are enabled then the colour map goes
      #from 1 to ncols-2.  The colours for the colour bar extensions are then
      #changed on the colourbar and plot after the plot is made
      cscale_ncols=np.size(plotvars.cs)
      colmap=cscale_get_map()


      #Filled contours
      if fill == True or blockfill == 1:
         colmap=cscale_get_map()
         cmap = matplotlib.colors.ListedColormap(colmap)
         if (plotvars.levels_extend == 'min' or plotvars.levels_extend == 'both'):
             cmap.set_under(plotvars.cs[0])
         if (plotvars.levels_extend == 'max' or plotvars.levels_extend == 'both'):
             cmap.set_over(plotvars.cs[-1])

         cfill=plotvars.plot.contourf(x,y,field*fmult,clevs, \
               extend=plotvars.levels_extend, cmap=cmap, tri=tri)

  
      #Block fill
      if blockfill == 1:   
         if isinstance(f[0], cf.Field):  
            if getattr(f[0].coord('lat'), 'hasbounds', False):
               xpts=np.squeeze(f.coord('lat').bounds.array)[:,0]
               ypts=np.squeeze(f.coord('pressure').bounds.array)[:,0]   
               bfill(f=field_orig*fmult, x=xpts, y=ypts, clevs=clevs, lonlat=0, bound=1)  
            else:
               bfill(f=field_orig*fmult, x=x_orig, y=y_orig, clevs=clevs, lonlat=0, bound=0)  

         else:
            bfill(f=field_orig*fmult, x=x_orig, y=y_orig, clevs=clevs, lonlat=0, bound=0)  
 


      #Contour lines and labels
      if lines == True: 
         cs=plotvars.plot.contour(x,y,field*fmult,clevs,colors='k', tri=tri)
         if line_labels == True:  
            nd=ndecs(clevs)
            fmt='%d'
            if nd != 0: fmt='%1.'+str(nd)+'f'
            plotvars.plot.clabel(cs, fmt=fmt, colors = 'k', fontsize=text_fontsize, fontweight=text_fontweight) 

            #Thick zero contour line
            if zero_thick is not None:
               cs = plotvars.plot.contour(x,y,field*fmult,[1e-32, 0],colors='k', linewidths=zero_thick, tri=tri)
     
  

      #Colorbar
      if colorbar == 1:  

         pad=0.15
         if plotvars.rows >= 3: pad=0.25
         if plotvars.rows >= 5: pad=0.3
         if colorbar_position is None:
             cbar=plotvars.master_plot.colorbar(cfill, orientation=colorbar_orientation, aspect=75, \
                                                pad=pad, ticks=colorbar_labels, \
                                                shrink=colorbar_shrink)
         else:
             position=plotvars.master_plot.add_axes(colorbar_position)  
             cbar=plotvars.master_plot.colorbar(cfill, cax=position, ticks=colorbar_labels, orientation=colorbar_orientation)
             gpos(pos=plotvars.pos)

         cbar.set_label(colorbar_title, fontsize=text_fontsize, fontweight=title_fontweight)
         cbar.set_ticklabels([str(i) for i in colorbar_labels]) #Bug in Matplotlib colorbar labelling
         for t in cbar.ax.get_xticklabels():
            t.set_fontsize(text_fontsize)
            t.set_fontweight(text_fontweight)

      #Title
      plotvars.plot.set_title(title, y=1.03, fontsize=title_fontsize, fontweight=title_fontweight)



   ########################
   # Longitude-pressure plot
   ########################
   if ptype == 3:
      if verbose: print 'con - making a longitude-pressure plot'
      if plotvars.user_plot == 0: gopen(user_plot=0)
      user_gset=plotvars.user_gset

      #Set plot limits
      if user_gset == 0:
         #Program selected data plot limits
         xmin=np.nanmin(x)
         if xmin < -170 and xmin >= -180: xmin=-180
         xmax=np.nanmax(x)
         if xmax > 170 and xmax <= 180: xmax=180 
         ymin=np.nanmin(y)
         if ymin <= 10: ymin=0
         ymax=np.nanmax(y)
      else:
         #User specified plot limits
         xmin=plotvars.xmin
         xmax=plotvars.xmax
         if plotvars.ymin < plotvars.ymax: 
            ymin=plotvars.ymin
            ymax=plotvars.ymax
         else:
            ymin=plotvars.ymax
            ymax=plotvars.ymin

      xstep=None
      if (xmin == -180 and xmax == 180): xstep=60
      ystep=None
      if (ymax == 1000): ystep=100
      if (ymax == 100000): ystep=10000

      ytype=0 #pressure or similar y axis
      if 'theta' in ylabel.split(' '): ytype=1
      if 'height' in ylabel.split(' '): 
         ytype=1
         ystep=100
         if (ymax - ymin) > 5000: ystep=500.0
         if (ymax - ymin) > 10000: ystep=1000.0
         if (ymax - ymin) > 50000: ystep=10000.0

      #Set plot limits and draw axes
      lonticks,lonlabels=mapaxis(min=xmin, max=xmax, type=1)
      if ylog != 1:   
         if ytype == 1: 
            gset(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, user_gset=user_gset)         
         else: 
            gset(xmin=xmin, xmax=xmax, ymin=ymax, ymax=ymin, user_gset=user_gset)



         heightticks=gvals(dmin=ymin, dmax=ymax, tight=1, mystep=ystep, mod=0)[0]
         heightlabels=heightticks

         if axes is True:
             if xaxis is True:
                 if xticks is not None:
                     lonticks=xticks
                     lonlabels=xticks
                     if xticklabels is not None: lonlabels=xticklabels
             else:
                 lonticks=[100000000]
                 xlabel=''

             if yaxis is True:
                 if yticks is not None:
                     heightticks=yticks
                     heightlabels=yticks
                     if yticklabels is not None: heightlabels=yticklabels
             else:
                 heightticks=[100000000]
                 ylabel=''


         else:
             lonticks=[100000000]
             heightticks=[100000000]
             xlabel=''
             ylabel=''

         axes_plot(xticks=lonticks, xticklabels=lonlabels,\
                   yticks=heightticks, yticklabels=heightlabels,\
                   xlabel=xlabel, ylabel=ylabel)




      #Log y axis 
      if ylog == 1:
          if ymin == 0: ymin=1
          gset(xmin=xmin, xmax=xmax, ymin=ymax, ymax=ymin, ylog=1, user_gset=user_gset)
          #axes_plot(xticks=lonticks, xticklabels=lonlabels, xlabel=xlabel, ylabel=ylabel)

          if axes is True:
              if xaxis is True:
                  if xticks is not None:
                      lonticks=xticks
                      lonlabels=xticks
                      if xticklabels is not None: lonlabels=xticklabels
              else:
                  lonticks=[100000000]
                  xlabel=''

              if yaxis is True:
                  if yticks is not None:
                      heightticks=yticks
                      heightlabels=yticks
                      if yticklabels is not None: heightlabels=yticklabels
              else:
                  latticks=[100000000]
                  xlabel=''

          if yticks is None:
              axes_plot(xticks=latticks, xticklabels=latlabels, xlabel=xlabel, ylabel=ylabel)
          else:
              axes_plot(xticks=latticks, xticklabels=latlabels, yticks=heightticks, yticklabels=heightlabels, \
                        xlabel=xlabel, ylabel=ylabel)





      #Get colour scale for use in contouring
      #If colour bar extensions are enabled then the colour map goes
      #from 1 to ncols-2.  The colours for the colour bar extensions are then
      #changed on the colourbar and plot after the plot is made
      cscale_ncols=np.size(plotvars.cs)
      colmap=cscale_get_map()


      #Filled contours
      if fill == True or blockfill == 1:
         colmap=cscale_get_map()
         cmap = matplotlib.colors.ListedColormap(colmap)
         if (plotvars.levels_extend == 'min' or plotvars.levels_extend == 'both'):
             cmap.set_under(plotvars.cs[0])
         if (plotvars.levels_extend == 'max' or plotvars.levels_extend == 'both'):
             cmap.set_over(plotvars.cs[-1])

         cfill=plotvars.plot.contourf(x,y,field*fmult,clevs, \
               extend=plotvars.levels_extend, cmap=cmap, tri=tri)

         #add colour scale extensions if required
         if (plotvars.levels_extend == 'both' or plotvars.levels_extend == 'min'):
            cfill.cmap.set_under(plotvars.cs[0])
         if (plotvars.levels_extend == 'both' or plotvars.levels_extend == 'max'):
            cfill.cmap.set_over(plotvars.cs[cscale_ncols-1])
  
      #Block fill
      if blockfill == 1:   
         if isinstance(f[0], cf.Field):  
            if getattr(f[0].coord('lat'), 'hasbounds', False):
               xpts=np.squeeze(f.coord('lat').bounds.array)[:,0]
               ypts=np.squeeze(f.coord('pressure').bounds.array)[:,0]   
               bfill(f=field_orig*fmult, x=xpts, y=ypts, clevs=clevs, lonlat=0, bound=1)  
            else:
               bfill(f=field_orig*fmult, x=x_orig, y=y_orig, clevs=clevs, lonlat=0, bound=0)  

         else:
            bfill(f=field_orig*fmult, x=x_orig, y=y_orig, clevs=clevs, lonlat=0, bound=0)  
 


      #Contour lines and labels
      if lines == True: 
         cs=plotvars.plot.contour(x,y,field*fmult,clevs,colors='k', tri=tri)
         if line_labels == True:  
            nd=ndecs(clevs)
            fmt='%d'
            if nd != 0: fmt='%1.'+str(nd)+'f'
            plotvars.plot.clabel(cs, fmt=fmt, colors = 'k', fontsize=text_fontsize, fontweight=text_fontweight) 

            #Thick zero contour line
            if zero_thick is not None:
               cs = plotvars.plot.contour(x,y,field*fmult,[1e-32, 0],colors='k', linewidths=zero_thick, tri=tri)
     
  

      #Colorbar
      if colorbar == 1:  

         pad=0.15
         if plotvars.rows >= 3: pad=0.25
         if plotvars.rows >= 5: pad=0.3
         if colorbar_position is None: 
             cbar=plotvars.master_plot.colorbar(cfill, orientation=colorbar_orientation, aspect=75, \
                                                pad=pad, ticks=colorbar_labels, \
                                                shrink=colorbar_shrink)
         else:
             position=plotvars.master_plot.add_axes(colorbar_position)  
             cbar=plotvars.master_plot.colorbar(cfill, cax=position, ticks=colorbar_labels, orientation=colorbar_orientation)
             gpos(pos=plotvars.pos)

         cbar.set_label(colorbar_title, fontsize=text_fontsize, fontweight=title_fontweight)
         cbar.set_ticklabels([str(i) for i in colorbar_labels]) #Bug in Matplotlib colorbar labelling
         for t in cbar.ax.get_xticklabels():
            t.set_fontsize(text_fontsize)
            t.set_fontweight(text_fontweight)

      #Title
      plotvars.plot.set_title(title, y=1.03, fontsize=title_fontsize, fontweight=title_fontweight)




   #################
   # Hovmuller plots
   #################
   if (ptype == 4 or ptype == 5): 
      if verbose: print 'con - making a Hovmuller plot'
      yplotlabel='Time'
      if ptype == 4: xplotlabel='Longitude'
      if ptype == 5: xplotlabel='Latitude'
      user_gset=plotvars.user_gset





      #Time strings set to None initially
      tmin=None
      tmax=None


      #Set plot limits

      if all(val is not None for val in [plotvars.xmin,plotvars.xmax,plotvars.ymin,plotvars.ymax]):
         #Store time strings for later use
         tmin=plotvars.ymin
         tmax=plotvars.ymax

         #Check data has CF attributes needed
         check_units=check_units=True
         check_calendar=True
         check_Units_reftime=True
         if hasattr(f.item('T'), 'units') is False: check_units=False
         if hasattr(f.item('T'), 'calendar') is False: check_calendar=False
         if hasattr(f.item('T'), 'Units') is True: 
             if not hasattr(f.item('T').Units, 'reftime'): check_Units_reftime=False
         else:
             check_Units_reftime=False
         if check_units is False or check_calendar is False or check_Units_reftime is False:
             print '\nThe required CF time information to make the plot is not available'
             print 'please fix the following before trying to plot again'
             if check_units is False: print 'Time axis missing: units'
             if check_calendar is False: print 'Time axis missing: calendar'
             if check_Units_reftime is False: print 'Time axis missing: Units.reftime'
             return


         #Change from date string in ymin and ymax to date as a float
         ref_time=f.item('T').units
         ref_calendar=f.item('T').calendar
         ref_time_origin=str(f.item('T').Units.reftime)


         time_units = cf.Units(ref_time, ref_calendar)
         t = cf.Data(cf.dt(plotvars.ymin), units=time_units)
         ymin=t.array
         t = cf.Data(cf.dt(plotvars.ymax), units=time_units)
         ymax=t.array
         xmin=plotvars.xmin
         xmax=plotvars.xmax
      else:
         xmin=np.nanmin(x)
         xmax=np.nanmax(x)
         ymin=np.nanmin(y)
         ymax=np.nanmax(y)


      #Set plot limits
      if plotvars.user_plot == 0: gopen(user_plot=0)
      gset(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, user_gset=user_gset)

      #Revert to time strings if set
      if all(val is not None for val in [tmin, tmax]):
         plotvars.ymin=tmin
         plotvars.ymax=tmax
 


      time_ticks, time_labels, ylabel=timeaxis(f.item('T'))

      if ptype == 4: lonlatticks, lonlatlabels=mapaxis(min=xmin, max=xmax, type=1)
      if ptype == 5: lonlatticks, lonlatlabels=mapaxis(min=xmin, max=xmax, type=2)

      #Draw axes
      if axes is True:
         if xaxis is True:
             if xticks is not None:
                 lonlatticks=xticks
                 lonlatlabels=xticks
                 if xticklabels is not None: lonlatlabels=xticklabels
         else:
              lonlatticks=[100000000]
              xlabel=''

         if yaxis is True:
             if yticks is not None:
                 timeticks=yticks
                 timelabels=yticks
                 if yticklabels is not None: timelabels=yticklabels
         else:
             timeticks=[100000000]
             ylabel=''


      else:
         latticks=[100000000]
         timeticks=[100000000]
         xplotlabel=''
         yplotlabel=''


      if xlabel != '': xplotlabel=xlabel
      if ylabel != '': yplotlabel=ylabel


      #Use the automatically generated labels if none are supplied
      if ylabel is None: yplotlabel=time_axis_label
      if np.size(time_ticks) > 0: timeticks=time_ticks
      if np.size(time_labels) > 0: timelabels=time_labels


      axes_plot(xticks=lonlatticks, xticklabels=lonlatlabels,\
                yticks=timeticks, yticklabels=timelabels,\
                xlabel=xplotlabel, ylabel=yplotlabel)



      #Get colour scale for use in contouring
      #If colour bar extensions are enabled then the colour map goes
      #from 1 to ncols-2.  The colours for the colour bar extensions are then
      #changed on the colourbar and plot after the plot is made
      cscale_ncols=np.size(plotvars.cs)
      colmap=cscale_get_map()


      #Filled contours
      if fill == True or blockfill == 1:
         colmap=cscale_get_map()
         cmap = matplotlib.colors.ListedColormap(colmap)
         if (plotvars.levels_extend == 'min' or plotvars.levels_extend == 'both'):
             cmap.set_under(plotvars.cs[0])
         if (plotvars.levels_extend == 'max' or plotvars.levels_extend == 'both'):
             cmap.set_over(plotvars.cs[-1])

         cfill=plotvars.plot.contourf(x,y,field*fmult,clevs, \
               extend=plotvars.levels_extend, cmap=cmap, tri=tri)

  
      #Block fill
      if blockfill == 1:   
         if isinstance(f[0], cf.Field):  
            if f[0].coord('lon').hasbounds:
               xpts=np.squeeze(f.coord('lat').bounds.array)[:,0]
               ypts=np.squeeze(f.coord('time').bounds.array)[:,0]   
               bfill(f=field_orig*fmult, x=xpts, y=ypts, clevs=clevs, lonlat=0, bound=1)  
            else:
               bfill(f=field_orig*fmult, x=x_orig, y=y_orig, clevs=clevs, lonlat=0, bound=0)  

         else:
            bfill(f=field_orig*fmult, x=x_orig, y=y_orig, clevs=clevs, lonlat=0, bound=0)  
 


      #Contour lines and labels
      if lines == True: 
         cs=plotvars.plot.contour(x,y,field*fmult,clevs,colors='k', tri=tri)
         if line_labels == True:  
            nd=ndecs(clevs)
            fmt='%d'
            if nd != 0: fmt='%1.'+str(nd)+'f'
            plotvars.plot.clabel(cs, fmt=fmt, colors = 'k', fontsize=text_fontsize, fontweight=text_fontweight) 

            #Thick zero contour line
            if zero_thick is not None:
               cs = plotvars.plot.contour(x,y,field*fmult,[1e-32, 0],colors='k', linewidths=zero_thick, tri=tri)
     


      #Colorbar
      if colorbar == 1:  

         pad=0.15
         if plotvars.rows >= 3: pad=0.25
         if plotvars.rows >= 5: pad=0.3
         if colorbar_position is None: 
             cbar=plotvars.master_plot.colorbar(cfill, orientation=colorbar_orientation, aspect=75, \
                                                pad=pad, ticks=colorbar_labels, \
                                                shrink=colorbar_shrink)
         else:
             position=plotvars.master_plot.add_axes(colorbar_position)  
             cbar=plotvars.master_plot.colorbar(cfill, cax=position, ticks=colorbar_labels, orientation=colorbar_orientation)
             gpos(pos=plotvars.pos)

         cbar.set_label(colorbar_title, fontsize=text_fontsize, fontweight=title_fontweight)
         cbar.set_ticklabels([str(i) for i in colorbar_labels]) #Bug in Matplotlib colorbar labelling
         for t in cbar.ax.get_xticklabels():
            t.set_fontsize(text_fontsize)
            t.set_fontweight(text_fontweight)

      #Title
      plotvars.plot.set_title(title, y=1.03, fontsize=title_fontsize, fontweight=title_fontweight)

      #reset plot limits if not a user plot
      if user_gset == 0: gset()


   #############
   #Rotated pole
   #############
   if ptype == 6: 
      #Rotated pole plots use a regularly spaced grid
      #The x and y points from the data are used to make the rotated axes
      xpts=np.arange(np.size(x))
      ypts=np.arange(np.size(y))

      if verbose: print 'con - making a rotated pole plot'
      user_gset=plotvars.user_gset
      if plotvars.user_plot == 0: gopen(user_plot=0)

      #Set plot limits 
      gset(xmin=0, xmax=np.size(x)-1, ymin=0, ymax=np.size(y)-1, user_gset=user_gset)


      #Get colour scale for use in contouring
      #If colour bar extensions are enabled then the colour map goes
      #from 1 to ncols-2.  The colours for the colour bar extensions are then
      #changed on the colourbar and plot after the plot is made
      cscale_ncols=np.size(plotvars.cs)
      colmap=cscale_get_map()


      #Filled contours
      if fill == True or blockfill == 1:
         colmap=cscale_get_map()
         cmap = matplotlib.colors.ListedColormap(colmap)
         if (plotvars.levels_extend == 'min' or plotvars.levels_extend == 'both'):
             cmap.set_under(plotvars.cs[0])
         if (plotvars.levels_extend == 'max' or plotvars.levels_extend == 'both'):
             cmap.set_over(plotvars.cs[-1])

         cfill=plotvars.plot.contourf(xpts,ypts,field*fmult,clevs,extend=plotvars.levels_extend,\
               cmap=cmap, tri=tri)


      #Block fill
      if blockfill == 1:  
         bfill(f=field_orig*fmult, x=xpts, y=ypts, clevs=clevs, lonlat=0, bound=0)  
 

      #Contour lines and labels 
      if lines == True:
         cs=plotvars.plot.contour(xpts,ypts,field*fmult,clevs,colors='k', tri=tri)
         if line_labels == True:     
            nd=ndecs(clevs)
            fmt='%d'
            if nd != 0: fmt='%1.'+str(nd)+'f'
            plotvars.plot.clabel(cs, fmt=fmt, colors = 'k', fontsize=text_fontsize, fontweight=text_fontweight) 
   
         #Thick zero contour line
         if zero_thick is not None:
            cs = plotvars.plot.contour(xpts,ypts,field*fmult,[1e-32, 0],colors='k', linewidths=zero_thick, tri=tri)


      #Colorbar
      if colorbar == 1:     

         pad=0.15
         if plotvars.rows >= 3: pad=0.25
         if plotvars.rows >= 5: pad=0.3
         if colorbar_position is None: 
             cbar=plotvars.master_plot.colorbar(cfill, orientation=colorbar_orientation, aspect=75, \
                                                pad=pad, ticks=colorbar_labels, \
                                                shrink=colorbar_shrink)
         else:
             position=plotvars.master_plot.add_axes(colorbar_position)  
             cbar=plotvars.master_plot.colorbar(cfill, cax=position, ticks=colorbar_labels, orientation=colorbar_orientation)
             gpos(pos=plotvars.pos)

         cbar.set_label(colorbar_title, fontsize=text_fontsize, fontweight=title_fontweight)
         cbar.set_ticklabels([str(i) for i in colorbar_labels]) #Bug in Matplotlib colorbar labelling
         for t in cbar.ax.get_xticklabels():
            t.set_fontsize(text_fontsize)
            t.set_fontweight(text_fontweight)

      #Rotated grid axes
      rgaxes(xpole=xpole, ypole=ypole, xvec=x, yvec=y)


      #Title
      plotvars.plot.set_title(title, y=1.03, fontsize=title_fontsize, fontweight=title_fontweight)





   ############
   #Other plots
   ############
   if ptype == 0: 
      if verbose: print 'con - making an other plot'
      if plotvars.user_plot == 0: gopen(user_plot=0)
      user_gset=plotvars.user_gset

      #Work out axes if none are supplied
      if any(val is None for val in [plotvars.xmin, plotvars.xmax, plotvars.ymin, plotvars.ymax]):
         xmin=np.nanmin(x)
         xmax=np.nanmax(x)
         ymin=np.nanmin(y)
         ymax=np.nanmax(y)
      else:
         xmin=plotvars.xmin
         xmax=plotvars.xmax
         ymin=plotvars.ymin
         ymax=plotvars.ymax

      xstep=(xmax-xmin)/10.0
      ystep=(ymax-ymin)/10.0

      #Set plot limits and set default plot labels
      gset(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, user_gset=user_gset)    
         
      xaxisticks=gvals(dmin=xmin, dmax=xmax, mystep=(xmax-xmin)/10.0, tight=1, mod=0)[0]
      xaxislabels=xaxisticks
      if ymin < ymax: yaxisticks=gvals(dmin=ymin, dmax=ymax, mystep=(ymax-ymin)/10.0, tight=1, mod=0)[0]
      if ymax < ymin: yaxisticks=gvals(dmin=ymax, dmax=ymin, mystep=(ymin-ymax)/10.0, tight=1, mod=0)[0]
      yaxislabels=yaxisticks
      if xlabel is not None: xplotlabel=xlabel 
      else:xplotlabel=''
      if ylabel is not None: yplotlabel=ylabel 
      else:yplotlabel=''

      #Draw axes
      if axes is True:
         if xaxis is True:
             if xticks is not None:
                 xaxisticks=xticks
                 xaxislabels=xticks
                 if xticklabels is not None: xaxislabels=xticklabels
         else:
              xaxisticks=[100000000]
              xlabel=''

         if yaxis is True:
             if yticks is not None:
                 yaxisticks=yticks
                 yaxislabels=yticks
                 if yticklabels is not None: yaxislabels=yticklabels
         else:
             yaxisticks=[100000000]
             ylabel=''


      else:
         xplotticks=[100000000]
         xplotticks=[100000000]
         xlabel=''
         ylabel=''

      axes_plot(xticks=xaxisticks, xticklabels=xaxislabels,\
                yticks=yaxisticks, yticklabels=yaxislabels,\
                xlabel=xplotlabel, ylabel=yplotlabel)




      #Get colour scale for use in contouring
      #If colour bar extensions are enabled then the colour map goes
      #from 1 to ncols-2.  The colours for the colour bar extensions are then
      #changed on the colourbar and plot after the plot is made
      cscale_ncols=np.size(plotvars.cs)
      colmap=cscale_get_map()


      #Filled contours
      if fill == True or blockfill == 1:
         colmap=cscale_get_map()
         cmap = matplotlib.colors.ListedColormap(colmap)
         if (plotvars.levels_extend == 'min' or plotvars.levels_extend == 'both'):
             cmap.set_under(plotvars.cs[0])
         if (plotvars.levels_extend == 'max' or plotvars.levels_extend == 'both'):
             cmap.set_over(plotvars.cs[-1])

         cfill=plotvars.plot.contourf(x,y,field*fmult,clevs,extend=plotvars.levels_extend,\
               cmap=cmap, tri=tri)


      #Block fill
      if blockfill == 1:  
         bfill(f=field_orig*fmult, x=x_orig, y=y_orig, clevs=clevs, lonlat=0, bound=0)  
 

      #Contour lines and labels 
      if lines == True:
         cs=plotvars.plot.contour(x,y,field*fmult,clevs,colors='k', tri=tri)
         if line_labels == True:     
            nd=ndecs(clevs)
            fmt='%d'
            if nd != 0: fmt='%1.'+str(nd)+'f'
            plotvars.plot.clabel(cs, fmt=fmt, colors = 'k', fontsize=text_fontsize, fontweight=text_fontweight) 
   
         #Thick zero contour line
         if zero_thick is not None:
            cs = plotvars.plot.contour(x,y,field*fmult,[1e-32, 0],colors='k', linewidths=zero_thick, tri=tri)


      #Colorbar
      if colorbar == 1:     

         pad=0.15
         if plotvars.rows >= 3: pad=0.25
         if plotvars.rows >= 5: pad=0.3
         if colorbar_position is None: 
             cbar=plotvars.master_plot.colorbar(cfill, orientation=colorbar_orientation, aspect=75, \
                                                pad=pad, ticks=colorbar_labels, \
                                                shrink=colorbar_shrink)
         else:
             position=plotvars.master_plot.add_axes(colorbar_position)  
             cbar=plotvars.master_plot.colorbar(cfill, cax=position, ticks=colorbar_labels, orientation=colorbar_orientation)
             gpos(pos=plotvars.pos)

         cbar.set_label(colorbar_title, fontsize=text_fontsize, fontweight=title_fontweight)
         cbar.set_ticklabels([str(i) for i in colorbar_labels]) #Bug in Matplotlib colorbar labelling
         for t in cbar.ax.get_xticklabels():
            t.set_fontsize(text_fontsize)
            t.set_fontweight(text_fontweight)

      #Title
      plotvars.plot.set_title(title, y=1.03, fontsize=title_fontsize, fontweight=title_fontweight)




   ##################
   #Save or view plot
   ##################

   if plotvars.user_plot == 0:       
      if verbose: print 'con - saving or viewing plot'
      #gset(user_gset=0)
      
      np.seterr(**old_settings)  # reset to default numpy error settings

      gclose()
  




def mapset(lonmin=None, lonmax=None, latmin=None, latmax=None, proj='cyl', boundinglat=0,
           lon_0=0, resolution='c', user_mapset=1):
   """
    | mapset sets the mapping parameters.
    |
    | lonmin=lonmin - minimum longitude
    | lonmax=lonmax - maximum longitude
    | latmin=latmin - minimum latitude
    | latmax=latmax - maximum latitude
    | proj=proj - 'cyl' for cylindrical projection. 'npstere' or 'spstere' for northern 
    |      hemisphere or southern hemisphere polar stereographic projection
    |      'moll' for the mollweide projection
    | boundinglat=boundinglat - edge of the viewable latitudes in a stereographic plot
    | lon_0=lon_0 - centre of desired map domain in stereographic or   plots
    | resolution=resolution - the map resolution - can be one of 'c' (crude), 'l' (low), 
    |      'i' (intermediate), 'h' (high), 'f' (full) or 'None'
    | user_mapset=user_mapset - variable to indicate whether a user call to mapset has been 
    |             made. 
    |
    | The default map plotting projection is the cyclindrical equidistant projection from 
    | -180 to 180 in longitude and -90 to 90 in latitude. To change the map view in this 
    | projection to over the United Kingdom, for example, you would use
    | mapset(lonmin=-6, lonmax=3, latmin=50, latmax=60) or mapset(-6, 3, 50, 60).
    |
    | The limits are -360 to 720 in longitude so to look at the equatorial Pacific you 
    | could use
    | mapset(lonmin=90, lonmax=300, latmin=-30, latmax=30)
    | or
    | mapset(lonmin=-270, lonmax=-60, latmin=-30, latmax=30)
    |
    | The proj parameter for the present accepts just two values - 'npstere' and 'spstere' 
    | for northern hemisphere or southern hemisphere polar stereographic projections. In 
    | addition to these the boundinglat parameter sets the edge of the viewable latitudes
    | and lat_0 sets the centre of desired map domain.
    |
    | Map settings are persistent until a new call to mapset is made. To reset to the default
    | map settings use mapset().

    :Returns:
     None
   """


   #Set the continent resolution
   plotvars.resolution=resolution 


   if all(val is None for val in [lonmin,lonmax,latmin,latmax]) and proj == 'cyl':
      plotvars.lonmin=-180
      plotvars.lonmax=180
      plotvars.latmin=-90 
      plotvars.latmax=90
      plotvars.proj='cyl'
      plotvars.user_mapset=0
      return


   if lonmin is None: lonmin=-180
   if lonmax is None: lonmax=180
   if latmin is None: latmin=-90
   if latmax is None: latmax=90

   if proj == 'moll':
      lonmin=lon_0-180
      lonmax=lon_0+180


   plotvars.lonmin=lonmin
   plotvars.lonmax=lonmax
   plotvars.latmin=latmin 
   plotvars.latmax=latmax
   plotvars.proj=proj
   plotvars.boundinglat=boundinglat 
   plotvars.lon_0=lon_0
   plotvars.user_mapset=user_mapset
   set_map()   



  

def levs(min=None, max=None, step=None, manual=None, extend='both'):
   """ 
    | The levs command manually sets the contour levels.

    | min=min - minimum level
    | max=max - maximum level
    | step=step - step between levels
    | manual= manual - set levels manually
    | extend='neither', 'both', 'min', or 'max' - colour bar limit extensions.

    | Use the levs command when a predefined set of levels is required. The min, max 
    | and step parameters are all needed to define a set of  levels. These can take 
    | integer or floating point numbers. If colour filled contours are plotted then 
    | the default is to extend the minimum and maximum contours coloured for out of 
    | range values - extend='both'.

    | Once a user call is made to levs the levels are persistent.  i.e. the next plot
    | will use the same set of levels.
    | Use levs() to reset to undefined levels.

    :Returns:
     None

   """ 

   if all(val is None for val in [min,max,step,manual]):
      plotvars.levels=None
      plotvars.levels_min=None
      plotvars.levels_max=None
      plotvars.levels_step=None 
      plotvars.levels_extend='both'
      plotvars.user_levs=0
      return   

   if manual is not None:
      plotvars.levels=manual
      plotvars.levels_min=None
      plotvars.levels_max=None
      plotvars.levels_step=None
      plotvars.user_levs=1
   else:
      if any(val is None for val in [min,max,step]):
         errstr='\n\
                 levs error\n\
                 min, max and step or manual need to be passed to levs to generate \n\
                 a set of contour levels\
                 \n'
              
         raise  Warning(errstr)
      else:
         plotvars.levels_min=min
         plotvars.levels_max=max
         plotvars.levels_step=step
         if type(step) is int:
             plotvars.levels=np.arange(min, max+step, step)
         else:
             vals=np.arange(min, max+step, step)
             if np.max(vals) > max: vals=vals[:-1]
             plotvars.levels=np.linspace(min, max, np.size(vals))
         plotvars.user_levs=1

   plotvars.levels_extend=extend



def mapaxis(min=min, max=max, type=type):
   """ 
    | mapaxis is used to work out a sensible set of longitude and latitude 
    | tick marks and labels.  This is an internal routine and is not used 
    | by the user.

    | min=min - minimum axis value
    | max=max - maximum axis value
    | type=type - 1 = longitude, 2 = latitude
  
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
   if type == 1:
      lonmin=min
      lonmax=max
      lonrange=lonmax-lonmin
      lonstep=60
      if lonrange <= 180: lonstep=30
      if lonrange <= 90: lonstep=10
      if lonrange <= 30: lonstep=5
      if lonrange <= 10: lonstep=2
      if lonrange <= 5: lonstep=1      
      #if plotvars.xstep is not None: lonstep=plotvars.xstep
     
      lons=np.arange(-720, 720+lonstep, lonstep)
      lonticks=[]
      for lon in lons:
         if lon >= lonmin and lon <= lonmax: lonticks.append(lon)
     
      lonlabels=[]
      for lon in lonticks:
         lon2=np.mod(lon + 180, 360) - 180
         if lon2 < 0 and lon2 > -180: lonlabels.append(str(abs(lon2))+'W')
         if lon2 > 0 and lon2 < 180: lonlabels.append(str(lon2)+'E')
         if lon2 == 0: lonlabels.append('0')
         if np.abs(lon2) == 180: lonlabels.append('180')
          
      return(lonticks, lonlabels) 
    
   if type == 2:
      latmin=min
      latmax=max
      latrange=latmax-latmin
      latstep=30
      if latrange <= 90: latstep=10  
      if latrange <= 30: latstep=5   
      if latrange <= 10: latstep=2
      if latrange <= 5: latstep=1  
      #if plotvars.ystep is not None: latstep=plotvars.ystep
    
      lats=np.arange(-90, 90+latstep, latstep)
      latticks=[]
      for lat in lats:
         if lat >= latmin and lat <= latmax: latticks.append(lat)   


      latlabels=[]
      for lat in latticks:
         if lat < 0: latlabels.append(str(abs(lat))+'S')
         if lat > 0: latlabels.append(str(lat)+'N')
         if lat == 0: latlabels.append('0')
     
      return(latticks, latlabels) 


def timeaxis(dtimes=None):
    """ 
     | timeaxis is used to work out a sensible set of time labels and tick 
     | marks given a time span  This is an internal routine and is not used 
     | by the user.

     | dtimes=None - data times as a CF variable i.e. f.item('T')
  
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

    time_ticks=[]
    time_labels=[]
    axis_label='Time'
    if plotvars.user_gset == 0:
        yearmin=min(dtimes.year.array)
        yearmax=max(dtimes.year.array)
        tmin=min(dtimes.dtarray)
        tmax=max(dtimes.dtarray)
    else:
        t = cf.Data(cf.dt(plotvars.ymin), units=time_units)
        yearmin=int(t.year)
        t = cf.Data(cf.dt(plotvars.ymax), units=time_units)
        yearmax=int(t.year)
        tmin=cf.dt(plotvars.ymin) ####Added cf.dt to this - correct?
        tmax=cf.dt(plotvars.ymax) ####Added cf.dt to this - correct?
             

    #Years
    span=yearmax-yearmin
    if span > 4 and span < 3000: 
        axis_label='Time (year)'
        tvals=[]
        if span <= 15: step=1
        if span > 15: step=2
        if span > 30: step=5
        if span > 60: step=10
        if span > 160: step=20
        if span > 300: step=50
        if span > 600: step=100
        if span > 1300: step=200

        if plotvars.tspace_year is not None: step=plotvars.tspace_year

        years=np.arange(yearmax/step+2)*step
        tvals=years[np.where((years >=yearmin) & (years <=yearmax))]

        #Catch tvals if not properly defined and use gvals to generate some year tick marks
        if np.size(tvals) < 2: tvals=gvals(dmin=yearmin, dmax=yearmax, tight=1)[0]

        for year in tvals:
            time_ticks.append(np.min((cf.Data(cf.dt(str(int(year))+'-01-01 00:00:00'), units=time_units).array)))
            time_labels.append(str(int(year)))

    #Months
    if yearmax-yearmin <= 4:

        time_label='Time (month and year)'
        months=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        #Check number of labels with 1 month steps
        tsteps=0
        for year in np.arange(yearmax-yearmin+1)+yearmin:
            for month in np.arange(12):
                mytime=cf.dt(str(year)+'-'+str(month+1)+'-01 00:00:00')                
                if mytime >= tmin and mytime <= tmax: tsteps=tsteps+1

        if tsteps < 17: mvals=np.arange(12)
        if tsteps >= 17: mvals=np.arange(4)*3

        if plotvars.tspace_month is not None: mvals=np.arange(12/plotvars.tspace_month)*plotvars.tspace_month

        for year in np.arange(yearmax-yearmin+1)+yearmin:
            for month in mvals:
                mytime=cf.dt(str(year)+'-'+str(month+1)+'-01 00:00:00')
                if mytime >= tmin and mytime <= tmax:
                    time_ticks.append(np.min((cf.Data(mytime, units=time_units).array)))
                    time_labels.append(str(months[month])+' '+str(int(year)))


    #Days and hours
    if np.size(tsteps) <= 2:
        myday=cf.dt(int(tmin.year),int(tmin.month), int(tmin.day))

        not_found=0
        hour_counter=0
        span=0
        while not_found <= 48:
            mydate=cf.Data(myday, dtimes.Units)+ cf.Data(hour_counter, 'hour')
            if mydate >= tmin and mydate <= tmax:
                span=span+1
            else:
                not_found=not_found+1
                
            hour_counter=hour_counter+1
            

        step=1
        if span > 13: step=1
        if span > 13: step=4
        if span > 25: step=6
        if plotvars.tspace_hour is not None: step=plotvars.tspace_hour
        if plotvars.tspace_day is not None: step=plotvars.tspace_day*24

        not_found=0
        hour_counter=0
        span=0
        axis_label='Time (day and hour)'
        time_ticks=[]
        time_labels=[]


        while not_found <= 48:
            mytime=cf.Data(myday, dtimes.Units)+ cf.Data(hour_counter, 'hour')
            if mytime >= tmin and mytime <= tmax:
                time_ticks.append(np.min(mytime.array))
                label=str(mytime.year)+'-'+str(mytime.month)+'-'+str(mytime.day)
                if step/24 != step/24.0: label=label+' '+str(mytime.hour)+':00:00'
                time_labels.append(label)
            else:
                not_found=not_found+1
                
            hour_counter=hour_counter+step





    return(time_ticks, time_labels, axis_label) 




def ndecs(data=None):
   """
   | ndecs finds the number of decimal places in an array.  Needed to make the 
   | colour bar match the contour line labelling.

   | data=data - imput array of values

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

   maxdecs=0
   for i in range(len(data)):
      number=data[i]
      a=str(number).split('.')  
      if np.size(a) == 2: 
         number_decs=len(a[1])
         if number_decs > maxdecs: maxdecs=number_decs
  
   return maxdecs


def axes(xticks=None, xticklabels=None, yticks=None, yticklabels=None,\
         xstep=None, ystep=None, xlabel=None, ylabel=None, title=None):	  
   """
    | axes is a function to set axes plotting parameters. The xstep and ystep 
    | parameters are used to label the axes starting at the left hand side and 
    | bottom of the plot respectively. For tighter control over labelling use 
    | xticks, yticks to specify the tick positions and xticklabels, yticklabels 
    | to specify the associated labels.

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
     
   if all(val is None for val in [xticks,yticks,xticklabels,yticklabels,xstep,ystep,xlabel,ylabel,title]):
      plotvars.xticks=None
      plotvars.yticks=None
      plotvars.xticklabels=None
      plotvars.yticklabels=None
      plotvars.xstep=None
      plotvars.ystep=None
      plotvars.xlabel=None
      plotvars.ylabel=None
      plotvars.title=None
      return

   plotvars.xticks=xticks
   plotvars.yticks=yticks
   plotvars.xticklabels=xticklabels
   plotvars.yticklabels=yticklabels
   plotvars.xstep=xstep
   plotvars.ystep=ystep
   plotvars.xlabel=xlabel
   plotvars.ylabel=ylabel
   plotvars.title=title



def axes_plot(xticks=None, xticklabels=None, yticks=None, yticklabels=None,\
         xstep=None, ystep=None, xlabel=None, ylabel=None, title=None):	    
   """
    | axes_plot is a system function to specify axes plotting parameters. The xstep and ystep 
    | parameters are used to label the axes starting at the left hand side and 
    | bottom of the plot respectively. For tighter control over labelling use 
    | xticks, yticks to specify the tick positions and xticklabels, yticklabels 
    | to specify the associated labels.

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

   if plotvars.plot_type == 1:
      xmin=plotvars.lonmin
      xmax=plotvars.lonmax
      ymin=plotvars.latmin
      ymax=plotvars.latmax
   else:
      xmin=plotvars.xmin
      xmax=plotvars.xmax
      ymin=plotvars.ymin
      ymax=plotvars.ymax
 
   #Retrieve any user set axes parameters
   if plotvars.xticks is not None: 
      xticks=plotvars.xticks
      if plotvars.xticklabels is None: xticklabels=None
   if plotvars.yticks is not None: 
      yticks=plotvars.yticks
      if plotvars.yticklabels is None: yticklabels=None
   if plotvars.xticklabels is not None: xticklabels=plotvars.xticklabels
   if plotvars.yticklabels is not None: yticklabels=plotvars.yticklabels
   if plotvars.xstep is not None: 
      xstep=plotvars.xstep
      xticks=None
      xticklabels=None
   if plotvars.ystep is not None: 
      ystep=plotvars.ystep
      yticks=None
      yticklabels=None
   
   if plotvars.xlabel is not None: xlabel=plotvars.xlabel
   if plotvars.ylabel is not None: ylabel=plotvars.ylabel
   if plotvars.title is not None: title=plotvars.title   
   title_fontsize=plotvars.title_fontsize
   text_fontsize=plotvars.text_fontsize
   axis_label_fontsize=plotvars.axis_label_fontsize
   if title_fontsize is None: title_fontsize=15
   if text_fontsize is None: text_fontsize=11
   if axis_label_fontsize is None: axis_label_fontsize=11
   axis_label_fontweight=plotvars.axis_label_fontweight
   title_fontweight=plotvars.title_fontweight
   text_fontweight=plotvars.text_fontweight

   if xlabel is not None: plotvars.plot.set_xlabel(xlabel, fontsize=axis_label_fontsize, \
                          fontweight=axis_label_fontweight)
   if ylabel is not None: plotvars.plot.set_ylabel(ylabel, fontsize=axis_label_fontsize, \
                          fontweight=axis_label_fontweight)

   if xstep is not None:
      ticks, mult=gvals(plotvars.xmin, plotvars.xmax, tight=1, mystep=xstep)
      plotvars.plot.set_xticks(ticks*10**mult)
   if ystep is not None:
      ticks, mult=gvals(plotvars.ymin, plotvars.ymax, tight=1, mystep=ystep)
      plotvars.plot.set_yticks(ticks*10**mult)


   if xticks is not None:
      plotvars.plot.set_xticks(xticks)
      if xticklabels is not None: plotvars.plot.set_xticklabels(xticklabels)

   if yticks is not None:
      plotvars.plot.set_yticks(yticks)
      if yticklabels is not None: plotvars.plot.set_yticklabels(yticklabels)  


   #Set font size and weight
   for label in plotvars.plot.xaxis.get_ticklabels():
      label.set_fontsize(axis_label_fontsize)
      label.set_fontweight(axis_label_fontweight)
   for label in plotvars.plot.yaxis.get_ticklabels():
      label.set_fontsize(axis_label_fontsize)
      label.set_fontweight(axis_label_fontweight)
       
   #Title
   if title is not None: 
      plotvars.plot.set_title(title, y=1.03, fontsize=title_fontsize, fontweight=title_fontweight)
    

def gset(xmin=None, xmax=None, ymin=None, ymax=None, xlog=False, ylog=False, user_gset=1):
   """
    | Set plot limits for all non longitude-latitide plots. 
    | xmin, xmax, ymin, ymax are all needed to set the plot limits.  
    | Set xlog/ylog to True or 1 to get a log axis.
  
    | xmin=None - x minimum
    | xmax=None - x maximum
    | ymin=None - y minimum
    | ymax=None - y maximum
    | xlog=False - log x
    | ylog=False - log y

    | Once a user call is made to gset the plot limits are persistent. i.e. the next plot
    | will use the same set of plot limits.
    | Use gset() to reset to undefined plot limits i.e. the full range of the data.

    :Returns:
     None

    | 
    | 
    | 
    | 

   """


   plotvars.user_gset=user_gset
 
   if all(val is None for val in [xmin,xmax,ymin,ymax]):
      plotvars.xmin=None
      plotvars.xmax=None
      plotvars.ymin=None
      plotvars.ymax=None
      plotvars.xlog=False
      plotvars.ylog=False
      plotvars.user_gset=0
      return

   if any(val is None for val in [xmin,xmax,ymin,ymax]):
      errstr='gset error\n\
              xmin, xmax, ymin, ymax all need to be passed to gset to set the plot limits\n'
      raise  Warning(errstr)     
      
  
   plotvars.xmin=xmin
   plotvars.xmax=xmax
   plotvars.ymin=ymin
   plotvars.ymax=ymax
   plotvars.xlog=xlog
   plotvars.ylog=ylog 

   #Set plot limits
   if plotvars.plot is not None:
      plotvars.plot.axis([plotvars.xmin, plotvars.xmax, plotvars.ymin, plotvars.ymax])
      if plotvars.xlog == True or plotvars.xlog == 1: plotvars.plot.set_yscale('log')
      if plotvars.ylog == True or plotvars.ylog == 1: plotvars.plot.set_yscale('log')  


  

def gopen(rows=1, columns=1, user_plot=1, file='python', \
          orientation='landscape', figsize=[11.7, 8.3], \
          left=0.12, right=0.92, top=0.92, bottom=0.08, wspace=0.2, hspace=0.2):
   """
    | gopen is used to open a graphic file.  

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



    :Returns:
     None

    | 
    | 
    | 
    | 
    | 

   """

   #Set values in globals
   plotvars.rows=rows
   plotvars.columns=columns 
   if file != 'python': plotvars.file=file
   plotvars.orientation=orientation
   plotvars.user_plot=user_plot

   if orientation != 'landscape':
      if orientation != 'portrait':
         errstr='gopen error\n\
                 orientation incorrectly set\n\
                 Input value was '\
                 +orientation+'\nValid options are portrait or landscape\n'
         raise  Warning(errstr)    

   #Set master plot size
   if orientation == 'landscape': plotvars.master_plot=plot.figure(figsize=(figsize[0], figsize[1]))
   else: plotvars.master_plot=plot.figure(figsize=(figsize[1], figsize[0]))
 
   #Set margins
   plotvars.master_plot.subplots_adjust(left=left, right=right, top=top, bottom=bottom, wspace=wspace, hspace=hspace)

   #Set initial subplot
   gpos(pos=1)

   #Change tick length for plots > 2x2
   if (columns > 2 or rows > 2):
      matplotlib.rcParams['xtick.major.size'] = 2
      matplotlib.rcParams['ytick.major.size'] = 2

 

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

   #Reset the user_plot variable to off
   plotvars.user_plot=0

   file=plotvars.file
   if file is not None:
      type=1
      if file[-3:] == '.ps': type=1
      if file[-4:] == '.eps': type=1
      if file[-4:] == '.png': type=1
      if file[-4:] == '.pdf': type=1
      if type is None: file=file+'.png'
      plotvars.master_plot.savefig(file, papertype='a4', orientation=plotvars.orientation)
      plot.close()
   else:

       
      if plotvars.viewer == 'display':
          #Use Imagemagick display command if this exists
          disp=which('display')
          if disp is not None: 
              tfile='cfplot.png'
              plotvars.master_plot.savefig(tfile, papertype='a4', orientation=plotvars.orientation)
              subprocess.Popen([disp, tfile])
          else:
              plotvars.viewer='matplotlib'
      else:
          plot.show()
          plot.close()


   #Reset plotting
   plotvars.plot=None


def showplot(*args):
   for data in args:
      plot=data
      plot.show()
      #dir(plot)
      #plot=args[0]



def gpos(pos=1):
   """ 
    | Set plot position. Plots start at top left and increase by one each plot
    | to the right. When the end of the row has been reached then the next plot
    | will bed the leftmost plot on the next row down.

    | pos=pos - plot position

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

   #Check inputs are okay
   if pos < 1 or pos > plotvars.rows*plotvars.columns:
      errstr='pos error - pos out of range:\n range = 1 - '
      errstr=errstr+str(plotvars.rows*plotvars.columns)
      errstr=errstr+'\n input pos was '+ str(pos)
      errstr=errstr+'\n'
      raise  Warning(errstr)    

   plotvars.plot=plotvars.master_plot.add_subplot(plotvars.rows, plotvars.columns, pos)
   plotvars.plot.tick_params(which='both', direction='out')
   
   #Set osition in global variables
   plotvars.pos=pos

   #if plotvars.user_plot == 0: 
   #   if plotvars.user_gset == 1: gset(user_gset=plotvars.user_gset)
   #   gset(user_gset=plotvars.user_gset)

  

#######################################
#pcon - convert mb to km and vice-versa
#######################################

def pcon(mb=None, km=None, h=7.0, p0=1000):
   """ 
    | pcon is a function for converting pressure to height in kilometers and 
    | vice-versa. This function uses the equation P=P0exp(-z/H) to translate 
    | between pressure and height. In pcon the surface pressure P0 is set to 
    | 1000.0mb and the scale height H is set to 7.0. The value of H can vary 
    | from 6.0 in the polar regions to 8.5 in the tropics as well as seasonally. 
    | The value of P0 could also be said to be 1013.25mb rather than 1000.0mb. 

    | As this relationship is approximate:
    | (i) Only use this for making the axis labels on y axis pressure plots
    | (ii) Put the converted axis on the right hand side to indicate that this 
    |      isn't the primary unit of measure

    | print pcon(mb=[1000, 300, 100, 30, 10, 3, 1, 0.3])
    | [0., 8.42780963 16.11809565 24.54590528 32.2361913, 40.66400093 48.35428695, 56.78209658]  

    | mb=None - input pressure 
    | km=None - input height
    | h=7.0 - default value for h
    | p0=1000 - default value for p0

    :Returns:
     | pressure(mb) if height(km) input, 
     | height(km) if pressure(mb) input
    """  

   if all(val is None for val in [mb, km]) == 2:
      errstr='pcon error - pcon must have mb or km input\n'
      raise  Warning(errstr)      
 
   if mb is not None: return h*(np.log(p0)-np.log(mb))
   if km is not None: return np.exp(-1.0*(np.array(km)/h-np.log(p0)))
 




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

   if text == None:
      errstr='\n supscr error - supscr must have text input\n'
      raise  Warning(errstr)        


   tform=''

   sup=0
   for i in text:
      if (i == '^'): sup=2
      if (i == '*'): sup=sup+1
   
      if (sup == 0): tform=tform+i
      if (sup == 1):
         if (i not in '*'): tform=tform+'*'+i; sup=0
      if (sup == 3):
         if i in '-0123456789': tform=tform+i
         else: tform=tform+'}$'+i; sup=0
      if (sup == 2): tform=tform+'$^{' ; sup=3
   
   if (sup == 3): tform=tform+'}$'


   tform=tform.replace('m2', 'm$^{2}$')   
   tform=tform.replace('m3', 'm$^{3}$')   
   tform=tform.replace('m-2', 'm$^{-2}$')
   tform=tform.replace('m-3', 'm$^{-3}$')
   tform=tform.replace('s-1', 's$^{-1}$')
   tform=tform.replace('s-2', 's$^{-2}$')


   return tform




def gvals(dmin=None, dmax=None, tight=0, mystep=None, mod=1): 
   """
    | gvals - work out a sensible set of values between two limits
    | This is an internal routine used for contour levels and axis 
    | labelling and is not used by the user.

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
      errstr='\n gvals error - gvals must have dmin and dmax input\n'
      raise  Warning(errstr)         


   #Return some values if dmin = dmax
   if dmin == dmax:
      vals=[dmin-0.001, dmin, dmin+0.001]
      mult=0
      return vals, mult



   mult=0 #field multiplyer
 
   #Generate reasonable step 
   step=(dmax-dmin)/16.0

   #Don't modify if dmin and dmax are both negative as this will create a race condition
   if dmin < 0 and dmax < 0: mod=0


   if mod == 1:
      if (mystep != None): step=mystep

      if step < 1:
         while dmax < 1:
            step=step*10.0
            dmin=dmin*10.0
            dmax=dmax*10.0
            mult=mult-1

      if step > 100:
         while step >= 1 or dmax >10:
            step=step/10.0
            dmin=dmin/10.0
            dmax=dmax/10.0
            mult=mult+1
     

   #Change step to be a sensible one
   step=int(dmax-dmin)/16


   if (step == 8 or step == 9): step=10
   if (step == 7 or step == 6 or step == 4): step=5
   if step == 3: step=2
   if (step >= 10): step=int(step/10)*10
   if (step == 0): step=1
   if (mystep != None): step=mystep


   #Make integer step
   if tight ==0:
      vals=(int(dmin)/step)*step
   else:
      vals=dmin
   while (np.nanmax(vals)+step) <= dmax:
      vals=np.append(vals, np.nanmax(vals)+step)
   

   #Remove upper and lower limits if tight=0 - i.e. a contour plot
   if tight == 0 and np.size(vals) > 1:
      if np.nanmax(vals) >= dmax: vals=vals[0:-1]
      if np.nanmin(vals) <= dmin: vals=vals[1:]


   if mystep is not None:
      if int(mystep) == mystep:      
         return vals, mult


   #Floating point step
   if (mult == 0 and np.size(vals) > 5):
      return vals, mult  
   else:
      step=float("%.1f" %((dmax-dmin)/16))
      if step == 0: step=float("%.2f" %((dmax-dmin)/16))

   if step == .9: step=1.0
   if step == .8: step=1.0
   if step == .7: step=.5
   if step == .6: step=.5
   if step == .3: step=.2
   if step == .09: step=0.1
   if step == .08: step=0.1
   if step == .07: step=.05
   if step == .06: step=.05
   if step == .03: step=.02


   if (dmax-dmin == step): step=step/10.
   vals=float("%.2f" %(int(dmin/step)*step))
   while (np.nanmax(vals)+step) <= dmax:
      vals=np.append(vals, float("%.2f" %(np.nanmax(vals)+step)))

   if tight == 0:
      if np.nanmax(vals) >= dmax: vals=vals[0:-1]
      if np.nanmin(vals) <= dmin: vals=vals[1:]

   return vals, mult



def cf_data_assign(f=None, colorbar_title=None, verbose=None):
   """
    | Check cf input data is okay and return data for contour plot.
    | This is an internal routine not used by the user.
    | f=None - input cf field
    | colorbar_title=None - input colour bar title
    | verbose=None - set to 1 to get a verbose idea of what the cf_data_assign is doing

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


   #Check input data has the correct number of dimensions
   #Take into account rotated pole fields having extra dimensions  
   ndim=len(f.axes(size=cf.gt(1)))
   if f.ref('rotated_latitude_longitude') is None:
      if (ndim > 2 or ndim < 1):
         print ''
         if (ndim > 2): errstr='cf_data_assign error - data has too many dimensions'
         if (ndim < 1): errstr='cf_data_assign error - data has too few dimensions'
         errstr=errstr+'\n cf-plot requires one or two dimensional data\n'
         for mydim in f.items():
            sn=getattr(f.item(mydim), 'standard_name', False)
            ln=getattr(f.item(mydim), 'long_name', False)
            if sn: 
               errstr=errstr+str(mydim)+','+str(sn)+','+str(f.item(mydim).size)+'\n'
            else:
               if ln: errstr=errstr+str(mydim)+','+str(ln)+','+str(f.item(mydim).size)+'\n'
         raise  Warning(errstr) 

   
 
   #Set up data arrays and variables
   lons=None
   lats=None
   height=None 
   time=None 
   xlabel=''
   ylabel=''
   has_lons=None
   has_lats=None
   has_height=None
   has_time=None
   #has_rotated_pole=None
   xpole=None
   ypole=None
   ptype=None


   #Extract coordinate data if a matching CF standard_name or axis is found
   for mydim in f.items():
       sn=getattr(f.item(mydim), 'standard_name', 'NoName')
       an=getattr(f.item(mydim), 'axis', 'NoName')

       standard_name_x=['longitude']
       if (sn in standard_name_x or an == 'X'):
          if verbose: print 'cf_data_assign standard_name, axis - assigned lons -', sn, an
          lons=np.squeeze(f.item(mydim).array)

       standard_name_y=['latitude']
       if (sn in standard_name_y or an == 'Y'):
          if verbose: print 'cf_data_assign standard_name, axis - assigned lats -', sn, an
          lats=np.squeeze(f.item(mydim).array)

       standard_name_z=['pressure', 'air_pressure', 'height', 'depth']
       if (sn in standard_name_z or an == 'Z'):
          if verbose: print 'cf_data_assign standard_name, axis - assigned height -', sn, an
          height=np.squeeze(f.item(mydim).array)

       standard_name_t=['time']
       if (sn in standard_name_t or an == 'T'):
          if verbose: print 'cf_data_assign standard_name, axis - assigned time -', sn, an
          time=np.squeeze(f.item(mydim).array)



   
   #CF defined units
   lon_units=['degrees_east', 'degree_east', 'degree_E', 'degrees_E', 'degreeE', 'degreesE']
   lat_units=['degrees_north', 'degree_north', 'degree_N', 'degrees_N', 'degreeN', 'degreesN']
   height_units=['mb', 'mbar', 'millibar', 'decibar', 'atmosphere', 'atm', 'pascal','Pa', 'hPa',\
                 'meter', 'metre', 'm', 'kilometer', 'kilometre', 'km'] 
   time_units=['day', 'days', 'd', 'hour', 'hours', 'hr', 'h', 'minute', 'minutes', 'min', 'mins',\
               'second', 'seconds', 'sec', 'secs', 's']



   #Extract coordinate data if a matching CF set of units is found
   for mydim in f.items():
      units=getattr(f.item(mydim), 'units', False)
      if units in lon_units:
         if lons is None:
            if verbose: print 'cf_data_assign units - assigned lons -', units
            lons=np.squeeze(f.item(mydim).array)
      if units in lat_units:         
         if lats is None:
            if verbose: print 'cf_data_assign units - assigned lats -', units
            lats=np.squeeze(f.item(mydim).array)
      if units in height_units:         
         if height is None:
            if verbose: print 'cf_data_assign units - assigned height -', units
            height=np.squeeze(f.item(mydim).array)
      if units in time_units:         
         if time is None:
            if verbose: print 'cf_data_assign units - assigned time -', units
            time=np.squeeze(f.item(mydim).array)

   
   #Extract coordinate data from variable name if not already assigned
   for mydim in f.items():
      if mydim[:3] == 'dim':
         name=cf_var_name(field=f, dim=mydim)
         if name[0:3] == 'lon': 
            if lons is None:
               if verbose: print 'cf_data_assign dimension name - assigned lons -', name
               lons=np.squeeze(f.item(mydim).array)

         if name[0:3] == 'lat': 
            if lats is None:
               if verbose: print 'cf_data_assign dimension name - assigned lats -', name
               lats=np.squeeze(f.item(mydim).array)

         if (name[0:5] == 'theta' or name[0:1] == 'p' or name == 'air_pressure'): 
            if height is None:
               if verbose: print 'cf_data_assign dimension name - assigned height -', name
               height=np.squeeze(f.item(mydim).array)

         if name[0:1] == 't': 
            if time is None:
               if verbose: print 'cf_data_assign dimension name - assigned time -', name
               time=np.squeeze(f.item(mydim).array)


   if np.size(lons) > 1: has_lons=1
   if np.size(lats) > 1: has_lats=1
   if np.size(height) > 1: has_height=1
   if np.size(time) > 1: has_time=1


   #assign field data   
   field=np.squeeze(f.array)

   #Check what plot type is required.
   #0=simple contour plot, 1=map plot, 2=latitude-height plot,
   #3=longitude-time plot, 4=latitude-time plot.
   if (np.size(lons) > 1 and np.size(lats) > 1):
      ptype=1
      x=lons
      y=lats

   if (np.size(lats) > 1 and np.size(height) > 1): 
      ptype=2
      x=lats
      y=height
      for mydim in f.items():
         name=cf_var_name(field=f, dim=mydim)
         if name[0:3] == 'lat': 
            xunits=str(getattr(f.item(mydim), 'Units', ''))
            if (xunits in lat_units): xunits='degrees'
            xlabel=name + ' (' + xunits + ')'
         if name[0:1] == 'p' or name[0:5] == 'theta' or name[0:6] == 'height': 
            yunits=str(getattr(f.item(mydim), 'Units', ''))
            ylabel=name + ' (' + yunits + ')'


   if (np.size(lons) > 1 and np.size(height) > 1): 
      ptype=3
      x=lons
      y=height
      for mydim in f.items():
         name=cf_var_name(field=f, dim=mydim)
         if name[0:3] == 'lon': 
            xunits=str(getattr(f.item(mydim), 'Units', ''))
            if (xunits in lon_units): xunits='degrees'
            xlabel=name + ' (' + xunits + ')'
         if name[0:1] == 'p' or name[0:5] == 'theta' or name[0:6] == 'height': 
            yunits=str(getattr(f.item(mydim), 'Units', ''))
            ylabel=name + ' (' + yunits + ')'



   if (np.size(lons) > 1 and np.size(time) > 1):
      ptype=4
      x=lons
      y=time

   if np.size(lats) > 1 and np.size(time) > 1:
      ptype=5     
      x=lats
      y=time




   #Rotated pole
   if f.ref('rotated_latitude_longitude') is not None: 
      ptype=6
      rotated_pole=f.ref('rotated_latitude_longitude')
      xpole=rotated_pole['grid_north_pole_longitude']
      ypole=rotated_pole['grid_north_pole_latitude']

      for mydim in f.items():
         if mydim[:3] == 'dim':
            if np.size(np.squeeze(f.item(mydim).array)) == np.shape(np.squeeze(f.array))[1]:
               x=np.squeeze(f.item(mydim).array)
               xunits=str(getattr(f.item(mydim), 'units', ''))
               xlabel=cf_var_name(field=f, dim=mydim)

            if np.size(np.squeeze(f.item(mydim).array)) == np.shape(np.squeeze(f.array))[0]:
               y=np.squeeze(f.item(mydim).array)
               #Flip y and data if reversed
               if y[0] > y[-1]:
                  y=y[::-1]
                  field=np.flipud(field)
               yunits=str(getattr(f.item(mydim), 'Units', ''))
               ylabel=cf_var_name(field=f, dim=mydim)+yunits     


   #time height plot
   if has_height == 1 and has_time == 1:
       ptype=0
       for mydim in f.items():
          if mydim[:3] == 'dim':
              if np.size(np.squeeze(f.item(mydim).array)) == np.shape(np.squeeze(f.array))[1]:
                 x=np.squeeze(f.item(mydim).array)
                 xunits=str(getattr(f.item(mydim), 'Units', ''))
                 xlabel=cf_var_name(field=f, dim=mydim)+xunits 
    
              if np.size(np.squeeze(f.item(mydim).array)) == np.shape(np.squeeze(f.array))[0]:
                 y=np.squeeze(f.item(mydim).array)
                 yunits=str(getattr(f.item(mydim), 'units', ''))
                 ylabel=cf_var_name(field=f, dim=mydim)+yunits 





   #None of the above
   if ptype is None:
      ptype=0
      for mydim in f.items():
         if mydim[:3] == 'dim':
             if np.size(np.squeeze(f.item(mydim).array)) == np.shape(np.squeeze(f.array))[1]:
                x=np.squeeze(f.item(mydim).array)
                xunits=str(getattr(f.item(mydim), 'units', ''))
                xlabel=cf_var_name(field=f, dim=mydim)+xunits 

             if np.size(np.squeeze(f.item(mydim).array)) == np.shape(np.squeeze(f.array))[0]:
                y=np.squeeze(f.item(mydim).array)
                yunits=str(getattr(f.item(mydim), 'Units', ''))
                ylabel=cf_var_name(field=f, dim=mydim)+yunits     






   #Assign colorbar_title
   if (colorbar_title == None):   
      #colorbar_title=''
      #if hasattr(f, 'id'): colorbar_title=f.id
      #if hasattr(f, 'ncvar'): colorbar_title=f.ncvar
      #if hasattr(f, 'short_name'): colorbar_title=f.short_name 
      #if hasattr(f, 'long_name'): colorbar_title=f.long_name 
      #if hasattr(f, 'standard_name'): colorbar_title=f.standard_name

      #colorbar_title=f.name('None')
      #colorbar_title=cf_var_name(field=f)+'('+supscr(getattr(f, 'Units', ''))+')'

      #colorbar_title=cf_var_name(field=f)

      colorbar_title='No Name'
      if hasattr(f, 'id'): colorbar_title=f.id
      if hasattr(f, 'ncvar'): colorbar_title=f.ncvar
      if hasattr(f, 'short_name'): colorbar_title=f.short_name 
      if hasattr(f, 'long_name'): colorbar_title=f.long_name 
      if hasattr(f, 'standard_name'): colorbar_title=f.standard_name


      
      if hasattr(f, 'Units'): 
         if str(f.Units) == '': colorbar_title=colorbar_title+''
         else: colorbar_title=colorbar_title+'('+supscr(str(f.Units))+')'
    

   #Return data
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

   #Input error trapping
   args = True
   errstr='\n'
   if np.size(field) == 1:
      if field == None:
         errstr=errstr+'con error - a field for contouring must be passed with the f= flag\n'
         args = False   
   if np.size(x) == 1:
      if x == None:
         errstr=errstr+'con error - x coordinates must be passed with the x= flag\n'
         args = False
   if np.size(y) == 1:
      if y == None:
         errstr=errstr+'con error - y coordinates must be passed with the y= flag\n'
         args = False  
   if args == False:
      raise  Warning(errstr)  
  
  
   #Check input dimensions look okay.
   #All inputs 2D
   if np.ndim(field) == 2 and np.ndim(x) == 2 and  np.ndim(y) == 2:
      xpts=np.shape(field)[1]
      ypts=np.shape(field)[0]
      if xpts != np.shape(x)[1] or xpts != np.shape(y)[1]: args = False
      if ypts != np.shape(x)[0] or ypts != np.shape(y)[0]: args = False
      if args is True: return

   #Field x and y all 1D
   if np.ndim(field) == 1 and np.ndim(x) == 1 and np.ndim(y) == 1:
      if np.size(x) != np.size(field): args = False
      if np.size(y) != np.size(field): args = False
      if args is True: return

   #Field 2D, x and y 1D
   if np.ndim(field) != 2: args = False 
   if np.ndim(x) != 1: args = False  
   if np.ndim(y) != 1: args = False 
   if np.ndim(field) == 2:
      if np.size(x) != np.shape(field)[1]: args = False  
      if np.size(y) != np.shape(field)[0]: args = False  
   
  
   if args is False:
      errstr=errstr+'Input arguments incorrectly shaped:\n'
      errstr=errstr+'x has shape:'+str(np.shape(x))+'\n'
      errstr=errstr+'y has shape:'+str(np.shape(y))+'\n'
      errstr=errstr+'field has shape'+str(np.shape(field))+'\n\n'
      errstr=errstr+'Expected x=xpts, y=ypts, field=(ypts,xpts)\n'
      errstr=errstr+'x=npts, y=npts, field=npts\n'
      errstr=errstr+'or x=[ypts, xpts], y=[ypts, xpts], field=[ypts, xpts]\n'
      raise  Warning(errstr)  



def cscale(cmap=None, ncols=None, white=None, below=None, above=None, reverse=0):
   """ 
   | cscale - choose and manipulate colour maps.  Around 200 colour scales are
   |          available - see the gallery section for more details.
   | 
   | cmap=cmap - name of colour map
   | ncols=ncols - number of colours for colour map
   | white=white - change these colours to be white
   | below=below - change the number of colours below the mid point of 
   |               the colour scale to be this
   | above=above - change the number of colours above the mid point of 
   |               the colour scale to be this
   | reverse=False - reverse the colour scale
   | 
   |
   | Personal colour maps are available by saving the map as red green blue 
   | to a file with a set of values on each line. 
   | 
   |  
   | Use cscale() To reset to the scale1 colour scale
   |
   :Returns:
      None

   | 
   | 
   | 
   |  
   """   
    


   #If no map requested reset to default  
   if cmap == None:
      cmap='scale1'
      plotvars.cscale_flag=0
   else:
      plotvars.cs_user=cmap
      plotvars.cscale_flag=1
      if ncols is not None:  plotvars.cscale_flag=2
      if white is not None:  plotvars.cscale_flag=2
      if below is not None:  plotvars.cscale_flag=2
      if above is not None:  plotvars.cscale_flag=2
      if reverse != 0:  plotvars.cscale_flag=2

   if cmap == 'scale1' or cmap == '':
      if cmap == 'scale1': myscale=cscale1
      if cmap == 'viridis': myscale=viridis
      #convert cscale1 or viridis from hex to rgb
      r=[]
      g=[]
      b=[]
      for myhex in myscale:
         myhex=myhex.lstrip('#')
         mylen=len(myhex)
         rgb=tuple(int(myhex[i:i+mylen/3], 16) for i in range(0, mylen, mylen/3))
         r.append(rgb[0])
         g.append(rgb[1])
         b.append(rgb[2])  


   else:
      import distutils.sysconfig as sysconfig

      package_path = os.path.dirname(__file__)
      file = os.path.join(package_path, 'colourmaps/'+cmap+'.rgb')
      #file = sysconfig.get_python_lib()+'/cfplot/colourmaps/'+cmap+'.rgb'
      if os.path.isfile(file) is False:
         if os.path.isfile(cmap) is False:
            errstr='\ncscale error - colour scale not found:\n'
            errstr=errstr+'File '+file+ ' not found\n'
            errstr=errstr+'File '+cmap+' not found\n'
            raise  Warning(errstr)  
         else:
            file=cmap

      #Read in rgb values and convert to hex
      f = open(file, 'r')
      lines = f.read()
      lines = lines.splitlines()
      r=[]
      g=[]
      b=[]
      hex=[]
      for line in lines:
          vals = line.split()
          r.append(int(vals[0]))
          g.append(int(vals[1]))
          b.append(int(vals[2]))


   #Reverse the colour scale if requested
   if reverse != 0:
       r=r[::-1]
       g=g[::-1]
       b=b[::-1]


   #Interpolate to a new number of colours if requested
   if ncols != None:
      x=np.arange(np.size(r))
      xnew=np.linspace(0, np.size(r)-1, num=ncols, endpoint=True)
      f_red=interpolate.interp1d(x, r)
      f_green=interpolate.interp1d(x, g)    
      f_blue=interpolate.interp1d(x, b)     
      r=f_red(xnew)
      g=f_green(xnew)
      b=f_blue(xnew)



   #Change the number of colours below and above the mid-point if requested
   if below != None or above != None:

      #Mid-point of colour scale
      npoints=np.size(r)/2

      
      #Below mid point x locations
      x_below=[]
      lower=0
      if below == 1: x_below=0     
      if below != None: lower=below
      if below == None: lower=npoints
      if (lower > 1): x_below=((npoints-1)/float(lower-1))*np.arange(lower)

    
      #Above mid point x locations      
      x_above=[]
      upper=0
      if above == 1: x_above=npoints*2-1
      if above != None: upper=above
      if above == None: upper=npoints
      if (upper > 1): x_above=((npoints-1)/float(upper-1))*np.arange(upper)+npoints


      #Append new colour positions
      xnew=np.append(x_below, x_above)


      #Interpolate to new colour scale
      xpts=np.arange(np.size(r))
      f_red=interpolate.interp1d(xpts, r )
      f_green=interpolate.interp1d(xpts, g)    
      f_blue=interpolate.interp1d(xpts, b) 
      r=f_red(xnew)
      g=f_green(xnew)
      b=f_blue(xnew)  
 





   #Convert to hex
   hex=[]   
   for col in  np.arange(np.size(r)):
      hex.append('#%02x%02x%02x' % (r[col],g[col],b[col]))    
     
         
   #White requested colour positions    
   if white != None:
      ccols=white
      if np.size(white) == 1:   
          hex[white]='#ffffff'  
      else:
         for col in white:
            hex[col]='#ffffff'  
  
  
   #Set colour scale 
   plotvars.cs=hex


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
   """   
   cscale_ncols=np.size(plotvars.cs)
   if (plotvars.levels_extend == 'both'): colmap=plotvars.cs[1:cscale_ncols-1]   
   if (plotvars.levels_extend == 'min'): colmap=plotvars.cs[1:]   
   if (plotvars.levels_extend == 'max'): colmap=plotvars.cs[:cscale_ncols-1]   
   if (plotvars.levels_extend == 'neither'): colmap=plotvars.cs  
   return (colmap)



def bfill(f=None, x=None, y=None, clevs=False, lonlat=False, bound=False):
   """ 
    | bfill - block fill a field with colour rectangles
    | This is an internal routine and is not used by the user.
    | 
    | f=None - field
    | x=None - x points for field
    | y=None - y points for field 
    | clevs=None - levels for filling
    | lonlat=False - lonlat data
    | bound=False - x and y are cf data boundaries
    | 
    | 
    | 
    :Returns:
       None
    |  
    | 
    | 
    |
   """


   #Assign f to field as this may be modified in lat-lon plots
   field=f
 
   #Add in extra levels for colour bar extensions if present.
   levs=np.array(clevs).astype(float)
   if (plotvars.levels_extend == 'min' or plotvars.levels_extend == 'both'):
      levs=np.insert(levs,0, -1e30)
   if (plotvars.levels_extend == 'max' or plotvars.levels_extend == 'both'):
      levs=np.append(levs, 1e30)



   if bound == 1:
      xpts=x
      ypts=y

      
      #print 'xpts are ', xpts
      #print ''
      #print 'ypts are ', ypts
      #print ''
      #print 'shape of data is ', np.shape(f)
      #print 'shape of x , y are ', np.shape(x), np.shape(y)

   if bound == 0:
      #Find x box boundaries
      xpts=x[0]-(x[1]-x[0])/2.0
      for ix in np.arange(np.size(x)-1): 
         xpts=np.append(xpts, x[ix]+(x[ix+1]-x[ix])/2.0)
      xpts=np.append(xpts, x[ix+1]+(x[ix+1]-x[ix])/2.0) 


      #Find y box boundaries
      ypts=y[0]-(y[1]-y[0])/2.0
      for iy in np.arange(np.size(y)-1): 
         ypts=np.append(ypts, y[iy]+(y[iy+1]-y[iy])/2.0)
      ypts=np.append(ypts, y[iy+1]+(y[iy+1]-y[iy])/2.0) 



   #Shift lon grid if needed
   if lonlat == 1:

      #Extract upper bound and original rhs of box longitude bounding points
      upper_bound=ypts[-1]
      xpts_orig=xpts
      ypts_orig=ypts
      
      #Reduce xpts and ypts by 1 or shiftgrid fails
      #The last points are the right / upper bounds for the last data box
      xpts=xpts[0:-1]
      ypts=ypts[0:-1]


      if plotvars.lonmin < np.nanmin(xpts): xpts=xpts-360
      if plotvars.lonmin > np.nanmax(xpts): xpts=xpts+360

      #Add cyclic information if missing.
      lonrange=np.nanmax(xpts)-np.nanmin(xpts)
      if lonrange < 360:
         field, xpts = addcyclic(field, xpts)

      #shiftgrid on lons and data
      field, xpts=shiftgrid(plotvars.lonmin, field, xpts) 

      right_bound=xpts[-1]+(xpts[-1]-xpts[-2])

      #Add end x and y end points
      xpts=np.append(xpts, right_bound)
      ypts=np.append(ypts, upper_bound)


   #Make plot
   #Set colour map
   cmin=0
   cmax=np.size(plotvars.cs)
   if (plotvars.levels_extend == 'min' or plotvars.levels_extend == 'both'): cmin=1
   if (plotvars.levels_extend == 'max' or plotvars.levels_extend == 'both'): cmax=np.size(plotvars.cs)-1

   cmap = matplotlib.colors.ListedColormap(plotvars.cs[cmin:cmax])
   if (plotvars.levels_extend == 'min' or plotvars.levels_extend == 'both'):
      cmap.set_under(plotvars.cs[0])
   if (plotvars.levels_extend == 'max' or plotvars.levels_extend == 'both'):
      cmap.set_over(plotvars.cs[-1])

   norm = matplotlib.colors.BoundaryNorm(clevs, ncolors=cmap.N, clip=False)
   im = plotvars.plot.pcolormesh(xpts, ypts, field, cmap=cmap, norm=norm)

   






def regrid(f=None, x=None, y=None, xnew=None, ynew=None, lonlat=None):

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

   #reassign input arrays
   regrid_f=f
   regrid_x=x
   regrid_y=y

   import numpy as np

   fieldout=[]

   #Reverse xpts and field if necessary
   if regrid_x[0] > regrid_x[-1]:
      regrid_x=regrid_x[::-1]            
      field=np.fliplr(regrid_f)

   #Reverse ypts and field if necessary
   if regrid_y[0] > regrid_y[-1]:
      regrid_y=regrid_y[::-1]         
      regrid_f=np.flipud(regrid_f)

   #Iterate over the new grid to get the new grid values.
   for i in np.arange(np.size(xnew)):

      xval=xnew[i]
      yval=ynew[i]

      #Find position of new grid point in the x and y arrays
      myxpos=find_pos_in_array(vals=regrid_x, val=xval)
      myypos=find_pos_in_array(vals=regrid_y, val=yval) 


      myxpos2=myxpos+1
      myypos2=myypos+1
      

      if (myxpos2 != myxpos): 
         alpha=(xnew[i]-regrid_x[myxpos])/(regrid_x[myxpos2]-regrid_x[myxpos]) 
      else: 
         alpha=(xnew[i]-regrid_x[myxpos])/1E-30

      newval1=regrid_f[myypos,myxpos]-(regrid_f[myypos,myxpos]-regrid_f[myypos,myxpos2])*alpha
      newval2=regrid_f[myypos2,myxpos]-(regrid_f[myypos2,myxpos]-regrid_f[myypos2,myxpos2])*alpha

      if (myypos2 != myypos): alpha2=(ynew[i]-regrid_y[myypos])/(regrid_y[myypos2]-regrid_y[myypos])
      else: alpha2=(ynew[i]-regrid_y[myypos])/1E-30

   
      newval3=newval1-(newval1-newval2)*alpha2
  
      fieldout=np.append(fieldout, newval3)

   return fieldout


def stipple(f=None, x=None, y=None, min=None, max=None, size=80, color='k', pts=50, marker='.'):
    
   """
    | stipple - put dots on the plot to indicate value of interest
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
    | 
    |     
    :Returns:
       None
    | 
    | 
   """


   #Extract required data for contouring 
   #If a cf-python field
   if isinstance(f[0], cf.Field):
      colorbar_title=''
      f=f[0]
      field, xpts, ypts, ptype, colorbar_title, xlabel, ylabel, xpole, ypole=\
         cf_data_assign(f, colorbar_title)
   else:
      field=f #field data passed in as f
      check_data(field, x, y)
      xpts=x
      ypts=y

   

   if plotvars.plot_type == 1:
      #Cylindrical projection
      #Add cyclic information if missing.
      lonrange=np.nanmax(xpts)-np.nanmin(xpts)
      if lonrange < 360:
         field, xpts = addcyclic(field, xpts)

      #Shift grid if needed
      if plotvars.lonmin < np.nanmin(xpts): xpts=xpts-360
      if plotvars.lonmin > np.nanmax(xpts): xpts=xpts+360

      field, xpts=shiftgrid(plotvars.lonmin, field, xpts)   

      if plotvars.proj == 'cyl':
         #Calculate interpolation points
         xnew, ynew=stipple_points(xmin=np.nanmin(xpts), xmax=np.nanmax(xpts),\
                                   ymin=np.nanmin(ypts), ymax=np.nanmax(ypts), pts=pts, stype=2)
  
         #Calculate points in map space
         xnew_map,ynew_map=plotvars.mymap(xnew,ynew)



      if plotvars.proj == 'npstere' or plotvars.proj == 'spstere':
         #Calculate interpolation points
         xnew, ynew, xnew_map, ynew_map=polar_regular_grid()




   if plotvars.plot_type == 2:
   #Calculate interpolation points
         
      xnew, ynew=stipple_points(xmin=np.nanmin(xpts), xmax=np.nanmax(xpts),\
                                ymin=np.nanmin(ypts), ymax=np.nanmax(ypts), pts=pts, stype=2)



   #Get values at the new points
   vals=regrid(f=field, x=xpts, y=ypts, xnew=xnew, ynew=ynew)

   #Work out which of the points are valid
   valid_points=np.array([], dtype='int32')
   for i in np.arange(np.size(vals)):
      if vals[i] >=min and vals[i] <=max:
         valid_points=np.append(valid_points, i)


      
   
   if plotvars.plot_type == 1:
      plotvars.plot.scatter(xnew_map[valid_points], ynew_map[valid_points], s=size, c=color, marker=marker)


   if plotvars.plot_type == 2:
      plotvars.plot.scatter(xnew[valid_points], ynew[valid_points], s=size, c=color, marker=marker)





def stipple_points(xmin=None, xmax=None, ymin=None, ymax=None, pts=None, stype=None):
    
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

   #Work out number of points in x and y directions
   if np.size(pts) == 1:
      pts_x=pts
      pts_y=pts
   if np.size(pts) == 2:
      pts_x=pts[0]
      pts_y=pts[1]

   #Create regularly spaced points
   xstep=(xmax-xmin)/float(pts_x)
   x1=[xmin+xstep/4]
   while (np.nanmax(x1)+xstep) < xmax-xstep/10:
      x1=np.append(x1,  np.nanmax(x1)+xstep)
   nxpts=np.size(x1)
   
   x2=[xmin+xstep*3/4]
   while (np.nanmax(x2)+xstep) < xmax-xstep/10:
      x2=np.append(x2,  np.nanmax(x2)+xstep)

   ystep=(ymax-ymin)/float(pts_y)
   y1=[ymin+ystep/2]
   while (np.nanmax(y1)+ystep) < ymax-ystep/10:
      y1=np.append(y1,  np.nanmax(y1)+ystep)


   
   #Create interpolation points
   xnew=[]
   ynew=[]
   iy=0

   for y in y1:
      iy=iy+1
      if stype == 1:
         xnew=np.append(xnew, x1)
         y2=np.zeros(np.size(x1))
         y2.fill(y)
         ynew=np.append(ynew, y2)

      if stype == 2:
         if iy%2 == 0: 
            xnew=np.append(xnew, x1)
            y2=np.zeros(np.size(x1))
            y2.fill(y)
            ynew=np.append(ynew, y2)
         if iy%2 == 1: 
            xnew=np.append(xnew, x2)
            y2=np.zeros(np.size(x2))
            y2.fill(y)
            ynew=np.append(ynew, y2)
      


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


   pos=-1
   if above is False:
      for myval in vals:
         if val > myval: pos=pos+1

   if above is 1:
      for myval in vals:
         if val >= myval: pos=pos+1

      if np.size(vals)-1 > pos: pos=pos+1

   return pos



def vect(u=None, v=None, x=None, y=None, scale=None, stride=None, pts=None,\
         key_length=None, key_label=None, ptype=None, title=None,\
         width=0.02, headwidth=3, headlength=5, headaxislength=4.5, pivot='middle', key_location=[0.9, -0.06],
         key_show=True, axes=True, xaxis=True, yaxis=True, xticks=None, xticklabels=None, \
         yticks=None, yticklabels=None, xlabel=None, ylabel=None, ylog=False):

   """
    | vect - plot vectors
    | 
    | u=None - u wind
    | v=None - v wind
    | x=None - x locations of u and v
    | y=None - y locations of u and v
    | scale=None - data units per arrow length unit.  A smaller values gives a larger vector.
                   Generally takes one value but in the case of two supplied values the second vector 
    |              scaling applies to the v field. 
    | stride=None - plot vector every stride points. Can take two values one for x and one for y.
    | pts=None - use bilinear interpolation to interpolate vectors onto a new grid - takes one or two values.
    |            If one value is passed then this is used for both the x and y axes.  
    | key_length=None - length of the key.  Generally takes one value but in the case
    |                   of two supplied values the second vector scaling applies to the v field. 
    | key_label=None - label for the key. Generally takes one value but in the case
    |                  of two supplied values the second vector scaling applies to the v field. 
    | key_location=[0.9, -0.06] - location of the vector key relative to the plot in normalised coordinates.
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
    | width=0.005 - shaft width in arrow units; default is 0.005 times the width of the plot
    | headwidth=3 - head width as multiple of shaft width, default is 3
    | headlength=5 - head length as multiple of shaft width, default is 5
    | headaxislength=4.5 - head length at shaft intersection, default is 4.5
    | pivot='middle' - the part of the arrow that is at the grid point; the arrow rotates about this point
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
    |
    :Returns:
     None
    | 
    | 
    | 
   """

   colorbar_title=''
   text_fontsize=plotvars.text_fontsize
   continent_thickness=plotvars.continent_thickness
   continent_color=plotvars.continent_color
   if text_fontsize is None: text_fontsize=11
   if continent_thickness is None: continent_thickness=1.5
   if continent_color is None: continent_color='k'
   #ylog=plotvars.ylog
   title_fontsize=plotvars.title_fontsize
   title_fontweight=plotvars.title_fontweight
   if title_fontsize is None: title_fontsize=15

   #Set potential user axis labels
   user_xlabel=xlabel
   user_ylabel=ylabel


   #Extract required data for contouring
   #If a cf-python field
   if isinstance(u[0], cf.Field):
      u=u[0]
      u_data, u_x, u_y, ptype, colorbar_title, xlabel, ylabel, xpole, ypole=\
         cf_data_assign(u, colorbar_title)
   else:
      #field=f #field data passed in as f
      check_data(u, x, y)
      u_data=deepcopy(u)
      u_x=deepcopy(x)
      u_y=deepcopy(y)
      xlabel=''
      ylabel=''


   if isinstance(v[0], cf.Field):
      v=v[0]
      v_data, v_x, v_y, ptype, colorbar_title, xlabel, ylabel, xpole, ypole=\
         cf_data_assign(v, colorbar_title)
   else:
      #field=f #field data passed in as f
      check_data(v, x, y)
      v_data=deepcopy(v)
      v_x=deepcopy(x)
      v_y=deepcopy(y)
      xlabel=''
      ylabel=''
   
   #Reset xlabel and ylabel values with user defined labels in specified
   if user_xlabel is not None: xlabel=user_xlabel
   if user_ylabel is not None: ylabel=user_ylabel

   if scale is None: 
       scale=np.nanmax(u_data)/4.0


   if key_length is None: key_length=scale






   #Open a new plot if necessary
   if plotvars.user_plot == 0: 
      gopen(user_plot=0)

   #Set plot type if user specified
   if (ptype != None): plotvars.plot_type=ptype

   
   if plotvars.plot_type == 1:
      #Set up mapping
      set_map()    
      mymap=plotvars.mymap   
    
      #add cyclic and shift grid 
      u_data, u_x = addcyclic(u_data, u_x)
      v_data, v_x = addcyclic(v_data, v_x)
      if plotvars.lonmin < np.nanmin(u_x): u_x=u_x-360.0
      if plotvars.lonmin < np.nanmin(v_x): v_x=v_x-360.0
      u_data, u_x = shiftgrid(plotvars.lonmin, u_data, u_x)
      v_data, v_x = shiftgrid(plotvars.lonmin, v_data, v_x)


   #stride data points to reduce vector density
   if stride is not None:
      if np.size(stride) == 1:
         xstride=stride
         ystride=stride
      if np.size(stride) == 2:
         xstride=stride[0]
         ystride=stride[1]


      iskip=1
      for ix in np.arange(np.size(u_x)):
         if iskip != xstride: u_x[ix]=float('nan') 
         iskip=iskip+1
         if iskip > xstride: iskip=1     
      iskip=1
      for iy in np.arange(np.size(u_y)):
         if iskip != ystride: u_y[iy]=float('nan') 
         iskip=iskip+1
         if iskip > ystride: iskip=1 

      
   #Use bilinear interpolation to find new vector positions and values on a map
   if pts is not None and plotvars.plot_type == 1:

      if plotvars.proj != 'npstere' and plotvars.proj != 'spstere': 
         #Calculate interpolation points and values
         xnew, ynew=stipple_points(xmin=plotvars.lonmin, xmax=plotvars.lonmax,\
                                   ymin=plotvars.latmin, ymax=plotvars.latmax, pts=pts, stype=1)

         u_vals=regrid(f=u_data, x=u_x, y=u_y, xnew=xnew, ynew=ynew)
         v_vals=regrid(f=v_data, x=u_x, y=u_y, xnew=xnew, ynew=ynew)

         #Plot vectors
         quiv=plotvars.mymap.quiver(xnew,ynew,u_vals,v_vals, pivot=pivot,units='inches', scale=scale,\
                                    width=width, headwidth=headwidth, headlength=headlength,\
                                    headaxislength=headaxislength)
      else:
         #Polar grid
         #Calculate interpolation points and values
         
         xnew, ynew, xnew_map, ynew_map=polar_regular_grid(pts=pts)

         u_vals=regrid(f=u_data, x=u_x, y=u_y, xnew=xnew, ynew=ynew)
         v_vals=regrid(f=v_data, x=u_x, y=u_y, xnew=xnew, ynew=ynew)

         #Rotate vector values
         hem=1 #Northern hemisphere
         if plotvars.proj == 'spstere': hem=-1
         for i in np.arange(np.size(u_vals)):
              if hem == 1:
                  newu=u_vals[i]*np.cos(np.radians(xnew[i]))-hem*v_vals[i]*np.sin(np.radians(xnew[i]))
                  newv=v_vals[i]*np.cos(np.radians(xnew[i]))+hem*u_vals[i]*np.sin(np.radians(xnew[i]))  
              else:
                  newu=hem*u_vals[i]*np.cos(np.radians(xnew[i]))+hem*v_vals[i]*np.sin(np.radians(xnew[i]))
                  newv=hem*v_vals[i]*np.cos(np.radians(xnew[i]))-hem*u_vals[i]*np.sin(np.radians(xnew[i]))  


              u_vals[i]=newu
              v_vals[i]=newv




         #Plot vectors
         quiv=plotvars.mymap.quiver(xnew_map,ynew_map,u_vals,v_vals, pivot=pivot,\
                                    units='inches', scale=scale,\
                                    width=width, headwidth=headwidth, headlength=headlength,\
                                    headaxislength=headaxislength)

      #Make key_label if none exists
      if key_label is None: 
          key_label=str(key_length)
          if isinstance(u[0], cf.Field): key_label=supscr(key_label+u.units)


      if key_show is True:
          quiv_key=plotvars.plot.quiverkey(quiv, key_location[0], key_location[1], key_length, key_label, labelpos='W')

   #Map vectors
   if plotvars.plot_type == 1:

      if pts is None:
         #convert lons, lats into map coordinates
         x,y=plotvars.mymap(*np.meshgrid(u_x, u_y))

         #plot vectors and key
         quiv=plotvars.mymap.quiver(u_x,u_y,u_data,v_data, pivot=pivot, units='inches', scale=scale,\
                                    width=width, headwidth=headwidth, headlength=headlength,\
                                    headaxislength=headaxislength)

         #Make key_label if none exists
         if key_label is None: 
             key_label=str(key_length)
         if isinstance(u[0], cf.Field): key_label=supscr(key_label+u.units)
         if key_show is True:
             quiv_key=plotvars.plot.quiverkey(quiv, key_location[0], key_location[1], key_length, key_label, labelpos='W')

      #axes
      if plotvars.proj == 'cyl':
         lonticks,lonlabels=mapaxis(min=plotvars.lonmin, max=plotvars.lonmax, type=1)
         latticks,latlabels=mapaxis(min=plotvars.latmin, max=plotvars.latmax, type=2)


         if axes is True:
             if xaxis is True:
                 if xticks is None:
                     axes_plot(xticks=lonticks, xticklabels=lonlabels)
                 else:
                     if xticklabels is None:
                         axes_plot(xticks=xticks, xticklabels=xticks)
                     else:
                         axes_plot(xticks=xticks, xticklabels=xticklabels)
             if yaxis is True:
                 if yticks is None:
                     axes_plot(yticks=latticks, yticklabels=latlabels)
                 else:
                     if yticklabels is None:
                         axes_plot(yticks=yticks, yticklabels=yticks)
                     else:
                         axes_plot(yticks=yticks, yticklabels=yticklabels)


         if user_xlabel is not None: plotvars.plot.set_xlabel(user_xlabel)
         if user_ylabel is not None: plotvars.plot.set_ylabel(user_ylabel)


   
      if plotvars.proj == 'npstere' or plotvars.proj == 'spstere': 
         latstep=30
         if 90-abs(plotvars.boundinglat) <= 50: latstep=10
         if axes is True:
             if xaxis is True:
                 if xticks is None:
                     mymap.drawmeridians(np.arange(0,360,60), labels=[1,1,1,1]) 
                 else:
                     mymap.drawmeridians(xticks, labels=[1,1,1,1]) 
             if yaxis is True:
                 if yticks is None:
                     mymap.drawparallels(np.arange(-90,120,latstep))
                 else:
                     mymap.drawparallels(yticks)




      #Coastlines and title
      mymap.drawcoastlines(linewidth=continent_thickness, color=continent_color)
      if title is not None:
         plotvars.plot.set_title(title, y=1.03, fontsize=title_fontsize, fontweight=title_fontweight)



   ########### 
   #Zonal plot
   ###########
   if plotvars.plot_type == 2: 

      user_gset=plotvars.user_gset
      if user_gset == 0:
         #Program selected data plot limits
         xmin=np.nanmin(u_x)
         if xmin < -80 and xmin >= -90: xmin=-90
         xmax=np.nanmax(u_x)
         if xmax > 80 and xmax <= 90: xmax=90 
         ymin=np.nanmin(u_y)
         if ymin <= 10: ymin=0
         ymax=np.nanmax(u_y)
      else:
         #User specified plot limits
         xmin=plotvars.xmin
         xmax=plotvars.xmax
         if plotvars.ymin < plotvars.ymax: 
            ymin=plotvars.ymin
            ymax=plotvars.ymax
         else:
            ymin=plotvars.ymax
            ymax=plotvars.ymin


      xstep=None
      if (xmin == -90 and xmax == 90): xstep=30
      ystep=None
      if (ymax == 1000): ystep=100
      if (ymax == 100000): ystep=10000

      ytype=0 #pressure or similar y axis
      if 'theta' in ylabel.split(' '): ytype=1
      if 'height' in ylabel.split(' '): 
         ytype=1
         ystep=100
         if (ymax - ymin) > 5000: ystep=500.0
         if (ymax - ymin) > 10000: ystep=1000.0
         if (ymax - ymin) > 50000: ystep=10000.0

      #Set plot limits and draw axes
      if ylog != 1:   
         if ytype == 1: 
            gset(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, user_gset=user_gset)
         else: 
            gset(xmin=xmin, xmax=xmax, ymin=ymax, ymax=ymin, user_gset=user_gset)         

         #Set default axis labels
         latticks,latlabels=mapaxis(min=xmin, max=xmax, type=2)
         yaxisticks=gvals(dmin=ymin, dmax=ymax, tight=1, mystep=ystep, mod=0)[0]

         heightticks=gvals(dmin=ymin, dmax=ymax, tight=1, mystep=ystep, mod=0)[0]
         heightlabels=heightticks

         if axes is True:
             if xaxis is True:
                 if xticks is not None:
                     latticks=xticks
                     latlabels=xticks
                     if xticklabels is not None: latlabels=xticklabels
             else:
                 latticks=[100000000]
                 xlabel=''

             if yaxis is True:
                 if yticks is not None:
                     heightticks=yticks
                     heightlabels=yticks
                     if yticklabels is not None: heightlabels=yticklabels
             else:
                 heightticks=[100000000]
                 ylabel=''


         else:
             latticks=[100000000]
             heightticks=[100000000]
             xlabel=''
             ylabel=''


         axes_plot(xticks=latticks, xticklabels=latlabels,\
                   yticks=heightticks, yticklabels=heightlabels,\
                   xlabel=xlabel, ylabel=ylabel)





      #Log y axis 
      if ylog == True or ylog == 1:
         if ymin == 0: ymin=1 #reset zero mb/height input to a small value
         gset(xmin=xmin, xmax=xmax, ymin=ymax, ymax=ymin, ylog=1, user_gset=user_gset)
         latticks,latlabels=mapaxis(min=xmin, max=xmax, type=2)

         if axes is True:
             if xaxis is True:
                 if xticks is not None:
                     latticks=xticks
                     latlabels=xticks
                     if xticklabels is not None: latlabels=xticklabels
             else:
                 latticks=[100000000]
                 xlabel=''

             if yaxis is True:
                 if yticks is not None:
                     heightticks=yticks
                     heightlabels=yticks
                     if yticklabels is not None: heightlabels=yticklabels
             else:
                 heightticks=[100000000]
                 ylabel=''


             if yticks is None:
                 axes_plot(xticks=latticks, xticklabels=latlabels, xlabel=xlabel, ylabel=ylabel)
             else:
                 axes_plot(xticks=latticks, xticklabels=latlabels, yticks=heightticks, yticklabels=heightlabels, \
                           xlabel=xlabel, ylabel=ylabel)






      #Regrid the data if requested
      if pts is not None:
         xnew, ynew=stipple_points(xmin=np.min(u_x), xmax=np.max(u_x),\
                                   ymin=np.min(u_y), ymax=np.max(u_y), pts=pts, stype=1)
         u_vals=regrid(f=u_data, x=u_x, y=u_y, xnew=xnew, ynew=ynew)
         v_vals=regrid(f=v_data, x=u_x, y=u_y, xnew=xnew, ynew=ynew)
        
         u_x=xnew
         u_y=ynew
         u_data=u_vals
         v_data=v_vals


      #set scale and key lengths
      if np.size(scale) == 1:
          scale_u=scale
          scale_v=scale
      else:
          scale_u=scale[0]
          scale_v=scale[1]

      if np.size(key_length) == 2:
          key_length_u=key_length[0]
          key_length_v=key_length[1]
          #scale v data
          v_data=v_data*scale_u/scale_v
      else:
          key_length_u=key_length
 
      #Plot the vectors 
      quiv=plotvars.plot.quiver(u_x,u_y,u_data,v_data, pivot=pivot, units='inches', scale=scale_u,\
                                width=width, headwidth=headwidth, headlength=headlength,\
                                headaxislength=headaxislength)

      #Plot single key
      if np.size(scale) == 1:  
          #Single scale vector
          if key_label is None:
              key_label_u=str(key_length_u)
              if isinstance(u[0], cf.Field): key_label_u=supscr(key_label_u+' ('+u.units+')')
          else:
              key_label_u=key_label[0]
          if key_show is True:
              quiv_key=plotvars.plot.quiverkey(quiv, key_location[0], key_location[1], key_length_u, key_label_u, labelpos='W')   

      #Plot two keys
      if np.size(scale) == 2:
          #translate from normalised units to plot units
          xpos=key_location[0]*(plotvars.xmax-plotvars.xmin)+plotvars.xmin
          ypos=key_location[1]*(plotvars.ymax-plotvars.ymin)+plotvars.ymin

          #horizontal and vertical spacings for offsetting vector reference text
          xoffset=0.01*abs(plotvars.xmax-plotvars.xmin)
          yoffset=0.01*abs(plotvars.ymax-plotvars.ymin)

          #Assign key labels if necessary
          if key_label is None:
              key_label_u=str(key_length_u)
              key_label_v=str(key_length_v)
              if isinstance(u[0], cf.Field): key_label_u=supscr(key_label_u+' ('+u.units+')')
              if isinstance(v[0], cf.Field): key_label_v=supscr(key_label_v+' ('+v.units+')')
          else:
              key_label_u=supscr(key_label[0])
              key_label_v=supscr(key_label[1])
         
          #Plot reference vectors and keys 
          if key_show is True:
              quiv1=plotvars.plot.quiver(xpos, ypos, key_length[0], 0, pivot='tail', units='inches', scale=scale[0], \
                                         headaxislength=headaxislength, width=width, headwidth=headwidth, \
                                         headlength=headlength, clip_on=False)
              quiv2=plotvars.plot.quiver(xpos, ypos, 0, key_length[1], pivot='tail', units='inches', scale=scale[1], \
                                         headaxislength=headaxislength, width=width, headwidth=headwidth, \
                                         headlength=headlength, clip_on=False)
              plotvars.plot.text(xpos, ypos+yoffset, key_label_u, horizontalalignment='left', verticalalignment='top')
              plotvars.plot.text(xpos-xoffset, ypos, key_label_v, horizontalalignment='right', verticalalignment='bottom')


      if title is not None:
          plotvars.plot.set_title(title, y=1.03, fontsize=plotvars.title_fontsize, fontweight=title_fontweight)


   ##########
   #Save plot
   ##########
   if plotvars.user_plot == 0: 
       gset()
       cscale()
       gclose()
  

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
   
   #Set up mapping
   if plotvars.proj == 'cyl':   
      lon_mid=plotvars.lonmin+(plotvars.lonmax-plotvars.lonmin)/2.0
      lat_mid=plotvars.latmin+(plotvars.latmax-plotvars.latmin)/2.0
      mymap = Basemap(projection='cyl',llcrnrlon=plotvars.lonmin, urcrnrlon=plotvars.lonmax, \
                      llcrnrlat=plotvars.latmin, urcrnrlat=plotvars.latmax, \
                      lon_0=lon_mid, lat_0=lat_mid, resolution=plotvars.resolution)  
 
   if plotvars.proj == 'npstere':
      mymap = Basemap(projection='npstere', boundinglat=plotvars.boundinglat, round='True',\
                      lon_0=plotvars.lon_0, lat_0=90, resolution=plotvars.resolution)

   if plotvars.proj == 'spstere':
      mymap = Basemap(projection='spstere', boundinglat=plotvars.boundinglat, round='True',\
                      lon_0=plotvars.lon_0, lat_0=-90, resolution=plotvars.resolution)

   if plotvars.proj == 'moll':
      mymap = Basemap(projection='moll', lon_0=plotvars.lon_0, resolution=plotvars.resolution)

   #Store map 
   plotvars.mymap=mymap



def polar_regular_grid(pts=50):
   """
    | polar_regular_grid - return a regular grid over a polar stereographic area
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


   mymap=plotvars.mymap

   boundinglat=plotvars.boundinglat
   lon_0=plotvars.lon_0

   if plotvars.proj == 'npstere':
      x, ymin=mymap(lon_0, boundinglat)
      x, ymax=mymap(lon_0+180, boundinglat)
   if plotvars.proj == 'spstere':
      x, ymin=mymap(lon_0+180, boundinglat)
      x, ymax=mymap(lon_0, boundinglat)
   xmin, y=mymap(lon_0-90, boundinglat)
   xmax, y=mymap(lon_0+90, boundinglat)




   xnew, ynew = stipple_points(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, pts=pts, stype=2)
   lons, lats=mymap(xnew, ynew, inverse=True)

   #Work out which of the points are valid
   valid_points=np.array([], dtype='int32')
   if plotvars.proj == 'npstere':
      for i in np.arange(np.size(lats)):
         if lats[i] >= boundinglat :
            valid_points=np.append(valid_points, i)
   if plotvars.proj == 'spstere':
      for i in np.arange(np.size(lats)):
         if lats[i] <= boundinglat :
            valid_points=np.append(valid_points, i)


   return lons[valid_points], lats[valid_points], xnew[valid_points], ynew[valid_points]



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

   id=getattr(field.item(dim), 'id', False)
   ncvar=getattr(field.item(dim), 'ncvar', False)
   short_name=getattr(field.item(dim), 'short_name', False)
   long_name=getattr(field.item(dim), 'long_name', False)
   standard_name=getattr(field.item(dim), 'standard_name', False)

   name='No Name'
   if id: name=id 
   if ncvar: name=ncvar 
   if short_name: name=short_name
   if long_name: name=long_name
   if standard_name: name=standard_name

   #name=field.name('No name')

   #name='No Name'
   #if hasattr(field.item(dim), 'id'): name=field.id
   #if hasattr(field.item(dim), 'ncvar'): name=field.ncvar
   #if hasattr(field.item(dim), 'short_name'): name=field.short_name 
   #if hasattr(field.item(dim), 'long_name'): name=field.long_name 
   #if hasattr(field.item(dim), 'standard_name'): name=field.standard_name


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
   
   #Define scale categories
   uniform=['viridis', 'magma', 'inferno', 'plasma', 'parula', 'gray']

   ncl_large=['amwg256', 'BkBlAqGrYeOrReViWh200', 'BlAqGrYeOrRe', 'BlAqGrYeOrReVi200',\
              'BlGrYeOrReVi200', 'BlRe', 'BlueRed', 'BlueRedGray', 'BlueWhiteOrangeRed',\
              'BlueYellowRed', 'BlWhRe', 'cmp_b2r',\
              'cmp_haxby', 'detail', 'extrema', 'GrayWhiteGray','GreenYellow',\
              'helix', 'helix1', 'hotres', 'matlab_hot', 'matlab_hsv', 'matlab_jet',\
              'matlab_lines', 'ncl_default', 'ncview_default', 'OceanLakeLandSnow',\
              'rainbow', 'rainbow+white+gray',  'rainbow+white','rainbow+gray',\
              'tbr_240-300', 'tbr_stdev_0-30', 'tbr_var_0-500', 'tbrAvg1',\
              'tbrStd1', 'tbrVar1', 'thelix', 'ViBlGrWhYeOrRe',\
              'wh-bl-gr-ye-re', 'WhBlGrYeRe', 'WhBlReWh', 'WhiteBlue',\
              'WhiteBlueGreenYellowRed', 'WhiteGreen', 'WhiteYellowOrangeRed',\
              'WhViBlGrYeOrRe', 'WhViBlGrYeOrReWh', 'wxpEnIR', '3gauss', '3saw']

   ncl_meteoswiss=['hotcold_18lev', 'hotcolr_19lev', 'mch_default', 'perc2_9lev', 'percent_11lev',\
                   'precip2_15lev', 'precip2_17lev', 'precip3_16lev', 'precip4_11lev', \
                   'precip4_diff_19lev', 'precip_11lev', 'precip_diff_12lev', 'precip_diff_1lev',\
                   'rh_19lev', 'spread_15lev']

   ncl_color_blindness=['StepSeq25', 'posneg_2', 'posneg_1', 'BlueDarkOrange18', 'BlueDarkRed18',\
                        'GreenMagenta16', 'BlueGreen14', 'BrownBlue12', 'Cat12']

   ncl_small=['amwg', 'amwg_blueyellowred','BlueDarkRed18', 'BlueDarkOrange18','BlueGreen14',\
              'BrownBlue12', 'Cat12', 'cmp_flux', 'cosam12', 'cosam',\
              'GHRSST_anomaly', 'GreenMagenta16',\
              'hotcold_18lev', 'hotcolr_19lev', 'mch_default', 'nrl_sirkes', \
              'nrl_sirkes_nowhite', 'perc2_9lev', 'percent_11lev', 'posneg_2', 'prcp_1', 'prcp_2',\
              'prcp_3', 'precip_11lev', 'precip_diff_12lev', 'precip_diff_1lev', 'precip2_15lev',\
              'precip2_17lev', 'precip3_16lev', 'precip4_11lev', 'precip4_diff_19lev', 'radar',\
              'radar_1', 'rh_19lev', 'seaice_1', 'seaice_2', 'so4_21', 'spread_15lev', 'StepSeq25',\
              'sunshine_9lev', 'sunshine_diff_12lev', 'temp_19lev', 'temp_diff_18lev', 'temp_diff_1lev',\
              'topo_15lev', 'wgne15', 'wind_17lev']


   orography=['os250kmetres', 'wiki-1.0.2', 'wiki-1.0.3', 'wiki-2.0', 'wiki-2.0-reduced', 'arctic']

   idl_guide=[]
   for i in np.arange(1,45):
      idl_guide.append('scale'+str(i))

   for category in 'uniform', 'ncl_meteoswiss', 'ncl_small', 'ncl_large', 'ncl_color_blindness', 'orography', 'idl_guide': 
      if category == 'uniform': 
         scales=uniform
         div='================== ====='
         chars=10
         print 'Perceptually uniform colour maps for use with continuous data'
         print '----------------------------------------------' 
         print ''
         print div
         print 'Name               Scale'
         print div

      if category == 'ncl_meteoswiss': 
         scales=ncl_meteoswiss
         div='================== ====='
         chars=19
         print 'NCAR Command Language - MeteoSwiss colour maps'
         print '----------------------------------------------' 
         print ''
         print div
         print 'Name               Scale'
         print div
      if category == 'ncl_small': 
         scales=ncl_small
         div='=================== ====='
         chars=20
         print 'NCAR Command Language - small color maps (<50 colours)'
         print '------------------------------------------------------'
         print ''
         print div
         print 'Name                Scale'
         print div
      if category == 'ncl_large': 
         scales=ncl_large
         div='======================= ====='
         chars=24
         print 'NCAR Command Language - large colour maps (>50 colours)'
         print '-------------------------------------------------------'
         print ''
         print div
         print 'Name                    Scale'
         print div
      if category == 'ncl_color_blindness': 
         scales=ncl_color_blindness
         div='================ ====='
         chars=17
         print 'NCAR Command Language - Enhanced to help with colour blindness'
         print '--------------------------------------------------------------'
         print ''
         print div
         print 'Name             Scale'
         print div
         chars=17
      if category == 'orography': 
         scales=orography
         div='================ ====='
         chars=17
         print 'Orography/bathymetry colour scales'
         print '----------------------------------'
         print ''
         print div
         print 'Name             Scale'
         print div
         chars=17
      if category == 'idl_guide': 
         scales=idl_guide
         div='======= ====='
         chars=8
         print 'IDL guide scales'
         print '----------------'
         print ''
         print div
         print 'Name    Scale'
         print div
         chars=8
       

      for scale in scales:
         #Make image of scale
         fig = plot.figure(figsize=(8,0.5))
         ax1 = fig.add_axes([0.05, 0.1, 0.9, 0.2])
         cscale(scale)
         ncols=np.size(plotvars.cs)
         cmap = matplotlib.colors.ListedColormap(plotvars.cs)
         cb1 = matplotlib.colorbar.ColorbarBase(ax1, cmap=cmap, orientation='horizontal', ticks=None)
         cb1.set_ticks([0.0,1.0])
         cb1.set_ticklabels(['',''])
         file='/home/swsheaps/public_html/cfplot_sphinx/images/colour_scales/'+scale+'.png'
         plot.savefig(file)
         plot.close()

         #Use covert to trim the png file to remove white space
         subprocess.call(["convert", "-trim", file, file])

         name_pad=scale
         while len(name_pad) < chars: name_pad=name_pad+' '
         print  name_pad+'.. image:: images/colour_scales/'+scale+'.png'

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



def setvars(file=None, title_fontsize=None, text_fontsize=None, axis_label_fontsize=None, \
        title_fontweight='normal', text_fontweight='normal', axis_label_fontweight='normal', \
        fontweight='normal', continent_thickness=None, continent_color=None, viewer='display', \
        tspace_year=None, tspace_month=None, tspace_day=None, tspace_hour=None):
   """
    | setvars - set plotting variables
    |
    | file=None - output file name
    | title_fontsize=None - title fontsize, default=15
    | text_fontsize='normal' - text font size, default=11
    | axis_label_fontsize=None - axis label fontsize, default=11
    | title_fontweight='normal' - title fontweight
    | text_fontweight='normal' - text font weight
    | axis_label_fontweight='normal' - axis font weight
    | continent_thickness=None - default=1.5
    | continent_color=None - default='k' (black)
    | viewer='display' - use ImageMagick display program to display the pictures.  Set to 
    |                    'matplotlib' to use the built in matplotlib viewer.  display is 
    |                    non-blocking of the command prompt while the built in matplotlib viewer
    |                    is blocking.
    | 
    | tspace_year=None - time axis spacing in years
    | tspace_month=None - time axis spacing in months
    | tspace_day=None - time axis spacing in days
    | tspace_hour=None - time axis spacing in hours
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

   if all(val is None for val in [file, title_fontsize, text_fontsize, axis_label_fontsize, continent_thickness, \
       title_fontweight, text_fontweight, axis_label_fontweight, fontweight, \
       continent_color]):
      plotvars.file=None
      title_fontsize=15
      text_fontsize=11
      axis_label_fontsize=11
      title_fontweight='normal'
      text_fontweight='normal'
      axis_label_fontweight='normal',
      fontweight='normal'
      continent_thickness=None
      continent_color=None
      tspace_year=None
      tspace_month=None
      tspace_day=None
      tspace_hour=None

   plotvars.file=file
   plotvars.title_fontsize=title_fontsize
   plotvars.axis_label_fontsize=axis_label_fontsize
   plotvars.continent_thickness=continent_thickness
   plotvars.continent_color=continent_color
   plotvars.text_fontsize=text_fontsize
   plotvars.text_fontweight=text_fontweight
   plotvars.axis_label_fontweight=axis_label_fontweight
   plotvars.title_fontweight=title_fontweight
   plotvars.viewer=viewer
   plotvars.tspace_year=tspace_year
   plotvars.tspace_month=tspace_month
   plotvars.tspace_day=tspace_day
   plotvars.tspace_hour=tspace_hour



def rgrot(xin=None, yin=None, xpole=None, ypole=None):
   """
    | rgrot - rotate longitude and latitude points onto a rotated grid
    |
    | xin=xin - longitude locations
    | yin=yin - latitude locations
    | xpole=xpole - xpole in degrees
    | ypole=ypole - ypole in degrees
    | 
    |
    |
    |
    :Returns:
      x and y points on rotated grid 
    | 
    | 
    | 
    | 
    | 
    | 
   """




   #Check input parameters
   if any(val is None for val in [xin, yin, xpole, ypole]):
      errstr='\n\
             rgrot error\n\
             xin, yin, xpole, ypole all need to be passed to rgrot to generate \n\
             rotated output points\
             \n'
      raise  Warning(errstr)


   #Define output arrays.
   xout=np.zeros(np.size(xin))
   yout=np.zeros(np.size(yin))

   #Tolerance limit.
   tol=1.0E-6 


   #Scale xpole to range -180 to 180.
   xpole_orig=xpole
   if (xpole > 180.0):  xpole=xpole-360.0

   #Latitude of zero meridian.
   x_zero=xpole+180.0


   #Sine and cosine of latitude of eq pole
   if (ypole >= 0.0):
      sin_ypole=np.sin(ypole*np.pi/180.0)
      cos_ypole=np.cos(ypole*np.pi/180.0)
   else:
      sin_ypole=-np.sin(ypole*np.pi/180.0)
      cos_ypole=-np.cos(ypole*np.pi/180.0)



   #Transform to rotated grid.
   for ix in np.arange(np.size(xin)):

      #Scale longitude to range -180 to +180 degs
      xpt=xin[ix]-x_zero
      if (xpt > 180.0): xpt=xpt-360.0
      if (xpt <= -180.0): xpt=xpt+360.0

      #Convert latitude & longitude to radians
      xpt=xpt*np.pi/180.0
      ypt=yin[ix]*np.pi/180.0

      #Calculate latitude.
      arg=-cos_ypole*np.cos(xpt)*np.cos(ypt)+np.sin(ypt)*sin_ypole
      arg=min([arg,1.0])
      arg=max([arg,-1.0])
      ypt2=np.arcsin(arg)
      yout[ix]=ypt2*180.0/np.pi

      #Calculate longitude.
      t1=(np.cos(ypt)*np.cos(xpt)*sin_ypole+np.sin(ypt)*cos_ypole)
      t2=np.cos(ypt2)
      if (t2 < tol): 
         xpt2=0.0
      else:
         arg=t1/t2
         arg=min([arg,1.0])
         arg=max([arg,-1.0])
         xpt2=np.arccos(arg)*180.0/np.pi
         if (xpt >= 0):
            xpt2=abs(xpt2)
         else:
            xpt2=-1.0*abs(xpt2)


      #Scale longitude to range 0 to 360 degs
      #if (xpt2 >= 360.0): xpt2=xpt2-360.0
      #if (xpt2 < 0.0): xpt2=xpt2+360.0
      xout[ix]=xpt2



   #Reset xpole
   xpole=xpole_orig


   return (xout, yout)




def rgunrot(xin=None, yin=None, xpole=None, ypole=None):
   """
    | rgunrot - translate points from a rotated grid to longitude/latitude grid
    |
    | xin=xin - longitude locations
    | yin=yin - latitude locations
    | xpole=xpole - xpole in degrees
    | ypole=ypole - ypole in degrees
    | 
    |
    |
    |
    :Returns:
      x and y points on longitude and latitude grid 
    | 
    | 
    | 
    | 
    | 
    | 
   """   

   #Check input parameters
   if any(val is None for val in [xin, yin, xpole, ypole]):
      errstr='\n\
             rgrot error\n\
             xin, yin, xpole, ypole all need to be passed to rgrot to generate \n\
             rotated output points\
             \n'
      raise  Warning(errstr)

   #Define output arrays.
   xout=np.zeros(np.size(xin))
   yout=np.zeros(np.size(yin))

   #Tolerance limit.
   tol=1.0E-6 


   #Form x and y arrays to hold grid coordinates.
   nx=np.size(xin)
   ny=np.size(yin)
   x=np.zeros([ny, nx])
   y=np.zeros([ny, nx])
   for iy in np.arange(ny):
       x[iy,:]=xin
   for ix in np.arange(nx):
      y[:,ix]=yin

   xpole_orig=xpole
   if (xpole > 180.0):  xpole=xpole-360.0

   #Sine and cosine of latitude of eq pole
   if (ypole >= 0.0):
      sin_ypole=np.sin(ypole*np.pi/180.0)
      cos_ypole=np.cos(ypole*np.pi/180.0)
   else:
      sin_ypole=-np.sin(ypole*np.pi/180.0)
      cos_ypole=-np.cos(ypole*np.pi/180.0)

   #Scale to -180 to 180
   xx=x
   yy=y
   pts=np.where(xx > 180)
   xx[pts]=xx[pts]-360.0
   pts=np.where(xx < 180)
   xx[pts]=xx[pts]+360.0
   xx=np.pi*xx/180.0
   yy=np.pi*yy/180.0


   arg=cosypole*np.cos(xx)*np.cos(yy)+np.sin(yy)*sinypole
   pts=WHERE(arg > 1.0)
   arg[pts]=1.0
   pts=np.where(arg <= -1.0)
   arg[pts]=-1.0
   ay=np.asin(arg)
   y=180.0*ay/np.pi


   t1=np.cos(YY)*np.cos(XX)*sinypole-np.sin(YY)*cosypole
   t2=np.cos(ay)


   ax=np.zeros([ny,nx])

   pts=np.where(t2 < tol)
   ax[pts]=0.0

   pts=np.where(t2 >= tol)

   if (np.size(pts) > 0):
      arg=t1/T2
      pts2=np.where(arg > 1.0)
      arg[pts2]=1.0
      pts2=np.where(arg < -1.0)
      arg[pts2]=-1.0
      arg=180.0*np.acos(arg)/np.pi
      ax[pts]=arg
      pts3=np.where(xx >= 0.0)
      ax[pts3]=np.abs(ax[pts3])
      pts3=np.where(xx < 0.0)
      ax[pts3]=-1.0*np.abs(ax[pts3]) 
      ax=ax+x0
                                       

   x=ax

   #Reset xpole
   xpole=xpole_orig

   return(x,y)


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

   #Check input parameters
   if any(val is None for val in [xvec, yvec, lons, lats]):
      errstr='\n\
             vloc error\n\
             xvec, yvec, lons, lats all need to be passed to vloc to generate \n\
             a set of location points\
             \n'
      raise  Warning(errstr)


   xarr=np.zeros(np.size(lons))
   yarr=np.zeros(np.size(lats))


   #Convert longitudes to -180 to 180.
   for i in np.arange(np.size(xvec)):
      xvec[i]=((xvec[i] + 180) % 360)-180 
   for i in np.arange(np.size(lons)):
      lons[i]=((lons[i] + 180) % 360)-180 

   #Centre around 180 degrees longitude if needed.
   if (max(xvec) > 150):
      for i in np.arange(np.size(xvec)):
         xvec[i]=(xvec[i]+360.0) % 360.0
      pts=np.where(xvec < 0.0)
      xvec[pts]=xvec[pts]+360.0 
      for i in np.arange(np.size(lons)):
         lons[i]=(lons[i]+360.0) % 360.0
      pts=np.where(lons < 0.0)
      lons[pts]=lons[pts]+360.0  


   #Find position in array
   for i in np.arange(np.size(lons)):

      if ((lons[i] < min(xvec)) or (lons[i] > max(xvec))): 
         xpt=-1
      else:
         xpts=np.where(lons[i] >= xvec)
         xpt=np.nanmax(xpts)

      if ((lats[i] < min(yvec)) or (lats[i] > max(yvec))): 
         ypt=-1
      else:
         ypts=np.where(lats[i] >= yvec)
         ypt=np.nanmax(ypts)

 
      if (xpt >= 0):
         xarr[i]=xpt+(lons[i]-xvec[xpt])/(xvec[xpt+1]-xvec[xpt]) 
      else:
         xarr[i]=None


      if (ypt >= 0) and ypt <= np.size(yvec)-2:  
         yarr[i]=ypt+(lats[i]-yvec[ypt])/(yvec[ypt+1]-yvec[ypt]) 
      else:
         yarr[i]=None 

   return (xarr, yarr)





def rgaxes(xpole=None, ypole=None, xvec=None, yvec=None, spacing=10.0, degspacing=0.75, \
           continents=True, grid=True, labels=True):
   """
    | rgaxes - label rotated grid plots
    |
    | xpole=None - location of xpole in degrees
    | ypole=None - location of ypole in degrees
    | xvec=None - location of x grid points
    | yvec=None - location of y grid points
    | spacing=10.0 - spacing of the grid for longitude and latitude (degrees)
    | degspacing=0.75 - spacing of the points along the grid (degrees)
    | continents=True - draw continents
    | grid=True - draw grid
    | labels=True - draw axis labels
    |
    | 
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

   #Invert y array if going from north to south
   #Otherwise this gives nans for all output
   yvec_orig=yvec
   if (yvec[0] > yvec[np.size(yvec)-1]): yvec=yvec[::-1]


   #Extract map continents
   m=Basemap(projection='cyl', resolution=plotvars.resolution)
   
   clines=m.drawcoastlines(linewidth=0.0)
   paths=clines.get_paths()        
   npaths=len(paths)

   gset(xmin=0, xmax=np.size(xvec)-1, ymin=0, ymax=np.size(yvec)-1, user_gset=0)

   #Set continent thickness and color if not already set
   if plotvars.continent_thickness is None: continent_thickness=1.5
   if plotvars.continent_color is None: continent_color='k'

   #Draw continents
   if continents is True:
      for i in np.arange(npaths):
         p=paths[i]
         pvert=p.vertices
         lons=pvert[:,0]
         lats=pvert[:,1]

         xout, yout=rgrot(xin=pvert[:,0], yin=pvert[:,1], xpole=xpole, ypole=ypole)  
         xpts, ypts = vloc(lons=xout, lats=yout, xvec=xvec, yvec=yvec)
         plotvars.plot.plot(xpts,ypts,linewidth=continent_thickness, \
                            color=continent_color)



   #Draw grid lines
   if grid is True:
      lons=-180+np.arange(360/spacing+1)*spacing
      lats=-90+np.arange(180/spacing+1)*spacing
      #latmin=np.nanmin(xpts)
      #lonmin=np.nanmin(ypts)

      #Longitudes
      for lon in lons:
         ipts=179./degspacing
         lona=np.zeros(ipts)+lon
         lata=-90+np.arange(ipts-1)*degspacing
         xout, yout=rgrot(xin=lona, yin=lata, xpole=xpole, ypole=ypole)   
         xpts, ypts=vloc(lons=xout, lats=yout, xvec=xvec, yvec=yvec)
         plotvars.plot.plot(xpts,ypts, ':', linewidth=2, color='k')

         #if labels is True:
            #Label code here

      #Latitudes
      for lat in lats:
         ipts=359.0/degspacing
         lata=np.zeros(ipts)+lat
         lona=-180.0+np.arange(ipts-1)*degspacing
         xout, yout=rgrot(xin=lona, yin=lata, xpole=xpole, ypole=ypole)   
         xpts, ypts=vloc(lons=xout, lats=yout, xvec=xvec, yvec=yvec)
         plotvars.plot.plot(xpts,ypts, ':', linewidth=2, color='k')

         #if labels is True:
            #Label code here

      #;Plot lower axis labels if required.
      #IF ((ylab EQ 1) or (ylab EQ 3)) THEN BEGIN
      # pts=WHERE(xyloc(*,1) GE 0.0, count)
      # IF (count GE 1) THEN BEGIN
      #  ipt=MIN(pts)
      #  IF (xyloc(ipt,0) GE 0) THEN BEGIN
      #   y0=ymin-200
      #   x0=xmin+xyloc(ipt,0)/(xpts-1)*(xmax-xmin)
      #   GPLOT, X=[x0, x0], Y=[ymin, ymin-150], /DEVICE
      #   GPLOT, X=x0, Y=y0-50 , TEXT=SCROP(((lons(ix) + 180) MOD 360)-180), ALIGN=0.5, VALIGN=1.0, /DEVICE
      #  ENDIF
      # ENDIF
      #ENDIF


   yvec=yvec_orig
   


def lineplot(f=None, x=None, y=None, fill=True, lines=True, line_labels=True, title=None, \
             ptype=0, linestyle='-', linewidth=1.0, color='k', xlog=False, ylog=False, verbose=None, swap_xy=False,\
             marker=None, markersize=5.0, label=None, legend_location=None, xunits=None, yunits=None, xname=None,\
             yname=None, xticks=None, yticks=None, xticklabels=None, yticklabels=None):
    """
    | lineplot is the interface to line plotting in cf-plot. The minimum use is lineplot(f) 
    | f - CF data to make a line plot from 
    | x - x locations of data in f (only use this if f is a numpy array)
    | y - y locations of data in f (only use this if f is a numpy array)
    | linestyle='-' - line style
    | color='k - line color
    | linewidth=1.0 - line width
    | marker=None - marker for points along the line
    | markersize=5.0 - size of the marker
    | xlog=False - log x-axis
    | ylog=False - log y-axis
    | label=None - line label - label for line
    | legend_location=None - location of legend, 'upper right' for instance
    | verbose=None - change to 1 to get a verbose listing of what lineplot is doing
    |
    | The following parameters override any CF data defaults:
    | title=None - plot title
    | xunits=None - x units
    | yunits=None - y units
    | xname=None - x name
    | yname=None - y name
    | xticks=None - x ticks
    | xticklabels=None - x tick labels
    | yticks=None - y ticks
    | yticklabels - y tick labels
    """
    if verbose: print 'lineplot - making a line plot'

    ##################
    #Open a new plot is necessary
    ##################
    if plotvars.user_plot == 0: gopen(user_plot=0)


    ##################
    #Extract required data 
    #If a cf-python field
    ##################
    if f is not None:
        if isinstance(f[0], cf.Field):
            #Check if this is a cf.Fieldlist and reject if it is
            if len(f) > 1:
                errstr='\n cf_data_assign error - passed field is a cf.Fieldlist\n'
                errstr=errstr+'Please pass one field for contouring\n'
                errstr=errstr+'i.e. f[0]\n'
                raise  Warning(errstr) 

            #Extract data
            if verbose: print 'lineplot - CF field, extracting data'

            has_count=0
            for mydim in f.items():
                if np.size(np.squeeze(f.item(mydim).array)) > 1:
                    has_count=has_count+1
                    x=np.squeeze(f.item(mydim).array)
                    if xname is None: xname=cf_var_name(field=f, dim=mydim)
                    if xunits is None: xunits=str(getattr(f.item(mydim), 'Units', ''))
                    y=np.squeeze(f.array)
                    if yunits is None: 
                        if hasattr(f, 'Units'): yunits=str(f.Units)
                    if yname is None: 
                        if hasattr(f, 'id'): yname=f.id
                        if hasattr(f, 'ncvar'): yname=f.ncvar
                        if hasattr(f, 'short_name'): yname=f.short_name 
                        if hasattr(f, 'long_name'): yname=f.long_name 
                        if hasattr(f, 'standard_name'): yname=f.standard_name



            if has_count != 1:
                errstr='\n lineplot error - passed field is not suitable for plotting as a line\n'
                for mydim in f.items():
                    sn=getattr(f.item(mydim), 'standard_name', False)
                    ln=getattr(f.item(mydim), 'long_name', False)
                    if sn:
                        errstr=errstr+str(mydim)+','+str(sn)+','+str(f.item(mydim).size)+'\n'
                    else:
                        if ln: errstr=errstr+str(mydim)+','+str(ln)+','+str(f.item(mydim).size)+'\n'
                raise  Warning(errstr) 

    else:
        if verbose: print 'lineplot - not a CF field, using passed data'




    #Set data values
    if verbose: print 'lineplot - setting data values'
    xpts=np.squeeze(x)
    ypts=np.squeeze(y)
    minx=np.min(x)
    miny=np.min(y)
    maxx=np.max(x)
    maxy=np.max(y)

    #Use user set values if present
    if plotvars.xmin is not None:
        minx=plotvars.xmin
        miny=plotvars.ymin
        maxx=plotvars.xmax
        maxy=plotvars.ymax


    #Set x and y labelling
    if xname is None:
        xlabel=''
    else:
        xlabel=xname
    if yname is None:
        ylabel=''
    else:
        ylabel=yname
    if xunits is not None: xlabel=xlabel+' ('+supscr(xunits)+')'
    if yunits is not None: ylabel=ylabel+' ('+supscr(yunits)+')'    
    if xticks is None:
        if xlabel[0:3] == 'lon': xticks, xticklabels=mapaxis(minx, maxx, type=1)
        if xlabel[0:3] == 'lat': xticks, xticklabels=mapaxis(minx, maxx, type=2)
        if np.size(f.item('T').array) > 1: 
            xticks, xticklabels, xlabel=timeaxis(f.item('T'))
    else:
        if xticklabels is None: xticklabels=xticks
    if yticks is not None:
        if yticklabels is None: yticklabels=yticks

    #Z on y-axis
    ztype=None
    if xunits in ['mb', 'mbar', 'millibar', 'decibar', 'atmosphere', 'atm', 'pascal','Pa', 'hPa']:
        swap_xy=True
        ztype=1
    if xunits in ['meter', 'metre', 'm', 'kilometer', 'kilometre', 'km']:
        xtype=2

    if swap_xy is True:
        if verbose: print 'lineplot - swapping x and y'
        xpts=y
        ypts=x
        minx=np.min(y)
        miny=np.min(x)
        maxx=np.max(y)
        maxy=np.max(x)
        xlabel=yname+' ('+supscr(yunits)+')'
        ylabel=xname+' ('+supscr(xunits)+')'

    if ztype == 1:
        miny=np.max(ypts)
        maxy=np.min(ypts)

    if ztype == 2:
        if f.positive == 'down':
            miny=np.max(ypts)
            maxy=np.min(ypts)



    #Make graph
    if verbose: print 'lineplot - making graph'
    plotvars.plot.axis([minx, maxx, miny, maxy])
    plotvars.plot.tick_params(direction='out', which='both')
    plotvars.plot.set_xlabel(xlabel)
    plotvars.plot.set_ylabel(ylabel)
    rotation=0
    align='center'
    if np.size(f.item('T').array) > 1:
        if swap_xy is False:
            rotation=45
            align='right'

    if swap_xy is not True:
        if xticks is not None:
            plotvars.plot.set_xticks(xticks)
            plotvars.plot.set_xticklabels(xticklabels, rotation=rotation, horizontalalignment=align)
        if yticks is not None:
            plotvars.plot.set_yticks(yticks)
            plotvars.plot.set_yticklabels(yticklabels)
    else:
        if xticks is not None:
            plotvars.plot.set_yticks(xticks)
            plotvars.plot.set_yticklabels(xticklabels)
        if yticks is not None:
            plotvars.plot.set_xticks(xticks)
            plotvars.plot.set_xticklabels(xticklabels, rotation=rotation, ha=ha)

    plotvars.plot.plot(xpts, ypts, color=color, linestyle=linestyle, linewidth=linewidth, marker=marker,\
                       markersize=markersize, label=label)   


    #Time axes sometimes spill over the edge of the plot limits so
    #use tight_layout() to adjust these plots
    if np.size(f.item('T').array) > 1: plotvars.master_plot.tight_layout()

    #Add a legend if needed
    if legend_location is not None: plotvars.plot.legend(loc=legend_location)

    #Set title
    if title is not None: plotvars.plot.set_title(title,fontsize=plotvars.title_fontsize, \
                                                  fontweight=plotvars.title_fontweight)








    ##################
    #Save or view plot
    ##################
    if plotvars.user_plot == 0:       
        if verbose: print 'Saving or viewing plot'
        #gset(user_gset=0)
        gclose()



