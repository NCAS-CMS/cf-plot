"""
Routines for making climate contour/vector plots using cf-python, matplotlib and basemap.
Andy Heaps NCAS-CMS September 2013.
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

import cf
from mpl_toolkits.basemap import Basemap, shiftgrid, addcyclic
import matplotlib
import matplotlib.pyplot as plot
import numpy as np
from subprocess import call
import sys
import os
from scipy import interpolate
import time



#####################################
#plotvars - global plotting variables
#####################################

#Default colour scale - blue to red with 18 colours
cscale1=['#0a3278', '#0f4ba5', '#1e6ec8', '#3ca0f0', '#50b4fa', '#82d2ff', '#a0f0ff', \
         '#c8faff', '#e6ffff', '#fffadc', '#ffe878', '#ffc03c', '#ffa000', '#ff6000', \
         '#ff3200', '#e11400', '#c00000', '#a50000']



plotvars=pvars(lonmin=-180, lonmax=180, latmin=-90, latmax=90, proj='cyl', \
               resolution='c', plot_type=1, boundinglat=0, lon_0=0, \
               levels=None, levels_min=None, levels_max=None, levels_step=None, \
               levels_extend='both', xmin=None, \
               xmax=None, ymin=None, ymax=None, xlog=None, ylog=None,\
               rows=1, columns=1, file='python', orientation='landscape', gtype='png',\
               user_plot=0, master_plot=None, plot=None, fontsize=None, cs=cscale1, \
               user_cs=0, user_levs=0)
       



def con(f=None, x=None, y=None, fill=True, lines=True, line_labels=True, title=None, \
        colorbar_title=None, colorbar=1, colorbar_label_skip=1, ptype=0, \
        negative_linestyle=None, blockfill=None, zero_thick=None, colorbar_shrink=None, \
        colorbar_orientation=None, image=True):
   """
    | con is the interface to contouring in cfplot. The minimum use is con(f) 
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
    | ptype=0 - plot type - not needed for cf fields.  1 = longitude-latitude,
    |           2 = latitude - height, 3 = no specific plot type
    | negative_linestyle=None - set to 1 to get dashed negative contours
    | zero_thick=None - add a thick zero contour line. Set to 3 for example.
    | blockfill=None - set to 1 for a blockfill plot
    | colbar_title=colbar_title - title for the colour bar
    | colorbar=1 - add a colour bar if a filled contour plot
    | colorbar_label_skip=1 - skip colour bar labels
    | colorbar_orientation=None - options are 'horizontal' and 'vertical'
    |                      The default for most plots is horizontal but
    |                      for polar stereographic plots this is vertical.
    | colorbar_shrink=None - value to shrink the colorbar by.  If the colorbar 
                             exceeds the plot area then values of 1.0, 0.55 or 0.5
                             may help it better fit the plot area.

    :Returns:
     None

   """ 



   #Extract required data for contouring
   #If a cf-python field
   if isinstance(f[0], cf.Field):
      field, x, y, ptype, colorbar_title, xlabel, ylabel=cf_data_assign(f, colorbar_title)
   else:
      field=f #field data passed in as f
      check_data(field, x, y)
      xlabel=''
      ylabel=''

   #Set contour line styles
   if negative_linestyle is None: matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
   else: matplotlib.rcParams['contour.negative_linestyle'] = negative_linestyle

   #Set contour lines off on block plots
   if blockfill == 1: 
      fill=False
      if lines is True: lines=False
      field_orig=field  
      x_orig=x
      y_orig=y   

      if (plotvars.proj == 'npstere' or plotvars.proj == 'spstere'):
         print ''
         print 'blockfill not supported for polar stereograpic plots'
         print ''
         return

   if fill == 0 and blockfill is None: colorbar=0

   #Revert to default colour scale if user_cs flag is set
   if plotvars.user_cs == 0:
      plotvars.cs=cscale1


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
               if colorbar_orientation == 'horizontal': colorbar_shrink=0.55
               if colorbar_orientation == 'vertical': colorbar_shrink=1.0
            if plotvars.orientation == 'portrait':
               if colorbar_orientation == 'horizontal': colorbar_shrink=1.0
               if colorbar_orientation == 'vertical': colorbar_shrink=0.5




   if (ptype != None): plotvars.plot_type=ptype
 
 
   #get contour levels
   if plotvars.user_levs == 1:
      #User defined
      clevs=plotvars.levels
      mult=0
      fmult=1
      if plotvars.user_cs == 0:
         is_zero=0
         col_zero=0
         for cval in clevs:
            if is_zero == 0: col_zero=col_zero+1   
            if cval == 0: is_zero=1

         if is_zero == 1:
            cscale('scale1', below=col_zero, above=np.size(clevs)-col_zero+1)
         else:
            cscale('cosam', ncols=np.size(clevs)+1)   

         plotvars.user_cs=0 #Revert to standard colour scale after plot

   else:
      #Automatic levels
      clevs, mult = gvals(dmin=np.min(field), dmax=np.max(field), tight=0)
      fmult=10**-mult

      #Adjust colour table
      if plotvars.user_cs == 0:
         is_zero=0
         col_zero=0
         for cval in clevs:
            if is_zero == 0: col_zero=col_zero+1   
            if cval == 0: is_zero=1

         if is_zero == 1:
            cscale('scale1', below=col_zero, above=np.size(clevs)-col_zero+1)
         else:
            cscale('cosam', ncols=np.size(clevs)+1)

         plotvars.user_cs=0 #Revert to standard colour scale after plot

   #Set colorbar labels
   if colorbar_label_skip > 1:
      colorbar_labels=clevs[np.arange(len(clevs)/colorbar_label_skip)*colorbar_label_skip]
   else: 
      colorbar_labels=clevs

   #Add mult to colorbar_title if used 
   if (colorbar_title == None): 
      colorbar_title=''
   else:
      if (mult != 0): colorbar_title=colorbar_title+' *10$^{'+str(mult)+'}$' 


   #Catch null titles and replace
   if (title == None): title=''
  



 
   ########## 
   # Map plot
   ##########
   if ptype == 1: 
  
      #Open a new plot is necessary
      if plotvars.user_plot == 0: gopen(user_plot=0)

      #Set up mapping
      lon_mid=plotvars.lonmin+(plotvars.lonmax-plotvars.lonmin)/2.0
      lat_mid=plotvars.latmin+(plotvars.latmax-plotvars.latmin)/2.0

      if plotvars.proj == 'cyl':
         mymap = Basemap(projection='cyl',llcrnrlon=plotvars.lonmin, urcrnrlon=plotvars.lonmax, \
                         llcrnrlat=plotvars.latmin, urcrnrlat=plotvars.latmax, \
                         lon_0=lon_mid, lat_0=lat_mid, resolution=plotvars.resolution)  
      else:	 
         if plotvars.proj == 'npstere':
            mymap = Basemap(projection='npstere', boundinglat=plotvars.boundinglat, \
                            lon_0=plotvars.lon_0, lat_0=90, resolution=plotvars.resolution)
         if plotvars.proj == 'spstere':
            mymap = Basemap(projection='spstere', boundinglat=plotvars.boundinglat, \
                            lon_0=plotvars.lon_0, lat_0=-90, resolution=plotvars.resolution)
   
      #Shift grid if needed
      if plotvars.lonmin < np.min(x): x=x-360
      if plotvars.lonmin > np.max(x): x=x+360

      field, x=shiftgrid(plotvars.lonmin, field, x)   
  

      #Add cyclic information if missing.
      lonrange=np.max(x)-np.min(x)
      if lonrange < 360:
         field, x = addcyclic(field, x)
         lonrange=np.max(x)-np.min(x)
   
   
      #Create the meshgrid
      lons, lats=mymap(*np.meshgrid(x, y))

      gset(xmin=plotvars.lonmin, xmax=plotvars.lonmax, ymin=plotvars.latmin, ymax=plotvars.latmax)

      #axes
      if plotvars.proj == 'cyl':
         lonticks,lonlabels=mapaxis(min=plotvars.lonmin, max=plotvars.lonmax, type=1)
         latticks,latlabels=mapaxis(min=plotvars.latmin, max=plotvars.latmax, type=2)
         axes(xticks=lonticks, xticklabels=lonlabels)
         axes(yticks=latticks, yticklabels=latlabels)
   
      if plotvars.proj == 'npstere' or plotvars.proj == 'spstere': 
         latstep=30
         if 90-abs(plotvars.boundinglat) <= 50: latstep=10
         mymap.drawparallels(np.arange(-90,120,latstep))
         mymap.drawmeridians(np.arange(0,420,60),labels=[1,1,1,1,1,1]) 


      #Filled contours
      if fill == True or blockfill == 1:
         #Get colour scale for use in contouring
         #If colour bar extensions are enabled then the colour map goes
         #from 1 to ncols-2.  The colours for the colour bar extensions are then 
         #changed on the colourbar and plot after the plot is made 
         cscale_ncols=np.size(plotvars.cs)
         colmap=cscale_get_map()
  
         #filled colour contours
         cfill = mymap.contourf(lons,lats,field*fmult,clevs,extend=plotvars.levels_extend,\
                 colors=colmap)

         #add colour scale extensions if required
         if (plotvars.levels_extend == 'both' or plotvars.levels_extend == 'min'):
            cfill.cmap.set_under(plotvars.cs[0])
         if (plotvars.levels_extend == 'both' or plotvars.levels_extend == 'max'):
            cfill.cmap.set_over(plotvars.cs[cscale_ncols-1])



      #Block fill
      if blockfill == 1:  
         if isinstance(f[0], cf.Field):  
            if f[0].coord('lon').isbounded:
               xpts=np.squeeze(f.coord('lon').bounds.array)[:,0]
               ypts=np.squeeze(f.coord('lat').bounds.array)[:,0]   
               bfill(f=field_orig*fmult, x=xpts, y=ypts, clevs=clevs, lonlat=1, bound=1)  
            else:
               bfill(f=field_orig*fmult, x=x_orig, y=y_orig, clevs=clevs, lonlat=1, bound=0)  


         else:
            bfill(f=field_orig*fmult, x=x_orig, y=y_orig, clevs=clevs, lonlat=1, bound=0)  



      #Contour lines and labels  
      if lines == True:
         cs = mymap.contour(lons,lats,field*fmult,clevs,colors='k')
         if line_labels == True:
            nd=ndecs(clevs)
            fmt='%d'
            if nd != 0: fmt='%1.'+str(nd)+'f'
            plotvars.plot.clabel(cs, fmt=fmt, colors = 'k', fontsize=plotvars.fontsize) 

         #Thick zero contour line   
         if zero_thick is not None:
            cs = mymap.contour(lons,lats,field*fmult,[1e-32, 0], colors='k', linewidths=zero_thick) 





      #Color bar
      if colorbar == 1:        
         pad=0.10
         if plotvars.rows >= 3: pad=0.15
         if plotvars.rows >= 5: pad=0.20 
         cbar=plotvars.master_plot.colorbar(cfill, orientation=colorbar_orientation, aspect=75, \
                                            pad=pad, ticks=colorbar_labels, drawedges=True, \
                                            shrink=colorbar_shrink)
         cbar.set_label(colorbar_title, fontsize=plotvars.fontsize)
         for t in cbar.ax.get_xticklabels(): t.set_fontsize(plotvars.fontsize)


      #axes
      if plotvars.proj == 'cyl':
         lonticks,lonlabels=mapaxis(min=plotvars.lonmin, max=plotvars.lonmax, type=1)
         latticks,latlabels=mapaxis(min=plotvars.latmin, max=plotvars.latmax, type=2)
         axes(xticks=lonticks, xticklabels=lonlabels)
         axes(yticks=latticks, yticklabels=latlabels)
   
      if plotvars.proj == 'npstere' or plotvars.proj == 'spstere': 
         latstep=30
         if 90-abs(plotvars.boundinglat) <= 50: latstep=10
         mymap.drawparallels(np.arange(-90,120,latstep))
         mymap.drawmeridians(np.arange(0,420,60),labels=[1,1,1,1,1,1]) 


      #Coastlines and title
      mymap.drawcoastlines(linewidth=1.0)
      plotvars.plot.set_title(title, y=1.03, fontsize=plotvars.fontsize)


  
   ########################
   # Latitude-pressure plot
   ########################
   if ptype == 2:

      if plotvars.user_plot == 0: gopen(user_plot=0)

      #Set plot limits
      if [plotvars.xmin, plotvars.xmax, plotvars.ymin, plotvars.ymax].count(None) == 4:
         #Program selected data plot limits
         xmin=np.min(x)
         if xmin < -80 and xmin >= -90: xmin=-90
         xmax=np.max(x)
         if xmax > 80 and xmax <= 90: xmax=90 
         ymin=np.min(y)
         ymax=np.max(y)
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

      ytype=0 #pressure or similar y axis
      if 'theta' in ylabel.split(' '): ytype=1

      #Set plot limits and draw axes
      if plotvars.ylog != 1:   
         if ytype == 1: 
            gset(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
            axes(xticks=gvals(dmin=xmin, dmax=xmax, tight=1, mystep=xstep)[0],\
                 yticks=gvals(dmin=ymin, dmax=ymax, tight=1, mystep=ystep)[0],\
                 xlabel=xlabel, ylabel=ylabel)
         else: 
            gset(xmin=xmin, xmax=xmax, ymin=ymax, ymax=ymin)
            axes(xticks=gvals(dmin=xmin, dmax=xmax, tight=1, mystep=xstep)[0],\
                 yticks=gvals(dmin=ymin, dmax=ymax, tight=1, mystep=ystep)[0],\
                 xlabel=xlabel, ylabel=ylabel)  

      #Log y axis 
      if plotvars.ylog == 1:
         gset(xmin=xmin, xmax=xmax, ymin=ymax, ymax=ymin, ylog=1)
         axes(xticks=gvals(dmin=xmin, dmax=xmax, tight=1, mystep=xstep)[0],\
              xlabel=xlabel, ylabel=ylabel)

      #Get colour scale for use in contouring
      #If colour bar extensions are enabled then the colour map goes
      #from 1 to ncols-2.  The colours for the colour bar extensions are then
      #changed on the colourbar and plot after the plot is made
      cscale_ncols=np.size(plotvars.cs)
      colmap=cscale_get_map()


      #Filled contours
      if fill == True or blockfill == 1:
         cfill=plotvars.plot.contourf(x,y,field*fmult,clevs, \
               extend=plotvars.levels_extend, colors=colmap)

         #add colour scale extensions if required
         if (plotvars.levels_extend == 'both' or plotvars.levels_extend == 'min'):
            cfill.cmap.set_under(plotvars.cs[0])
         if (plotvars.levels_extend == 'both' or plotvars.levels_extend == 'max'):
            cfill.cmap.set_over(plotvars.cs[cscale_ncols-1])
  
      #Block fill
      if blockfill == 1:   
         if isinstance(f[0], cf.Field):  
            if f[0].coord('lon').isbounded:
               xpts=np.squeeze(f.coord('lat').bounds.array)[:,0]
               ypts=np.squeeze(f.coord('pressure').bounds.array)[:,0]   
               bfill(f=field_orig*fmult, x=xpts, y=ypts, clevs=clevs, lonlat=0, bound=1)  
            else:
               bfill(f=field_orig*fmult, x=x_orig, y=y_orig, clevs=clevs, lonlat=0, bound=0)  

         else:
            bfill(f=field_orig*fmult, x=x_orig, y=y_orig, clevs=clevs, lonlat=0, bound=0)  
 


      #Contour lines and labels
      if lines == True: 
         cs=plotvars.plot.contour(x,y,field*fmult,clevs,colors='k')
         if line_labels == True:  
            nd=ndecs(clevs)
            fmt='%d'
            if nd != 0: fmt='%1.'+str(nd)+'f'
            plotvars.plot.clabel(cs, fmt=fmt, colors = 'k', fontsize=plotvars.fontsize) 

            #Thick zero contour line
            if zero_thick is not None:
               cs = plotvars.plot.contour(x,y,field*fmult,[1e-32, 0],colors='k', linewidths=zero_thick)
     
  

      #Colorbar
      if colorbar == 1:  

         pad=0.15
         if plotvars.rows >= 3: pad=0.25
         if plotvars.rows >= 5: pad=0.3
         cbar=plotvars.master_plot.colorbar(cfill, orientation=colorbar_orientation, aspect=75, \
                                            pad=pad, ticks=colorbar_labels, drawedges=True, \
                                            shrink=colorbar_shrink)
         cbar.set_label(colorbar_title, fontsize=plotvars.fontsize)
         for t in cbar.ax.get_xticklabels():
            t.set_fontsize(plotvars.fontsize)


      #Title
      plotvars.plot.set_title(title, y=1.03, fontsize=plotvars.fontsize)



 
   ############
   #Other plots
   ############
   if ptype == 0: 

      if plotvars.user_plot == 0: gopen(user_plot=0)

      #Work out axes if none are supplied
      if [plotvars.xmin, plotvars.xmax, plotvars.ymin, plotvars.ymax].count(None) > 0:
         xmin=0
         xmax=np.shape(field)[0]
         xstep=(xmax-xmin)/5
         ymin=0
         ymax=np.shape(field)[1]
         ystep=(ymax-ymin)/5  
   
      #Draw axes
      #plotvars.plot=plot
      #axes()
      #plot=plotvars.plot  

      #Get colour scale for use in contouring
      #If colour bar extensions are enabled then the colour map goes
      #from 1 to ncols-2.  The colours for the colour bar extensions are then
      #changed on the colourbar and plot after the plot is made
      cscale_ncols=np.size(plotvars.cs)
      colmap=cscale_get_map()


      #Filled contours
      if fill == True or blockfill == 1:
         cfill=plotvars.plot.contourf(x,y,field*fmult,clevs,extend=plotvars.levels_extend,\
               colors=colmap)

         #add colour scale extensions if required
         if (plotvars.levels_extend == 'both' or plotvars.levels_extend == 'min'):
             cfill.cmap.set_under(plotvars.cs[0])
         if (plotvars.levels_extend == 'both' or plotvars.levels_extend == 'max'):
             cfill.cmap.set_over(plotvars.cs[cscale_ncols-1])


      #Block fill
      if blockfill == 1:  
         bfill(f=field_orig*fmult, x=x_orig, y=y_orig, clevs=clevs, lonlat=0, bound=0)  
 

      #Contour lines and labels 
      if lines == True:
         cs=plotvars.plot.contour(x,y,field*fmult,clevs,colors='k')
         if line_labels == True:     
            nd=ndecs(clevs)
            fmt='%d'
            if nd != 0: fmt='%1.'+str(nd)+'f'
            plotvars.plot.clabel(cs, fmt=fmt, colors = 'k', fontsize=plotvars.fontsize) 
   
         #Thick zero contour line
         if zero_thick is not None:
            cs = plotvars.plot.contour(x,y,field*fmult,[1e-32, 0],colors='k', linewidths=zero_thick)


      #Colorbar
      if colorbar == 1:     

         pad=0.15
         if plotvars.rows >= 3: pad=0.25
         if plotvars.rows >= 5: pad=0.3
         cbar=plotvars.master_plot.colorbar(cfill, orientation=colorbar_orientation, aspect=75, \
                                            pad=pad, ticks=colorbar_labels, drawedges=True, \
                                            shrink=colorbar_shrink)
         cbar.set_label(colorbar_title, fontsize=plotvars.fontsize)
         for t in cbar.ax.get_xticklabels():
            t.set_fontsize(plotvars.fontsize)


      #Title
      plotvars.plot.set_title(title, y=1.03, fontsize=plotvars.fontsize)



   ##########
   #Save plot
   ##########

   if plotvars.user_plot == 0: gclose()
  




def mapset(lonmin=-180, lonmax=180, latmin=-90, latmax=90, proj='cyl', boundinglat=0,
           lon_0=0, resolution='c'):
   """
    | mapset sets the mapping parameters.

    | lonmin=lonmin - minimum longitude
    | lonmax=lonmax - maximum longitude
    | latmin=latmin - minimum latitude
    | latmax=latmax - maximum latitude
    | proj=proj - 'cyl' for cylindrical projection. 'npstere' or 'spstere' for northern 
    |      hemisphere or southern hemisphere polar stereographic projection
    | boundinglat=boundinglat - edge of the viewable latitudes in a stereographic plot
    | lon_0=lon_0 - centre of desired map domain in a stereographic plot
    | resolution=resolution - the map resolution - can be one of 'c' (crude), 'l' (low), 
    |      'i' (intermediate), 'h' (high), 'f' (full) or 'None'

    | The default map plotting projection is the cyclindrical equidistant projection from 
    | -180 to 180 in longitude and -90 to 90 in latitude. To change the map view in this 
    | projection to over the United Kingdom, for example, you would use
    | mapset(lonmin=-6, lonmax=3, latmin=50, latmax=60) or mapset(-6, 3, 50, 60).

    | The limits are -360 to 720 in longitude so to look at the equatorial Pacific you 
    | could use
    | mapset(lonmin=90, lonmax=300, latmin=-30, latmax=30)
    | or
    | mapset(lonmin=-270, lonmax=-60, latmin=-30, latmax=30)

    | The proj parameter for the present accepts just two values - 'npstere' and 'spstere' 
    | for northern hemisphere or southern hemisphere polar stereographic projections. In 
    | addition to these the boundinglat parameter sets the edge of the viewable latitudes
    | and lat_0 sets the centre of desired map domain.

    | Map settings are persistent until a new call to mapset is made. To reset to the default
    | map settings use mapset().

    :Returns:
     None
   """

   plotvars.lonmin=lonmin
   plotvars.lonmax=lonmax
   plotvars.latmin=latmin 
   plotvars.latmax=latmax
   plotvars.proj=proj
   plotvars.boundinglat=boundinglat 
   plotvars.lon_0=lon_0
   plotvars.resolution=resolution 
 

  

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

    | Use levs() To reset to undefined levels.

    :Returns:
     None

   """ 

   if min is None and max is None and step is None and manual is None:
      plotvars.levels=None
      plotvars.levels_min=None
      plotvars.levels_max=None
      plotvars.levels_step=None 
      plotvars.extend='both'
      plotvars.user_levs=0
      raise myerror(2*2)
      return
    
   if manual is not None:
      plotvars.levels=manual
      plotvars.levels_min=None
      plotvars.levels_max=None
      plotvars.levels_step=None
      plotvars.user_levs=1
   else:
      if [min,max,step].count(None) > 0:
         print 'min, max and step or manual need to be passed to levs to generate \
              a set of contour levels'
         return
      else:
         plotvars.levels_min=min
         plotvars.levels_max=max
         plotvars.levels_step=step
         plotvars.levels=np.arange(min, max+step, step)
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
    | axes is a function to specify axes plotting parameters. The xstep and ystep 
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
 
 
   if xlabel is not None: plotvars.plot.set_xlabel(xlabel, fontsize=plotvars.fontsize)
   if ylabel is not None: plotvars.plot.set_ylabel(ylabel, fontsize=plotvars.fontsize)

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


   #Set font size
   for label in plotvars.plot.xaxis.get_ticklabels():
      label.set_fontsize(plotvars.fontsize)
   for label in plotvars.plot.yaxis.get_ticklabels():
      label.set_fontsize(plotvars.fontsize)
       
   #Title
   if title is not None: plotvars.plot.set_title(title, y=1.03, fontsize=plotvars.fontsize)
    

