

import cf, cfplot as cfp
f=cf.read('data5.nc')
u=f.select('eastward_wind')
v=f.select('northward_wind')

g=f=cf.read('scicomp2/data1.nc')
ugrid=g.select('eastward_wind')
vgrid=g.select('northward_wind')


unew=ugrid.regrids(u)
vnew=vgrid.regrids(v)


u700=unew.subspace(Z=700)
v700=vnew.subspace(Z=700)

cfp.vect(u700, v700, key_length=10, scale=100)






f=cf.read('data8.nc')[6]
f.delprop('source')
f.delprop('history')
f.standard_name='eastward_wind' 
f.item('T').standard_name='time'
f.item('X').standard_name='longitude'
f.item('Y').standard_name='latitude'
f.item('Z').standard_name='pressure'




f=cf.read('data7.nc').select('eastward_wind')
f.delprop('source')
f.delprop('history')
f.standard_name='eastward_wind' 
f.item('T').standard_name='time'
f.item('X').standard_name='longitude'
f.item('Y').standard_name='latitude'
f.item('Z').standard_name='pressure'









import cf, cfplot as cfp
temp=cf.read("scicomp2/ens_*.nc")
temp_mean=temp.collapse('mean', 'realization')
temp_sd=temp.collapse('sd', 'realization')

cfp.gopen()
cfp.gset(xmin='5000-1-1', xmax='5201-1-1', ymin=275, ymax=284)
for r in temp.item('realization').array:
    cfp.lineplot(temp.subspace(realization=r), linewidth=0.1)

cfp.lineplot(temp_mean, color='red', linewidth=3, title='Global mean temperature ensembles with mean in red')
cfp.lineplot(temp_mean+temp_sd, color='blue', linewidth=3)
cfp.lineplot(temp_mean-temp_sd, color='blue', linewidth=3)

cfp.gclose()



import cf, cfplot as cfp
u_low=cf.read('/home/swsheaps/cfplot.src/cfplot/scicomp2/data5.nc')
u_high=cf.read('/home/swsheaps/cfplot.src/cfplot/scicomp2/data6.nc')
u_new=u_low.regrids(u_high)




import cf, cfplot as cfp
f=cf.read('scicomp2/data4.nc')
temp=f.subspace(time=cf.wi(cf.dt('1900-01-01'), cf.dt('1980-01-01')))
temp_annual=temp.collapse('T: mean', group=cf.Y())
temp_annual_global=temp_annual.collapse('area: mean')
temp_annual_global.Units -= 273.15

#cfp.lineplot(temp_annual_global, title='Global average annual temperature', color='blue')

x=temp_annual_global.item('T').array
y=temp_annual_global.array
cfp.lineplot(x=x,y=y)



import cf, cfplot as cfp
f=cf.read('/opt/graphics/cfplot_data/ggap.nc')[7]

cfp.cscale(cmap='scale1', ncols=10, white=[4,5])
cfp.levs(manual=[-20, -10, -5,  -1, 0, 1, 5, 10, 20], extend='both')

cfp.mapset(proj='npstere')
cfp.con(f.subspace(pressure=500))


x=temp_annual_global.item('T').array
y=temp_annual_global.array
cfp.lineplot(x=x,y=y)



Blockfill
---------

import cf, cfplot as cfp, numpy as np
cfp.setvars(viewer='matplotlib')

cfp.gopen(rows=2)
cfp.axes(xticklabels=[], yticklabels=[], xlabel=None, ylabel=None)

cfp.mapset(lonmin=80, lonmax=160, latmin=-20, latmax=20)
cfp.cscale('precip_11lev', ncols=9)
cfp.levs(min=0, max=16, step=2, extend='max') 


cfp.gpos(1)
s=cf.read('/net/elm/export/elm/data-05/xr840994/amip_pr/GPCP/AMIPlcd_JJA.nc')[0]
lsm=cf.read('/net/elm/export/elm/data-05/xr840994/mask/lsm_lcdamip.nc')[0]

s_new=s.where(lsm, cf.masked)

cfp.con(s_new, lines=1, title='(a) JJA GPCP Climatology')

cfp.gpos(2)
cfp.con(s_new, blockfill=1, lines=1, title='(b) JJA GPCP Climatology')

cfp.gclose()


import cf, cfplot as cfp, numpy as np
cfp.setvars(viewer='matplotlib')
f=cf.read('/opt/graphics/cfplot_data/ggap.nc')[7]
cfp.cscale('scale1')
cfp.levs(-40,40, 5)
cfp.gopen(rows=2)
cfp.con(f.collapse('mean','longitude'))
cfp.gpos(2)
cfp.con(f.collapse('mean','longitude'), lines=1, blockfill=1)
cfp.gclose()





import cf, cfplot as cfp
cfp.setvars(legend_text_size='40',legend_text_weight='bold')


f=cf.read('/opt/graphics/cfplot_data/ggap.nc')[7]
g=f.collapse('X: mean')
xticks=[-90,-75,-60,-45,-30,-15,0,15,30,45,60,75,90]
xticklabels=['90S','75S','60S','45S','30S','15S','0','15N','30N','45N','60N','75N','90N']
xpts=[-30, 30, 30, -30, -30]
ypts=[-8, -8, 5, 5, -8]

cfp.gset(xmin=-90, xmax=90, ymin=-10, ymax=50)
cfp.gopen()
cfp.lineplot(g.subspace(pressure=100), marker='o', color='blue',\
             title='Zonal mean zonal wind', label='100mb')
cfp.lineplot(g.subspace(pressure=200), marker='D', color='red',\
             label='200mb', xticks=xticks, xticklabels=xticklabels,\
             legend_location='upper right')
cfp.plotvars.plot.plot(xpts,ypts, linewidth=3.0, color='green')
cfp.plotvars.plot.text(35, -2, 'Region of interest', horizontalalignment='left')


cfp.gclose()











import cf, cfplot as cfp, numpy as np
f=cf.read('/opt/graphics/cfplot_data/ggap.nc')[8]
g=f.subspace(pressure=1000)
print 'min / max', np.min(g.array), np.max(g.array)
cfp.con(g)









min = -75
max = 35
step = 5
n = int((max - min)/step)
np.linspace(min, min + n*step, n + 1)










