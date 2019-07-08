

from neuron import h # Open NEURON

## Create basic AdExp neuron with default parameters
def createAdExp(section, **kwargs):
    cell = h.AdExp(0.5, sec=section) # Create a new AdExp neuron at location 0 (doesn't matter where) in h.Section() "section"
    cell.rpeso = 30
    cell.mNMDA = 1.0 # Was 0
    cell.v0_block = -55
    cell.k_block = 5
    cell.mAMPA = 1
    cell.iEXT = 50
    cell.tau_w = 280
    cell.G_l = 10
    cell.a = 2
    cell.C = 281
    cell.E_l = -70.6
    cell.V_thre = -50.4
    cell.Delta_T = 2
    cell.V_reset = -70.6
    cell.b = 40
    cell.label = -1
    return cell

dummy = h.Section()

class AdExpCell(): 
    """
    ADEXP
    
    Python wrapper for an AdExp neuron.
    
    Usage example:
        from neuron import h
        from adexp import createcell
        dummy = h.Section()
        cell = createAdExp(dummy)
    
    Version: 2019jul03 by cliffk
    """
    def __init__(self, host=None, cellid=-1):
        self.type=type
        if host is None:  # need to set up a sec for this
            self.sec=h.Section(name='AdExp'+str(cellid))
            self.sec.L, self.sec.diam = 6.3, 5 # empirically tuned
            self.adx = createAdExp(self.sec) 
        else: 
            self.sec = dummy
            self.adx = createAdExp(self.sec) 