def gset(xmin=None, xmax=None, ymin=None, ymax=None, xlog=None, ylog=None):
   """
    | Set plot limits for all non longitude-latitide plots. 
    | xmin, xmax, ymin, ymax are all needed to set the plot limits.  
    | Set xlog/ylog to 1 to get a log axis.
  
    | xmin=None - x minimum
    | xmax=None - x maximum
    | ymin=None - y minimum
    | ymax=None - y maximum
    | xlog=None - log x
    | ylog=None - log y


    :Returns:
     None

    | 
    | 
    | 
    | 

   """

   plotvars.xlog=xlog
   plotvars.ylog=ylog
 
   if [xmin,xmax,ymin,ymax].count(None) == 4:
      plotvars.xmin=None
      plotvars.xmax=None
      plotvars.ymin=None
      plotvars.ymax=None
      plotvars.xlog=None
      plotvars.ylog=None
      return

   if [xmin,xmax,ymin,ymax].count(None) > 0:
      print 'xmin, xmax, ymin, ymax all need to be passed to gset to set the plot limits'
      return
  
   plotvars.xmin=xmin
   plotvars.xmax=xmax
   plotvars.ymin=ymin
   plotvars.ymax=ymax
   plotvars.xlog=xlog
   plotvars.ylog=ylog 

   #Set plot limits
   if plotvars.plot is not None:
      plotvars.plot.axis([plotvars.xmin, plotvars.xmax, plotvars.ymin, plotvars.ymax])
      if plotvars.xlog == 1: plotvars.plot.set_yscale('log')
      if plotvars.ylog == 1: plotvars.plot.set_yscale('log')  


  

