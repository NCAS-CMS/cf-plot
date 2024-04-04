import cf, cfplot as cfp

f = cf.read("/opt/graphics/cfplot_data/tas_A1.nc")
cfp.levs(230, 300, 10, extend="neither")

cfp.con(f.subspace(time=15))
cfp.con(f.subspace(time=15), title="Block", blockfill=True, lines=True)


# Need to use cscale with the correct number of colours
cfp.con(f.subspace(time=15))
cfp.con(f.subspace(time=15), title="Block", blockfill=True, lines=True)


import cf, cfplot as cfp

saw = cf.read("veg.frac.n216e.orca025.2095.nc").collapse(
    "long_name:_pseudo_level_order: sum"
)

cfp.levs(manual=[0.9999, 1.0001])

cfp.con(saw, blockfill=1, lines=False, title="Block")
cfp.con(saw, lines=False, title="Contour")
