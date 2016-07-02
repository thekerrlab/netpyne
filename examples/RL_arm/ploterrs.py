# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 11:13:23 2016

@author: cliffk
"""

from pylab import loadtxt, subplot, shape, plot
from glob import glob
armtfiles = glob('armt*.txt')
errsfiles = glob('errs*.txt')

nfiles = len(armtfiles)
for f in range(nfiles):
    print('Loading %s...' % errsfiles[f])
    armt = loadtxt(armtfiles[f])
    errs = loadtxt(errsfiles[f])
    
    subplot(nfiles,1,f+1)
    for tr in range(shape(errs)[0]):
        plot(armt[tr,:],errs[tr,:])

print('Done.')