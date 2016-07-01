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

sim.trainTestID = -1    # Nonzero is a normal run. Zero is a run but with no RL.
sim.sysArgOffset = 0
if 'main.py' in sys.argv:
    sim.sysArgOffset = sys.argv.index('main.py')
if len(sys.argv) > sim.sysArgOffset+1:
    sim.trainTestID = int(sys.argv[1+sim.sysArgOffset])   # The first command line argument should be the number of the training run.
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
sim.setupRecording()              # setup variables to record for each cell (spikes, V traces, etc)

###############################################################################
# Set up virtual arm, proprioceptive/motor encoding and RL
###############################################################################

# Arm parameters
sim.useArm = 1  # include arm in simulation
sim.animArm = 0  # show arm animation
sim.graphsArm = 0  #  plot arm graphs
sim.saveResultsArm = 1  # export arm results
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
if sim.trainTestID != 0:
    sim.useRL = True   # Should be True when not debugging...
else:
    sim.useRL = False
sim.timeoflastRL = -1
sim.RLinterval = 50
sim.minRLerror = 0.002 # minimum error change for RL (m)
sim.targetid = 1 # initial target 
sim.allWeights = [] # list to store weights
sim.weightsfilename = 'weights.txt'  # file to store weights
sim.plotWeights = 0  # plot weights

# Exploratory movements
sim.explorMovs = 1 # exploratory movements (noise to EM pop)
sim.explorMovsRate = 100 # stim max firing rate for motor neurons of specific muscle groups to enforce explor movs
sim.explorMovsDur = 500 # max duration of each excitation to each muscle during exploratory movments init = 1000
sim.timeoflastexplor = -inf # time when last exploratory movement was updated
sim.randseed = 5  # random seed

# reset arm every trial
sim.trialReset = True # whether to reset the arm after every trial time
sim.oneLastReset = False
sim.timeoflastreset = 0 # time when arm was last reseted

# train/test params
sim.gridTrain = False
sim.trialTime = 1*1e3
sim.trainTime = 1 * sim.trialTime
sim.testTime = 1 * sim.trialTime
sim.cfg['duration'] = sim.trainTime + sim.testTime
sim.numTrials = ceil(sim.cfg['duration']/sim.trialTime)
sim.numTargets = 1
sim.targetid = 2 # target to train+test
sim.trialTargets = [sim.targetid]*sim.numTrials #[i%sim.numTargets for i in range(int(sim.numTrials+1))] # set target for each trial
sim.resetids = []

# file suffix corresponding to params
sim.outFileSuffix = '[tar%i][(%i+%i)x%ims][%ix][rand%i%i%i]' % (sim.targetid, int(sim.trainTime/sim.trialTime), int(sim.testTime/sim.trialTime), sim.trialTime, params.netParams['cscale'],params.simConfig['seeds']['conn'],params.simConfig['seeds']['stim'],params.simConfig['seeds']['loc'])
print 'File suffix: ' + sim.outFileSuffix

###############################################################################
# Overwrite network weights from file if it exists
###############################################################################

netWeightsFilename = 'netWeights' + sim.outFileSuffix + '.pkl'
params.simConfig['filename'] = 'netWeights' + sim.outFileSuffix     # Overwrite params filename.

# An initial run in a runsim bash sequence resets netWeights file.
if sim.trainTestID == 0:
    from os import remove
    try:
        remove(netWeightsFilename)
        print('Removed %s' % netWeightsFilename)
    except:
        pass

print('Trying to load net weights from file...')
dataloaded = False
try:
    import pickle
    data = pickle.load(open(netWeightsFilename))
    dataloaded = True
except Exception as E:
    print('No weight data has been loaded for this network')
    print(E)
if dataloaded:
    allgids = [data['net']['cells'][i]['gid'] for i in range(len(data['net']['cells']))]
    for lid,gid in enumerate(sim.net.lid2gid):
        datacell = data['net']['cells'][allgids.index(gid)] # DOESN'T WORK because data['net']['cells'][gid]['gid'] is NOT gid
        simcell = sim.net.cells[lid]
        for co,conn in enumerate(datacell['conns']):
            simcell.conns[co]['weight'] = conn['weight']
            simcell.conns[co]['hNetcon'].weight[0] = conn['weight']
    print('...success!')

