









import cf
import numpy as np
import cfplot as cfp
f=cf.read("test.nc")
cfp.gopen()
cfp.con(f[-1],colorbar=False)
cfp.cbar(levs=np.array([0.5,1.5,2.5,3.5]),position=[0.2, 0.1, 0.6, 0.02],title='',labels=['a','b','c'])
cfp.gclose()




import cf
import cfplot as cfp
f=cf.read('cfplot_data/tas_A1.nc')[0]
cfp.levs(230, 260, 10)
cfp.con(f.subspace(time=15))



cfp.con(f.subspace(time=15), colorbar_labels=['1', '2', '3', '4'])







import cf
import numpy as np
import cfplot as cfp
f=cf.read("test.nc")
cfp.gopen()
cfp.con(f[-1],colorbar=False)
cfp.levs(manual=[0.5,1.5,2.5,3.5])
# cfp.cbar(levs=np.array([0.5,1.5,2.5,3.5]), orientation='vertical',title='',labels=['a','b','c', 'd'])

cfp.cbar(orientation='horizontal',title='',labels=['a','b', 'c'], mid=True, extend='neither')
cfp.gclose()



# Sadie's plot - wrong colorbar spacing
import cf, cfplot as cfp
i=cf.read('chess_landfrac.nc')[0]
cfp.con(i)

cfp.con(f=i.array, x=i.dim('X').array, y=i.dim('Y').array, blockfill=True)


# wrong colorbar label spacing
import cf
import cfplot as cfp
f=cf.read('cfplot_data/tas_A1.nc')[0]
cfp.con(f.subspace(time=15), lines=False, colorbar_label_skip=2)


# northern hemisphere lcc
import cf
import cfplot as cfp
f=cf.read('cfplot_data/tas_A1.nc')[0]
cfp.mapset(proj='lcc', lonmin=-50, lonmax=50, latmin=20, latmax=85)
cfp.con(f.subspace(time=15))

# southern hemisphere lcc
import cf
import cfplot as cfp
f=cf.read('cfplot_data/tas_A1.nc')[0]
cfp.mapset(proj='lcc', lonmin=-50, lonmax=50, latmin=-80, latmax=-10)
cfp.con(f.subspace(time=15))


import matplotlib.pyplot as plt
import cartopy.crs as ccrs
lonmin=0
lonmax=90
latmin=-80
latmax=-10
lon_0 = lonmin + (lonmax - lonmin)/2.0
lat_0 = latmin + (latmax - latmin)/2.0
print('lon_0 is ', lon_0, 'lat_0 is', lat_0)

proj=ccrs.LambertConformal(central_longitude=lon_0, central_latitude=lat_0, cutoff=40)
ax = plt.axes(projection = proj)
ax.set_extent((lonmin,lonmax, latmin,latmax), crs = ccrs.PlateCarree())



proj=ccrs.LambertConformal(central_longitude=lon_0, central_latitude=lat_0, cutoff=40, standard_parallels=[-33, -45])
ax = plt.axes(projection = proj)
ax.set_extent((lonmin,lonmax, latmin,latmax), crs = ccrs.PlateCarree())





import cf, cfplot as cfp
f=cf.read('cr.nc')[0]
cfp.con(f)




