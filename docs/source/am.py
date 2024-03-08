
import cf, cfplot as cfp
import numpy as np
from netCDF4 import Dataset as NetCDFFile

NJ=108;
NI=168;
NT=10;
#print('read in data')
wl=NetCDFFile('/home/swsheaps/cfplot.src/cfplot/wanglinho_clim_glosea_testhighvals.nc');
wl_time=wl.variables['t'][:];
wl_index=wl.variables['precip'][:,0,:,:];
wl_lat=wl.variables['latitude'][:];
wl_lon=wl.variables['longitude'][:];

index_startdates=np.zeros((NJ,NI));
for j in range(0,NJ):
  for i in range(0,NI):
    index_startdates[j,i]=np.argmax(wl_index[:,j,i] > 5.0);
      

index_startdates[index_startdates==0.0]=np.nan
#print(index_startdates_mean)

index_startdates_plusoffset=index_startdates+26

#cfp.setvars(file='wang_linho_onset_glosea_fromclim_untiljul.png')
#cfp.axes(xticks=np.arange(40,200,20),yticks=np.arange(-10,60,10))

cfp.gopen(rows=2)
cfp.cscale('scale1', ncols=12, white=0)
cfp.setvars(viewer='')
cfp.levs(min=24, max=35, step=1, extend='max')
cfp.mapset(50,180, -10, 50)
cfp.con(f=index_startdates_plusoffset, x=wl_lon, y=wl_lat, lines=False, ptype=1);
cfp.gpos(2)
index_startdates_plusoffset=index_startdates_plusoffset-1
cfp.con(f=index_startdates_plusoffset, x=wl_lon, y=wl_lat, lines=False, ptype=1, blockfill=1);
cfp.gclose()




