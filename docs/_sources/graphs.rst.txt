.. _graphs:

Graph plots: line and scatter
*****************************

To make a basic line plot with optional markers, use :func:`cfplot.lineplot`,
as in Example 27 below.

.. include:: examples/example_27.rst


Note other valid markers are:

|    '.' 	point
|    ',' 	pixel
|    'o' 	circle
|    'v' 	triangle_down
|    '^' 	triangle_up
|    '<' 	triangle_left
|    '>' 	triangle_right
|    '1' 	tri_down
|    '2' 	tri_up
|    '3' 	tri_left
|    '4' 	tri_right
|    '8' 	octagon
|    's' 	square
|    'p' 	pentagon
|    '*' 	star
|    'h' 	hexagon1
|    'H' 	hexagon2
|    '+' 	plus
|    'x' 	x
|    'D' 	diamond
|    'd' 	thin_diamond


To make a basic scatter plot without lines, you can use
:func:`cfplot.lineplot` and set ``lines=False`` with a `marker` value specified,
or you can use the :func:`cfplot.scatter` which calls :func:`cfplot.lineplot`
with ``line=False`` and ``marker='o'`` pre-set for you (where you can
override the latter but not the former), as in Example 27b below.

.. include:: examples/example_27b.rst


| When making a multiple line plot:
| a) Set the axis limits if required with cfp.gset before plotting the lines.
|    Using cfp.gset after the last line has been plotted may give unexpected
|    axis limits and / or labelling.  This is a feature of matplotlib.
| b) The last call to lineplot is the one that any of the above
|    axis overrides should be placed in.
| c) All calls to lineplot with the label attribute will appear in the legend.

.. include:: examples/example_28.rst


The cfp.plotvars.plot object contains the matplotlib plot and will accept
normal Matplotlib plotting commands. As an example of this the following
code within a :func:`cfplot.gopen()` and :func:`cfplot.gclose()` construct
will make a legend that is independent of any previously made lines and
attached labels.


|    import matplotlib.lines as mlines
|    green_line = mlines.Line2D([], [], color='green',  label='green')
|    black_line = mlines.Line2D([], [], color='black', ls='--' ,  label='black dashed')
|    cfp.plotvars.plot.legend(handles=[green_line, black_line])

Valid locations for the legend_location keyword are:

|	'right'
|	'center left'
|	'upper right'
|	'lower right'
|	'best'
|	'center'
|	'lower left'
|	'center right'
|	'upper left'
|	'upper center'
|	'lower center'

When making a call to lineplot the following parameters override any
predefined CF defaults:

| title=None - plot title
| xunits=None - x units
| yunits=None - y units
| xname=None - x name
| yname=None - y name
| xticks=None - x ticks
| xticklabels=None - x tick labels
| yticks=None - y ticks
| yticklabels - y tick labels


.. include:: examples/example_29.rst

In this example we subset a time data series of global temperature, area
mean the data, convert to Celsius and plot a linegraph.

When using gset to set the limits on the plotting axes and a time axis
pass time strings to give the limits i.e.
``cfp.gset(xmin='1980-1-1', xmax='1990-1-1', ymin=285, ymax=295)``

The correct date format is ``YYYY-MM-DD`` or ``YYYY-MM-DD HH:MM:SS``.
Anything else will give unexpected results.


.. include:: examples/example_30.rst

In this example we plot two x-axes, one with zonal mean zonal wind data
and one with temperature data. The option for a twin x-axis is
``twiny=True``. This is a matplotlib
keyword which has been adopted within the cf-plot code.
