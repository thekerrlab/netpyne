"""
analysis/info.py

Functions to plot and analyze information theory-related results

Contributors: salvadordura@gmail.com
"""
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

try:
    basestring
except NameError:
    basestring = str
    
from builtins import zip
from future import standard_library
standard_library.install_aliases()
from netpyne import __gui__

if __gui__:
    import matplotlib.pyplot as plt
import numpy as np
from .utils import exception, _saveFigData, _showFigure, getCellsInclude


# -------------------------------------------------------------------------------------------------------------------
## Calculate normalized transfer entropy
# -------------------------------------------------------------------------------------------------------------------
@exception
def nTE(cells1 = [], cells2 = [], spks1 = None, spks2 = None, timeRange = None, binSize = 20, numShuffle = 30):
    ''' 
    Calculate normalized transfer entropy
        - cells1 (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Subset of cells from which to obtain spike train 1 (default: [])
        - cells2 (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Subset of cells from which to obtain spike train 1 (default: [])
        - spks1 (list): Spike train 1; list of spike times; if omitted then obtains spikes from cells1 (default: None)
        - spks2 (list): Spike train 2; list of spike times; if omitted then obtains spikes from cells2 (default: None)
        - timeRange ([min, max]): Range of time to calculate nTE in ms (default: [0,cfg.duration])
        - binSize (int): Bin size used to convert spike times into histogram 
        - numShuffle (int): Number of times to shuffle spike train 1 to calculate TEshuffled; note: nTE = (TE - TEShuffled)/H(X2F|X2P)

        - Returns nTE (float): normalized transfer entropy 
    '''

    from neuron import h
    import netpyne
    from .. import sim
    import os
            
    root = os.path.dirname(netpyne.__file__)
    
    if 'nte' not in dir(h): 
        try: 
            print(' Warning: support/nte.mod not compiled; attempting to compile from %s via "nrnivmodl support"'%(root))
            os.system('cd ' + root + '; nrnivmodl support')
            from neuron import load_mechanisms
            load_mechanisms(root)
            print(' Compilation of support folder mod files successful')
        except:
            print(' Error compiling support folder mod files')
            return

    h.load_file(root+'/support/nte.hoc') # nTE code (also requires support/net.mod)
    
    if not spks1:  # if doesnt contain a list of spk times, obtain from cells specified
        cells, cellGids, netStimPops = getCellsInclude(cells1)
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkts = [spkt for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]
            except:
                spkts = []
        else: 
            spkts = []

        # Add NetStim spikes
        spkts = list(spkts)
        numNetStims = 0
        for netStimPop in netStimPops:
            if 'stims' in sim.allSimData:
                cellStims = [cellStim for cell,cellStim in sim.allSimData['stims'].items() if netStimPop in cellStim]
                if len(cellStims) > 0:
                    spktsNew = [spkt for cellStim in cellStims for spkt in cellStim[netStimPop] ]
                    spkts.extend(spktsNew)
                    numNetStims += len(cellStims)

        spks1 = list(spkts)

    if not spks2:  # if doesnt contain a list of spk times, obtain from cells specified
        cells, cellGids, netStimPops = getCellsInclude(cells2)
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkts = [spkt for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]
            except:
                spkts = []
        else: 
            spkts = []

        # Add NetStim spikes
        spkts = list(spkts)
        numNetStims = 0
        for netStimPop in netStimPops:
            if 'stims' in sim.allSimData:
                cellStims = [cellStim for cell,cellStim in sim.allSimData['stims'].items() if netStimPop in cellStim]
                if len(cellStims) > 0:
                    spktsNew = [spkt for cellStim in cellStims for spkt in cellStim[netStimPop] ]
                    spkts.extend(spktsNew)
                    numNetStims += len(cellStims)

        spks2 = list(spkts)

    # time range
    if getattr(sim, 'cfg', None):
        timeRange = [0,sim.cfg.duration]
    else:
        timeRange = [0, max(spks1+spks2)]

    inputVec = h.Vector()
    outputVec = h.Vector()
    histo1 = np.histogram(spks1, bins = np.arange(timeRange[0], timeRange[1], binSize))
    histoCount1 = histo1[0] 
    histo2 = np.histogram(spks2, bins = np.arange(timeRange[0], timeRange[1], binSize))
    histoCount2 = histo2[0] 

    inputVec.from_python(histoCount1)
    outputVec.from_python(histoCount2)
    out = h.normte(inputVec, outputVec, numShuffle)
    TE, H, nTE, _, _ = out.to_python()
    return nTE


