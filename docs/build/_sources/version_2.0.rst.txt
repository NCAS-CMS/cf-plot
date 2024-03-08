.. _version_2.0:
version 2.0 changes
*******************

Code base changes.


1. Pep8 compliance
==================

The cf-plot code has been made pep8 compliant using the pep8 online checker http://pep8online.com and the Python autopep8 program.  After running the code through autopep8 --in-place --aggressive cfplot.py the code was then run through the online checker and manually changed where needed.  The code is now much easier to read and the logic easier to follow.

 ::

   Done


2. Regression testing
=====================

Regression code has been added so that new releases are more robust.  The gallery plots are compared to a series of previous plots using python md5 checksums.  If tany plots are different the plots are passed through the Imagemagick compare routine and the differences displayed on the screen.

 ::

   Done


3. Merge all X,Y,T vs Z contour code
====================================

The three X,Y,T vs Z contour code sections were merged together to reduce code sprawl.

 ::

   Done


