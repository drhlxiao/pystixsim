#!/usr/bin/env python
# coding: utf-8

# In[1]:


#STIX simulator


# In[2]:


import sys
sys.path.append('.')
import glob
import numpy as np
import math
from matplotlib import animation

from core.grid_parameters import NOMINAL as ngd


import matplotlib.pyplot as plt



from core.stix_imager import StixImager
from core import stix_grid as sgd

steps=20

plt.close('all')
def simulate(det_idx, sun_x, sun_y, 
             user_phase_front, user_rot_deg_front,
             user_phase_rear, user_rot_deg_rear, compute_pattern, debug=False, nominal_grid=True
            ):
    #plt.close('all')
    #if not nominal_grid:
    sgd.StixGrid.debug=debug
      
    sgd.StixGrid.set_parameter_type('real' if not nominal_grid else 'nominal')
    
    im=StixImager(det_idx)

    
    im.create(sun_x, sun_y, user_phase_front, user_rot_deg_front, user_phase_rear, 
              user_rot_deg_rear, compute_pattern=True)
    im.plot()
    #plt.show()



MAX_ROT=2
NUM_PIXELS_FOR_FITS=8

def getChi2(pat, exp, exp_error):
    sum1=sum(pat)
    sum2=sum(exp)
    chi2=0
    norm=sum2/sum1
    for i in range(NUM_PIXELS_FOR_FITS):
        dy=norm*pat[i] -exp[i]
        chi2+= dy*dy/(exp_error[i]*exp_error[i])
    #return sum([sum2*x/sum1-for x in pat ])
    
    return math.sqrt(chi2), norm

def find_solution(det_idx, filename, steps, scan_type, save_fig=False): 
    with open(filename) as f:
        sun_x, sun_y=[float(x) for x in f.readline().split()] 
        pixel_data=[l.split() for l in f.readlines()]
        exp_data=[[float(x) for x in l] for l in pixel_data if l[0]==str(det_idx)]
    exp=[]
    exp_error=[]
    for p in exp_data:
        exp.append(p[2])
        exp_error.append(p[3])
        
    im=StixImager(det_idx)
   
    max_phase=ngd[str(det_idx+1)]['FrontPitch']
    chi2map=np.zeros((steps,steps))
    current_chi2min=math.inf
    min_values={}
   
    
    phase_front_space=np.linspace(0,max_phase, steps)
    phase_rear_space=np.linspace(0,max_phase,steps)
    rot_front_space=np.linspace(-MAX_ROT,MAX_ROT, steps)
    rot_rear_space=np.linspace(-MAX_ROT,MAX_ROT,steps)
    i=0
    rear_rot=0
    front_rot=0    
    phase_rear=0
    phase_front=0
    if scan_type=='phase':
        for i,phase_front in enumerate(phase_front_space):
            print(f'Detector {det_idx}, Completed:  {int(i/steps*100)} %')
            for j,phase_rear in enumerate(phase_rear_space):


                shadow=im.create(sun_x, sun_y, phase_front, front_rot, 
                             phase_rear, rear_rot, compute_pattern=True)
                pattern, ratio=shadow['pattern'], shadow['ratio']
                chi2, norm_factor=getChi2(pattern, exp, exp_error)
                if save_fig:
                    fig, (ax,ax2,ax3,ax4)=im.plot()
                    #ax2.plot(exp[0:8]/norm_factor)
                    ax2.lines[-1].set_label('sim')
                    ax2.plot(exp/norm_factor, label='obs')
                    ax3.set_title('simulated pattern')
                    
                    fig.suptitle(f'phase front:{phase_front:0.2f}, phase_rear:{phase_rear:.2f}')
                    plt.savefig(f'phase_{i}_{j}.svg')
                    
                chi2map[j][i]=chi2
                if chi2<current_chi2min:
                    min_values={'min_pat':pattern,
                    'min_factor':norm_factor,
                    'min_rot_front':front_rot,
                    'min_rot_rear':rear_rot,
                    'phase_front':phase_front,
                    'phase_rear':phase_rear}
                    current_chi2min=chi2
    else:
        for i,phase_front in enumerate(phase_front_space):
            print(f'Completed:  {int(i/steps*100)} %')
            for j, front_rot in enumerate(rot_front_space):
           
                shadow=im.create(sun_x, sun_y, phase_front, front_rot, 
                             phase_rear, rear_rot, compute_pattern=True)
                pattern, ratio=shadow['pattern'], shadow['ratio']
                chi2, norm_factor=getChi2(pattern, exp, exp_error)
                if save_fig:
                    fig, (ax,ax2,ax3,ax4)=im.plot()
                    #ax2.plot(exp[0:8]/norm_factor)
                    ax2.lines[-1].set_label('sim')
                    ax2.plot(exp/norm_factor, label='obs')
                    ax3.set_title('simulated pattern')
                    
                    fig.suptitle(f'phase:{phase_front}, rot:{front_rot:.2f}')
                    plt.savefig(f'rot_{i}_{j}.svg')
               
                chi2map[j][i]=chi2
                if chi2<current_chi2min:
                    min_values={'min_pat':pattern,
                    'min_factor':norm_factor,
                    'min_rot_front':front_rot,
                    'min_rot_rear':rear_rot,
                    'phase_front':phase_front,
                    'phase_rear':phase_rear}
                    current_chi2min=chi2
        
            

    result={
        'chi2':chi2map,
        'exp':exp,
        'exp_error':exp_error
    }
    result.update(min_values)
    return result





