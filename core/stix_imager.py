import sys
sys.path.append('.')
import math
import numpy as np
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
import matplotlib.pyplot as plt

from core.stix_detector import StixDetector
from core.stix_grid import StixGrid
from core import stix_cfl

from core import grid_parameters as sgp

TOP_BIG_PIXEL_PATTERN_ONLY=True
#set to true if only calculate pattern for big pixels


def StixImager(det_idx):
    if det_idx == 8:
        return stix_cfl.CFL()
    elif det_idx != 9:
        return StixNormalImager(det_idx)


class StixNormalImager(object):
    def __init__(self, det_idx):
        self.det_idx = det_idx

        self.detector = StixDetector
        self.det_pixel_polygons = self.detector.get_pixel_polygons()
        self.pixel_vertices = self.detector.get_pixel_vertices()
        self.front_grid = StixGrid()
        self.rear_grid = StixGrid()
        self.pixel_areas = self.detector.get_pixel_areas()
        self.front_grid.create(det_idx, 'front', 0, 0)
        self.rear_grid.create(det_idx, 'rear', 0, 0)
        self.pattern = []
        self.shadow_polygons = {}

        self.cache = {}
    """
    def create(self,
               sun_x=0,
               sun_y=0,
               user_phase_front=0,
               user_rot_deg_front=0,
               user_phase_rear=0,
               user_rot_deg_rear=0,
               compute_pattern=True):

        self.front_grid.create(self.det_idx, 'front', user_phase_front,
                               user_rot_deg_front)
        self.rear_grid.create(self.det_idx, 'rear', user_phase_rear,
                              user_rot_deg_rear)

        front_shadow_vertices = self.front_grid.projection(sun_x, sun_y)
        rear_shadow_vertices = self.rear_grid.projection(sun_x, sun_y)

        #def compute_pattern(det, det_pixel_vertices, prj_front, prj_rear):
        self.open_ratio = 0
        self.pattern = np.zeros(12)
        shadow_area = np.zeros(12)

        if compute_pattern:
            all_polygons = []
            for g in front_shadow_vertices['strips']:
                all_polygons.append(Polygon(g))
            for g in rear_shadow_vertices['strips']:
                all_polygons.append(Polygon(g))
            u = unary_union(all_polygons)
            shadow = []
            for ip, p in enumerate(self.det_pixel_polygons):
                insec = p.intersection(u)
                #if insec:
                #    #shadow.append(insec)
                if insec:
                    shadow_area[ip] = insec.area
            self.pattern = self.pixel_areas - shadow_area
            self.open_ratio = np.sum(self.pattern) / np.sum(self.pixel_areas)

        self.shadow_polygons = {
            'detector': self.pixel_vertices,
            'front': front_shadow_vertices,
            'rear': rear_shadow_vertices,
            'ratio': self.open_ratio,
            'pattern': self.pattern
        }

        #self.cache[cache_key]=self.shadow_polygons
        return self.shadow_polygons
        """
    
    def get_pattern_fast(self,
               sun_x=0,
               sun_y=0,
               user_phase_front=0,
               user_rot_deg_front=0,
               user_phase_rear=0,
               user_rot_deg_rear=0, num_samples=10000):
        res=self.detector.get_random_points(num_samples)
        pattern = np.zeros(12)
        for k, v in res.items():
            if k>4:
                continue
            in_front_shadow=self.front_grid.grid_shadow_contains(self.det_idx, 'front', v,
            sun_x, sun_y, user_phase_front,  user_rot_deg_front) 
            in_rear_shadow=self.rear_grid.grid_shadow_contains(self.det_idx, 'rear', v,
            sun_x, sun_y, user_phase_rear,  user_rot_deg_rear) 
            in_any_shadow=in_front_shadow+in_rear_shadow
            pattern[k]= (in_any_shadow==0).sum() /in_any_shadow.size
        return {'pattern':pattern, 'in_shadow':in_any_shadow}

            


    def create(self,
               sun_x=0,
               sun_y=0,
               user_phase_front=0,
               user_rot_deg_front=0,
               user_phase_rear=0,
               user_rot_deg_rear=0,
               compute_pattern=True):
        #method: mc, using Monte Carlo
        #topo: using topo

        self.front_grid.create(self.det_idx, 'front', user_phase_front,
                               user_rot_deg_front)
        self.rear_grid.create(self.det_idx, 'rear', user_phase_rear,
                              user_rot_deg_rear)

        front_shadow_vertices = self.front_grid.project(sun_x, sun_y)
        rear_shadow_vertices = self.rear_grid.project(sun_x, sun_y)

        #def compute_pattern(det, det_pixel_vertices, prj_front, prj_rear):
        self.open_ratio = 0
        self.pattern = np.zeros(12)
        shadow_area = np.zeros(12)

        if compute_pattern:
            """
            if method=='mc':
                res=self.detector.get_random_points(100000)
                for k, v in res.items():
                    in_shadow=False
                    _x,_y=v[0],v[1]
                    for pnt in v:
                        if self.front_grid.is_in_shadow(_x,_y):
                            in_shadow=True
                            break
                        if self.rear_grid.is_in_shadow(_x,_y):
                            in_shadow=True
                            break
                        if not in_shadow:
                            self.pattern[k]+=1
                    num_points=len(v)
                    self.pattern[k]/=num_points

            else:
            """
            all_polygons = []
            pixel_ply=self.det_pixel_polygons[0:4] if TOP_BIG_PIXEL_PATTERN_ONLY else self.det_pixel_polygons

            for ip, p in enumerate(pixel_ply):
                intersects=[]
                for g in front_shadow_vertices['strips']:
                    ps=Polygon(g)
                    up=p.intersection(ps)
                    if up:
                        intersects.append(up)
                for g in rear_shadow_vertices['strips']:
                    ps=Polygon(g)
                    up=p.intersection(ps)
                    if up:
                        intersects.append(up)
                u = unary_union(intersects)
                shadow_area[ip] = u.area

            self.pattern = self.pixel_areas - shadow_area

            if TOP_BIG_PIXEL_PATTERN_ONLY:
                self.pattern[4:12]=0
                self.open_ratio = np.sum(self.pattern) / np.sum(self.pixel_areas)
            else:
                self.open_ratio = np.sum(self.pattern) / np.sum(self.pixel_areas[0:4])


        self.shadow_polygons = {
            'detector': self.pixel_vertices,
            'front': front_shadow_vertices,
            'rear': rear_shadow_vertices,
            'ratio': self.open_ratio,
            'pattern': self.pattern
        }

        #self.cache[cache_key]=self.shadow_polygons
        return self.shadow_polygons

    project = create


    def plot(self,
             fig=None,
             ax=None,
             ax2=None,
             ax3=None,
             ax4=None,
             draw_front=True,
             draw_rear=True,
             draw_det=True):
        #draw: big or visibility
        if not ax or not fig:
            if self.shadow_polygons['pattern'] is not None:
                fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(2,
                                                            2,
                                                            figsize=(9, 8))
            else:
                fig, ax = plt.subplots()

        #print(self.shadow_polygons)

        if ax:
            if draw_front:
                self.front_grid.plot(ax)
            if draw_rear:
                self.rear_grid.plot(ax)
            if draw_det:
                self.detector.plot(ax)
            ax.set_title(f'Collimator # {self.det_idx+1}')
            ax.set_aspect('equal', 'box')

        if self.shadow_polygons['pattern'] is not None:
            pattern = self.shadow_polygons['pattern']

            if ax2:
                ax2.plot(range(12), pattern)
                ax2.set_ylabel('Open area (mm2)')
                ax2.set_xlabel('Pixel')
                ax2.set_title('Open area')
                print(f'Open area percentage {self.open_ratio*100:.1f}%')

            if ax3:
                x = [0, 1, 2, 3]
                vis_real = pattern[2] - pattern[0]
                vis_img = pattern[3] - pattern[1]
                ax3.plot(x, pattern[0:4], label='big top')
                print(
                    f'VIS:{vis_real:.2E}+{vis_img:.2E}i, {self.open_ratio*100:.1f}% open'
                )
                ax3.plot(x, pattern[4:8], label='big bottom')
                ax3.plot(x, 10 * np.array(pattern[8:12]), label='small x 10')
                ax3.set_ylabel('Open area (mm2)')
                ax3.set_xlabel('Pixel')
                ax3.legend()
            if ax4:

                unsym = [pattern[i + 4] - pattern[i] for i in range(4)]
                ax4.plot(x, unsym)
                ax4.set_title('Pattern difference between top and bottom')
                ax4.set_xlabel('Pixel')
                ax4.set_ylabel('Open area diff. (mm2)')
            plt.tight_layout()
        return fig, (ax, ax2, ax3, ax4)


def get_pattern(sun_x=0, sun_y=0, nominal_grid=True):
    StixGrid.set_parameter_type('real' if not nominal_grid else 'nominal')
    StixGrid.debug=False
    pattern=np.zeros((32,12))
    for i in range(32):
        if i==9:
            continue
        im=StixImager(i)
        pat=im.create(sun_x, sun_y)
        #if i!=8:
        #    pat=im.get_pattern_fast(sun_x,sun_y)
        #else:
        #    pat=im.create(sun_x, sun_y)

        pattern[i]=pat['pattern']
    return pattern

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print('sim det')
    elif len(sys.argv) == 2:
        im = StixImager(int(sys.argv[1]))
        im.create()
        im.plot()
        plt.show()
    else:
        get_pattern()


    #sfreq = Slider(axfreq, 'Freq', 0.1, 30.0, valinit=f0, valstep=delta_f)
    #samp = Slider(axamp, 'Amp', 0.1, 10.0, valinit=a0)
