# -*- coding: utf-8 -*-
"""
Created on Fri Jul 01 14:35:19 2016

@author: David Kedziora
"""

filedir = '/home/cliffk/2016cns/data/'

filesuffix = '[tar1][(1+1)x5000ms][4x][stdp0][rand999]'
# Note: This code only works for (1+1)x...ms and a constant timestep!
factor = 1.0/2.0  # At what fraction of total duration does test start?

lockradius = 0.04
dosave = False

from pylab import figure, loadtxt, show, mean, where, arange

fig1 = figure()
ax1 = fig1.add_subplot(111)
fig2 = figure()
ax2 = fig2.add_subplot(111)
fig3 = figure()
ax3 = fig3.add_subplot(111)
fig4 = figure()
ax4 = fig4.add_subplot(111)
fig5 = figure()
ax5 = fig5.add_subplot(111)
fig6 = figure()
ax6 = fig6.add_subplot(111)

errdata = loadtxt(filedir + 'errs' + filesuffix + '.txt')
tdata = loadtxt(filedir + 'armt' + filesuffix + '.txt')

itlist = arange(len(errdata))

teststart = len(tdata[0])*factor + 1
initerror = errdata[0][teststart]
testtimestart = tdata[0][teststart]
testtimeend = tdata[0][-1]

minerrs = []
mint = []
averrs = []
loct = []

for i in xrange(len(errdata)):
    intarget = where(errdata[i][teststart:] < lockradius)[0]
    if len(intarget):
        loct.append(tdata[i][teststart+intarget[0]])
        outtarget = where(errdata[i][teststart+intarget[0]:] > lockradius)[0]
        if len(outtarget):
            errdata[i][teststart+intarget[0]+outtarget[0]:] = errdata[i][teststart+intarget[0]+outtarget[0]-1]
    else:
        loct.append(0)
        
    
    crgb = [float(len(errdata)-i)/float(len(errdata)), 0.0, float(i)/float(len(errdata))]
    ax1.plot(tdata[i][1:teststart],errdata[i][1:teststart],'-',color=crgb)
    ax2.plot(tdata[i][teststart:],errdata[i][teststart:],'-',color=crgb)
#    for err in errdata[i][teststart:]:
#        if err < initerror/4:
#            print i
#            ax2.plot(tdata[i][teststart:],errdata[i][teststart:],'-',color=crgb)
#            break
    minerrs.append(min(errdata[i][teststart:]))
    mint.append(tdata[i][teststart+where(errdata[i][teststart:] == min(errdata[i][teststart:]))[0][0]])
    averrs.append(mean(errdata[i][teststart:]))
ax3.plot([itlist[0],itlist[-1]],[errdata[0][teststart],errdata[0][teststart]],'r--')
ax3.plot([itlist[0],itlist[-1]],[minerrs[0],minerrs[0]],'b--')
ax3.plot(itlist,minerrs,'k-')
ax4.plot([itlist[0],itlist[-1]],[averrs[0],averrs[0]],'b--')
ax4.plot(itlist,averrs,'k-')
ax5.plot([min(mint),max(mint)],[lockradius,lockradius],'r--')
ax5.plot(mint,minerrs,'ko')
ax6.bar(itlist,loct)

  
ax1.set_xlim([tdata[0][0],tdata[0][teststart]])
ax1.set_xlabel('t (ms)')
ax1.set_ylabel('Training Error')
if dosave: fig1.savefig('Plots/trainerr' + filesuffix + '.png')

ax2.set_xlim([tdata[0][teststart],tdata[0][-1]])
ax2.set_xlabel('t (ms)')
ax2.set_ylabel('Test Error')
if dosave: fig2.savefig('Plots/testerr' + filesuffix + '.png')

ax3.set_xlim([itlist[0],itlist[-1]])
ax3.set_xlabel('Iteration')
ax3.set_ylabel('Minimum Error')
if dosave: fig3.savefig('Plots/minerr' + filesuffix + '.png')

ax4.set_xlim([itlist[0],itlist[-1]])
ax4.set_xlabel('Iteration')
ax4.set_ylabel('Average Test Error')
if dosave: fig4.savefig('Plots/averr' + filesuffix + '.png')

ax5.set_xlim([min(mint),max(mint)])
ax5.set_xlabel('t (ms)')
ax5.set_ylabel('Test Error')
if dosave: fig5.savefig('Plots/locmin' + filesuffix + '.png')

ax6.set_xlim([itlist[0],itlist[-1]+1])
ax6.set_ylim([testtimestart,(int(max(loct)/1000)+1)*1000])
ax6.set_xlabel('Iteration')
ax6.set_ylabel('Time of Lock-On (ms)')
if dosave: fig6.savefig('Plots/timetolock' + filesuffix + '.png')

show()