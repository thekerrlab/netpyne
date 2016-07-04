# -*- coding: utf-8 -*-
"""
Created on Fri Jul 01 14:35:19 2016

@author: David Kedziora
"""


from pylab import figure, loadtxt, show, where, arange, subplot, legend, array, text, title
filedir = '/home/cliffk/2016cns/data/'

toplot = [
'trajectories',
#'averrs'
]



#from matplotlib.pyplot import rc 
#rc('font', family='serif') 
#rc('font', serif='Linux Biolinum') 
#rc('font', size=16)

def boxoff(ax):
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')





if 'trajectories' in toplot:

    filesuffices = [0]*2
    filesuffices[0] = '[tar1][(1+1)x5000ms][1x][stdp0][rl1e-4][rand555]'
    filesuffices[1] = '[tar1][(1+1)x5000ms][4x][stdp0][rl1e-4][rand555]'
    factor = 1.0/2.0  # At what fraction of total duration does test start?
    lockradius = 0.04
    dosave = False
    timefactor = 1e3
    
    nfiles = len(filesuffices)
    errdatapair = []
    tdatapair = []
    for fs in filesuffices:
        errdatapair.append(loadtxt(filedir + 'errs' + fs + '.txt'))
        tdatapair.append(loadtxt(filedir + 'armt' + fs + '.txt'))
    
    fig1 = figure(figsize=(10,7))
    fig1.subplots_adjust(right=0.70) # Less space on right
    ax = []
    titles = ['100 sensory neurons', '400 sensory neurons']
    for f in range(nfiles):
        ax.append(subplot(nfiles,1,f+1))
        errdata = array(errdatapair[f])
        tdata = array(tdatapair[f])
        itlist = arange(len(errdata))
        
        teststart = len(tdata[0])*factor + 1
        initerror = errdata[0][teststart]
        testtimestart = tdata[0][teststart]
        testtimeend = tdata[0][-1]
        
        for i in range(len(errdata)):
            intarget = where(errdata[i][teststart:] < lockradius)[0]
            if len(intarget):
                outtarget = where(errdata[i][teststart+intarget[0]:] > lockradius)[0]
                if len(outtarget):
                    errdata[i][teststart+intarget[0]+outtarget[0]:] = errdata[i][teststart+intarget[0]+outtarget[0]-1]
            
            crgb = [float(len(errdata)-i)/float(len(errdata)), 0.0, float(i)/float(len(errdata))]
            ax[f].plot(tdata[i][1:teststart]/timefactor,errdata[i][1:teststart], '-',color=crgb, label='%i'%i, linewidth=2)
            title(titles[f])

        ax[f].set_xlim([tdata[0][0]/timefactor,tdata[0][teststart]/timefactor])
        if f==nfiles-1: ax[f].set_xlabel('Time (s)')
        else: ax[f].set_xticks([])
        ax[f].set_ylabel('Distance to target (m)')
        boxoff(ax[f])
        if f==0:
            text(5.4, 0.42, 'Trial number', fontsize=12)
            legend(loc='upper left', bbox_to_anchor=(1.1, 0.7), frameon=False, fontsize=10)
        if dosave: fig1.savefig('Plots/trainerr' + filesuffices[f] + '.png')
        
        show()




if 'averrs' in toplot:

    filesuffices = []
    scales = [0,1,2,4]
    nscales = len(scales)
    nseeds = 10
    ntrials = 0
    
    errdata = zeros((nscales, nseeds, ))
    for scale in scales:
        for seed in range(10):
    filesuffices[0] = '[tar1][(1+1)x5000ms][1x][stdp0][rl1e-4][rand555]'
    filesuffices[1] = '[tar1][(1+1)x5000ms][4x][stdp0][rl1e-4][rand555]'
    factor = 1.0/2.0  # At what fraction of total duration does test start?
    lockradius = 0.04
    dosave = False
    timefactor = 1e3
    
    nfiles = len(filesuffices)
    errdatapair = []
    tdatapair = []
    for fs in filesuffices:
        errdatapair.append(loadtxt(filedir + 'errs' + fs + '.txt'))
        tdatapair.append(loadtxt(filedir + 'armt' + fs + '.txt'))
    
    fig1 = figure(figsize=(10,7))
    fig1.subplots_adjust(right=0.70) # Less space on right
    ax = []
    titles = ['100 sensory neurons', '400 sensory neurons']
    for f in range(nfiles):
        ax.append(subplot(nfiles,1,f+1))
        errdata = array(errdatapair[f])
        tdata = array(tdatapair[f])
        itlist = arange(len(errdata))
        
        teststart = len(tdata[0])*factor + 1
        initerror = errdata[0][teststart]
        testtimestart = tdata[0][teststart]
        testtimeend = tdata[0][-1]
        
        for i in range(len(errdata)):
            intarget = where(errdata[i][teststart:] < lockradius)[0]
            if len(intarget):
                outtarget = where(errdata[i][teststart+intarget[0]:] > lockradius)[0]
                if len(outtarget):
                    errdata[i][teststart+intarget[0]+outtarget[0]:] = errdata[i][teststart+intarget[0]+outtarget[0]-1]
            
            crgb = [float(len(errdata)-i)/float(len(errdata)), 0.0, float(i)/float(len(errdata))]
            ax[f].plot(tdata[i][1:teststart]/timefactor,errdata[i][1:teststart], '-',color=crgb, label='%i'%i, linewidth=2)
            title(titles[f])

        ax[f].set_xlim([tdata[0][0]/timefactor,tdata[0][teststart]/timefactor])
        if f==nfiles-1: ax[f].set_xlabel('Time (s)')
        else: ax[f].set_xticks([])
        ax[f].set_ylabel('Distance to target (m)')
        boxoff(ax[f])
        if f==0:
            text(5.4, 0.42, 'Trial number', fontsize=12)
            legend(loc='upper left', bbox_to_anchor=(1.1, 0.7), frameon=False, fontsize=10)
        if dosave: fig1.savefig('Plots/trainerr' + filesuffices[f] + '.png')
        
        show()