def gopen(rows=1, columns=1, user_plot=1, file='python', \
          orientation='landscape', gtype='png', \
          fontsize=None):
   """
    | gopen is used to open a graphic file.  

    | rows=1 - number of plot rows on the page
    | columns=1 - number of plot columns on the page
    | user_plot=1 - internal plot variable - do not use.
    | file='python' - default file name
    | orientation='landscape' - orientation - also takes 'portrait'
    | gtype='png' - default graphics type
    | fontsize=None - font size - default is 11 for a single plot

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
   plotvars.type=gtype
   plotvars.user_plot=user_plot

   if orientation != 'landscape':
      if orientation != 'portrait':
         print ''
         print 'Error - orientation incorrectly set'
         print 'Input value was ', orientation
         print 'Valid options are portrait or landscape'
         print ''
         return

   #Set master plot size
   if orientation == 'landscape': plotvars.master_plot=plot.figure(figsize=(11.7, 8.3))
   else: plotvars.master_plot=plot.figure(figsize=(8.3, 11.7))
 
   #Set margins
   plotvars.master_plot.subplots_adjust(left=0.12, right=0.92, top=0.92, bottom=0.08)
  
   #Set fontsize
   if fontsize is None:
      if rows*columns == 1: plotvars.fontsize=11
      else: plotvars.fontsize=8
   else: plotvars.fontsize=fontsize

   #Set initial subplot
   #if user_plot == 0:
   gpos(pos=1)

   #Change tick length for plots > 2x2
   if (columns > 2 or rows > 2):
      matplotlib.rcParams['xtick.major.size'] = 2
      matplotlib.rcParams['ytick.major.size'] = 2

 

def gclose(view=True):
   """
    | gclose saves a graphics file.  The default is to view the file as well
    | using the ImageMagick display command.  Use view=0 to turn this off.
  
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
   plotvars.user_plot=0

   file=plotvars.file
   type=1
   if file[-3:] == '.ps': type=2
   if file[-4:] == '.eps': type=2
   if file[-4:] == '.png': type=3

   if type == 1: file=file+'.'+plotvars.gtype

   plotvars.master_plot.savefig(file, papertype='a4',\
                                orientation=plotvars.orientation)
 
   if view is True:
      if (type == 2): call(["display", "-rotate", "90", file])
      else: call(["display", file])




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
      print ''
      print 'Error - pos out of range:'
      print 'range = 1 - ', plotvars.rows*plotvars.columns
      print 'input pos was', pos
      print ''
      return


   plotvars.plot=plotvars.master_plot.add_subplot(plotvars.rows, plotvars.columns, pos)
   plotvars.plot.tick_params(which='both', direction='out')


  

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

   if [mb, km].count(None) == 0:
      print 'pcon must have mb or km input'
      return
 
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

   if [text].count(None) == 1:
      print 'supscr must have text input'
      return

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
 
   return tform




