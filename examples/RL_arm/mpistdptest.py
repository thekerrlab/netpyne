# -*- coding: utf-8 -*-
"""
"Minimal" example of STDP with...out MPI.

@author: David Kedziora
"""

from neuron import h, init, run
from pylab import figure, plot, show, array, rand, arange
from optima import tic, toc

duration = 1000
ncells = 1000
connprob = 0.2
h.dt = 0.5


## Create basic Izhikevich neuron with default parameters. Not to be called directly, only via one of the other functions.
def createcell(sec, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid):
    cell = h.Izhi(0,sec=sec)    # Create a new Izhikevich neuron at location 0 (doesn't matter where) in h.Section() "section".
    cell.C = C                      # Capacitance.
    cell.k = k
    cell.vr = vr                    # Resting membrane potential.
    cell.vt = vt                    # Membrane threshold.
    cell.vpeak = vpeak              # Peak voltage.
    cell.a = a
    cell.b = b
    cell.c = c
    cell.d = d
    cell.celltype = celltype        # Set cell celltype (used for setting celltype-specific dynamics).
    cell.cellid = cellid            # Cell ID for keeping track which cell this is.
    return cell

## Excitatory layer 2/3 pyramidal cell.
def pyramidal(sec, C=100, k=3, vr=-60, vt=-50, vpeak=30, a=0.01, b=5, c=-60, d=400, celltype=1, cellid=-1):
    cell = createcell(sec, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
    return cell

## Create cells
cells = []
secs = []
allcells = arange(ncells)
for c in allcells:
    sec = h.Section() # Create a dummy section to put the point processes in
    cell = pyramidal(sec) # Create the cells
    secs.append(sec)
    cells.append(cell)
    



## Create synapses
threshold = 40 # Set voltage threshold
delay = 1 # Set connection delay
singlesyns = []
stdpmechs = []
presyns = []
pstsyns = []
precells = allcells[rand(ncells)<connprob]
pstcells = allcells[rand(ncells)<connprob]
for c1 in precells:
    for c2 in pstcells:
        if c1!=c2:
            singlesyn = h.NetCon(cells[c1],cells[c2], threshold, delay, 0.5) # Create a connection between the cells
            singlesyn.weight[0]=10
            stdpmech = h.STDP(0,sec=secs[c1]) # Create the STDP mechanism
            stdpmech.verbose = 0.0
            delay = 1 # Set connection delay
            presyn = h.NetCon(cells[c1],stdpmech, threshold, delay, 1) # Feed presynaptic spikes to the STDP mechanism -- must have weight >0
            pstsyn = h.NetCon(cells[c2],stdpmech, threshold, delay, -1) # Feed postsynaptic spikes to the STDP mechanism -- must have weight <0
            h.setpointer(singlesyn._ref_weight[0],'synweight',stdpmech) # Point the STDP mechanism to the connection weight
            singlesyns.append(singlesyn)
            stdpmechs.append(stdpmech)
            presyns.append(presyn)
            pstsyns.append(pstsyn)

sources = []
sourceconns = []
for c in allcells:
    source = h.NetStim()                    # Create a NetStim
    source.interval = 1#(float(50)/1e3)**-1   # Interval between spikes
    source.number = duration                      # Number of spikes
    source.noise = 1                        # Fractional noise in timing
    source.start = 25                       # Delay 
    
    sourceconn = h.NetCon(source, cells[c])
    sourceconn.weight[0] = 1
    sources.append(source)
    sourceconns.append(sourceconn)




tvec = h.Vector()
wvec = h.Vector()
tvec.record(h._ref_t)
wvec.record(singlesyn._ref_weight[0])

evec1 = h.Vector()
evec2 = h.Vector()
ptr1 = cells[0]._ref_V
ptr2 = cells[1]._ref_V
evec1.record(ptr1)
evec2.record(ptr2)



init()
t = tic()
run(duration)
toc(t)

figure(1)
plot(array(tvec),array(wvec),'r')
#ylim(-0.1,1.1)
figure(2)
#plot(array(tvec),array(evec1))
plot(array(tvec),array(evec2))
show()
