.. _example15:

Example 15: Polar projection vector plot
----------------------------------------


.. code-block:: python
   :caption: Making a vector plot on a North Pole polar projection

    f = cf.read("cfplot_data/ggap.nc")

    u = f.select_by_identity("eastward_wind")[0]
    v = f.select_by_identity("northward_wind")[0]
    u = u.subspace(Z=500)
    v = v.subspace(Z=500)

    cfp.setvars(
        land_color="rosybrown",
        ocean_color="lightsteelblue",
        feature_zorder=2,
    )
    cfp.mapset(proj="npstere")

    cfp.gopen(columns=2)
    cfp.vect(
        u=u,
        v=v,
        key_length=25,
        scale=160,
        stride=6,
        title="Polar plot using data grid",
    )
    cfp.gpos(2)
    cfp.vect(
        u=u,
        v=v,
        pts=40,  # difference to other plot
        key_length=25,
        scale=160,
        stride=6,
        title="Polar plot with regular point distribution",
    )
    cfp.gclose()


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_15.png