def gvals(dmin=None, dmax=None, tight=0, mystep=None): 
   """
    | gvals - work out a sensible set of values between two limits
    | This is an internal routine used for contour levels and axis 
    | labelling and is not used by the user.

    | dmin=None - minimum
    | dmax=None - maximum
    | tight=0 - return values tight to input min and max
    | mystep=None - use this step
    | 
    | 
    | 
    | 
    |
    | 
    | 
   """

   if [dmin, dmax].count(None) > 0:
      print 'gvals must have dmin and dmax input'
      return


   mult=0 #field multiplyer

   #return user selected levels
   if [plotvars.levels_min, plotvars.levels_max,\
       plotvars.levels_step].count(None) == 0:
      vals=np.arange(plotvars.levels_min, plotvars.levels_max\
           +plotvars.levels_step, plotvars.levels_step)
      return vals, mult
 
   #Generate reasonable step 
   step=(dmax-dmin)/16.0
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
   vals=(int(dmin)/step)*step
   while (np.max(vals)+step) <= dmax:
      vals=np.append(vals, np.max(vals)+step)

   #Remove upper and lower limits if tight=0 - i.e. a contour plot
   if tight == 0 and np.size(vals) > 1:
      if np.max(vals) >= dmax: vals=vals[0:-1]
      if np.min(vals) <= dmin: vals=vals[1:]

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
   while (np.max(vals)+step) <= dmax:
      vals=np.append(vals, float("%.2f" %(np.max(vals)+step)))

   if tight == 0:
      if np.max(vals) >= dmax: vals=vals[0:-1]
      if np.min(vals) <= dmin: vals=vals[1:]

   return vals, mult



