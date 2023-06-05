import matplotlib.path as mplPath
import numpy as np

def mlp():
    inn=0
    outn=0
    for i in range(100):
        poly_path = mplPath.Path(np.array([[190, 50],
                                            [50, 500],
                                            [500, 310],
                                            [310, 190]]))
        for j in range(1000):
            point = (200, 100)
            poly_path.contains_point(point)
            point = (1200, 1000)
            poly_path.contains_point(point)

    print('done')

mlp()
