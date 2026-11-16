.. _example18:

Example 18: Polar stipple plot
------------------------------


.. code-block:: python
   :caption: A stipple plot in the North Pole polar stereographic projection.

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]
    g = f[0, :, :]  # first time value subspace, same as shorthand f[0]

    cfp.gopen()

    cfp.cscale("WhiteBlue")
    cfp.mapset(proj="npstere")
    cfp.con(
        g,
        lines=False,
        title=(
            "Northern polar temperature distribution with cold-region "
            "(<-20 degC) stippling"
        ),
    )

    # Highlight particularly cold regions (below <-20 degC)
    cfp.stipple(
        f=g,
        min=g.min().datum(),
        max=253.15,  # i.e. 20 degrees Celsius
        size=20,
        color="red",
        marker="x",
        edgecolors="red",
    )

    cfp.gclose()


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_18.png