###############################################################################
# Continue setup
###############################################################################

# create Arm class and setup
if sim.useArm:
    sim.arm = Arm(sim.animArm, sim.graphsArm, sim.saveResultsArm)
    sim.arm.targetid = 0
    sim.arm.setup(sim)  # pass framework as argument

# Function to run at intervals during simulation
def runArm(t):
    # turn off RL and explor movs for last testing trial 
    if t >= sim.trainTime:
        sim.useRL = False
        sim.explorMovs = False

    if sim.useArm:
        sim.arm.run(t, sim) # run virtual arm apparatus (calculate command, move arm, feedback)
    if sim.useRL and (t - sim.timeoflastRL >= sim.RLinterval): # if time for next RL
        sim.timeoflastRL = h.t
        vec = h.Vector()
        if sim.rank == 0:
            critic = sim.arm.RLcritic(h.t) # get critic signal (-1, 0 or 1)
            sim.pc.broadcast(vec.from_python([critic]), 0) # convert python list to hoc vector for broadcast data received from arm
            
        else: # other workers
            sim.pc.broadcast(vec, 0)
            critic = vec.to_python()[0]
        if critic != 0: # if critic signal indicates punishment (-1) or reward (+1)
            print 't=',t,'- adjusting weights based on RL critic value:', critic
            for cell in sim.net.cells:
                for conn in cell.conns:
                    STDPmech = conn.get('hSTDP')  # check if has STDP mechanism
                    if STDPmech:   # run stdp.mod method to update syn weights based on RLprint cell.gid
                        STDPmech.reward_punish(float(critic))

        # store weight changes
        sim.allWeights.append([]) # Save this time
        for cell in sim.net.cells:
            for conn in cell.conns:
                if 'hSTDP' in conn:
                    sim.allWeights[-1].append(float(conn['hNetcon'].weight[0])) # save weight only for STDP conns

    
    
def saveWeights(sim):
    ''' Save the weights for each plastic synapse '''
    with open(sim.weightsfilename,'w') as fid:
        for weightdata in sim.allWeights:
            fid.write('%0.0f' % weightdata[0]) # Time
            for i in range(1,len(weightdata)): fid.write('\t%0.8f' % weightdata[i])
            fid.write('\n')
    print('Saved weights as %s' % sim.weightsfilename)    


def plotWeights():
    from pylab import figure, loadtxt, xlabel, ylabel, xlim, ylim, show, pcolor, array, colorbar

    figure()
    weightdata = loadtxt(sim.weightsfilename)
    weightdataT=map(list, zip(*weightdata))
    vmax = max([max(row) for row in weightdata])
    vmin = min([min(row) for row in weightdata])
    pcolor(array(weightdataT), cmap='hot_r', vmin=vmin, vmax=vmax)
    xlim((0,len(weightdata)))
    ylim((0,len(weightdata[0])))
    xlabel('Time (weight updates)')
    ylabel('Synaptic connection id')
    colorbar()
    show()
    

###############################################################################
# Run Network with virtual arm
###############################################################################

sim.runSimWithIntervalFunc(sim.updateInterval, runArm)        # run parallel Neuron simulation

# Update cell-conn data with final weights.
for cell in sim.net.cells:
    for conn in cell.conns:
#        print('%f vs %f' % (conn['weight'], conn['hNetcon'].weight[0]))
        conn['weight'] = conn['hNetcon'].weight[0]

sim.gatherData()                  # gather spiking data and cell info from each node
sim.saveData()                    # save params, cell info and sim output to file (pickle,mat,txt,etc)
sim.analysis.plotData()               # plot spike raster
sim.arm.close(sim)

if sim.plotWeights:
    try:
        saveWeights(sim) 
        plotWeights()
    except:
        print('Plotting/saving weights failed')

if sim.trainTestID > -1: sys.exit()  # exit nrniv console in the case of sequential runs