# -------------------------------------------------------------------------------------------------------------------
## Calculate granger causality
# -------------------------------------------------------------------------------------------------------------------
@exception
def granger(cells1=[], cells2=[], spks1=None, spks2=None, label1='spkTrain1', label2='spkTrain2', timeRange=None, binSize=5, testGranger=False,
    plotFig = True, saveData = None, saveFig = None, showFig = True):
    ''' 
    Calculate and optionally plot Granger Causality 
        - cells1 (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Subset of cells from which to obtain spike train 1 (default: [])
        - cells2 (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Subset of cells from which to obtain spike train 2 (default: [])
        - spks1 (list): Spike train 1; list of spike times; if omitted then obtains spikes from cells1 (default: None)
        - spks2 (list): Spike train 2; list of spike times; if omitted then obtains spikes from cells2 (default: None)
        - label1 (string): Label for spike train 1 to use in plot
        - label2 (string): Label for spike train 2 to use in plot
        - timeRange ([min, max]): Range of time to calculate nTE in ms (default: [0,cfg.duration])
        - binSize (int): Bin size used to convert spike times into histogram 
        - plotFig (True|False): Whether to plot a figure showing Granger Causality Fx2y and Fy2x
        - saveData (None|'fileName'): File name where to save the final data used to generate the figure (default: None)
        - saveFig (None|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)(default: None)
        - showFig (True|False): Whether to show the figure or not;
            if set to True uses filename from simConfig (default: None)

        - Returns 
            F: list of freqs
            Fx2y: causality measure from x to y 
            Fy2x: causality from y to x 
            Fxy: instantaneous causality between x and y 
            fig: Figure handle 
    '''
    
    from .. import sim
    import numpy as np
    from netpyne.support.bsmart import pwcausalr

    if not spks1:  # if doesnt contain a list of spk times, obtain from cells specified
        cells, cellGids, netStimPops = getCellsInclude(cells1)
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkts = [spkt for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]
            except:
                spkts = []
        else: 
            spkts = []

        # Add NetStim spikes
        spkts = list(spkts)
        numNetStims = 0
        for netStimPop in netStimPops:
            if 'stims' in sim.allSimData:
                cellStims = [cellStim for cell,cellStim in sim.allSimData['stims'].items() if netStimPop in cellStim]
                if len(cellStims) > 0:
                    spktsNew = [spkt for cellStim in cellStims for spkt in cellStim[netStimPop] ]
                    spkts.extend(spktsNew)
                    numNetStims += len(cellStims)

        spks1 = list(spkts)

    if not spks2:  # if doesnt contain a list of spk times, obtain from cells specified
        cells, cellGids, netStimPops = getCellsInclude(cells2)
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkts = [spkt for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]
            except:
                spkts = []
        else: 
            spkts = []

        # Add NetStim spikes
        spkts = list(spkts)
        numNetStims = 0
        for netStimPop in netStimPops:
            if 'stims' in sim.allSimData:
                cellStims = [cellStim for cell,cellStim in sim.allSimData['stims'].items() if netStimPop in cellStim]
                if len(cellStims) > 0:
                    spktsNew = [spkt for cellStim in cellStims for spkt in cellStim[netStimPop] ]
                    spkts.extend(spktsNew)
                    numNetStims += len(cellStims)

        spks2 = list(spkts)


    # time range
    if timeRange is None:
        if getattr(sim, 'cfg', None):
            timeRange = [0,sim.cfg.duration]
        else:
            timeRange = [0, max(spks1+spks2)]

    histo1 = np.histogram(spks1, bins = np.arange(timeRange[0], timeRange[1], binSize))
    histoCount1 = histo1[0] 

    histo2 = np.histogram(spks2, bins = np.arange(timeRange[0], timeRange[1], binSize))
    histoCount2 = histo2[0] 

    fs = int(1000/binSize)
    F,pp,cohe,Fx2y,Fy2x,Fxy = pwcausalr(np.array([histoCount1, histoCount2]), 1, len(histoCount1), 10, fs, int(fs/2))


    # check reliability
    if testGranger:
        import scipy
        ''' Option 1: granger causality tests -- not sure how to interpret results
        try:
            from statsmodels.tsa.stattools import grangercausalitytests as gt
        except:
            print('To test Granger results please install the statsmodel package: "pip install statsmodel"')
            exit()

        tests = gt(np.array([histoCount1, histoCount2]).T, maxlag=10)
        '''

        # do N=25 shuffles of histoCount2
        Nshuffle = 50
        x2yShuffleMaxValues = []
        y2xShuffleMaxValues = []
        histoCount2Shuffled = np.array(histoCount2)
        for ishuffle in range(Nshuffle):
            # for each calculate max Granger value (starting at freq index 1) 
            np.random.shuffle(histoCount2Shuffled)
            _, _, _, Fx2yShuff, Fy2xShuff, _ = pwcausalr(np.array([histoCount1, histoCount2Shuffled]), 1, len(histoCount1), 10, fs, int(fs / 2))
            x2yShuffleMaxValues.append(max(Fx2yShuff[0][1:]))
            y2xShuffleMaxValues.append(max(Fy2xShuff[0][1:]))

        # calculate z-score 
        # |z| > 1.65 = p-value < 0.1 = confidence interval 90% 
        # |z| > 1.96 = p-value < 0.05 = confidence interval 95% 
        # |z| > 2.58 = p-value < 0.01 = confidence interval 99% 
        # https://pro.arcgis.com/en/pro-app/tool-reference/spatial-statistics/what-is-a-z-score-what-is-a-p-value.htm

        # calculate mean and std
        x2yMean = np.mean(x2yShuffleMaxValues)
        x2yStd = np.std(x2yShuffleMaxValues)
        x2yZscore = abs(np.max(Fx2y[0][1:]) - x2yMean) / x2yStd
        x2yPvalue = scipy.stats.norm.sf(x2yZscore)

        y2xMean = np.mean(y2xShuffleMaxValues)
        y2xStd = np.std(y2xShuffleMaxValues)
        y2xZscore = abs(np.max(Fy2x[0][1:]) - y2xMean) / y2xStd
        y2xPvalue = scipy.stats.norm.sf(x2yZscore)



    # plot granger
    fig = -1
    if plotFig:
        fig = plt.figure()
        plt.plot(F, Fy2x[0], label = label2 + ' -> ' + label1)
        plt.plot(F, Fx2y[0], 'r', label = label1 + ' -> ' + label2)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Granger Causality')
        plt.legend()
        
        # save figure data
        if saveData:
            figData = {'cells1': cells1, 'cells2': cells2, 'spks1': cells1, 'spks2': cells2, 'binSize': binSize, 'Fy2x': Fy2x[0], 'Fx2y': Fx2y[0], 
            'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
        
            _saveFigData(figData, saveData, '2Dnet')
     
        # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_'+'2Dnet.png'
            plt.savefig(filename)

        # show fig 
        if showFig: _showFigure()

    if testGranger:
        return fig, {'F': F, 'Fx2y': Fx2y[0], 'Fy2x': Fy2x[0], 'Fxy': Fxy[0],'MaxFx2yZscore': x2yZscore,'MaxFy2xZscore': y2xZscore, 'MaxFx2yPvalue': x2yPvalue,'MaxFy2xPvalue': y2xPvalue}
    else:
        return fig, {'F': F, 'Fx2y': Fx2y[0], 'Fy2x': Fy2x[0], 'Fxy': Fxy[0]}