def cf_data_assign(f=None, colorbar_title=None):
   """
    | Check cf input data is okay and return data for contour plot.
    | This is an internal routine not used by the user.
    | f=None - input cf field
    | colorbar_title=None - input colour bar title

    :Returns:
     | f - data for contouring
     | x - x coordinates of data (optional)
     | y - y coordinates of data (optional)
     | ptype - plot type
     | colorbar_title - colour bar title
     | xlabel - xlabel for plot
     | ylabel - y labels for plot
   """


   #Check if this is a cf.Fieldlist
   if isinstance(f, cf.FieldList):
      print ''
      print 'Error - this is a cf.Fieldlist'
      print 'Please pass one field for contouring'
      print 'i.e. f[0]'
      print ''
      return

   #Find out axis names and check input data has the correct dimensions
   naxes=0
   data_dims=0
   axes_names=[]
   axes_size=[]
   axes_keys=[]
   for key, value in f.domain.iteritems():
     axes_names.append(value.ncvar)
     axes_size=np.append(axes_size, value.size)
     axes_keys.append(key)
     if (axes_size[naxes] > 1): data_dims=data_dims+1
     naxes=naxes+1



   #Check input data has the correct dimensions
   if (data_dims > 2):
      print ''
      print 'Error - data has too many dimensions'
      for i in np.arange(naxes):
         print axes_names[i], int(axes_size[i])
      print ''
      return
   
 
   #Default to nothing for height and time
   height=None 
   time=None 
   xlabel=''
   ylabel=''
 
   lons=np.squeeze(f.coord('lon').array)
   lats=np.squeeze(f.coord('lat').array)
   if 'theta' in axes_names: height=np.squeeze(f.coord('theta').array)
   if 'p' in axes_names: height=np.squeeze(f.coord('pressure').array)
   time=np.squeeze(f.coord('time').array)
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
      xunits=str(f.domain['dim2'].Units)
      yunits=str(f.domain['dim1'].Units)
      if (xunits == 'degrees_north' or  xunits == 'degrees_south'): xunits='degrees'
      xlabel=axes_names[axes_keys.index('dim2')] + ' (' + xunits + ')'
      ylabel=axes_names[axes_keys.index('dim1')] + ' (' + yunits + ')'

   if (np.size(lons) > 1 and np.size(time) > 1):
      ptype=3
      x=lons
      y=time

   if np.size(lats) > 1 and np.size(time) > 1:
      x=lats
      y=time 
      xlabel='Latitude'
      ylabel='Time'  


   if (np.size(lats) > 1 and np.size(time) > 1):ptype=4 


   if (colorbar_title == None):   
      if hasattr(f, 'name'): colorbar_title=f.name
      if hasattr(f, 'standard_name'): colorbar_title=f.standard_name
      if hasattr(f, 'long_name'): colorbar_title=f.long_name 
      if hasattr(f, 'Units'): colorbar_title=colorbar_title+'('+supscr(str(f.Units))+')'
    
   return(field, x, y, ptype, colorbar_title, xlabel, ylabel)



