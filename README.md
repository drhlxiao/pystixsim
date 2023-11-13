# STIX imager software simulator - pystixsim

The Spectrometer Telescope for Imaging X-rays (STIX) on Solar Orbiter is a hard X-ray imaging spectrometer covering the energy range from 4 to 150 keV. STIX observes hard X-ray bremsstrahlung emissions from solar flares and therefore provides diagnostics of the hottest ('10 MK) flare plasma while quantifying the location, spectrum, and energy content of flare-accelerated nonthermal electrons.

pystixsim is a simulator written in Python for the STIX imager that can simulate observed count patterns  for sources of different shapes. 
In the simulator, each grid window is represented by a set of polygons. 
When simulating a point source at a particular location, the polygons are projected onto the detector plane, 
allowing for the determination of the illuminated area on each pixel using boolean operations with the projected polygons.

For non-point X-ray sources, patterns can be synthesized  by weighting the  patterns of  point sources at different locations. 
## How it works
<a href="https://docs.google.com/presentation/d/12wVX86CBa87V-FSFBKRonBJIQk50MO23WgO1X3Y6ZDI/edit?usp=sharing">How it works </a>

## Examples:

https://github.com/drhlxiao/pystixsim/blob/main/examples/STIX_pattern_simulator.ipynb
## Contact
Please contact me (hualin.xiao(at)fhnw.ch) if you would like to use it. 


The simulator has been used for the following work:
* Image classification and reconstruction using machine learning <br>
  See the conference talk:  https://meetingorganizer.copernicus.org/EGU22/EGU22-6371.html <br>
  https://docs.google.com/presentation/d/1pHYuUKThdrTX-ZZFeHY_D0FCeF0csCIa4DpE0NtzkIU/edit?usp=sharing

* https://docs.google.com/presentation/d/16zWLs8cxUZdWyrgQD1FjuyoMptZYDzfGzjJaMdy24KQ/edit?usp=sharing
  
