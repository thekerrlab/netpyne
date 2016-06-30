import params  # import parameters file
from netpyne import sim  # import netpyne init module
from arm import Arm
from neuron import h
from time import time, sleep
from pylab import radians, inf, ceil
import sys

###############################################################################
# Deal with command line args
###############################################################################

sim.trainTestID = 0
if len(sys.argv) > 1:
    sim.trainTestID = int(sys.argv[1])   # The first command line argument should be the number of the training run.
    print("Training run: %i" % sim.trainTestID)

###############################################################################
# Set up Network
###############################################################################

sim.initialize(                
      simConfig = params.simConfig, 
      netParams = params.netParams)  
sim.net.createPops()                  # instantiate network populations
sim.net.createCells()                 # instantiate network cells based on defined populations
sim.net.connectCells()                # create connections between cells based on params
#sim.setupRecording()              # setup variables to record for each cell (spikes, V traces, etc)



###############################################################################
# Load existing data if it exists
###############################################################################
#try:
#    print('Trying to load data from file...')
#    import pickle
#    filename = 'simdata.pkl'
#    data = pickle.load(open(filename))
#    for ce,cell in enumerate(data['net']['cells']):
#        for co,conn in enumerate(cell['conns']):
#            sim.net.cells[ce].conns[co]['weight'] = conn['weight']
#    print('...success!')
#except Exception as E:
#    print('Data not loaded from file')
#    raise E
    


###############################################################################
# Set up virtual arm, proprioceptive/motor encoding and RL
###############################################################################

# Arm parameters
sim.useArm = 0  # include arm in simulation
sim.animArm = 0  # show arm animation
sim.graphsArm = 0  #  plot arm graphs
sim.updateInterval = 20  # delay between arm updated (ms)
sim.initArmMovement = 50  # time at which to start moving arm (ms)
sim.armLen = [0.4634 - 0.173, 0.7169 - 0.4634] # elbow - shoulder from MSM;radioulnar - elbow from MSM;  
sim.startAng = [0.62,1.53] # starting shoulder and elbow angles (rad) = natural rest position
sim.targetDist = 0.15 # target distance from center (15 cm)

# Propriocpetive encoding
allCellTags = sim.gatherAllCellTags()
sim.pop_sh = [gid for gid,tags in allCellTags.iteritems() if tags['popLabel'] == 'Psh']
sim.pop_el = [gid for gid,tags in allCellTags.iteritems() if tags['popLabel'] == 'Pel']
sim.minPval = radians(-30) 
sim.maxPval = radians(135)
sim.minPrate = 0.01
sim.maxPrate = 100

# Motor encoding
sim.nMuscles = 4 # number of muscles
motorGids = [gid for gid,tags in allCellTags.iteritems() if tags['popLabel'] == 'EM']
cellsPerMuscle = len(motorGids) / sim.nMuscles
sim.motorCmdCellRange = [motorGids[i:i+cellsPerMuscle] for i in xrange(0, len(motorGids), cellsPerMuscle)]  # cell gids of motor output to each muscle
sim.cmdmaxrate = 120  # value to normalize motor command num spikes
sim.cmdtimewin = 50  # window to sum spikes of motor commands
sim.antagInh = 1  # inhibition from antagonic muscle

# RL
sim.useRL = 1
sim.timeoflastRL = -1
sim.RLinterval = 50
sim.minRLerror = 0.002 # minimum error change for RL (m)

# Exploratory movements
sim.randseed = 5  # random seed


# train/test params
sim.cfg['duration'] = 0.5*1e3



###############################################################################
# Run Network with virtual arm
###############################################################################

sim.runSim()        # run parallel Neuron simulation  
sim.gatherData()                  # gather spiking data and cell info from each node