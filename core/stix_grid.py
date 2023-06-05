import math
import numpy as np
import sys
sys.path.append('.')

import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

from core import grid_parameters as sgp


def deg2rad(x):
    return x * math.pi / 180


def arcsec2rad(x):
    return deg2rad(x / 3600.)


def plot_polygons(points, ax, fc='none', ec='black', alpha=1, lw=1):
    if isinstance(points, np.ndarray):
        points = points.tolist()
    if not points:
        return
    codes = [Path.MOVETO
             ] + [Path.LINETO] * (len(points) - 2) + [Path.CLOSEPOLY]
    path = Path(points, codes)
    patch = patches.PathPatch(path, fc=fc, ec=ec, alpha=alpha, lw=lw)
    ax.add_patch(patch)


class StixGrid(object):
    pitch_key = {'front': 'FrontPitch', 'rear': 'RearPitch'}
    orient_key = {'front': 'FrontOrient', 'rear': 'RearOrient'}
    phase_key = {'front': 'FrontPhase', 'rear': 'RearPhase'}
    slit_key = {
        'nominal': {
            'front': 'SlitWidth',
            'rear': 'SlitWidth'
        },
        'real': {
            'front': 'FrontSlitWidth',
            'rear': 'FrontSlitWidth'
        }
    }
    debug = False

    grid_parameters = {'nominal': sgp.nominal, 'real': sgp.real}
    grid_data = grid_parameters['nominal']
    parameter_type = 'nominal'  # can be real

    @classmethod
    def set_parameter_type(cls, pt):
        if pt not in ['nominal', 'real']:
            print('The type can only be "nominal" or "real"!')
            return
        cls.grid_data = cls.grid_parameters[pt]
        cls.parameter_type = pt

    def __init__(self):
        self.strip_polygons = []
        self.strip_shadow_polygons = {}
        self.strip_cache = {}
        self.which_grid = None
        self.num_strips = 0
        self.strip_centers = {}
        self.user_rot_deg = 0
        self.user_phase = 0
        #print('Grid parameter:',self.parameter_type)

    def get_shadow_vertices(self):
        return self.strip_shadow_polygons

    def get_num_strips(self):
        return self.num_strips

        """
        def get_strip0_phase(self, det_idx, which_grid):
        '''get the center of strip 0 
          y=yc+(x-xc)*tan(alpha)
          see Matje's Phd thesis for the definition of phase 
        '''
        xc = sgp.center_coords[key]['x']
        yc = sgp.center_coords[key]['y']
        phase = sgp.real[key][self.phase_key[which_grid]]
        r = abs(yc - xc *
                math.tan(self.alpha)) / math.sqrt(1 + math.tan(self.alpha)**2)
        num_pitchs = int(r / pitch) + 1
        strip0_center_phase = num_pitchs * pitch + real_phase - r - 0.5 * pitch

        # slit center
        return strip0_center_phase
        """

    def config_grid(self,
               det_idx,
               which_grid='front',
               user_phase=0,
               user_rot_deg=0):

        self.det_idx = det_idx
        self.user_phase = user_phase
        self.user_rot_deg = user_rot_deg

        self.which_grid = which_grid
        self.strip_polygons = []
        self.strip_shadow_polygons = {}

        det_id= str(self.det_idx + 1)

        #angle
        rot = 90 - self.grid_data[det_id][
            self.orient_key[which_grid]] + user_rot_deg
        #rot is the orientation as defined in Majte 's phd thesis, with respect to y axis
        self.rot_deg = rot + 180 if rot < 0 else rot
        self.alpha = self.rot_deg * math.pi / 180.  
        #alpha is the orientation of strips with respect to X
        #according to the definition in Matje's Phd thesis, the angle should be with respect to X in in units of rad

        self.theta=self.alpha+math.pi/2
        #the polar angle of the line pedicular to grid strips

        self.slit_width = self.grid_data[det_id][self.slit_key[
            self.parameter_type][which_grid]]
        self.pitch = self.grid_data[det_id][self.pitch_key[which_grid]]
        self.strip_half_width = (self.pitch -
                                 self.slit_width) * 0.5  #half width

        if self.parameter_type != 'nominal':
            #if real grid parameter
            xc = sgp.center_coords[det_id]['x'] 
            yc = sgp.center_coords[det_id]['y']
            #grid center coordinates
            meas_phase = sgp.real[det_id][self.phase_key[which_grid]]
            # measurement was at the slit center

            r = (yc - xc * math.tan(self.alpha)) / math.sqrt(
                1 + math.tan(self.alpha)**2)
            #r can be positive or negative, so dose the frame center phase
            frame_center_phase=math.fmod(r, self.pitch)

            self.phase =  frame_center_phase + meas_phase + user_phase - 0.5 * self.pitch
            #here the phase of strip center is relative to the frame center
            #phase of the center grid
            #0.5*self.pitch is added because the real phase was measured for slit center, we need strip center
        
        else:
            self.phase = user_phase
            #user defined phase if using nominal grid, the default value is 0

        self.strip0_phase = self.phase
        self.frame_width, self.frame_height = sgp.grid_dim[which_grid]
        #grid frame dimensions
        self.frame_half_width, self.frame_half_height = (self.frame_width / 2.,
                                                         self.frame_height /
                                                         2.)

    

    def grid_shadow_contains(self, det_id, which_grid, det_points,
            sun_x, sun_y ,
            user_phase,  user_rot_deg 
            ):
        """
          test if points are in the shadow of grid
          Arguments
          which_grid: str
                can be 'rear' or font
          det_points:  np.ndarray
                 points at detector  for example, [(x0,y0),(x1,y1), ..]

        """
        if not isinstance(det_points, np.ndarray):
            det_points=np.array(det_points)
        self.config_grid(det_id, which_grid, user_phase, user_rot_deg)
        stix_x, stix_y = sun_y, sun_x #rotated by 90 deg
        z = sgp.grid_z.get(which_grid, 0)
        dx = -z * math.tan(arcsec2rad(stix_x))
        dy = -z * math.tan(arcsec2rad(stix_y))
        #offset on detector 
        frame_vtx= np.array(sgp.frame_vertices[self.which_grid])
        frame_x_minmax=(np.min(frame_vtx[:,0]),  np.max(frame_vtx[:,0]))
        frame_y_minmax=(np.min(frame_vtx[:,1]),  np.max(frame_vtx[:,1]))

        is_within_frame=lambda px,py: (frame_x_minmax[0]<px< frame_x_minmax[1] ) and  (frame_y_minmax[0]<py< frame_y_minmax[1] )


        pnts_x=det_points[:,0]-dx
        pnts_y=det_points[:,1]-dy

        num_in_shadow=0
        num_out_shadow=0
        num=pnts_x.size

        in_shadow = np.zeros_like(pnts_x)

        for i in range(num):
            px,py=pnts_x[i],pnts_y[i]
            if not is_within_frame(px,py):
                in_shadow[i]=1
                continue
            #dist_to_strip0=  abs (py-px*math.tan(self.alpha))/math.sqrt(1+math.tan(alpha)**2) -self.strip0_phase
            #below is correct
            dist_to_strip0= abs((py-px*math.tan(self.alpha))/math.sqrt(1+math.tan(self.alpha)**2) -self.strip0_phase)
            dist_to_strip_center=math.fmod(dist_to_strip0, self.pitch) #distance to the closest strip center
            in_shadow[i] = 1 if dist_to_strip_center < self.strip_half_width else 0
            #point lines in a strip
        return in_shadow







    def create(self,
               det_idx,
               which_grid='front',
               user_phase=0,
               user_rot_deg=0):

        if det_idx in [8, 9]:
            return
        cache_key = (det_idx, which_grid, user_phase, user_rot_deg)
        if cache_key in self.strip_cache:
            self.strip_polygons = self.strip_cache[cache_key]
            return

        self.config_grid(det_idx, which_grid, user_phase, user_rot_deg)
        self.create_strips()
        #create strips, polygons 

        self.strip_cache[cache_key] = self.strip_polygons

    def project(self, sun_x_arcsec=0, sun_y_arcsec=0):
        """
            project grid frame and grids to detector
        """
        #print(f'projection {self.which_grid}')
        if not any(
            [sun_x_arcsec, sun_y_arcsec, self.user_rot_deg, self.user_phase]):
            self.strip_shadow_polygons = {
                'strips': self.strip_polygons,
                'frame': np.array(sgp.frame_vertices[self.which_grid]),
                'sun_x': sun_x_arcsec,
                'sun_y': sun_y_arcsec
            }
            return self.strip_shadow_polygons

        new_vertices = []

        stix_x, stix_y = sun_y_arcsec, sun_x_arcsec
        z = sgp.grid_z.get(self.which_grid, 0)
        dx = -z * math.tan(arcsec2rad(stix_x))
        dy = -z * math.tan(arcsec2rad(stix_y))

        for strip in self.strip_polygons:
            strip_pnts = []
            for pnt in strip:
                strip_pnts.append((pnt[0] + dx, pnt[1] + dy))
            new_vertices.append(strip_pnts)

        self.strip_shadow_polygons = {
            'strips':
            np.array(new_vertices),
            'frame':
            np.array([(p[0] + dx, p[1] + dy)
                      for p in sgp.frame_vertices[self.which_grid]]),
            'sun_x':
            sun_x_arcsec,
            'sun_y':
            sun_y_arcsec
        }
        return self.strip_shadow_polygons

        

        '''def is_in_shadow(self, x,y):
        """
            test a point at detector surface if it is in shadow of any strips 
        """
        pnt=(x,y)
        
        for ply in self.strip_shadow_polygons['strips']:
            print(type(ply))
            poly_path = Path(ply)
            #if poly_path.contains_point(pnt):
            return True
        return False
        '''

    def intersect_frame(self, i):
        """
         calculate coordinates of lines intersecting with frame for the i-th strip
        """
        if self.rot_deg == 0 or self.rot_deg == 180:
            vts = []
            x = self.strip0_phase + self.pitch * i
            if x + self.strip_half_width >= -self.frame_half_width and x - self.strip_half_width <= self.frame_half_width:
                vts = [[x - self.strip_half_width, -self.frame_half_height],
                       [x - self.strip_half_width, self.frame_half_height],
                       [x + self.strip_half_width, self.frame_half_height],
                       [x + self.strip_half_width, -self.frame_half_height],
                       [x - self.strip_half_width, -self.frame_half_height]]
                for v in vts:
                    if v[0] > self.frame_half_width:
                        v[0] = self.frame_half_width
                    if v[0] < -self.frame_half_width:
                        v[0] = -self.frame_half_width

            #print('strip:',x, self.which_grid, self.strip_half_width, self.frame_half_height, self.frame_half_width, vts)
            return vts, (x, self.frame_half_height)

        strip_center_phase = self.strip0_phase + i * self.pitch
        strip_i_left = strip_center_phase - self.strip_half_width
        strip_i_right = strip_center_phase + self.strip_half_width

        #angle of the line pedicular with grids  with respect to x
        pol2xy = lambda r: (r * math.cos(self.theta), r * math.sin(self.theta)
                            )  # perpendicular to the strips
        #polar coordinates to Cartesian 
        #polar angle is alpha+/-pi/2, where alpha is the angle between strip and x-axis 

        strip_center_xy = pol2xy(strip_center_phase)
        x_left, y_left = pol2xy(strip_i_left)
        x_right, y_right = pol2xy(strip_i_right)

        points_left = self._get_intersecs(x_left, y_left)
        points_right = self._get_intersecs(x_right, y_right)
        #corners=self._get_included_cornners(strip_center_xy, i)
        #corners=[]

        vertices = points_left + points_right  #+corners
        # points interacts with frames


        if len(vertices) < 3:
            return [], strip_center_xy
        vts = sorted(vertices, key=self._clockwiseangle_and_distance)
        if vts:
            vts.append(vts[0])  #close polygon
        return vts, strip_center_xy

    def _clockwiseangle_and_distance(self, point):
        if not point:
            return []
        origin = [0, 0]
        refvec = [0, 1]
        vector = [point[0] - origin[0], point[1] - origin[1]]
        # Length of vector: ||v||
        lenvector = math.hypot(vector[0], vector[1])
        # If length is zero there is no angle
        if lenvector == 0:
            return -math.pi, 0
        # Normalize vector: v/||v||
        normalized = [vector[0] / lenvector, vector[1] / lenvector]
        dotprod = normalized[0] * refvec[0] + normalized[1] * refvec[
            1]  # x1*x2 + y1*y2
        diffprod = refvec[1] * normalized[0] - refvec[0] * normalized[
            1]  # x1*y2 - y1*x2
        angle = math.atan2(diffprod, dotprod)
        # Negative angles represent counter-clockwise angles so we need to subtract them
        # from 2*pi (360 degrees)
        if angle < 0:
            return 2 * math.pi + angle, lenvector
        # I return first the angle because that's the primary sorting criterium
        # but if two vectors have the same angle then the shorter distance should come first.
        return angle, lenvector

    def _fy(self, xx, x0, y0):
        return y0 + (xx - x0) * math.tan(self.alpha)
        # y =
    def _fx(self, yy, x0, y0):
        return (yy - y0) / math.tan(self.alpha) + x0

    def _get_included_cornners(self, strip_center_xy, i=-1):
        x0, y0 = strip_center_xy
        corners = [(-self.frame_half_width, self.frame_half_height),
                   (self.frame_half_width, self.frame_half_height),
                   (self.frame_half_width, -self.frame_half_height),
                   (-self.frame_half_width, -self.frame_half_height)]
        points = []
        for c in corners:
            x, y = c
            d = abs(y0 + (x - x0) * math.atan(self.alpha) -
                    y) / math.sqrt(1 + math.atan(self.alpha)**2)
            #distance to corners
            if d < self.strip_half_width:
                points.append(c)
                #print(i, d, self.strip_half_width)
        return points

    def _get_intersecs(self, x0, y0):
        points = [
            (-self.frame_half_width, self._fy(-self.frame_half_width, x0,
                                              y0)),  #left
            (self._fx(self.frame_half_height, x0,
                      y0), self.frame_half_height),  #top
            (self.frame_half_width, self._fy(self.frame_half_width, x0,
                                             y0)),  #right
            (self._fx(-self.frame_half_height, x0,
                      y0), -self.frame_half_height),  #bottom
        ]
        vs = []
        #check if in the frame
        for p in points:
            if p[0] <= self.frame_half_width and p[
                    0] >= -self.frame_half_width and p[
                        1] >= -self.frame_half_height and p[
                            1] <= self.frame_half_height:
                vs.append(p)

        return vs

    
    def create_strips(self):
        _strip_polygons = []
        i = 0
        self.num_strips = 0
        while True:
            strip_pnts, center = self.intersect_frame(i)
            if not strip_pnts:
                break
            else:
                _strip_polygons.append(strip_pnts)
                self.num_strips += 1
                self.strip_centers[i] = center
            i += 1
        i = -1
        while True:
            strip_pnts, center = self.intersect_frame(i)
            if not strip_pnts:
                break
            else:
                #print(i)
                _strip_polygons.append(strip_pnts)
                self.num_strips += 1
                self.strip_centers[i] = center
            i -= 1

        self.strip_polygons = np.array(_strip_polygons)
        #print(self.strip_polygons)

    def plot(self, ax):
        if ax == None:
            fig, ax = plt.subplots()
        #print(self.strip_shadow_polygons)
        if not self.strip_shadow_polygons:
            return
        for v in self.strip_shadow_polygons['strips']:
            plot_polygons(v, ax, fc='grey', ec='none', alpha=1, lw=1)
        plot_polygons(self.strip_shadow_polygons['frame'],
                      ax,
                      fc='none',
                      ec='black',
                      alpha=1,
                      lw=1)
        ax.set_xlim(-13, 13)
        ax.set_ylim(-13, 13)
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_title(f'Collimator # {self.det_idx+1}')
        ax.set_aspect('equal', 'box')
        if self.debug:
            xc = [p[0] for p in self.strip_centers.values()]
            yc = [p[1] for p in self.strip_centers.values()]
            ax.plot(xc, yc, '.-')
        return ax


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('sim <which_grid> det ')
    else:
        fig, ax = plt.subplots()
        det = int(sys.argv[2])
        grid = StixGrid()
        grid.create(det, which_grid=sys.argv[1], user_phase=0, user_rot_deg=0)
        grid.project()
        grid.plot(ax)
        plt.show()

    #sfreq = Slider(axfreq, 'Freq', 0.1, 30.0, valinit=f0, valstep=delta_f)
    #samp = Slider(axamp, 'Amp', 0.1, 10.0, valinit=a0)
