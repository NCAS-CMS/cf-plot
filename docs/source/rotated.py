# example 1
import cf
import cfplot as cfp

f = cf.read("cfplot_data/rgp.nc")[0]
cfp.cscale("plasma")
cfp.con(f)


f.construct("dimensioncoordinate0").array

f.construct("dimensioncoordinate1").array


# example 2
import cf
import cfplot as cfp

f = cf.read("cfplot_data/rgp.nc")[0]
cfp.cscale("plasma")
cfp.mapset(proj="rotated")
cfp.con(f)


# example 3
import cf
import cfplot as cfp

f = cf.read("cfplot_data/20160601-05T0000Z_INCOMPASS_km4p4_uv_RH_500.nc")
cfp.mapset(50, 100, 5, 35)
cfp.levs(0, 90, 15, extend="neither")

cfp.gopen()
cfp.con(f[0], lines=False)
cfp.vect(u=f[1], v=f[2], stride=40, scale=5, key_length=10)
cfp.gclose()


# David's issue
import cf, cfplot as cfp

x = cf.read("aaaaoa.pmh8dec.pp")[0]
print(x)
cfp.con(x)


humidity = x[0]
rotated_pole = humidity.ref("rotated_latitude_longitude")
xpole = rotated_pole["grid_north_pole_longitude"]
ypole = rotated_pole["grid_north_pole_latitude"]

humidity


# Sam's issue
import cf, cfplot as cfp

sst = cf.read("nemo_ay652o_1m_19500901-19501001_grid-T.nc")[-8]
sst2 = sst.subspace(X=cf.wi(-30, 30), Y=cf.wi(20, 80))
cfp.mapset(-20, 20, 30, 70)
cfp.con(sst2)

# okay with
cfp.con(f=np.squeeze(sst2.array), x=sst2.item("X"), y=sst2.item("Y"), ptype=1)
