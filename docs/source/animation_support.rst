.. _intro:

*****************
Animation Support
*****************

Animation support in cf-plot is TODO FLEDGLING STATE



Contour Animation Titles
------------------------

``cfp.con()`` supports animation-aware title updates via:

- ``animation=True``
- ``animation_axis="auto"`` (or one of ``"T"``, ``"Z"``, ``"Y"``, ``"X"``)
- ``animation_title_template="{title} [{frame}]"`` (optional)

With ``animation_axis="auto"``, axis inference is based on ``ptype``:

- for ``ptype != 0``, choose a singleton axis not used by that ``ptype``;
- for ``ptype == 0``, fallback preference is singleton ``T``, then ``Z``, then ``Y``, then ``X``.

Example:

.. code-block:: python

    cfp.con(
        f,
        animation=True,
        reuse_map_background=True,
        animation_axis="auto",
        animation_title_template="{title} [{frame}]",
        title="Air temperature",
    )
