.. _download:
Download/Install
****************

The following notes refer to the Python 3 versions of cf-python and cf-plot which was released on 1st October 2019.

Is cf-plot already installed?
=============================

|    **Jasmin**
|    export PATH=/home/users/ajh/anaconda3/bin:$PATH
|    ln -s /home/users/ajh/cfplot_data ~


|    **Archer**
|    export PATH=/home/n02/n02/ajh/anaconda3/bin:$PATH
|    export QT_XCB_NO_XI2=true
|    ln -s /home/n02/n02/ajh/cfplot_data ~


|    **Reading University RACC cluster**
|    module load ncas_anaconda3
|    ln -s /share/apps/NCAS/cfplot_data ~


|    **Monsoon postproc server**
|    **to be installed** Contact andy.heaps@ncas.ac.uk for details.





To install cf-plot
==================

Linux and Mac
#############
To install cf-plot on your own Linux PC or Mac download and install miniconda. On the command line type:

::

   conda install -c ncas -c conda-forge cf-python cf-plot udunits2
   conda install -c conda-forge mpich esmpy


The first line installs cf-python and cf-plot.  The second installs esmpy, together with the netcdf-fortran and mpich requirements, which cf-python uses for regriding data.  Note that Matplotlib 3 was used in the development of cf-plot and it is advised to upgrade to this version if you are not using it already.  Using Matplotlib 2 can give different plot spacings and results such as missing contour plots.



Windows
#######
We have a small development team and Linux is our main working environment. Windows isn't an option for us at present given our target user base.  

If you have a Windows operating system there are a couple of options for running Linux:

1) Install the Microsoft Windows Subsystem for Linux (WSL).  Once this is working install cf-python and cf-plot as per the Linux instructions above.

2) Installing a Linux Virtual Machine is simple and works well.  Installation instructions and a Mint Linux Virtual Machine are available at http://gws-access.ceda.ac.uk/public/ncas_climate/ajh/data_analysis_tools/VM.  






Other install methods for Linux and Mac OSX
###########################################
Using pip:

::

   pip install cf-python
   pip install cf-plot

If you are upgrading the version of cf-python or cf-plot to the latest ones then add the --upgrade after the install above. A specific version can be installed using pip install cf-plot==3.0.20 for example.

Using GitHub:

::

   git clone git://github.com/NCAS-CMS/cf-plot.git
   (or possibly git clone https://github.com/NCAS-CMS/cf-plot.git)
   cd cf-plot
   python setup.py install


You will need to download and install `cf-python <https://cfpython.bitbucket.io>`_ to use cf-plot.  Other cf-plot dependencies are: Numpy, Scipy, Matplotlib, NetCDF4 and Cartopy.


Sample data sets
################

These are available in the cfplot_data directory which can be linked using:

|   Jasmin: **ln -s /home/users/ajh/cfplot_data ~**
|   Reading Academic Computing Cluster (RACC): **ln -s /share/apps/NCAS/cfplot_data ~**


If you are on a different server then download the `sample netCDF datasets <http://gws-access.ceda.ac.uk/public/ncas_climate/ajh/data_analysis_tools/cfplot_data.tar>`_


 
|
|
|
|
|
|
|
| 


