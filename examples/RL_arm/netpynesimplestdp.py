
###############################################################################
### Set up connection parameters
###############################################################################


connParams = []  

# Background and stims
connParams.append(
    {'label': 'backgroundE',
    'preTags': {'popLabel': 'background'}, 'postTags': {'popLabel': 'E'}, # background -> Exc
    'connFunc': 'fullConn',
    'weight': 0.00005, 
    'delay': 'uniform(1,5)',
    'syn': 'NMDA'})  


# Excitatory
connParams.append(
    {'label': 'E->E',
    'preTags': {'popLabel': 'E'}, 'postTags': {'popLabel': 'E'},  # ES -> ES (plastic)
    'weight': 5,      
    'probability': 1.0,              
    'delay': 5,     
    'syn': 'AMPA'}) 


###############################################################################
### NETWORK PARAMETERS
###############################################################################

netParams = {}  # dictionary to store sets of network parameters

# Cell properties list
netParams['scaleConnWeight'] = 0.00001 # Connection weight scale factor -- 

# Izhi cell params (used in cell properties)
izhiParams = {}
izhiParams['RS'] = {'_type':'Izhi2007b', 'C':100, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}

# Cell properties list
netParams['cellParams'] = []

## RS Izhi cell params
cellRule = {'label': 'RS_Izhi', 'conditions': {'cellType': 'RS', 'cellModel': 'Izhi2007b'}, 'sections': {}}
soma = {'geom': {}, 'pointps':{}, 'syns': {}}  #  soma
soma['geom'] = {'diam': 6.3, 'L': 5}
soma['pointps']['Izhi'] = izhiParams['RS'] 
cellRule['sections'] = {'soma': soma}  # add sections to dict
netParams['cellParams'].append(cellRule)  # add dict to list of cell properties


