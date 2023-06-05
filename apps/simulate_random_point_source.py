import sys
sys.path.append('.')
sys.path.append('..')
import numpy as np
import math
from core import stix_imager
import matplotlib.pyplot as plt
from shapely import speedups
speedups.enable()
import time
from multiprocessing import Pool

CPU_CORES=4

filename='stix_imager_grid_simulations.csv'
fo=open(filename,'a')
ns=0
def worker(loc):
    global ns
    x,y=loc[0],loc[1]
    print(f'{ns}, {x},{y}')
    pattern=stix_imager.get_pattern(x,y)
    pattern=pattern.reshape(-1)
    csv_data=f'{x},{y},'+','.join([str(x) for x in pattern])+'\n'
    fo.write(csv_data)
    fo.flush()
    ns+=1


def simulate():
    #num=100000):
    R_SUN=3600
    #rho = np.sqrt(np.random.uniform(0, 1, num))
    #phi = np.random.uniform(0, 2*np.pi, num)
    #X = R_SUN * rho* np.cos(phi)
    #Y = R_SUN*rho* np.sin(phi)
    num=201
    _X=np.linspace(-100, 100, num)
    _Y=np.linspace(-100, 100, num)
    X,Y=np.meshgrid(_X,_Y)
    X=X.reshape(-1)
    Y=Y.reshape(-1)
    pool = Pool(processes=CPU_CORES)
    locs=[(x,y)  for x, y in zip(X,Y)]
    pool.map(worker, locs)
    pool.start()

    pool.join()
    print("All threads finished.")
    


    #plt.scatter(X, Y, s = 4)
    #plt.show()
    #return X,Y

simulate()
    
