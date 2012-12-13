"""
Module for making climate contour/vector plots using cf-python, matplotlib and basemap.
Andy Heaps NCAS-CMS November 2012.
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


##################################
#pvars - global plotting variables
##################################

p=pvars(lonmin=-180, lonmax=180, latmin=-90, latmax=90, proj='cyl', resolution='c',\
       boundinglat=0, lon_0=False, levels_min=False, levels_max=False, levels_step=False,\
       levels_extend='both',\
       xstep=False, ystep=False, xmin=False, xmax=False, ymin=False, ymax=False,\
       xlog=False, ylog=False, xlabel=False, ylabel=False,\
       xplots=False, yplots=False, file=False, portrait=False, gtype=False)
       
############
#con routine
############
def con(f=False, x=False, y=False, fill=True, lines=True, title=False, colbar_title=False):
 """
 Module for contouring data using Matplotlib and basemap.
 """
 from mpl_toolkits.basemap import Basemap, shiftgrid, addcyclic
 import matplotlib.pyplot as plt
 import numpy as np
 from subprocess import call
 import cf

 
 
 if title == False:
  title=''
  
 #Check all needed data is passed in.
 args = True
 
 #Check if this is a cf-python field.
 if isinstance(f, cf.Field):
  dims=f.space.dimensions['data']
  ndims= np.shape(dims)
  lons=f.coord('lon').array 
  lats=f.coord('lat').array
  height=f.coord('height').array
  time=f.coord('time').array
  if colbar_title == False:
   colbar_title=f.standard_name+' '+str(f.Units)
   
  
  f=f.array.squeeze()           
  if np.size(lons) > 1 and np.size(lats) > 1:
   x=lons
   y=lats
  if np.size(lats) > 1 and np.size(height) > 1:
   x=lats
   y=height   
  if np.size(lats) > 1 and np.size(time) > 1:
   x=lats
   y=time 
   xtitle='Latitude'
   ytitle='Time'
 
 if np.size(f) == 1:
  if f == False:
   print 'con error - a field for contouring must be passed with the f= flag'
   args = False   
  
 if np.size(x) == 1:
  if x == False:
   print 'con error - x coordinates must be passed with the x= flag'
   args = False

 if np.size(y) == 1:
  if y == False:
   print 'con error - y coordinates must be passed with the y= flag'
   args = False
  
 if args == False:
  return
  
 if colbar_title == False:
  colbar_title=''
  
#Check input dimensions look okay.
 if np.ndim(f) != 2:
  args = False 
 if np.ndim(x) != 1:
  args = False  
 if np.ndim(y) != 1:
  args = False  
 if np.ndim(f) == 2:
  if np.size(x) != np.shape(f)[1]:
   args = False  
  if np.size(y) != np.shape(f)[0]:
   args = False  
   
  
 if args == False:
  print ''
  print "Input arguments incorrectly shaped:"
  print "x has shape:", np.shape(x)
  print "y has shape:", np.shape(y)
  print "f has shape:", np.shape(f)
  print "Expected x=xpts, y=ypts, f=(xpts,ypts)"
  return;


#Check what plot type is required.
 xrange=abs(np.max(x)-np.min(x))
 yrange=abs(np.max(y)-np.min(y))

 
 ptype=0 #0=simple contour plot, 1=map plot, 2=lat-height plot.
 if xrange >= 340 and xrange <= 360:
  if yrange >= 160 and yrange <= 180:
   ptype=1
     
 if xrange >= 160 and xrange <= 180:
  if yrange >= 900 and yrange <= 1100:
   ptype=2
      

 #Work out the levels.
 if  p.levels_min != False:
  clevs=np.arange(p.levels_min, p.levels_max+p.levels_step, p.levels_step)
 else:
  dmin=np.min(f)
  dmax=np.max(f)
  drange=dmax-dmin
  haszero=0
  if dmin < 0:
   if dmax > 0:
    haszero=1
  step=int(drange/16)
  
  if step < 1:
   mult=0
   step=drange/16
   while step <= 1:
    step=step*10.
    mult=mult+1
    f=f*10.
   
   title=title+' *1e'+str(mult)
   dmin=np.min(f)
   dmax=np.max(f)
   drange=dmax-dmin
   step=int(drange/16)


  if haszero == 1:
   clevs=np.arange(-8*step,9*step,step)
  if haszero == 0:
   clevs=np.arange(int(dmin+step/2),int(dmin+step/2)+16*step,step)
 
 
 ##########################  
 # Longitude-latitude plot.
 ##########################
 if ptype == 1: 
 
  lon_mid=p.lonmin+(p.lonmax-p.lonmin)/2.0
  lat_mid=p.latmin+(p.latmax-p.latmin)/2.0
  if p.proj == 'cyl':
   mymap = Basemap(projection='cyl',llcrnrlon=p.lonmin, urcrnrlon=p.lonmax, llcrnrlat=p.latmin, urcrnrlat=p.latmax,
             lon_0=lon_mid, lat_0=lat_mid, resolution=p.resolution)  
  else:	 
   if p.proj == 'npstere':
    mymap = Basemap(projection='npstere', boundinglat=p.boundinglat, lon_0=p.lon_0, lat_0=90, resolution=p.resolution)
   if p.proj == 'spstere':
    mymap = Basemap(projection='spstere', boundinglat=p.boundinglat, lon_0=p.lon_0, lat_0=-90, resolution=p.resolution)
   
  if p.lonmin < np.min(x):
   x=x-360
  if p.lonmin > np.max(x):
   x=x+360
  
  f, x=shiftgrid(p.lonmin, f, x)   
  

  #Add cyclic information if missing.
  lonrange=np.max(x)-np.min(x)
  if lonrange < 360:
   f, x = addcyclic(f, x)
   lonrange=np.max(x)-np.min(x)
   
   
  #Create meshgrid.
  lons, lats=mymap(*np.meshgrid(x, y))
  
  plt.figure(figsize=(11, 8))
  plt.subplots_adjust(left=0.08, right=0.92, top=0.92, bottom=0.08)
  plt.rcParams['contour.negative_linestyle'] = 'solid'

  #contour and colour bar.
  if fill == True:
   cs = mymap.contourf(lons,lats,f,clevs,extend=p.levels_extend)
   cbar=plt.colorbar(orientation='horizontal', aspect=75, pad=0.08, ticks=clevs)
   cbar.set_label(colbar_title)
   
  if lines == True:
   cs = mymap.contour(lons,lats,f,clevs,colors='k')
   nd=ndecs(clevs)
   fmt='%d'
   if nd != 0:
    fmt='%1.'+str(nd)+'f'
   plt.clabel(cs, fmt=fmt, colors = 'k', fontsize=11) 
#    print 'in nd =  0 section'
#    plt.clabel(cs, fmt = '%d', colors = 'k', fontsize=11) 
#   else:
#    fmt='%1.'+str(nd)+'f'
#    plt.clabel(cs, fmt=fmt, colors = 'k', fontsize=11) 
   
 
  #axes
  plt.tick_params(direction='out')
  if p.proj == 'cyl':
   lonticks,lonlabels=mapaxis(min=p.lonmin, max=p.lonmax, type=1)
   latticks,latlabels=mapaxis(min=p.latmin, max=p.latmax, type=2)
   plt.xticks(lonticks,lonlabels)
   plt.yticks(latticks,latlabels)
  if p.proj == 'npstere' or p.proj == 'spstere':   
   latstep=30
   if 90-abs(p.boundinglat) <= 50:
    latstep=10
   mymap.drawparallels(np.arange(-90,120,latstep))
   mymap.drawmeridians(np.arange(0,420,60),labels=[1,1,1,1,1,1]) 
  
  mymap.drawcoastlines(linewidth=1.0)
  plt.title(title, y=1.03)

 
  
 ########################## 
 # Latitude-pressure plot.
 ##########################
 if ptype == 2:
  #for key, value in kwargs.iteritems():
   #setattr(plt, key, value)
   #getattr(plt, key)(value)


  plt.figure(figsize=(11, 8))
  plt.tick_params(direction='out', which='both')
  plt.axis([-90,90,1000,0.316])
  plt.xlabel('Latitude (degrees)')
  plt.ylabel('Pressure (mb)')
  plt.yscale('log')
  plt.xticks(np.arange(-90, 120, 30))
  plt.yticks([1000,100,10,1])

  plt.subplots_adjust(left=0.12, right=0.92, top=0.92, bottom=0.08)

  cs = plt.contourf(x,y,f,clevs,extend=leveld_extend)
  cb = plt.colorbar(orientation='horizontal', aspect=75, pad=0.12, ticks=clevs)
  cb.set_label('Temperature in degrees Celsius')
  cs = plt.contour(x,y,f,clevs,colors='k')
  plt.clabel(cs, fmt = '%d', colors = 'k', fontsize=11, inline_spacing=4)
  plt.title(title, y=1.03)


  
 ############
 #Other plots
 ############
 if ptype == 0: 
  print 'in plot'
  plt.figure(figsize=(11, 8))
  plt.tick_params(direction='out', which='both')
  
  xmin=p.xmin
  xmax=p.xmax
  ymin=p.ymin
  ymax=p.ymax
  xstep=p.xstep
  ystep=p.ystep
  if p.xlabel != False:
   plt.xlabel(p.xlabel)
  if p.ylabel != False:
   plt.ylabel(p.ylabel)
  if xmin is False and xmax is False and ymin is False and ymax is False:
   xmin=0
   xmax=np.shape(f)[0]
   xstep=(xmax-xmin)/5
   ymin=0
   ymax=np.shape(f)[1]
   ystep=(ymax-ymin)/5  
   
  plt.axis([xmin, xmax, ymin, ymax])
  if p.xlog is True:
   plt.xscale('log')
  if p.ylog is True:
   plt.yscale('log')      
  plt.xticks(np.arange(xmin, xmax+xstep, xstep))
  plt.yticks(np.arange(ymin, ymax+ystep, ystep))

  plt.subplots_adjust(left=0.12, right=0.92, top=0.92, bottom=0.08)

  cs = plt.contourf(x, y, f, clevs,extend=p.levels_extend)
  cb = plt.colorbar(orientation='horizontal', aspect=75, pad=0.12, ticks=clevs)
  cb.set_label(colbar_title)
  cs = plt.contour(x,y,f,clevs,colors='k')
  plt.clabel(cs, fmt = '%d', colors = 'k', fontsize=11, inline_spacing=4)
  plt.title(title, y=1.03)



 #############
 #Save picture
 #############
 #plt.savefig('python.ps', format='ps', papertype='a4', orientation='landscape')
 plt.savefig('python.png', format='png', papertype='a4', orientation='landscape')
 #call(["display", "-rotate", "90", "python.png"])
 call(["display", "python.png"])



############
#mapset routine
############
def mapset(lonmin=False, lonmax=False, latmin=False, latmax=False, proj=False, boundinglat=False,
        lon_0=False, resolution=False):
 import numpy as np
 if lonmin is False:
  p.lonmin=-180
 else:
  p.lonmin=lonmin
  
 if lonmax is False:
  p.lonmax=180
 else:
  p.lonmax=lonmax

 if latmin is False:
  p.latmin=-90
 else:
  p.latmin=latmin
  
 if latmax is False:
  p.latmax=90
 else:
  p.latmax=latmax
  
 if proj is False:
  p.proj='cyl'
 else:
  p.proj=proj
   
 if boundinglat is False:
  p.boundinglat=0
 else:
  p.boundinglat=boundinglat

 if lon_0 is False:
  p.lon_0=0
 else:
  p.lon_0=lon_0
  
 if resolution is False:
  p.resolution='c'
 else:
  p.resolution=resolution 
  
      
############
#levs routine
############
def levs(min=False, max=False, step=False, extend='both'):
 import numpy as np
 if min is False and max is False and step is False:
  p.levels_min=False
  p.levels_max=False
  p.levels_step=False
  p.levels_extend='both'
  return
    
 if [min,max,step].count(False) > 0:
  print 'min, max and step need to be passed to levs to generate a set of levels'
  return
  
 p.levels_min=min
 p.levels_max=max
 p.levels_step=step
 p.levels_extend=extend


########################################
#mapaxis routine - tickmarks and labels
########################################
def mapaxis(min=min, max=max, type=type):
  import numpy as np
  if type == 1:
   lonmin=min
   lonmax=max
   lonrange=lonmax-lonmin
   lonstep=60
   if lonrange <= 180:
    lonstep=30
   if lonrange <= 90:
    lonstep=10  
   if lonrange <= 30:
    lonstep=5
   if lonrange <= 10:
    lonstep=2
   if lonrange <= 5:
    lonstep=1      
   if p.xstep is not False:
    lonstep=p.xstep
     
   lons=np.arange(-720, 720+lonstep, lonstep)
   lonticks=[]
   for lon in lons:
    if lon >= lonmin and lon <= lonmax:
     lonticks.append(lon)
     
   lonlabels=[]
   for lon in lonticks:
    lon2=np.mod(lon + 180, 360) - 180
    if lon2 < 0 and lon2 > -180:
     lonlabels.append(str(abs(lon2))+'W')
    if lon2 > 0 and lon2 < 180:
     lonlabels.append(str(lon2)+'E')
    if lon2 == 0:
     lonlabels.append('0')
    if lon2 == -180 or lon2 == 180:
     lonlabels.append('180')
          
   return(lonticks, lonlabels) 
    
  if type == 2:
   latmin=min
   latmax=max
   latrange=latmax-latmin
   latstep=30
   if latrange <= 90:
    latstep=10  
   if latrange <= 30:
    latstep=5   
   if latrange <= 10:
    latstep=2
   if latrange <= 5:
    latstep=1  
   if p.ystep is not False:
    latstep=p.ystep
    
   lats=np.arange(-90, 90+latstep, latstep)
   latticks=[]
   for lat in lats:
    if lat >= latmin and lat <= latmax:
     latticks.append(lat)   


   latlabels=[]
   for lat in latticks:
    if lat < 0:
     latlabels.append(str(abs(lat))+'S')
    if lat > 0:
     latlabels.append(str(lat)+'N')
    if lat == 0:
     latlabels.append('0')
     
   return(latticks, latlabels) 



##########################################################
#ndecs - find maximum number of decimal places in an array
##########################################################
def ndecs(data=False):
 import numpy as np
 maxdecs=0
 for i in range(len(data)):
  number=data[i]
  a=str(number).split('.')  
  if np.size(a) == 2:
   number_decs=len(a[1])
   if number_decs > maxdecs:
    maxdecs=number_decs
  
 return maxdecs



#############
#axes routine
#############
def axes(xstep=False, ystep=False, xlog=False, ylog=False, xlabel=False, ylabel=False):
	 
 #for var in ['xstep', 'ystep', 'xlog', 'ylog', 'xlabel', 'ylabel']:
 #  print 'var is ', var
 #return
   
 if xstep is False:
  p.xstep=False
 else:
  p.xstep=xstep
  
 if ystep is False:
  p.ystep=False
 else:
  p.ystep=ystep  
  
 if xlog is False:
  p.xlog=False
 else:
  p.xlog=xlog  
  
 if ylog is False:
  p.ylog=False
 else:
  p.ylog=ylog     
  
 if xlabel is False:
  p.xlabel=False 
 else:
  p.xlabel=xlabel
  
 if ylabel is False:
  p.ylabel=False
 else:
  p.ylabel=ylabel  
  
    
  
###################################
#gopen - select graphics properties
###################################
def gopen(xplots=False, yplots=False, file=False, portrait=False, gtype=False):
 if xplots is False:
  p.xplots=1
 else:
  p.xplots=xplots
  
 if yplots is False:
  p.yplots=1
 else:
  p.yplots=yplots
 
 if file is False:
  p.file=False
 else:
  p.file=file

 if portrait is False:
  p.portrait=False
 else:
  p.portrait='portrait'
 
 if gtype is False:
  p.gtype='ps'
 else:
  p.gtype=gtype
  


   
   
