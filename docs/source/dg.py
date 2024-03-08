
# Good
import cf
import cfplot as cfp
f=cf.read('cfplot_data/rgp.nc')[0]
cfp.cscale('plasma')
cfp.con(f)


# Good
import cf
import cfplot as cfp
f=cf.read('cfplot_data/rgp.nc')[0]
cfp.cscale('plasma')
cfp.mapset(proj='rotated')
cfp.con(f)




# Wrong region for plot  -179.9999 to 179.9999
# check that the grid lons and lats are correct in con routine
import cf, cfplot as cfp, numpy as np

f=cf.read('um_u-ba050_20140910T0000Z_Iceland_ukv_a_pf024.pp_extract.nc')[0]
cfp.con(f)



#This works though
f=cf.read('um_u-ba050_20140910T0000Z_Iceland_ukv_a_pf024.pp_extract.nc')[0]
data=np.squeeze(f.array)
lons=f.item('aux4').array
lats=f.item('aux3').array
cfp.con(f=data, x=lons, y=lats, lines=False, ptype=1)



# Looks okay

import cf, cfplot as cfp, numpy as np
cfp.mapset(proj='rotated')

f=cf.read('um_u-ba050_20140910T0000Z_Iceland_ukv_a_pf024.pp_extract.nc')[0]
cfp.con(f, lines=False)





# Looks okay
import cf
import cfplot as cfp

f=cf.read('cfplot_data/20160601-05T0000Z_INCOMPASS_km4p4_uv_RH_500.nc')
cfp.vect(u=f[1], v=f[2], stride=40, key_length=10)



import cf
import cfplot as cfp
f=cf.read('cfplot_data/20160601-05T0000Z_INCOMPASS_km4p4_uv_RH_500.nc')

cfp.mapset(50, 100, 5, 35)
cfp.levs(0, 90, 15, extend='neither')

cfp.gopen()
cfp.con(f[0], lines=False)
cfp.vect(u=f[1], v=f[2], stride=40, key_length=10)
cfp.gclose()







