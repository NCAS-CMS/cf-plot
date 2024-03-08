***********************************************
Python, cf-python and cf-plot version 3 changes
***********************************************


----------------
Python 3 changes
----------------

The headline change that everyone will see is with the print function now requiring brackets

|    **print 'output is ', output**    <--- Python 2
|    **print('output is ', output)**    <--- Python 3


Integer arithmetic has changed and now requires // rather than /:

|    **3/2 = 1**   <--- Python 2
|    **3/2 = 1.5**    <--- Python 3
|    **3//2 = 1**    <--- Python 3


Use range rather than xrange for iterable loops:

|    **for i in xrange(10):**   <--- Python 2
|    **for i in range(10):**   <--- Python 3


Unicode has changed.

See `The key differences between Python 2.7.x and Python 3.x with examples <https://sebastianraschka.com/Articles/2014_python_2_3_key_diff.html>`_  for more details.





-------------------
cf-python 3 changes
-------------------

To see what is in a cf field in cf-python 3 use g.construct instead of g.item.

For example, to see what levels are available in the temperature data use:

|    **g.construct('longitude').array** - uses the standard_name attribute if it exists
|    **g.construct('long_name=longitude').array** - uses the long_name attribute(in this case the long_name is also longitude)
|    **g.construct('X').array** - uses the field X axis

For more details see `differences between cf-python version 2 and version 3 <https://ncas-cms.github.io/cf-python/2_to_3_changes.html>`_

Mac OSX is now supported.




-----------------
cf-plot 3 changes
-----------------

cf-plot 3 now uses matplotlib 3 which might cause some subtle plot differences from cf-plot 2.  The colorbar is now a routine that can be called independently of a colour plot and the plot relationship to the colour bar may be subtly different because of this.

Mac OSX is now supported.


--------------------
Regridding unchanged
--------------------

The regridding interface and backend use of esmpy is unchanged.





