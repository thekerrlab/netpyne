# -*- coding: utf-8 -*-
"""
Created on Sun Jul  3 11:24:49 2016

@author: cliffk
"""

# To be run after running main.py
#from main import sim # Doesn't work

from optima import alpinecolormap
import matplotlib.pyplot as plt
plt.rcParams['image.cmap'] = 'viridis'
#plt.register_cmap(name='alpine', data=alpinecolormap())
#plt.set_cmap(alpinecolormap())
sim.analysis.plotConn(include=['allCells'], logscale=True)
#plt.set_cmap(alpinecolormap())
#plt.rcParams['image.cmap'] = 'gray'

#sim.analysis.plot2Dnet()