def check_data(field=None, x=None, y=None):
   """
    | check_data - check user input contour data is correct.
    | This is an internal routine and is not used by the user.

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

   args = True

   if np.size(field) == 1:
      if field == None:
         err='con error - a field for contouring must be passed with the f= flag'
         args = False   
  
   if np.size(x) == 1:
      if x == None:
         err='con error - x coordinates must be passed with the x= flag'
         args = False

   if np.size(y) == 1:
      if y == None:
         err='con error - y coordinates must be passed with the y= flag'
         args = False
  
   if args == False:
      print ''
      print err
      print ''
      return
  
  
   #Check input dimensions look okay.
   if np.ndim(field) != 2: args = False 
   if np.ndim(x) != 1: args = False  
   if np.ndim(y) != 1: args = False 
   if np.ndim(field) == 2:
      if np.size(x) != np.shape(field)[1]: args = False  
      if np.size(y) != np.shape(field)[0]: args = False  
   
  
   if args is False:
      print ''
      print 'Input arguments incorrectly shaped:'
      print 'x has shape:', np.shape(x)
      print 'y has shape:', np.shape(y)
      print 'field has shape:', np.shape(field)
      print 'Expected x=xpts, y=ypts, field=(xpts,ypts)'
      print ''
      return;




def cscale(cmap=None, ncols=None, white=None, below=None, above=None):
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
      plotvars.user_cs=0
   else:
      plotvars.user_cs=1

   import distutils.sysconfig as sysconfig
   file = sysconfig.get_python_lib()+'/cfplot/colourmaps/'+cmap+'.rgb'
   if os.path.isfile(file) is False:
      if os.path.isfile(cmap) is False:
         print 'Colour scale not found:'
         print 'File ', file, 'doesn\'t exist'
         print 'File ', cmap, 'doesn\'t exist'
         print ''
         return
      else:
         file=cmap

   #Read in rgb values and convert to hex
   f = open(file, 'r')
   lines = f.read()
   lines = lines.splitlines()
   r = []
   g=[]
   b=[]
   hex=[]
   for line in lines:
       vals = line.split()
       r.append(int(vals[0]))
       g.append(int(vals[1]))
       b.append(int(vals[2]))



   #Interpolate to a new number of colours if requested
   if ncols != None:
      x=np.arange(np.size(r))
      xnew=((np.size(r)-1)/float(ncols-1))* np.arange(ncols)
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
   | 
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




class myerror(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)


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
    |  
    | 
    | 
    |  
   """


   #Assign f to field as this may be modified in lat-lon plots
   field=f
 
   #Add in extra levels for colour bar extensions if present.
   levs=clevs.astype(float)
   if (plotvars.levels_extend == 'min' or plotvars.levels_extend == 'both'):
      levs=np.insert(levs,0, -1e30)
   if (plotvars.levels_extend == 'max' or plotvars.levels_extend == 'both'):
      levs=np.append(levs, 1e30)



   if bound == 1:
      xpts=x
      ypts=y


   if bound == 0:
      #Find x box boundaries
      xpts=x[0]-(x[1]-x[0])/2.0
      for ix in np.arange(np.size(x)-1): 
         xpts=np.append(xpts, x[ix]+(x[ix+1]-x[ix])/2.0)
      #xpts=np.append(xpts, x[ix+1]+(x[ix+1]-x[ix])/2.0) 


      #Find y box boundaries
      ypts=y[0]-(y[1]-y[0])/2.0
      for iy in np.arange(np.size(y)-1): 
         ypts=np.append(ypts, y[iy]+(y[iy+1]-y[iy])/2.0)
      ypts=np.append(ypts, y[iy+1]+(y[iy+1]-y[iy])/2.0) 



   #Shift lon grid if needed
   if lonlat == 1:
      if plotvars.lonmin < np.min(xpts): xpts=xpts-360
      if plotvars.lonmin > np.max(xpts): xpts=xpts+360

      #Add cyclic information if missing.
      lonrange=np.max(xpts)-np.min(xpts)
      if lonrange < 360:
         field, xpts = addcyclic(field, xpts)

      field, xpts=shiftgrid(plotvars.lonmin, field, xpts) 



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

   











