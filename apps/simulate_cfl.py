import sys
sys.path.append('.')
sys.path.append('..')
import numpy as np
import math
from core import stix_cfl
import matplotlib.pyplot as plt
from shapely import speedups
speedups.enable()
from multiprocessing import Process
import time
import pickle

cfl=stix_cfl.CFL()

#num=2*int((3600/7.)**2)
num=500000

#R_SUN=1900
#rho = np.sqrt(np.random.uniform(0, 1, num))
#phi = np.random.uniform(0, 2*np.pi, num)
#X = R_SUN * rho* np.cos(phi)
#Y = R_SUN*rho* np.sin(phi)

_X=np.linspace(-2000,2000,801)
_Y=np.linspace(-2000,2000,801)

X,Y=np.meshgrid(_X,_Y)
X=X.reshape(-1)
Y=Y.reshape(-1)

lut=np.zeros((Y.size,14))
ns=0
for x, y in zip(X,Y):
    pattern=cfl.get_pattern(x,y)
    lut[ns,0]=x
    lut[ns,1]=y
    lut[ns,2:]=pattern['pattern']
    if ns%1000==0:
        print(ns)
    ns+=1
np.savez_compressed('skylut.npz',lut=lut, x=_X, y=_Y)
print("saved to skylut.npz")



