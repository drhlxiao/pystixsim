import sys
sys.path.append('.')
import math
import numpy as np


import matplotlib.pyplot as plt
from pystixsim import detector

from shapely.geometry import Polygon

#http://localhost:8890/notebooks/flare_coarse_locator_skylut_generator_for_web.ipynb#

from pystixsim import grid_parameters as sgp


class CFL(object):
    def __init__(self, x_arcsec=0, y_arcsec=0):
        self.det_idx = 8
        self.detector = detector.StixDetector
        self.det_pixel_polygons = self.detector.get_pixel_polygons()
        self.pixel_vertices = self.detector.get_pixel_vertices()

        self.top_shadow = None
        self.bottom_shadow = None
        self.x_arcsec, self.y_arcsec = x_arcsec, y_arcsec
        self.top_aperture_vtx = None
        self.bottom_aperture_vtx = None
        self.project(x_arcsec, y_arcsec)

    def project(self, x_arcsec=0, y_arcsec=0):
        """
            project cfl pattern to detector
            returns shadow area and open area ratio 
        """
        self.x_arcsec, self.y_arcsec = x_arcsec, y_arcsec

        x_ang_deg = x_arcsec / 3600.
        y_ang_deg = y_arcsec / 3600.
        y_ang = math.radians(x_ang_deg)  #rotated by 90 deg
        x_ang = math.radians(y_ang_deg)
        #rotation is needed because the mounting of stix on spacecraft
        new_path = {}
        area = {}
        sum_area = 0
        self.top_aperture_vtx = [(p[0] + sgp.r_front_detector * math.tan(x_ang),
                              p[1] + sgp.r_front_detector * math.tan(y_ang))
                             for p in sgp.cfl_aperture_coords['top']]
        #here it should be + because STIX is mounted on spacecraft
        self.bottom_aperture_vtx = [(p[0] + sgp.r_front_detector * math.tan(x_ang),
                                 p[1] + sgp.r_front_detector * math.tan(y_ang))
                                for p in sgp.cfl_aperture_coords['bottom']]
        self.bottom_shadow = Polygon(self.bottom_aperture_vtx)
        self.top_shadow = Polygon(self.top_aperture_vtx)

        for k, v in enumerate(self.detector.pixel_polygons):
            area[k] = self.top_shadow.intersection(
                v).area + self.bottom_shadow.intersection(v).area
        pattern = np.array([area[i] for i in range(12)])
        open_ratio = np.sum(pattern) / np.sum(self.detector.pixel_areas)
        return {
            'ratio': open_ratio,
            'pattern': pattern
            }

    create = project
    get_pattern= project

    def plot(self, fig=None, ax=None, ax2=None, draw_pattern=True, title=True):
        #draw: big or visibility
        if not ax or not fig:
            fig, (ax, ax2) = plt.subplots(1, 2, figsize=(9, 4))

        x_ang_deg = self.y_arcsec / 3600
        y_ang_deg = self.x_arcsec / 3600
        x_ang = math.radians(x_ang_deg)
        y_ang = math.radians(y_ang_deg)
        cfl_pro_paths = {}
        #intersec_area={}

        for name, path in sgp.cfl_aperture_coords.items():
            points = [(p[0] + sgp.r_front_detector * math.tan(x_ang),
                       p[1] + sgp.r_front_detector * math.tan(y_ang))
                      for p in path]
            # be caution to the sign
            cfl_pro_paths[name] = points

        for k, v in cfl_pro_paths.items():
            color = 'white'
            if k == 'outer':
                color = 'grey'
            detector.ply2path(v, ax, fc=color, ec=color,alpha=1)
        self.detector.plot(ax, show=False)
        ax.set_xlim([-25, 25])
        ax.set_ylim([-25, 25])
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        if title is True:
            ax.set_title(f'CFL sun_x={self.x_arcsec},sun_y={self.y_arcsec} sec')

        
        
        ax.set_aspect('equal')
        if ax2:
            res= self.project(self.x_arcsec, self.y_arcsec)
            ax2.plot(res['pattern'])
            ax2.set_xlabel('Pixel #')
            ax2.set_ylabel('Exposure area / mm2')
            ax2.set_title('Pattern')
        plt.show()


if __name__ == '__main__':
    x=0
    y=1200
    p = CFL(x, y)
    res = p.project(x, y)
    p.plot()
    print(res)
