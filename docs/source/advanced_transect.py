

import cf
import cfplot as cfp
import numpy as np
import cartopy.crs as ccrs
f=cf.read('cfplot_data/ggap.nc')[1]
g=f.subspace(pressure=1000) # g is a 2D eastward wind field at 500mb


# Extract out the lons, lats and data
lons=g.item('X').array
lats=g.item('Y').array
data=np.squeeze(g.array)


# Flip the lats upside down so they start at -89.14152 and go to 89.14152
# Flip the data as well to match the new latitudes
lats = lats[::-1]
data = np.flipud(data)


# Generate a set of lons and lats to interpolate to
# Here we are making a set of points at 1 degree east and from -87 to 87
# The interpolation points need to be inside the lons and lats of the original data
lons_interp=np.arange(179)
lats_interp=np.arange(179)*0.5-89


# Interpolate the data to the new grid
data_interp=cfp.regrid(f=data, x=lons, y=lats, xnew=lons_interp, ynew=lats_interp)


# Finally let's visually compare our transect data with the original contour field
cfp.gopen(user_position=True)
cfp.mapset(0, 180, -90, 0)
cfp.gpos(xmin=0.25,xmax=0.75, ymin=0.5, ymax=1)
cfp.con(g, lines=False)
cfp.plotvars.mymap.plot(lons_interp, lats_interp , linewidth=2.0,
                        color='g', transform=ccrs.PlateCarree())
cfp.gpos(xmin=0.25,xmax=0.75, ymin=0.1, ymax=0.4)
cfp.lineplot(y=data_interp, x=lons_interp, title='Interpolated transect',
             xticks=np.arange(7)*30, xticklabels=['0', '30E', '60E', '90E', '120E', '150E', '180E'],
             yticks=np.arange(10)*2-8,
             xlabel='longitude', ylabel='eastward wind (ms-1)')
cfp.gclose()



