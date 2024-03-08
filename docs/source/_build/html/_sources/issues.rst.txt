cf-plot issues
**************

If you find a problem with cf-plot please email Sadie Bartholomew (sadie.bartholomew@ncas.ac.uk) with the following:

|   (i) the cf-python and cf-plot version numbers used:
|       print('cf-python version', cf.__version__)
|       print('cf-plot version', cfp.__version__)
|   (i) A short piece of code showing the problem
|   (iii) The data needed to make the plot


i.e. if you make a plot using:

::

   f=cf.read('cfplot_data/ggap.nc')[1]
   cfp.con(f.collapse('mean','longitude'))

Then use cf-python to write out the data used to make the plot and then send the data (newfile.nc) and plotting line to me.  

::

   f=cf.read('cfplot_data/ggap.nc')[1]
   g=f.collapse('mean','longitude')
   cf.write(g, 'newfile.nc')


Send the data (newfile.nc) and plotting lines as per below example to me:

::

   g=cf.read('newfile.nc')
   cfp.con(g)


If you are using arrays of data use numpy to write out the relevant data:

::

   np.save('lons.npy', lons)
   np.save('lats.npy', lats)
   np.save('field.npy', field)

|  
|  
|  




| 
| 
| 
| 
| 
| 
| 
| 
| 
| 
| 
| 



