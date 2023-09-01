# STIX imager software simulator  stixsim
The Spectrometer Telescope for Imaging X-rays (STIX) on Solar Orbiter is a hard X-ray imaging spectrometer covering the energy range from 4 to 150 keV. STIX observes hard X-ray bremsstrahlung emissions from solar flares and therefore provides diagnostics of the hottest ('10 MK) flare plasma while quantifying the location, spectrum, and energy content of flare-accelerated nonthermal electrons.

stixsim  is a STIX imager simulator written in Python. It allows for the simulation of patterns observed by Stix from any random source shapes. 
In this simulator, each grid is described as a set of polygons. These polygons are then projected onto the detector plane, 
and the illuminated area on each pixel is determined using boolean operations with the shadows of the front and rear grids.

How it works: 
https://docs.google.com/presentation/d/12wVX86CBa87V-FSFBKRonBJIQk50MO23WgO1X3Y6ZDI/edit?usp=sharing


Please contact me (hualin.xiao(at)fhnw.ch) if you are interested in using it. 


The simulator has been used for the following work:
* Image classification and reconstruction using machine learning <br>
  See the conference talk:  https://meetingorganizer.copernicus.org/EGU22/EGU22-6371.html <br>
  https://docs.google.com/presentation/d/1pHYuUKThdrTX-ZZFeHY_D0FCeF0csCIa4DpE0NtzkIU/edit?usp=sharing
