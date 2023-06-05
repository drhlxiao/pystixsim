import math
import numpy as np
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches


def ply2path(data, ax, center=[0, 0], ec='green', fc='none', alpha=0.6):
    data2 = [(x[0] + center[0], x[1] + center[1]) for x in data]
    if data2[0]!=data2[-1]:
        data2.append(data[-1])
    codes = [Path.LINETO] * len(data2)
    codes[0] = Path.MOVETO
    codes[-1] = Path.CLOSEPOLY
    path = Path(data2, codes)
    patch = patches.PathPatch(path, facecolor=fc, ec=ec, alpha=alpha, lw=1)
    ax.add_patch(patch)
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rect:
    def __init__(self, w, h):
        self.w = w
        self.h = h
def shift_polygon(vertices, dx,dy):
    res=[]
    for v in vertices:
        res.append([v[0]+dx, v[1]+dy])
    return res

class _StixDetector(object):
    def __init__(self, origin=(0, 0)):
        self._origin = origin
        self.pixel_vertices = {}
        self.pixel_polygons = {}
        self.pixel_polygon_mlp_path=[]
        self.pixel_areas = []

        self.create(origin)
        self.random_points=None
    def get_random_points(self,num=100000):
        """
            Generate random points on the detector surface
            0.1 area,
            0.25 open area ratio
            0.25 modulation
        """
        
        x=np.random.uniform(-4.4,4.4,num)
        y=np.random.uniform(-4.6,4.6,num)
        res={i:[] for i in range(12)}
        print("Uncertainty (big pixel %%):", 100/math.sqrt(0.1*num* 0.25 *0.25 ))
        for _x, _y in zip(x,y): 
            pnt=(_x,_y)
            for i, p in enumerate(self.pixel_polygon_mlp_path):
                if p.contains_point(pnt):
                    res[i].append(pnt)
                    break
        return res



    def get_pixel_polygons(self):
        return self.pixel_polygons

    def get_pixel_vertices(self):
        return self.pixel_vertices

    def get_pixel_areas(self):
        return self.pixel_areas

    def create(self, origin=(0, 0)):
        self.pixel_vertices = {}
        self.pixel_polygons = []
        big=Rect(2.15,4.55)
        small=Rect(1.05,0.86)
        bigs=Rect(1.1,0.455)
        dw=2.2 # delta distance
        
        p0=Point(-3.3, 2.3)
        
        p8=Point(-3.85,0)
        
        p0_coord=[ (p0.x - big.w/2, p0.y + big.h/2), 
                   (p0.x + big.w/2, p0.y + big.h/2),
                   (p0.x + big.w/2, p0.y - big.h/2),
                   (p0.x - big.w/2 + bigs.w, p0.y - big.h/2),
                   (p0.x - big.w/2 + bigs.w, p0.y - big.h/2 + bigs.h),
                   (p0.x - big.w/2 , p0.y - big.h/2 + bigs.h),
                   (p0.x - big.w/2, p0.y + big.h/2)]
        p5_coord=[]
        for p in p0_coord:
            p5_coord.append((p[0],-p[1]))
        p8_coord=[(p8.x - small.w/2, p8.y+small.h/2),
                  (p8.x + small.w/2, p8.y+small.h/2),
                  (p8.x + small.w/2, p8.y-small.h/2),
                  (p8.x - small.w/2, p8.y-small.h/2),
               (p8.x - small.w/2, p8.y+small.h/2)
            
        ]
        
      
        
   
        for i in range(4):
            #for j in range(6):
            
            self.pixel_vertices[i] = shift_polygon(p0_coord, dw*i,0)
            

            self.pixel_vertices[i + 4] =shift_polygon(p8_coord, dw*i,0)
          
      
            self.pixel_vertices[i + 8] = shift_polygon(p5_coord, dw*i,0)
        self.pixel_polygons = [
            Polygon(self.pixel_vertices[i]) for i in range(12)
        ]
        self.pixel_polygon_mlp_path = [
            Path(self.pixel_vertices[i]) for i in range(12)
        ]
        self.pixel_areas = np.array([p.area for p in self.pixel_polygons])

    def plot(self, ax=None, ec='green', show=False):
        if not ax:
            fig, ax = plt.subplots()
        for k, v in self.pixel_vertices.items():
            ply2path(v, ax)
        if show:
            plt.show()


StixDetector = _StixDetector()

if __name__=='__main__':
    #res=StixDetector.get_random_points(500000)
    fig,ax=plt.subplots()
    #for k, v in res.items():
    #    print(k, len(v))
    #    v=np.array(v).T
    #    ax.scatter(v[0],v[1],label=f'{k}')
    StixDetector.plot(ax)
    plt.show()
        
