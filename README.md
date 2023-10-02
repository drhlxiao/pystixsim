# STIX imager software simulator - stixsim
The Spectrometer Telescope for Imaging X-rays (STIX) on Solar Orbiter is a hard X-ray imaging spectrometer covering the energy range from 4 to 150 keV. STIX observes hard X-ray bremsstrahlung emissions from solar flares and therefore provides diagnostics of the hottest ('10 MK) flare plasma while quantifying the location, spectrum, and energy content of flare-accelerated nonthermal electrons.

pystixsim  is a STIX imager simulator written in Python. It allows for simulations of count patterns observed by STIX  for sources with any shapes. 
In the simulator, each grid window is described as a set of polygons. 
For a point source at a given location, the polygons are then projected onto the detector plane, therefore the illuminated area on each pixel can be determined using boolean operations of 
the projected polygons. 

<a href="https://docs.google.com/presentation/d/12wVX86CBa87V-FSFBKRonBJIQk50MO23WgO1X3Y6ZDI/edit?usp=sharing">How it works </a>


Please contact me (hualin.xiao(at)fhnw.ch) if you would like to use it. 


The simulator has been used for the following work:
* Image classification and reconstruction using machine learning <br>
  See the conference talk:  https://meetingorganizer.copernicus.org/EGU22/EGU22-6371.html <br>
  https://docs.google.com/presentation/d/1pHYuUKThdrTX-ZZFeHY_D0FCeF0csCIa4DpE0NtzkIU/edit?usp=sharing