# Synaptic mechanism parameters
netParams['synMechParams'] = []
netParams['synMechParams'].append({'label': 'AMPA', 'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}) # AMPA
netParams['synMechParams'].append({'label': 'NMDA', 'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 1.50, 'e': 0}) # NMDA
netParams['synMechParams'].append({'label': 'GABA', 'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}) # GABAA


# Population parameters
netParams['popParams'] = []  # create list of populations - each item will contain dict with pop params
netParams['popParams'].append({'popLabel': 'E','cellModel': 'Izhi2007b', 'cellType': 'RS', 'numCells':   int(2)}) # add dict with params for this pop 
netParams['popParams'].append({'popLabel': 'background', 'cellModel': 'NetStim', 'rate': 100, 'noise': 0.5})  # background inputs

# Connectivity parameters
netParams['connParams'] = connParams

# STDP
choice = 'allE' # Choices: 'all', 'none', 'allE', 'allEM', 'allES', 'EtoES'; default 'EtoES'
STDPparams = {'hebbwt': 0.000001, 'antiwt':-0.0000013, 'wmax': 50, 'RLon': 1 , 'RLhebbwt': 0.01, 'RLantiwt': -0.0123, 
              'tauhebb': 1000, 'RLwindhebb': 50, 'useRLexp': 1, 'softthresh': 0, 'verbose':1}

# Loop over, assigning STDP rules
addplasticity = []
for i,connParam in enumerate(netParams['connParams']):
    if choice=='all':     doadd = True
    elif choice=='none':  doadd = False
    elif choice=='allE':  doadd = connParam['preTags']['popLabel']=='E'
    else: raise Exception('Invalid choice for STDP connections')
    if doadd: addplasticity.append(i) # Yes, conditional met: add this connParam

# Loop over the ones we identified plasticity needs to be added to
for i in addplasticity:
    netParams['connParams'][i]['plasticity'] = {'mech': 'STDP', 'params': STDPparams}



###############################################################################
### SIMULATION PARAMETERS
###############################################################################

simConfig = {}  # dictionary to store simConfig

# Simulation parameters
simConfig['duration'] = 0.5*1e3 # Duration of the simulation, in ms
simConfig['dt'] = 0.1 # Internal integration timestep to use
simConfig['randseed'] = 1 # Random seed to use
simConfig['createNEURONObj'] = True  # create HOC objects when instantiating network
simConfig['createPyStruct'] = True  # create Python structure (simulator-independent) when instantiating network
simConfig['timing'] = True  # show timing  and save to file
simConfig['verbose'] = 1 # show detailed messages 


# Recording 
simConfig['recordCells'] = []  # list of cells to record from 
simConfig['recordTraces'] = {}
simConfig['recordStim'] = False  # record spikes of cell stims
simConfig['recordStep'] = 1.0 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig['filename'] = 'simdata'  # Set file output name
simConfig['saveFileStep'] = 1000 # step size in ms to save data to disk
simConfig['savePickle'] = False # Whether or not to write spikes etc. to a .mat file
simConfig['saveJson'] = False # Whether or not to write spikes etc. to a .mat file
simConfig['saveMat'] = False # Whether or not to write spikes etc. to a .mat file
simConfig['saveTxt'] = False # save spikes and conn to txt file
simConfig['saveDpk'] = False # save to a .dpk pickled file


# Analysis and plotting 
simConfig['plotRaster'] = True # Whether or not to plot a raster
simConfig['plotCells'] = [] # ['Pel', 'Psh', 'ES', 'EM', 'IM', 'IS']  # plot recorded traces for this list of cells
simConfig['plotLFPSpectrum'] = False # plot power spectral density
simConfig['maxspikestoplot'] = 3e8 # Maximum number of spikes to plot
simConfig['plotConn'] = False # whether to plot conn matrix
simConfig['plotWeightChanges'] = False # whether to plot weight changes (shown in conn matrix)
simConfig['plot3dArch'] = False # plot 3d architecture
simConfig['plot2Dnet'] = True



from netpyne import sim  # import netpyne init module

###############################################################################
# Set up Network
###############################################################################

sim.updateInterval = 10.0
sim.initialize(simConfig=simConfig, netParams=netParams)  
sim.net.createPops()                  # instantiate network populations
sim.net.createCells()                 # instantiate network cells based on defined populations
sim.net.connectCells()                # create connections between cells based on params
sim.setupRecording()              # setup variables to record for each cell (spikes, V traces, etc)



###############################################################################
# Save weights
###############################################################################
sim.allWeights = []
sim.weightsfilename = 'weights.txt'
wtind = 0
RL = 1
critic = -1.0
def storeweights(t):
    if RL:
        for cell in sim.net.cells:
            for conn in cell.conns:
                STDPmech = conn.get('hSTDP')  # check if has STDP mechanism
                if STDPmech:   # run stdp.mod method to update syn weights based on RL
                    STDPmech.reward_punish(float(critic))

    sim.allWeights.append([t]) # Save this time
    for cell in sim.net.cells:
        for conn in cell.conns:
            sim.allWeights[-1].append(float(conn['hNetcon'].weight[wtind])) # Remove duplicates, I think -- WARNING, not sure
    
def saveWeights(sim):
    ''' Save the weights for each plastic synapse '''
    with open(sim.weightsfilename,'w') as fid:
        for weightdata in sim.allWeights:
            fid.write('%0.0f' % weightdata[0]) # Time
            for i in range(1,len(weightdata)): fid.write('\t%0.8f' % weightdata[i])
            fid.write('\n')
    print('Saved weights as %s' % sim.weightsfilename)    


def plotWeights():
    eps = 1e-9
    from pylab import figure, loadtxt, plot, subplot, xlabel, ylabel, ylim,show
    figure()
    
    subplot(211)
    weightdata = loadtxt(sim.weightsfilename)
    for i in range(1,len(weightdata[0])): # Loop over each synpse
        plot(weightdata[:,0], weightdata[:,i])
    ylim((0,ylim()[1]))
    xlabel('Time (ms)')
    ylabel('Synaptic weight (abs.)')
    
    subplot(212)
    for i in range(1,len(weightdata[0])): # Loop over each synpse
        plot(weightdata[:,0], (weightdata[:,i]+eps)/(weightdata[-1,i]+eps)) # For some reason 0 is empty for many
    #ylim((0,ylim()[1]))
    xlabel('Time (ms)')
    ylabel('Weight (relative to final)')
    show()
    


    
###############################################################################
# Run Network with virtual arm
###############################################################################
sim.runSimWithIntervalFunc(sim.updateInterval, storeweights) # run parallel Neuron simulation  
sim.gatherData()                  # gather spiking data and cell info from each node
sim.saveData()                    # save params, cell info and sim output to file (pickle,mat,txt,etc)
sim.analysis.plotData()               # plot spike raster
saveWeights(sim)
plotWeights()