test_files=glob.glob('exp_data/*.txt')



def phase_fit(det_idx,steps,exp_data, scan_type, nominal_grid=True, save_fig=False):
    sgd.StixGrid.set_parameter_type('real' if not nominal_grid else 'nominal')
    result=find_solution(det_idx, exp_data,steps, scan_type, save_fig)
    #fig, (ax,ax2)=plt.subplots(1,2)
    fig = plt.figure(figsize=(9,3))
    ax=fig.add_subplot(1,2,1)
    ax2=fig.add_subplot(1,2,2)
    x=range(8)
    norm_pat=np.array(result['min_pat'])*result['min_factor']
    ax.errorbar(x, result['exp'][0:8], xerr=0, yerr=result['exp_error'][0:8], label='Measurements')
    ax.plot(x, norm_pat[0:8],label='Best match')
    ax.legend()
    #plt.title(f'detector {det_idx+1}, front phase:{result["phase_front"]:03f}, rear phase: {result["phase_rear"]:03f} ')
    ax.set_title(f'Det #{det_idx+1}, front phase:{result["phase_front"]:.2f}, rear phase: {result["phase_rear"]:.2f},rot:{result["min_rot_front"]:.2f}')
    ax.set_xlabel('Pixel')
    ax.set_ylabel('Counts')
    #plt.show()
    #fig=plt.figure()
    
    if scan_type=='phase':
        (X,Y)=np.meshgrid( np.linspace(0, 360, steps),np.linspace(0, 360, steps) )
    else:
        (X,Y)=np.meshgrid( np.linspace(0, 360, steps),np.linspace(-MAX_ROT, MAX_ROT, steps) )
    #print(X)
    pchi=ax2.pcolormesh(X, Y, result['chi2'])
    ax2.set_xlabel('Front grid phase (deg)')
    fig.colorbar(pchi, ax=ax2)
    ax2.set_title('Chi2')
    ylabel='Rear grid phase (deg)' if scan_type=='phase' else 'Front rot. correction (deg)'
    ax2.set_ylabel(ylabel)
    
    return result
    #plt.ylabel('Front rot. correction (deg)')

test_files=glob.glob('exp_data/*.txt')
from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('All_det_fit.pdf')
exp_data=test_files[0]
det_ids=[i for i in range(0,32) if i not in [8,9,10,11,12,16,17,18]]

results={}
min_phases=[0]*32
min_rot=[0]*32
def save_results():
    fig,(ax1,ax2)=plt.subplots(2,1)
    ax1.plot(np.arange(32), min_rot)
    ax1.set_xlabel('Detector Index')
    ax1.set_ylabel('Angle (deg)')
    ax1.set_title('Best fit rotation angle correction')

    ax2.plot(np.arange(32),min_phases)
    ax2.set_xlabel('Detector Index')
    ax2.set_ylabel('Phase (mm)')
    ax2.set_title('Best fit phase correction')
    pp.savefig()
    pp.close()
    print('Done')


def process(det_idx):
    #for det_idx in det_ids:
    print(det_idx)
    try:
        result= phase_fit(det_idx,steps,exp_data, scan_type='rot', nominal_grid=False, save_fig=False)
        results[det_idx]=result
        min_rot[det_idx]=result['min_rot_front']
        min_phases[det_idx]=result['phase_front']
        #plt.show()
        pp.savefig()
    except KeyboardInterrupt: 
        save_results()
    return result

from multiprocessing import Pool
agents = 7
try:
    with Pool(processes=agents) as pool:
        result = pool.map(process, [19,20,25])
except KeyboardInterrupt: 
    save_results()

save_results()

