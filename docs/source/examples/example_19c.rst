.. _example19c:

Example 19c: Accommodating more than one colour bar
---------------------------------------------------


.. code-block:: python
   :caption: Using the approach to make a single figure with multiple plots
             on it to fit an extra colour bar

   fl = cf.read(f"{self.data_dir}/ggap.nc")
   u = fl.select_by_identity("eastward_wind")[0]
   v = fl.select_by_identity("northward_wind")[0]

   # Process fields to prepare for plotting
   u = u.subspace(pressure=500)
   v = v.subspace(pressure=500)
   u = u.anchor("X", -180)
   v = v.anchor("X", -180)

   # Calculate magnitude to pass to the streamplot
   magnitude = (u**2 + v**2) ** 0.5
   mag = magnitude.squeeze().data.array

   # NOTE WELL: must not use _configure_example_output("19c") here until
   # we set up a means to use setvars without resetting other config.,
   # else it resets the viewer so the actual plot doesn't (all) get
   # plotted on and associated with the test file to compare to.
   fname = str(TEST_GEN_DIR / "gen_fig_19c.png")
   cfp.setvars(
       file=fname,
       viewer="matplotlib",
       continent_thickness=0.75,
   )

   cfp.gopen(user_position=True)
   cfp.gpos()

   cfp.cscale("GreenYellow", ncols=20)
   levs2 = np.arange(-36, 40, 4)
   cfp.levs(levs2)

   # Place first colour bar, to be used for the next plot call (cfp.con)
   cfp.cbar(
       levs=levs2,
       position=[0.2, 0.1, 0.6, 0.02],
       title="Contour fill: eastward wind component magnitude",
   )
   cfp.con(u, lines=False, colorbar=False, zorder=0)

   cfp.cscale("viridis", ncols=8)
   levs1 = np.arange(-20, 50, 10)
   cfp.levs(levs1)

   # Place second colour bar, to be used for the next plot call (cfp.stream)
   cfp.cbar(
       levs=levs1,
       position=[0.01, 0.2, 0.02, 0.6],
       orientation="vertical",
       title="Stream lines: full wind magnitude",
   )
   cfp.stream(u=u, v=v, density=2, color=mag, zorder=3)

   cfp.gclose()


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_19c.png
