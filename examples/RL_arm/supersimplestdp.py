# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 08:58:47 2016

@author: David Kedziora
"""

from neuron import h, init, run
from pylab import figure, plot, ylim, show, array

duration = 4000

## Create basic Izhikevich neuron with default parameters. Not to be called directly, only via one of the other functions.
def createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid):
    cell = h.Izhi(0,sec=section)    # Create a new Izhikevich neuron at location 0 (doesn't matter where) in h.Section() "section".
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
def pyramidal(section, C=100, k=3, vr=-60, vt=-50, vpeak=30, a=0.01, b=5, c=-60, d=400, celltype=1, cellid=-1):
    cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
    return cell

## Create cells
ncells = 2
cells = []
seclist = []
#for c in range(ncells): cells.append(h.IntFire4(0,sec=dummy)) # Create the cells
for c in range(ncells):
    dummy = h.Section() # Create a dummy section to put the point processes in
#    cells.append(pyramidal(section=dummy)) # Create the cells
    cells.append(h.Izhi2007b(0,sec=dummy)) # Create the cells
#    cells.append(h.IntFire4(0,sec=dummy)) # Create the cells
    seclist.append(dummy)




## Create synapses
threshold = 40 # Set voltage threshold
delay = 1 # Set connection delay
singlesyn = h.NetCon(cells[0],cells[1], threshold, delay, 0.5) # Create a connection between the cells
#singlesyn.weight[1]=10
singlesyn.weight[0]=10
stdpmech = h.STDP(0,sec=dummy) # Create the STDP mechanism
stdpmech.verbose = 1.0
delay = 1 # Set connection delay
presyn = h.NetCon(cells[0],stdpmech, threshold, delay, 1) # Feed presynaptic spikes to the STDP mechanism -- must have weight >0
pstsyn = h.NetCon(cells[1],stdpmech, threshold, delay, -1) # Feed postsynaptic spikes to the STDP mechanism -- must have weight <0
h.setpointer(singlesyn._ref_weight[0],'synweight',stdpmech) # Point the STDP mechanism to the connection weight

source = h.NetStim()                    # Create a NetStim
source.interval = 1#(float(50)/1e3)**-1   # Interval between spikes
source.number = duration                      # Number of spikes
source.noise = 1                        # Fractional noise in timing
source.start = 25                       # Delay 
        
connection = h.NetCon(source, cells[0])
connection.weight[0] = 1




tvec = h.Vector()
wvec = h.Vector()
tvec.record(h._ref_t)
wvec.record(singlesyn._ref_weight[0])

evec1 = h.Vector()
evec2 = h.Vector()
ptr1 = seclist[0](0.5)._ref_v
ptr2 = seclist[1](0.5)._ref_v
#ptr1 = cells[0]._ref_V
#ptr2 = cells[1]._ref_V
evec1.record(ptr1)
evec2.record(ptr2)

init()
run(duration)

figure(1)
plot(array(tvec),array(wvec),'r')
#ylim(-0.1,1.1)
figure(2)
plot(array(tvec),array(evec1))
plot(array(tvec),array(evec2))
show()
