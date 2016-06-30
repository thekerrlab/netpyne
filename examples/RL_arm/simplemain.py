import simpleparams  # import parameters file
from netpyne import sim  # import netpyne init module


###############################################################################
# Set up Network
###############################################################################

sim.initialize(                
      simConfig = simpleparams.simConfig, 
      netParams = simpleparams.netParams)  
sim.net.createPops()                  # instantiate network populations
sim.net.createCells()                 # instantiate network cells based on defined populations
sim.net.connectCells()                # create connections between cells based on params
sim.setupRecording()              # setup variables to record for each cell (spikes, V traces, etc)


###############################################################################
# Run Network with virtual arm
###############################################################################

sim.runSim()        # run parallel Neuron simulation  
sim.gatherData()                  # gather spiking data and cell info from each node