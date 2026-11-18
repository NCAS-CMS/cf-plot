.. _example30:

Example 30: Line plot with two x axes
-------------------------------------


.. code-block:: python
   :caption: Adding an extra x axis to a line plot

   fl = cf.read(f"cfplot_data/ggap.nc")

   f_u = fl.select_by_identity("eastward_wind")[0]
   f_t = fl.select_by_identity("air_temperature")[0]

   u = f_u.collapse("X: mean")
   # Use cf.isclose with an absolute tolerance corresponding to the final
   # decimal place we specify, so we can choose a certain value without having
   # to specify all digits in each (they are far from being round numbers).
   u1 = u.subspace(Y=cf.isclose(-61.1, atol=0.1))
   u2 = u.subspace(Y=cf.isclose(0.561, atol=0.001))

   t = f_t.collapse("X: mean")
   t1 = t.subspace(Y=cf.isclose(-61.1, atol=0.1))
   t2 = t.subspace(Y=cf.isclose(0.561, atol=0.001))

   cfp.gopen()
   cfp.gset(-30, 30, 1000, 0)
   cfp.lineplot(u1, color="r")
   cfp.lineplot(u2, color="r")
   cfp.gset(190, 300, 1000, 0, twiny=True)
   cfp.lineplot(t1, color="b")
   cfp.lineplot(t2, color="b")
   cfp.gclose()


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_30.png
