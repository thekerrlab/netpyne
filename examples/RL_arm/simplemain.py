import params  # import parameters file
from netpyne import sim  # import netpyne init module
from arm import Arm
from neuron import h
from time import time, sleep
from pylab import radians, inf, ceil
import sys


###############################################################################
# Set up Network
###############################################################################

sim.initialize(                
      simConfig = params.simConfig, 
      netParams = params.netParams)  
sim.net.createPops()                  # instantiate network populations
sim.net.createCells()                 # instantiate network cells based on defined populations
sim.net.connectCells()                # create connections between cells based on params
sim.setupRecording()              # setup variables to record for each cell (spikes, V traces, etc)


# train/test params
sim.cfg['duration'] = 0.5*1e3



###############################################################################
# Run Network with virtual arm
###############################################################################

sim.runSim()        # run parallel Neuron simulation  
sim.gatherData()                  # gather spiking data and cell info from each node